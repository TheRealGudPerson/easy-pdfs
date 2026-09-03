import sys

from PySide6.QtWidgets import QApplication

from easypdf.main_window import MainWindow
from easypdf import __version__


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("EasyPDF")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("EasyPDF")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()