import sys
from PySide6.QtWidgets import QApplication
from GUI import GUI
from transformer import precheck_hash_dupe

if __name__ == "__main__":
    precheck_hash_dupe()
    app = QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec())