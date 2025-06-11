from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtCore import Qt

from mooney import MooneyApp
from greyscale_widget import GreyscaleWidget
from init import Init
from pairs import Pairs
from superimpose import Superimpose
from readme_widget import README
from rename import Rename  # ⬅️ New import


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoonPy Home Screen")
        self.setMinimumSize(400, 500)

        # Main vertical layout container
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # Welcome label
        welcome_label = QLabel(
            "Welcome to MoonPy\n\nCreated by Joel S. Solomons and Christopher J. Berry"
        )
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setWordWrap(True)
        welcome_label.setStyleSheet(
            """
            font-size: 18px;
            font-weight: 600;
            color: #ddd;
            """
        )
        main_layout.addWidget(welcome_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Button style
        button_style = """
            QPushButton {
                background-color: #2a9d8f;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #21867a;
            }
            QPushButton:pressed {
                background-color: #176459;
            }
        """

        # Button factory
        def make_button(text, slot):
            btn = QPushButton(text)
            btn.setStyleSheet(button_style)
            btn.clicked.connect(slot)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(44)
            return btn

        # Buttons
        self.readme_button = make_button("README / How to Use", self.open_readme)
        self.init_button = make_button("Initialise Image Folders", self.open_init)
        self.greyscale_button = make_button("Greyscaler", self.open_greyscale)
        self.mooney_button = make_button("Mooney Processor", self.open_mooney)
        self.pairs_button = make_button("Create Man/Nat-A/B Pairings", self.open_pairs)
        self.supermooney_button = make_button("superMooney Processor", self.open_supermooney)
        self.rename_button = make_button("Build Experiment", self.open_rename)  # ⬅️ New button

        for btn in [
            self.readme_button,
            self.init_button,
            self.greyscale_button,
            self.mooney_button,
            self.pairs_button,
            self.supermooney_button,
            self.rename_button  # ⬅️ Add to layout
        ]:
            main_layout.addWidget(btn)

        # Spacer
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Main container
        container = QWidget()
        container.setLayout(main_layout)

        # Dark theme
        dark_style = """
            QWidget {
                background-color: #121212;
                color: #CCCCCC;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QPushButton {
                background-color: #2a9d8f;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #21867a;
            }
            QPushButton:pressed {
                background-color: #176459;
            }
            QFrame {
                background-color: #444444;
            }
            QLabel {
                color: #ddd;
            }
        """
        container.setStyleSheet(dark_style)
        self.setCentralWidget(container)

    def open_readme(self):
        self.readme_window = README()
        self.readme_window.show()

    def open_init(self):
        self.init_window = Init()
        self.init_window.show()

    def open_greyscale(self):
        self.greyscale_window = GreyscaleWidget()
        self.greyscale_window.show()

    def open_mooney(self):
        self.mooney_window = MooneyApp()
        self.mooney_window.show()

    def open_pairs(self):
        self.pairs_window = Pairs()
        self.pairs_window.show()

    def open_supermooney(self):
        self.supermooney_window = Superimpose()
        self.supermooney_window.show()

    def open_rename(self):
        self.rename_window = Rename()
        self.rename_window.show()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_win = MainApp()
    main_win.show()
    sys.exit(app.exec_())

