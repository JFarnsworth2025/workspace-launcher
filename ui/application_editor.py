from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ApplicationEditor(QDialog):

    def __init__(self, application: dict | None = None) -> None:
        super().__init__()

        self.application = (
            application.copy()
            if application is not None
            else {
                "name": "",
                "path": "",
                "launch_type": "application",
                "arguments": [],
            }
        )

        self.setWindowTitle(
            "Edit Application" if application is not None else "Add Application"
        )
        self.resize(500, 220)

        self.name_input = QLineEdit()
        self.name_input.setText(self.application["name"])

        self.path_input = QLineEdit()
        self.path_input.setText(self.application["path"])

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_application)

        form_layout = QFormLayout()
        form_layout.addRow("Display Name:", self.name_input)
        form_layout.addRow("Executable Path:", self.path_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(browse_button)
        layout.addWidget(buttons)

    def browse_application(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Application", "", "Applications (*.exe);;All Files (*)"
        )

        if path:
            self.path_input.setText(path)

    def validate_and_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Application name cannot be empty.")
            return

        if not self.path_input.text().strip():
            QMessageBox.warning(self, "Warning", "Executable path cannot be empty.")
            return

        self.accept()

    def get_application(self) -> dict:
        application = self.application.copy()
        application["name"] = self.name_input.text().strip()
        application["path"] = self.path_input.text().strip()
        return application
