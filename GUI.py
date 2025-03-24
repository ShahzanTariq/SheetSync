from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit, QFileDialog, QPlainTextEdit
from PySide6.QtCore import Qt, QSize

import os

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helper")

        layout = QVBoxLayout()

        # Show CSV Line
        csv_layout = QVBoxLayout()
        csv_title = QLabel("Current Line")
        csv_layout.addWidget(csv_title)
        self.currLine = QPlainTextEdit(readOnly=True)
        csv_layout.addWidget(self.currLine)
        layout.addLayout(csv_layout)


        self.currLine.setPlainText("hello this is a csv line")



        self.setLayout(layout)