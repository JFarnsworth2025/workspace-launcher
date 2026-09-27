from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QCheckBox,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from services.settings_service import load_settings, save_settings


class OnboardingWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("onboardingWindow")
        self.setWindowTitle("Welcome to Workspace Launcher")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self.setFixedSize(560, 400)

        self.title_label = QLabel("Make Workspace Launcher yours")
        self.title_label.setObjectName("onboardingTitle")

        self.subtitle_label = QLabel(
            "Before we build your dashboard, choose how you would like to be greeted."
        )
        self.subtitle_label.setObjectName("onboardingSubtitle")
        self.subtitle_label.setWordWrap(True)

        self.name_frame = QFrame()
        self.name_frame.setObjectName("onboardingSection")

        self.name_label = QLabel("What should we call you?")
        self.name_label.setObjectName("onboardingSectionTitle")

        self.name_description = QLabel(
            "This name appears in your morning, afternoon, and evening greeting."
        )
        self.name_description.setObjectName("onboardingDescription")
        self.name_description.setWordWrap(True)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("onboardingNameInput")
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setMaxLength(40)

        self.verse_checkbox = QCheckBox("Show daily Bible verse")
        self.verse_checkbox.setObjectName("onboardingCheckbox")
        self.verse_checkbox.setChecked(True)

        self.continue_button = QPushButton("Continue to Workspace Launcher")
        self.continue_button.setObjectName("primaryButton")
        self.continue_button.clicked.connect(self.save_profile)

        name_layout = QVBoxLayout(self.name_frame)
        name_layout.setContentsMargins(18, 16, 18, 16)
        name_layout.setSpacing(9)
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_description)
        name_layout.addWidget(self.name_input)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.name_frame)
        layout.addWidget(self.verse_checkbox)
        layout.addStretch()
        layout.addWidget(self.continue_button)

        self.name_input.setFocus()

    def save_profile(self) -> None:
        greeting_name = self.name_input.text().strip()

        if not greeting_name:
            QMessageBox.warning(
                self,
                "Name Required",
                "Please enter a name to continue.",
                QMessageBox.StandardButton.Ok,
            )
            self.name_input.setFocus()
            return

        try:
            settings = load_settings()
            settings["greeting_name"] = greeting_name
            settings["bible_verse"] = self.verse_checkbox.isChecked()
            save_settings(settings)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Could Not Save Profile", str(error))
            return

        self.accept()
