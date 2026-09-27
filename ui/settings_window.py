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
from services.startup_service import sync_startup


class SettingsWindow(QDialog):
    def __init__(self, settings: dict, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("settingsWindow")
        self.settings = settings.copy()
        self.setWindowTitle("Workspace Settings")
        self.resize(460, 220)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("settingsNameInput")
        self.name_input.setPlaceholderText("Your name")
        self.name_input.setMaxLength(40)
        self.name_input.setText(self.settings["greeting_name"])

        self.close_applications_checkbox = QCheckBox(
            "Select Yes by default when asked to close applications"
        )
        self.close_applications_checkbox.setChecked(
            self.settings["close_applications_on_end"]
        )
        self.close_applications_checkbox.setObjectName("settingsCheckbox")

        explanation = QLabel(
            "You will still be asked before applications are stopped. "
            "Force-stopping applications can lose unsaved work. "
            "Files, folders, and websites remain open."
        )
        explanation.setWordWrap(True)

        self.verse_checkbox = QCheckBox("Show daily Bible verse")
        self.verse_checkbox.setObjectName("settingsCheckbox")
        self.verse_checkbox.setChecked(self.settings["bible_verse"])

        self.quote_checkbox = QCheckBox("Show daily motivational quote")
        self.quote_checkbox.setObjectName("settingsCheckbox")
        self.quote_checkbox.setChecked(self.settings["motivation_quote"])

        self.tray_checkbox = QCheckBox("Keep running in the system tray when closing the window")
        self.tray_checkbox.setObjectName("settingsCheckbox")
        self.tray_checkbox.setChecked(self.settings["close_to_tray"])

        self.launch_on_startup_checkbox = QCheckBox("Launch Workspace Launcher when Windows starts")
        self.launch_on_startup_checkbox.setObjectName("settingsCheckbox")
        self.launch_on_startup_checkbox.setChecked(self.settings["launch_on_startup"])

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.button(QDialogButtonBox.StandardButton.Save).setObjectName("primaryButton")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setObjectName("secondaryButton")
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Name for your daily greeting:"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.close_applications_checkbox)
        layout.addWidget(explanation)
        layout.addWidget(self.verse_checkbox)
        layout.addWidget(self.quote_checkbox)
        layout.addWidget(self.tray_checkbox)
        layout.addWidget(self.launch_on_startup_checkbox)
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
        settings["bible_verse"] = self.verse_checkbox.isChecked()
        settings["motivation_quote"] = self.quote_checkbox.isChecked()
        settings["close_to_tray"] = self.tray_checkbox.isChecked()
        settings["launch_on_startup"] = self.launch_on_startup_checkbox.isChecked()
        settings["close_applications_on_end"] = (
            self.close_applications_checkbox.isChecked()
        )
        try:
            sync_startup(settings["launch_on_startup"])
        except OSError as error:
            QMessageBox.warning(self, "Startup Setting Could Not Be Changed", str(error))
            return

        try:
            save_settings(settings)
        except (OSError, ValueError) as error:
            message = str(error)
            try:
                sync_startup(self.settings["launch_on_startup"])
            except OSError as restore_error:
                message += "\n\nThe Windows startup setting could not be restored: " + str(restore_error)
            QMessageBox.warning(self, "Could Not Save Settings", message)
            return

        self.settings = settings
        self.accept()
