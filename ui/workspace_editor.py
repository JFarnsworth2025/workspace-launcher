from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)


class WorkspaceEditor(QDialog):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Create Workspace")
        self.resize(400, 180)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Example: Python Development")

        self.order_input = QSpinBox()
        self.order_input.setRange(1, 999)
        self.order_input.setValue(1)

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
        return {
            "name": self.name_input.text().strip(),
            "order": self.order_input.value(),
            "applications": [],
        }
