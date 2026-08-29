import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
)
from config import APP_NAME


def main() -> None:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle(APP_NAME)
    window.resize(1000, 700)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
