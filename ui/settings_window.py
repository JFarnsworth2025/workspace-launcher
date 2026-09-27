from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from services.settings_service import save_settings


class SettingsWindow(QDialog):
    def __init__(self, settings: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.settings = settings.copy()
        self.setWindowTitle("Workspace Settings")
        self.resize(460, 220)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your name")
        self.name_input.setMaxLength(40)
        self.name_input.setText(self.settings["greeting_name"])

        self.close_applications_checkbox = QCheckBox(
            "Select Yes by default when asked to close applications"
        )
        self.close_applications_checkbox.setChecked(
            self.settings["close_applications_on_end"]
        )

        explanation = QLabel(
            "You will still be asked before applications are stopped. "
            "Force-stopping applications can lose unsaved work. "
            "Files, folders, and websites remain open."
        )
        explanation.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Name for your daily greeting:"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.close_applications_checkbox)
        layout.addWidget(explanation)
        layout.addWidget(buttons)

    def save(self) -> None:
        greeting_name = self.name_input.text().strip()
        if not greeting_name:
            QMessageBox.warning(
                self,
                "Name Required",
                "Enter the name you would like to see in your daily greeting.",
            )
            self.name_input.setFocus()
            return

        settings = self.settings.copy()
        settings["greeting_name"] = greeting_name
        settings["close_applications_on_end"] = (
            self.close_applications_checkbox.isChecked()
        )
        try:
            save_settings(settings)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Could Not Save Settings", str(error))
            return

        self.settings = settings
        self.accept()
