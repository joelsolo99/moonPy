from PyQt5.QtWidgets import QScrollArea, QLabel, QVBoxLayout, QWidget, QTextEdit, QPushButton
from PyQt5.QtCore import Qt

class README(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("README \u2013 Instructions and Purpose")

        instructions = """
        <h2>About This App</h2>
        <p>
        This application assists in the creation of Mooney images and superMooney images,
        typically used in studies of priming, implicit memory and the "I See It Differently" (ISID) effect.
        </p>

        <h3>How to Use</h3>
<p>
    By pressing the <strong>Initialise Image Folders</strong> button, folders for each output will be created:
    <em>1_source_images, 2_grey, 3_mooney, 4_super_pairings, 5_cyan, 6_magenta,</em> and
    <em>7_superimposed</em> (with subfolders for counterbalance conditions).
</p>
<ol>
    <li>Create two folders:
        <ul>
            <li>One containing square images of <strong>natural</strong> items</li>
            <li>One containing square images of <strong>manufactured</strong> items</li>
        </ul>
    </li>
    <li>Ensure both folders contain an <em>equal number</em> of images.</li>
    <li>The app will then:
        <ol type="a">
            <li>Crop the images to the same size (if needed)</li>
            <li>Convert them to greyscale</li>
            <li>Threshold them to produce Mooney-style (black and white) images</li>
            <li>Create colourised versions:
                <ul>
                    <li><strong>Cyan</strong> version of each image</li>
                    <li><strong>Magenta</strong> version of each image</li>
                </ul>
            </li>
            <li>Superimpose natural and manufactured images together (cyan + magenta), with one being from set A and the other from set B.</li>
        </ol>
    </li>
</ol>

<h3>Output</h3>
<p>
    The app will generate folders containing:
    <ul>
        <li>Cyan and magenta versions of the original Mooney images</li>
        <li>Superimposed pairs in counterbalanced combinations</li>
    </ul>
</p>


        <h3>Purpose</h3>
        <p>
        This tool is intended to support cognitive and perceptual psychology research,
        especially experiments investigating how prior knowledge and exposure can qualitatively
        alter the perception of ambiguous or degraded stimuli.
        </p>

        <h3>Authors</h3>
        <p>
        Joel S. Solomons<br>
        Christopher J. Berry
        </p>
        """

        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setHtml(instructions)
        self.text_box.setStyleSheet("font-size: 14px;")

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.text_box)
        layout.addWidget(self.close_button, alignment=Qt.AlignRight)
        self.setLayout(layout)
        self.resize(600, 500)
