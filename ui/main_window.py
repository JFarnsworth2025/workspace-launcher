from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QWidget,
    QListWidget,
)
from config import APP_NAME
from ui.workspace_editor import WorkspaceEditor
from services.workspace_service import save_workspace, load_workspaces


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(1000, 700)

        central_widget = QWidget()

        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.workspace_list = QListWidget()
        layout.addWidget(self.workspace_list)

        create_workspace_button = QPushButton("Create Workspace")
        layout.addWidget(create_workspace_button)
        create_workspace_button.clicked.connect(self.create_workspace)

        self.refresh_workspaces()

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
        self.refresh_workspaces()

    def refresh_workspaces(self) -> None:
        self.workspace_list.clear()
        workspaces = load_workspaces()
        for workspace in workspaces:
            self.workspace_list.addItem(workspace["name"])
