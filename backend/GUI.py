from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit, QFileDialog, QPlainTextEdit
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from masterUtil import *

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        masterCSV = masterUtil()
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

        self.table = QTableWidget()
        headers = ["Date", "Amount", "Description", "Category", "Card Name"]
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Date", "Amount", "Description", "Category", "Card Name"])
        self.table.setRowCount(1)

        row_data = masterCSV.get_current_row()
        transactionText = QLabel(str(row_data['Transaction Date']))
        self.table.setCellWidget(0,0,transactionText)
        self.table.set
        
            
        layout.addWidget(self.table)

        self.setLayout(layout)