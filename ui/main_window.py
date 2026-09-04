from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QWidget,
)
from config import APP_NAME
from ui.workspace_editor import WorkspaceEditor
from services.workspace_service import save_workspace


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(1000, 700)

        central_widget = QWidget()

        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        create_workspace_button = QPushButton("Create Workspace")
        layout.addWidget(create_workspace_button)
        create_workspace_button.clicked.connect(self.create_workspace)

    def create_workspace(self) -> None:

        workspace_editor = WorkspaceEditor()

        result = workspace_editor.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        workspace = workspace_editor.get_workspace()

        if workspace["name"] == "":
            QMessageBox.warning(self, "Warning", "Workspace name cannot be empty.")
            return

        save_workspace(workspace)
