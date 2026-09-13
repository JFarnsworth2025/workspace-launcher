from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtWidgets import (
    QComboBox,
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
            "Edit Workspace Item" if application is not None else "Add Workspace Item"
        )
        self.resize(550, 260)

        self.item_type_input = QComboBox()
        self.item_type_input.addItem("Application", "application")
        self.item_type_input.addItem("File or Shortcut", "file")
        self.item_type_input.addItem("Folder", "folder")
        self.item_type_input.addItem("Website", "website")

        self.name_input = QLineEdit()
        self.name_input.setText(self.application["name"])

        self.path_input = QLineEdit()
        self.path_input.setText(self.application["path"])

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_item)

        form_layout = QFormLayout()
        form_layout.addRow("Item Type:", self.item_type_input)
        form_layout.addRow("Display Name:", self.name_input)
        form_layout.addRow("Path or URL:", self.path_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.browse_button)
        layout.addWidget(buttons)

        item_type = self.application.get("item_type")

        if item_type is None:
            item_type = "application"

            if self.application.get("launch_type") == "resource":
                path = self.application["path"]

                if path.lower().startswith("http://") or path.lower().startswith(
                    "https://"
                ):
                    item_type = "website"

                elif Path(path).is_dir():
                    item_type = "folder"

                else:
                    item_type = "file"

        index = self.item_type_input.findData(item_type)
        self.item_type_input.setCurrentIndex(index if index >= 0 else 0)

        self.item_type_input.currentIndexChanged.connect(self.update_item_type)
        self.update_item_type()

    def update_item_type(self) -> None:
        item_type = self.item_type_input.currentData()

        placeholders = {
            "application": "Enter the path to the application executable",
            "file": "Enter the path to the file or shortcut",
            "folder": "Enter the path to the folder",
            "website": "Enter the URL of the website (e.g., https://www.example.com)",
        }

        self.path_input.setPlaceholderText(placeholders[item_type])
        self.browse_button.setEnabled(item_type != "website")

    def browse_item(self) -> None:
        item_type = self.item_type_input.currentData()

        if item_type == "website":
            return

        if item_type == "folder":
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        else:
            file_filter = (
                "Applications (*.exe);;All Files (*)"
                if item_type == "application"
                else "All Files (*)"
            )
            path, _ = QFileDialog.getOpenFileName(self, "Select Item", "", file_filter)

        if path:
            self.path_input.setText(path)

    def get_application(self) -> dict:
        application = self.application.copy()
        item_type = self.item_type_input.currentData()

        application["name"] = self.name_input.text().strip()
        application["path"] = self.path_input.text().strip()
        application["item_type"] = item_type
        application["launch_type"] = (
            "application" if item_type == "application" else "resource"
        )

        return application

    def validate_and_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Warning", "Display name cannot be empty.")
            return

        path = self.path_input.text().strip()

        if not path:
            QMessageBox.warning(self, "Warning", "Enter a path or URL.")
            return

        if self.item_type_input.currentData() == "website":
            try:
                url = urlparse(path)
                valid_url = url.scheme in ("http", "https") and bool(url.hostname)
            except ValueError:
                valid_url = False

            if not valid_url:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Enter a website URL beginning with http:// or https://.",
                )
                return

        self.accept()
