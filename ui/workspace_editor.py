from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QPushButton,
)
from ui.application_editor import ApplicationEditor


class WorkspaceEditor(QDialog):

    def __init__(self, workspace: dict | None = None) -> None:
        super().__init__()

        self.workspace = (
            workspace.copy()
            if workspace is not None
            else {
                "name": "",
                "order": 1,
                "applications": [],
            }
        )

        self.applications = self.workspace.get("applications", []).copy()

        self.setWindowTitle(
            "Edit Workspace" if workspace is not None else "Create Workspace"
        )
        self.resize(540, 400)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Python Development")
        self.name_input.setText(self.workspace["name"])

        self.order_input = QSpinBox()
        self.order_input.setRange(1, 999)
        self.order_input.setValue(self.workspace.get("order", 1))

        form_layout = QFormLayout()
        form_layout.addRow("Workspace name:", self.name_input)
        form_layout.addRow("Display order:", self.order_input)

        self.application_list = QListWidget()
        add_button = QPushButton("Add Item")
        edit_button = QPushButton("Edit Item")
        remove_button = QPushButton("Remove Item")

        add_button.clicked.connect(self.add_application)
        edit_button.clicked.connect(self.edit_application)
        remove_button.clicked.connect(self.remove_application)

        application_buttons = QHBoxLayout()
        application_buttons.addWidget(add_button)
        application_buttons.addWidget(edit_button)
        application_buttons.addWidget(remove_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.application_list)
        layout.addLayout(application_buttons)
        layout.addWidget(buttons)

        self.refresh_applications()

    def get_workspace(self) -> dict:
        workspace = self.workspace.copy()
        workspace["name"] = self.name_input.text().strip()
        workspace["order"] = self.order_input.value()
        workspace["applications"] = self.applications.copy()
        return workspace

    def refresh_applications(self) -> None:
        self.application_list.clear()
        for app in self.applications:
            self.application_list.addItem(app["name"])

    def add_application(self) -> None:
        editor = ApplicationEditor()
        if editor.exec() != QDialog.DialogCode.Accepted:
            return

        application = editor.get_application()
        self.applications.append(application)
        self.refresh_applications()

    def get_selected_application_row(self) -> int:
        row = self.application_list.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select an item first.")
            return -1
        return row

    def edit_application(self) -> None:
        row = self.get_selected_application_row()
        if row == -1:
            return

        editor = ApplicationEditor(self.applications[row])
        if editor.exec() != QDialog.DialogCode.Accepted:
            return

        self.applications[row] = editor.get_application()
        self.refresh_applications()

    def remove_application(self) -> None:
        row = self.get_selected_application_row()
        if row == -1:
            return

        del self.applications[row]
        self.refresh_applications()
