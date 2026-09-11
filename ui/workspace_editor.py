from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)


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

        self.setWindowTitle(
            "Edit Workspace" if workspace is not None else "Create Workspace"
        )
        self.resize(400, 180)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Python Development")
        self.name_input.setText(self.workspace["name"])

        self.order_input = QSpinBox()
        self.order_input.setRange(1, 999)
        self.order_input.setValue(self.workspace.get("order", 1))

        form_layout = QFormLayout()
        form_layout.addRow("Workspace name:", self.name_input)
        form_layout.addRow("Display order:", self.order_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

    def get_workspace(self) -> dict:
        workspace = self.workspace.copy()
        workspace["name"] = self.name_input.text().strip()
        workspace["order"] = self.order_input.value()
        return workspace
