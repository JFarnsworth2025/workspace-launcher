from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from services.settings_service import save_settings
from services.startup_service import sync_startup


class SettingsWindow(QDialog):
    def __init__(self, settings: dict, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings.copy()
        self.setup_window()
        self.create_widgets()
        self.create_layouts()

    def setup_window(self) -> None:
        self.setObjectName("settingsWindow")
        self.setWindowTitle("Workspace Launcher | Settings")
        self.resize(620, 680)
        self.setMinimumSize(560, 620)

    def create_widgets(self) -> None:
        self.title_label = QLabel("Settings")
        self.title_label.setObjectName("settingsTitle")

        self.subtitle_label = QLabel(
            "Choose how Workspace Launcher starts and what appears on your dashboard."
        )
        self.subtitle_label.setObjectName("settingsSubtitle")
        self.subtitle_label.setWordWrap(True)

        self.personalization_frame = QFrame()
        self.personalization_frame.setObjectName("settingsSection")

        self.personalization_title = QLabel("Personalization")
        self.personalization_title.setObjectName("settingsSectionTitle")

        self.personalization_description = QLabel(
            "Choose the name Workspace Launcher uses in your daily greeting."
        )
        self.personalization_description.setObjectName("settingsSectionDescription")
        self.personalization_description.setWordWrap(True)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("settingsNameInput")
        self.name_input.setPlaceholderText("Your name")
        self.name_input.setMaxLength(40)
        self.name_input.setText(self.settings["greeting_name"])

        self.startup_frame = QFrame()
        self.startup_frame.setObjectName("settingsSection")

        self.startup_title = QLabel("Startup & Updates")
        self.startup_title.setObjectName("settingsSectionTitle")

        self.startup_description = QLabel(
            "Control what happens when Windows or Workspace Launcher starts."
        )
        self.startup_description.setObjectName("settingsSectionDescription")
        self.startup_description.setWordWrap(True)

        self.launch_on_startup_checkbox = QCheckBox(
            "Launch Workspace Launcher when Windows starts"
        )
        self.launch_on_startup_checkbox.setObjectName("settingsCheckbox")

        self.tray_checkbox = QCheckBox(
            "Keep Workspace Launcher running in the tray when the window is closed"
        )
        self.tray_checkbox.setObjectName("settingsCheckbox")

        self.check_for_updates_checkbox = QCheckBox("Automatically check for updates")
        self.check_for_updates_checkbox.setObjectName("settingsCheckbox")

        self.workspace_behavior_frame = QFrame()
        self.workspace_behavior_frame.setObjectName("settingsSection")

        self.workspace_behavior_title = QLabel("Workspace Behavior")
        self.workspace_behavior_title.setObjectName("settingsSectionTitle")

        self.workspace_behavior_description = QLabel(
            "You will still be asked before applications are stopped. Force-stopping can lose unsaved work. "
            "Files, folders, and websites always remain open."
        )
        self.workspace_behavior_description.setObjectName(
            "settingsSectionDescription"
        )
        self.workspace_behavior_description.setWordWrap(True)

        self.close_applications_checkbox = QCheckBox(
            "Select Yes by default when asked to close applications"
        )
        self.close_applications_checkbox.setObjectName("settingsCheckbox")

        self.content_frame = QFrame()
        self.content_frame.setObjectName("settingsSection")

        self.content_title = QLabel("Dashboard Content")
        self.content_title.setObjectName("settingsSectionTitle")

        self.content_description = QLabel(
            "Choose the daily content shown above your workspace cards."
        )
        self.content_description.setObjectName("settingsSectionDescription")
        self.content_description.setWordWrap(True)

        self.quote_checkbox = QCheckBox("Show the daily motivation quote")
        self.quote_checkbox.setObjectName("settingsCheckbox")

        self.verse_checkbox = QCheckBox("Show the daily Bible verse")
        self.verse_checkbox.setObjectName("settingsCheckbox")

        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.save)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondaryButton")
        self.cancel_button.clicked.connect(self.reject)

        self.launch_on_startup_checkbox.setChecked(self.settings["launch_on_startup"])
        self.tray_checkbox.setChecked(self.settings["close_to_tray"])
        self.close_applications_checkbox.setChecked(
            self.settings["close_applications_on_end"]
        )
        self.check_for_updates_checkbox.setChecked(self.settings["check_for_updates"])
        self.quote_checkbox.setChecked(self.settings["motivation_quote"])
        self.verse_checkbox.setChecked(self.settings["bible_verse"])

    def create_layouts(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(26, 24, 26, 24)
        main_layout.setSpacing(12)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addSpacing(4)

        personalization_layout = QVBoxLayout(self.personalization_frame)
        personalization_layout.setContentsMargins(18, 16, 18, 16)
        personalization_layout.setSpacing(9)
        personalization_layout.addWidget(self.personalization_title)
        personalization_layout.addWidget(self.personalization_description)
        personalization_layout.addWidget(self.name_input)

        startup_layout = QVBoxLayout(self.startup_frame)
        startup_layout.setContentsMargins(18, 16, 18, 16)
        startup_layout.setSpacing(9)
        startup_layout.addWidget(self.startup_title)
        startup_layout.addWidget(self.startup_description)
        startup_layout.addSpacing(3)
        startup_layout.addWidget(self.launch_on_startup_checkbox)
        startup_layout.addWidget(self.tray_checkbox)
        startup_layout.addWidget(self.check_for_updates_checkbox)

        workspace_behavior_layout = QVBoxLayout(self.workspace_behavior_frame)
        workspace_behavior_layout.setContentsMargins(18, 16, 18, 16)
        workspace_behavior_layout.setSpacing(9)
        workspace_behavior_layout.addWidget(self.workspace_behavior_title)
        workspace_behavior_layout.addWidget(self.workspace_behavior_description)
        workspace_behavior_layout.addSpacing(3)
        workspace_behavior_layout.addWidget(self.close_applications_checkbox)

        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(18, 16, 18, 16)
        content_layout.setSpacing(9)
        content_layout.addWidget(self.content_title)
        content_layout.addWidget(self.content_description)
        content_layout.addSpacing(3)
        content_layout.addWidget(self.quote_checkbox)
        content_layout.addWidget(self.verse_checkbox)

        main_layout.addWidget(self.personalization_frame)
        main_layout.addWidget(self.startup_frame)
        main_layout.addWidget(self.workspace_behavior_frame)
        main_layout.addWidget(self.content_frame)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        main_layout.addLayout(button_layout)

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
        settings["check_for_updates"] = self.check_for_updates_checkbox.isChecked()
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
