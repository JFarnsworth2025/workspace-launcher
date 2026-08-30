from PySide6.QtWidgets import (
    QMainWindow,
)
from config import APP_NAME


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(1000, 700)
