import os
import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog,
    QMessageBox, QProgressBar, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class GreyscaleWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
        files = [f for f in os.listdir(self.input_dir) if f.lower().endswith(valid_extensions)]
        total = len(files)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for i, file in enumerate(files, 1):
            img_path = os.path.join(self.input_dir, file)
            img = cv2.imread(img_path)
            if img is None:
                continue
            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            base_name = os.path.splitext(file)[0]  # remove original extension
            save_path = os.path.join(self.output_dir, base_name + '.jpg')

            cv2.imwrite(save_path, grey)
            self.progress.emit(int(i / total * 100))

        self.finished.emit()


class GreyscaleWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Greyscale Image Converter")

        self.input_dir = "1_source_images"
        self.output_dir = "2_grey"

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.info_label = QLabel("Select input and output directories to convert images to greyscale JPGs.")
        self.info_label.setWordWrap(True)

        self.input_btn = QPushButton("Select Input Folder")
        self.input_btn.clicked.connect(self.select_input_folder)
        self.input_path_label = QLabel(self.input_dir)
        self.input_path_label.setStyleSheet("color: gray;")

        self.output_btn = QPushButton("Select Output Folder")
        self.output_btn.clicked.connect(self.select_output_folder)
        self.output_path_label = QLabel(self.output_dir)
        self.output_path_label.setStyleSheet("color: gray;")

        self.convert_btn = QPushButton("Convert to Greyscale")
        self.convert_btn.setEnabled(True)
        self.convert_btn.clicked.connect(self.start_conversion)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout.addWidget(self.info_label)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_btn)
        input_layout.addWidget(self.input_path_label)
        layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_btn)
        output_layout.addWidget(self.output_path_label)
        layout.addLayout(output_layout)

        layout.addWidget(self.convert_btn)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.resize(500, 200)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_dir = folder
            self.input_path_label.setText(folder)
            self.check_ready()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = folder
            self.output_path_label.setText(folder)
            self.check_ready()

    def check_ready(self):
        if self.input_dir and self.output_dir:
            self.convert_btn.setEnabled(True)
        else:
            self.convert_btn.setEnabled(False)

    def start_conversion(self):
        if not self.input_dir or not self.output_dir:
            QMessageBox.warning(self, "Warning", "Please select both input and output folders.")
            return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        self.worker = GreyscaleWorker(self.input_dir, self.output_dir)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()

    def conversion_finished(self):
        QMessageBox.information(self, "Done", "All images have been converted to greyscale JPGs.")
        self.convert_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        self.close()  # Close this widget only, not the whole app


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = GreyscaleWidget()
    window.show()
    sys.exit(app.exec_())
