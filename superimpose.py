import os
import sys
import csv
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt


class Superimpose(QWidget):
    def __init__(self):
        super().__init__()

        # Default folders relative to current working directory
        cwd = os.getcwd()
        self.cwd = cwd  # save for relative path display

        self.input_folder = os.path.join(cwd, "3_mooney")
        self.pairings_file = os.path.join(cwd, "4_super_pairings", "pairs.csv")
        self.output_cyan = os.path.join(cwd, "5_cyan")
        self.output_magenta = os.path.join(cwd, "6_magenta")
        self.output_combined = os.path.join(cwd, "7_superimposed")

        self.pairings = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Superimpose Images (Counterbalanced)")

        self.status_label = QLabel("No folders selected.", self)

        self.alpha_input = QLineEdit("0.5", self)
        self.alpha_label = QLabel("Alpha (0\u20131):", self)

        self.select_input_button = QPushButton("Select Input Image Folder")
        self.select_input_button.clicked.connect(self.select_input_folder)

        self.select_pairings_button = QPushButton("Select Pairings CSV")
        self.select_pairings_button.clicked.connect(self.select_pairings_file)

        self.select_output_button = QPushButton("Select Output Folders")
        self.select_output_button.clicked.connect(self.select_output_folders)

        self.run_button = QPushButton("Run All")
        self.run_button.clicked.connect(self.run_all)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)

        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(self.alpha_label)
        alpha_layout.addWidget(self.alpha_input)
        layout.addLayout(alpha_layout)

        layout.addWidget(self.select_input_button)
        layout.addWidget(self.select_pairings_button)
        layout.addWidget(self.select_output_button)
        layout.addWidget(self.run_button)
        layout.addWidget(self.done_button)

        self.setLayout(layout)
        self.resize(500, 300)
        self.update_status_label()

    def update_status_label(self):
        def rel_path(p):
            try:
                return os.path.relpath(p, self.cwd)
            except Exception:
                return p  # fallback

        info = []
        if self.input_folder:
            info.append(f"Input: {rel_path(self.input_folder)}")
        else:
            info.append("Input folder not set")

        if self.pairings_file:
            info.append(f"CSV: {rel_path(self.pairings_file)}")
        else:
            info.append("Pairings CSV not set")

        if self.output_cyan:
            info.append(f"Cyan: {rel_path(self.output_cyan)}")
        else:
            info.append("Cyan output folder not set")

        if self.output_magenta:
            info.append(f"Magenta: {rel_path(self.output_magenta)}")
        else:
            info.append("Magenta output folder not set")

        if self.output_combined:
            info.append(f"Superimposed: {rel_path(self.output_combined)}")
        else:
            info.append("Superimposed output folder not set")

        self.status_label.setText("\n".join(info))

    def get_alpha(self):
        try:
            alpha = float(self.alpha_input.text())
            if not (0 <= alpha <= 1):
                raise ValueError
            return alpha
        except ValueError:
            raise ValueError("Alpha must be a number between 0 and 1.")

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Image Folder")
        if folder:
            self.input_folder = folder
        self.update_status_label()

    def select_pairings_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Pairings CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.pairings_file = file_path
        self.update_status_label()

    def select_output_folders(self):
        cyan = QFileDialog.getExistingDirectory(self, "Select Folder for Cyan Images")
        magenta = QFileDialog.getExistingDirectory(self, "Select Folder for Magenta Images")
        combined = QFileDialog.getExistingDirectory(self, "Select Folder for Superimposed Images")
        if cyan and magenta and combined:
            self.output_cyan = cyan
            self.output_magenta = magenta
            self.output_combined = combined
        self.update_status_label()

    def run_all(self):
        try:
            if not all([self.input_folder, self.pairings_file, self.output_cyan, self.output_magenta, self.output_combined]):
                raise ValueError("Please select all folders and files.")

            alpha = self.get_alpha()

            with open(self.pairings_file, 'r') as f:
                reader = csv.DictReader(f)
                self.pairings = [(row["man"], row["nat"]) for row in reader]

            for idx, (imgA_name, imgB_name) in enumerate(self.pairings, start=1):
                a_path = os.path.join(self.input_folder, imgA_name)
                b_path = os.path.join(self.input_folder, imgB_name)

                a_img = Image.open(a_path).convert('L')
                b_img = Image.open(b_path).convert('L')

                arr_a = np.array(a_img) / 255.0
                arr_b = np.array(b_img) / 255.0

                a_cyan = self.make_cyan(arr_a, alpha)
                b_magenta = self.make_magenta(arr_b, alpha)

                b_cyan = self.make_cyan(arr_b, alpha)
                a_magenta = self.make_magenta(arr_a, alpha)

                a_cyan.save(os.path.join(self.output_cyan, f"{idx}_A_cyan.png"))
                b_cyan.save(os.path.join(self.output_cyan, f"{idx}_B_cyan.png"))
                a_magenta.save(os.path.join(self.output_magenta, f"{idx}_A_magenta.png"))
                b_magenta.save(os.path.join(self.output_magenta, f"{idx}_B_magenta.png"))

                combo1 = self.alpha_composite_white_bg(a_cyan, b_magenta)
                combo2 = self.alpha_composite_white_bg(b_cyan, a_magenta)

                cb1_folder = os.path.join(self.output_combined, "CB1")
                cb2_folder = os.path.join(self.output_combined, "CB2")
                os.makedirs(cb1_folder, exist_ok=True)
                os.makedirs(cb2_folder, exist_ok=True)

                if idx % 2 == 1:
                    combo1.save(os.path.join(cb1_folder, f"{idx}_A_cyan__B_magenta.png"))
                    combo2.save(os.path.join(cb2_folder, f"{idx}_B_cyan__A_magenta.png"))
                else:
                    combo2.save(os.path.join(cb1_folder, f"{idx}_B_cyan__A_magenta.png"))
                    combo1.save(os.path.join(cb2_folder, f"{idx}_A_cyan__B_magenta.png"))

            QMessageBox.information(self, "Done", f"\u2705 Processed {len(self.pairings)} image pairs.")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def make_cyan(self, intensity_arr, alpha):
        h, w = intensity_arr.shape
        rgba = np.ones((h, w, 4), dtype=np.uint8) * 255

        black_mask = intensity_arr < 0.5

        rgba[..., 0][black_mask] = 0
        rgba[..., 1][black_mask] = 255
        rgba[..., 2][black_mask] = 255
        rgba[..., 3][black_mask] = int(255 * alpha)

        rgba[..., 3][~black_mask] = 0

        return Image.fromarray(rgba, mode='RGBA')

    def make_magenta(self, intensity_arr, alpha):
        h, w = intensity_arr.shape
        rgba = np.ones((h, w, 4), dtype=np.uint8) * 255

        black_mask = intensity_arr < 0.5

        rgba[..., 0][black_mask] = 255
        rgba[..., 1][black_mask] = 0
        rgba[..., 2][black_mask] = 255
        rgba[..., 3][black_mask] = int(255 * alpha)

        rgba[..., 3][~black_mask] = 0

        return Image.fromarray(rgba, mode='RGBA')

    def alpha_composite_white_bg(self, img1, img2):
        white_bg = Image.new("RGBA", img1.size, (255, 255, 255, 255))
        composite = Image.alpha_composite(white_bg, img1)
        composite = Image.alpha_composite(composite, img2)
        return composite


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Superimpose()
    widget.show()
    sys.exit(app.exec_())

