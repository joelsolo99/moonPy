import os
import cv2
import sys
import pandas as pd
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QSlider, QVBoxLayout,
    QHBoxLayout, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage


class MooneyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.grey_dir = None
        self.mooney_dir = None
        self.param_dir = None
        self.param_csv = None

        self.finished = False
        self.history = []
        self.index = 0

        self.init_ui()
        self.select_initial_folders()

    def init_ui(self):
        self.setWindowTitle("Mooney Image Processor")

        self.input_btn = QPushButton("Select Input Folder")
        self.input_btn.clicked.connect(self.select_input_folder)
        self.input_path_label = QLabel("")
        self.input_path_label.setStyleSheet("color: gray;")

        self.output_btn = QPushButton("Select Output Folder")
        self.output_btn.clicked.connect(self.select_output_folder)
        self.output_path_label = QLabel("")
        self.output_path_label.setStyleSheet("color: gray;")

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)
        self.image_label.setFixedSize(500, 500)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.sigma_slider = QSlider(Qt.Horizontal)
        self.sigma_slider.setMinimum(0)
        self.sigma_slider.setMaximum(30)
        self.sigma_slider.setValue(4)
        self.sigma_slider.valueChanged.connect(self.update_preview)
        self.sigma_label = QLabel("Sigma: 2.0")

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(127)
        self.threshold_slider.valueChanged.connect(self.update_preview)
        self.threshold_label = QLabel("Threshold: 127")

        self.save_button = QPushButton("\u2705 Save & Next")
        self.save_button.clicked.connect(self.save_and_next)

        self.undo_button = QPushButton("\u21a9\ufe0f Undo")
        self.undo_button.clicked.connect(self.undo)
        self.undo_button.setEnabled(False)

        folder_layout = QHBoxLayout()
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_btn)
        input_layout.addWidget(self.input_path_label)
        output_layout = QVBoxLayout()
        output_layout.addWidget(self.output_btn)
        output_layout.addWidget(self.output_path_label)
        folder_layout.addLayout(input_layout)
        folder_layout.addLayout(output_layout)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(self.sigma_label)
        slider_layout.addWidget(self.sigma_slider)
        slider_layout.addWidget(self.threshold_label)
        slider_layout.addWidget(self.threshold_slider)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.undo_button)

        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(folder_layout)
        main_layout.addStretch()
        main_layout.addLayout(image_layout)
        main_layout.addStretch()
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.resize(850, 850)

    def select_initial_folders(self):
        self.select_input_folder()
        if not self.grey_dir:
            return

        self.select_output_folder()
        if not self.mooney_dir:
            return

        self.select_param_folder()
        if not self.param_dir:
            return

        self.param_csv = os.path.join(self.param_dir, "threshold_blur.csv")
        self.update_path_labels()
        self.load_or_choose_start()

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder", "")
        if folder:
            self.grey_dir = folder
            self.input_path_label.setText(folder)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder:
            self.mooney_dir = folder
            self.output_path_label.setText(folder)
            os.makedirs(self.mooney_dir, exist_ok=True)

    def select_param_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Save Param File", "")
        if folder:
            self.param_dir = folder

    def update_path_labels(self):
        self.input_path_label.setText(self.grey_dir)
        self.output_path_label.setText(self.mooney_dir)

    def load_or_choose_start(self):
        os.makedirs(self.mooney_dir, exist_ok=True)

        if os.path.exists(self.param_csv):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Existing CSV Found")
            msg_box.setText("threshold_blur.csv already exists.\n\nWould you like to resume or start over?")
            resume_btn = msg_box.addButton("Resume", QMessageBox.YesRole)
            start_over_btn = msg_box.addButton("Start Over", QMessageBox.NoRole)
            msg_box.setDefaultButton(resume_btn)
            msg_box.exec_()

            resume = msg_box.clickedButton() == resume_btn
        else:
            resume = False

        if resume:
            self.params_df = pd.read_csv(self.param_csv)
        else:
            self.params_df = pd.DataFrame(columns=["filename", "sigma", "threshold"])
            self.params_df.to_csv(self.param_csv, index=False)

        all_files = sorted([f for f in os.listdir(self.grey_dir) if f.lower().endswith(".jpg")])
        processed = set(self.params_df["filename"])
        self.image_files = [f for f in all_files if f not in processed]

        if not self.image_files:
            QMessageBox.information(self, "No images", "No unprocessed JPG images found. Closing.")
            self.close()
            return

        self.index = 0
        self.finished = False
        self.history.clear()
        self.load_image()

    def reload_images(self):
        if os.path.exists(self.param_csv):
            self.params_df = pd.read_csv(self.param_csv)
        else:
            self.params_df = pd.DataFrame(columns=["filename", "sigma", "threshold"])

        all_files = sorted([f for f in os.listdir(self.grey_dir) if f.lower().endswith(".jpg")])
        processed = set(self.params_df["filename"])
        self.image_files = [f for f in all_files if f not in processed]

        if not self.image_files:
            QMessageBox.information(self, "No images", "No unprocessed JPG images found in new folder.")
            self.close()
            return

        self.index = 0
        self.finished = False
        self.history.clear()
        self.load_image()

    def update_preview(self):
        if self.finished or self.index >= len(self.image_files):
            return

        sigma = self.sigma_slider.value() / 2
        threshold = self.threshold_slider.value()
        self.sigma_label.setText(f"Sigma: {sigma:.1f}")
        self.threshold_label.setText(f"Threshold: {threshold}")

        image_path = os.path.join(self.grey_dir, self.image_files[self.index])
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return

        if sigma > 0:
            ksize = int(2 * round(3 * sigma) + 1)
            img_blur = cv2.GaussianBlur(img, (ksize, ksize), sigma)
        else:
            img_blur = img.copy()

        _, img_thresh = cv2.threshold(img_blur, threshold, 255, cv2.THRESH_BINARY)

        height, width = img_thresh.shape
        q_img = QImage(img_thresh.data, width, height, width, QImage.Format_Grayscale8)

        pixmap = QPixmap.fromImage(q_img).scaled(
            500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

    def load_image(self):
        if self.index >= len(self.image_files):
            self.finish_processing()
            return

        self.sigma_slider.setValue(4)
        self.threshold_slider.setValue(127)
        self.update_preview()

    def save_and_next(self):
        if self.finished or self.index >= len(self.image_files):
            return

        sigma = self.sigma_slider.value() / 2
        threshold = self.threshold_slider.value()
        filename = self.image_files[self.index]
        image_path = os.path.join(self.grey_dir, filename)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return

        if sigma > 0:
            ksize = int(2 * round(3 * sigma) + 1)
            img_blur = cv2.GaussianBlur(img, (ksize, ksize), sigma)
        else:
            img_blur = img.copy()

        _, img_thresh = cv2.threshold(img_blur, threshold, 255, cv2.THRESH_BINARY)
        Image.fromarray(img_thresh).save(os.path.join(self.mooney_dir, filename))

        new_row = pd.DataFrame([{
            "filename": filename,
            "sigma": sigma,
            "threshold": threshold
        }])
        self.params_df = pd.concat([self.params_df, new_row], ignore_index=True)
        self.params_df.to_csv(self.param_csv, index=False)

        self.history.append({
            "index": self.index,
            "filename": filename,
            "sigma": sigma,
            "threshold": threshold
        })
        self.undo_button.setEnabled(True)

        self.index += 1
        self.load_image()

    def undo(self):
        if not self.history:
            QMessageBox.information(self, "Undo", "Nothing to undo.")
            self.undo_button.setEnabled(False)
            return

        last_entry = self.history.pop()
        self.index = last_entry["index"]
        filename = last_entry["filename"]

        self.params_df = self.params_df[self.params_df["filename"] != filename]
        self.params_df.to_csv(self.param_csv, index=False)

        mooney_path = os.path.join(self.mooney_dir, filename)
        if os.path.exists(mooney_path):
            os.remove(mooney_path)

        self.sigma_slider.setValue(int(last_entry["sigma"] * 2))
        self.threshold_slider.setValue(int(last_entry["threshold"]))

        self.load_image()

        if not self.history:
            self.undo_button.setEnabled(False)

    def finish_processing(self):
        if self.finished:
            return
        self.finished = True
        self.sigma_slider.setEnabled(False)
        self.threshold_slider.setEnabled(False)
        self.save_button.setEnabled(False)
        self.undo_button.setEnabled(False)

        QMessageBox.information(self, "Done", "\u2705 All images processed.")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MooneyApp()
    window.show()
    sys.exit(app.exec_())

