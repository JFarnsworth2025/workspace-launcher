import sys
from PySide6.QtWidgets import (
    QApplication,
)
from ui.main_window import MainWindow
from config import PROJECT_ROOT


def main() -> None:
    app = QApplication(sys.argv)

    stylesheet = ""
    for filename in [
        "global.qss",
        "typography.qss",
        "header.qss",
        "workspace_cards.qss",
        "buttons.qss",
        "inputs.qss",
        "scrollbars.qss",
        "dialogs.qss",
        "history.qss",
        "workspace_manager.qss",
        "settings.qss",
    ]:
        with (PROJECT_ROOT / "styles" / filename).open(encoding="utf-8") as file:
            stylesheet += file.read() + "\n"
    app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
