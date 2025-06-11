import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog,
    QMessageBox, QProgressBar, QApplication
)
from PyQt5.QtCore import Qt


class Rename(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Build Experiment Folder")

        self.greyscale_path = None
        self.mooney_path = None
        self.superimposed_path = None
        self.output_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select folders and build the experiment folder (8_experiment)."))

        # Greyscale
        self.gs_button = QPushButton("Select Greyscale Folder")
        self.gs_button.clicked.connect(self.select_greyscale)
        self.gs_label = QLabel("No folder selected")
        layout.addWidget(self.gs_button)
        layout.addWidget(self.gs_label)

        # Mooney
        self.mn_button = QPushButton("Select Mooney Folder")
        self.mn_button.clicked.connect(self.select_mooney)
        self.mn_label = QLabel("No folder selected")
        layout.addWidget(self.mn_button)
        layout.addWidget(self.mn_label)

        # Superimposed
        self.sp_button = QPushButton("Select Superimposed Folder")
        self.sp_button.clicked.connect(self.select_superimposed)
        self.sp_label = QLabel("No folder selected")
        layout.addWidget(self.sp_button)
        layout.addWidget(self.sp_label)

        # Output
        self.out_button = QPushButton("Select Output Folder (e.g., 8_experiment)")
        self.out_button.clicked.connect(self.select_output)
        self.out_label = QLabel("No folder selected")
        layout.addWidget(self.out_button)
        layout.addWidget(self.out_label)

        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Run button
        self.run_button = QPushButton("Build Experiment")
        self.run_button.clicked.connect(self.build_experiment)
        layout.addWidget(self.run_button)

        # Done button
        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.close)
        layout.addWidget(self.done_button)

        self.setLayout(layout)
        self.resize(600, 400)

    def set_label_relative(self, label_widget, path):
        try:
            relative_path = os.path.relpath(path, os.getcwd())
            if relative_path.startswith(".."):  # outside current working dir
                label_widget.setText(path)
            else:
                label_widget.setText(relative_path)
        except ValueError:
            label_widget.setText(path)

    def select_greyscale(self):
        path = QFileDialog.getExistingDirectory(self, "Select Greyscale Folder")
        if path:
            self.greyscale_path = path
            self.set_label_relative(self.gs_label, path)

    def select_mooney(self):
        path = QFileDialog.getExistingDirectory(self, "Select Mooney Folder")
        if path:
            self.mooney_path = path
            self.set_label_relative(self.mn_label, path)

    def select_superimposed(self):
        path = QFileDialog.getExistingDirectory(self, "Select Superimposed Folder")
        if path:
            self.superimposed_path = path
            self.set_label_relative(self.sp_label, path)

    def select_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_path = path
            self.set_label_relative(self.out_label, path)

    def build_experiment(self):
        if not all([self.greyscale_path, self.mooney_path, self.superimposed_path, self.output_path]):
            QMessageBox.critical(self, "Error", "Please select all required folders.")
            return

        all_files = []

        # Greyscale
        for f in os.listdir(self.greyscale_path):
            if f.endswith(".jpg"):
                all_files.append(("1_greyscale_" + f, os.path.join(self.greyscale_path, f)))

        # Mooney
        for f in os.listdir(self.mooney_path):
            if f.endswith(".jpg"):
                all_files.append(("2_mooney_" + f, os.path.join(self.mooney_path, f)))

        # Superimposed: CB1 and CB2
        for cb in ["CB1", "CB2"]:
            cb_folder = os.path.join(self.superimposed_path, cb)
            if os.path.isdir(cb_folder):
                for f in os.listdir(cb_folder):
                    if f.endswith(".png"):
                        prefix = f.split("_")[0]
                        new_name = f"3_super_{cb}_{prefix}.png"
                        all_files.append((new_name, os.path.join(cb_folder, f)))

        self.progress.setMaximum(len(all_files))
        self.progress.setValue(0)

        for i, (new_name, src_path) in enumerate(all_files):
            dest_path = os.path.join(self.output_path, new_name)
            shutil.copyfile(src_path, dest_path)
            self.progress.setValue(i + 1)

        QMessageBox.information(self, "Done", "Renaming complete. Experiment is ready to go!")


# Only run directly for testing
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = Rename()
    window.show()
    sys.exit(app.exec_())

