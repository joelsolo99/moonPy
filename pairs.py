import os
import random
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog,
    QMessageBox, QHBoxLayout, QSpinBox, QListWidget, QApplication
)
from PyQt5.QtCore import Qt
import sys


class Pairs(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Random Image Pair Generator")

        # Default input folder to '3_mooney' relative to cwd if exists, else None
        default_folder = os.path.join(os.getcwd(), "3_mooney")
        self.folder_path = default_folder if os.path.isdir(default_folder) else None

        # Hold current pairs for re-randomising
        self.current_pairs_a_man_b_nat = []
        self.current_pairs_b_man_a_nat = []

        self.init_ui()

        # If default folder exists, update label and enable generate button
        if self.folder_path:
            rel_path = os.path.relpath(self.folder_path, os.getcwd())
            self.folder_label.setText(rel_path)
            self.gen_btn.setEnabled(True)

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_label = QLabel(
            "Select folder containing images.\n"
            "Pairs will be formed between files with prefixes:\n"
            "- 'a_man_' paired with 'b_nat_'\n"
            "- 'b_man_' paired with 'a_nat_'\n"
            "Pairs saved as pairs.csv in sibling folder '4_super_pairings'."
        )
        self.info_label.setWordWrap(True)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_btn = QPushButton("Select Folder")
        self.folder_btn.clicked.connect(self.select_folder)
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("color: gray;")
        folder_layout.addWidget(self.folder_btn)
        folder_layout.addWidget(self.folder_label)

        # Random seed input
        seed_layout = QHBoxLayout()
        seed_label = QLabel("Random Seed:")
        self.seed_spin = QSpinBox()
        self.seed_spin.setMinimum(0)
        self.seed_spin.setMaximum(999999999)
        self.seed_spin.setValue(12345)
        seed_layout.addWidget(seed_label)
        seed_layout.addWidget(self.seed_spin)

        # Buttons: Generate & Re-randomise
        btn_layout = QHBoxLayout()
        self.gen_btn = QPushButton("Generate Pairs")
        self.gen_btn.setEnabled(False)
        self.gen_btn.clicked.connect(self.generate_pairs)

        self.rerand_btn = QPushButton("Re-randomise Pairs")
        self.rerand_btn.setEnabled(False)
        self.rerand_btn.clicked.connect(self.rerandomise_pairs)

        btn_layout.addWidget(self.gen_btn)
        btn_layout.addWidget(self.rerand_btn)

        # List widget to show pairs
        self.pair_list_widget = QListWidget()

        # Done button to close widget (not app)
        self.done_btn = QPushButton("Done")
        self.done_btn.clicked.connect(self.close)

        layout.addWidget(self.info_label)
        layout.addLayout(folder_layout)
        layout.addLayout(seed_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Current pairs:"))
        layout.addWidget(self.pair_list_widget)
        layout.addWidget(self.done_btn)

        self.setLayout(layout)
        self.resize(700, 400)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing Images")
        if folder:
            self.folder_path = folder
            rel_path = os.path.relpath(folder, os.getcwd())
            self.folder_label.setText(rel_path)
            self.gen_btn.setEnabled(True)
            self.rerand_btn.setEnabled(False)  # No pairs yet
            self.pair_list_widget.clear()

    def generate_pairs(self):
        if not self.folder_path:
            QMessageBox.warning(self, "Error", "No folder selected.")
            return

        # List jpg files in folder
        file_list = [f for f in os.listdir(self.folder_path) if f.lower().endswith(".jpg")]

        # Separate into groups by prefix
        self.a_man_files = [f for f in file_list if f.startswith("a_man_")]
        self.b_man_files = [f for f in file_list if f.startswith("b_man_")]
        self.a_nat_files = [f for f in file_list if f.startswith("a_nat_")]
        self.b_nat_files = [f for f in file_list if f.startswith("b_nat_")]

        # Check required files present
        if len(self.a_man_files) == 0 or len(self.b_nat_files) == 0:
            QMessageBox.critical(self, "Error", "No valid a_man or b_nat files found.")
            return
        if len(self.b_man_files) == 0 or len(self.a_nat_files) == 0:
            QMessageBox.critical(self, "Error", "No valid b_man or a_nat files found.")
            return

        seed = self.seed_spin.value()
        random.seed(seed)

        # Generate pairs
        self.current_pairs_a_man_b_nat = self._random_pairs(self.a_man_files, self.b_nat_files)
        self.current_pairs_b_man_a_nat = self._random_pairs(self.b_man_files, self.a_nat_files)

        self.show_pairs()
        self.rerand_btn.setEnabled(True)
        self.save_pairs()

    def rerandomise_pairs(self):
        if not self.folder_path:
            QMessageBox.warning(self, "Error", "No folder selected.")
            return

        # Shuffle with a new random seed each time for variation
        random_seed = random.randint(0, 999999999)
        random.seed(random_seed)

        self.current_pairs_a_man_b_nat = self._random_pairs(self.a_man_files, self.b_nat_files)
        self.current_pairs_b_man_a_nat = self._random_pairs(self.b_man_files, self.a_nat_files)

        self.show_pairs()
        self.save_pairs()

    def _random_pairs(self, list1, list2):
        n = min(len(list1), len(list2))
        sample1 = random.sample(list1, n)
        sample2 = random.sample(list2, n)
        return list(zip(sample1, sample2))

    def show_pairs(self):
        self.pair_list_widget.clear()
        super_number = 1
        for man, nat in self.current_pairs_a_man_b_nat:
            man_rel = os.path.relpath(os.path.join(self.folder_path, man), os.getcwd())
            nat_rel = os.path.relpath(os.path.join(self.folder_path, nat), os.getcwd())
            self.pair_list_widget.addItem(f"{super_number}: {man_rel}  <-->  {nat_rel}")
            super_number += 1
        for man, nat in self.current_pairs_b_man_a_nat:
            man_rel = os.path.relpath(os.path.join(self.folder_path, man), os.getcwd())
            nat_rel = os.path.relpath(os.path.join(self.folder_path, nat), os.getcwd())
            self.pair_list_widget.addItem(f"{super_number}: {man_rel}  <-->  {nat_rel}")
            super_number += 1

    def save_pairs(self):
        pairs1 = pd.DataFrame(self.current_pairs_a_man_b_nat, columns=["man", "nat"])
        pairs2 = pd.DataFrame(self.current_pairs_b_man_a_nat, columns=["man", "nat"])
        pairs = pd.concat([pairs1, pairs2], ignore_index=True)
        pairs.insert(0, "super_number", range(1, len(pairs) + 1))

        output_folder = os.path.join(os.path.dirname(self.folder_path), "4_super_pairings")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, "pairs.csv")

        pairs.to_csv(output_file, index=False)
        QMessageBox.information(self, "Success", f"Pairs saved to:\n{output_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Pairs()
    window.show()
    sys.exit(app.exec_())
