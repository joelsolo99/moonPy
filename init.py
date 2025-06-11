import os
import shutil
import random
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog,
    QMessageBox, QHBoxLayout, QInputDialog, QApplication, QProgressBar
)
from PyQt5.QtCore import Qt
from PIL import Image
import sys


class Init(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Directories Initialiser")

        self.manufactured_dir = None
        self.natural_dir = None
        self.output_base_dir = None  # NEW: base output folder selected by user

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_label = QLabel(
            "Select two folders: one containing Manufactured images, "
            "and one containing Natural images.\n"
            "The app will split each folder's images randomly into two groups (A and B), "
            "copying them into '1_source_images' with appropriate prefixes.\n"
            "Images will be cropped to a square size (default 500x500).\n\n"
            "Finally, you will select where to create the output folders."
        )
        self.info_label.setWordWrap(True)

        # Manufactured folder selection
        self.manuf_btn = QPushButton("Select Manufactured Folder")
        self.manuf_btn.clicked.connect(self.select_manufactured_folder)
        self.manuf_path_label = QLabel("No folder selected")
        self.manuf_path_label.setStyleSheet("color: gray;")

        # Natural folder selection
        self.nat_btn = QPushButton("Select Natural Folder")
        self.nat_btn.clicked.connect(self.select_natural_folder)
        self.nat_path_label = QLabel("No folder selected")
        self.nat_path_label.setStyleSheet("color: gray;")

        # Output folder selection (new)
        self.output_btn = QPushButton("Select Output Folder")
        self.output_btn.clicked.connect(self.select_output_folder)
        self.output_path_label = QLabel("No output folder selected")
        self.output_path_label.setStyleSheet("color: gray;")

        # Initialise button
        self.init_btn = QPushButton("Initialise Image Directories")
        self.init_btn.setEnabled(False)
        self.init_btn.clicked.connect(self.initialise_directories)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)

        # Layout setup
        layout.addWidget(self.info_label)

        manuf_layout = QHBoxLayout()
        manuf_layout.addWidget(self.manuf_btn)
        manuf_layout.addWidget(self.manuf_path_label)
        layout.addLayout(manuf_layout)

        nat_layout = QHBoxLayout()
        nat_layout.addWidget(self.nat_btn)
        nat_layout.addWidget(self.nat_path_label)
        layout.addLayout(nat_layout)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_btn)
        output_layout.addWidget(self.output_path_label)
        layout.addLayout(output_layout)

        layout.addWidget(self.init_btn)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.resize(600, 350)

    def select_manufactured_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Manufactured Folder")
        if folder:
            self.manufactured_dir = folder
            self.manuf_path_label.setText(folder)
            self.check_ready()

    def select_natural_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Natural Folder")
        if folder:
            self.natural_dir = folder
            self.nat_path_label.setText(folder)
            self.check_ready()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_base_dir = folder
            self.output_path_label.setText(folder)
            self.check_ready()

    def check_ready(self):
        self.init_btn.setEnabled(bool(self.manufactured_dir and self.natural_dir and self.output_base_dir))

    def crop_to_square(self, image_path, size):
        """Crop the image at image_path to a centered square of given size."""
        with Image.open(image_path) as img:
            width, height = img.size
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            top = (height - min_dim) // 2
            right = left + min_dim
            bottom = top + min_dim
            img_cropped = img.crop((left, top, right, bottom))
            img_resized = img_cropped.resize((size, size), Image.LANCZOS)
            img_resized.save(image_path)

    def initialise_directories(self):
        size, ok = QInputDialog.getInt(
            self,
            "Crop Size",
            "Enter square crop size in pixels:",
            value=500,
            min=10,
            max=2000,
            step=10
        )
        if not ok:
            return

        base = self.output_base_dir
        source_dir = os.path.join(base, "1_source_images")

        # Prepare output directory
        if os.path.exists(source_dir):
            reply = QMessageBox.question(
                self,
                "Overwrite Confirmation",
                ("The folder '1_source_images' already exists at the selected output location. "
                 "Do you want to overwrite its contents?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            for filename in os.listdir(source_dir):
                file_path = os.path.join(source_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            os.makedirs(source_dir)

        # Count total images to process for progress bar
        total_files = 0
        folders_files = []
        for kind, folder in [('man', self.manufactured_dir), ('nat', self.natural_dir)]:
            if not folder or not os.path.exists(folder):
                QMessageBox.warning(
                    self,
                    "Error",
                    f"The folder for {kind} images does not exist."
                )
                return

            files = os.listdir(folder)
            if len(files) == 0:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"No files found in the {kind} folder."
                )
                return

            total_files += len(files)
            folders_files.append((kind, folder, files))

        # Show and set progress bar max
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        processed = 0
        for kind, folder, files in folders_files:
            random.shuffle(files)
            midpoint = len(files) // 2
            group_a_files = files[:midpoint]
            group_b_files = files[midpoint:]

            for file in group_a_files:
                src = os.path.join(folder, file)
                clean_file = file
                if clean_file.startswith('a_') or clean_file.startswith('b_'):
                    clean_file = clean_file[2:]
                dest = os.path.join(source_dir, f"a_{kind}_{clean_file}")
                shutil.copy2(src, dest)
                self.crop_to_square(dest, size)
                processed += 1
                self.progress_bar.setValue(processed)
                QApplication.processEvents()  # keep UI responsive

            for file in group_b_files:
                src = os.path.join(folder, file)
                clean_file = file
                if clean_file.startswith('a_') or clean_file.startswith('b_'):
                    clean_file = clean_file[2:]
                dest = os.path.join(source_dir, f"b_{kind}_{clean_file}")
                shutil.copy2(src, dest)
                self.crop_to_square(dest, size)
                processed += 1
                self.progress_bar.setValue(processed)
                QApplication.processEvents()  # keep UI responsive

        # Create required folders after processing images
        required_folders = [
            "2_grey",
            "3_mooney",
            "4_super_pairings",
            "5_cyan",
            "6_magenta",
            "7_superimposed",
            "8_experiment"
        ]
        for folder in required_folders:
            full_path = os.path.join(base, folder)
            if not os.path.exists(full_path):
                os.makedirs(full_path)

        QMessageBox.information(self, "Done", "Images copied, cropped, initialised, and folders created successfully.")
        self.progress_bar.setVisible(False)
        self.close()  # Only close this widget, app remains running


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Init()
    window.show()
    sys.exit(app.exec_())

