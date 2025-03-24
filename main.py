import sys
from PySide6.QtWidgets import QApplication
from GUI import GUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec())