import sys
from PySide6.QtWidgets import QApplication
from pdfmanager.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Manager")
    app.setOrganizationName("PDF Manager")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
