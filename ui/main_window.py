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
from services.workspace_service import save_workspace, load_workspaces, delete_workspace


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

        edit_workspace_button = QPushButton("Edit Workspace")
        layout.addWidget(edit_workspace_button)
        edit_workspace_button.clicked.connect(self.edit_workspace)

        delete_workspace_button = QPushButton("Delete Workspace")
        layout.addWidget(delete_workspace_button)
        delete_workspace_button.clicked.connect(self.delete_selected_workspace)

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

        try:
            save_workspace(workspace)
        except FileExistsError as e:
            QMessageBox.warning(self, "Warning", str(e))
            return
        self.refresh_workspaces()

    def refresh_workspaces(self) -> None:
        self.workspace_list.clear()
        self.workspaces = load_workspaces()
        for workspace in self.workspaces:
            self.workspace_list.addItem(workspace["name"])

    def get_selected_workspace(self) -> dict | None:
        row = self.workspace_list.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select a workspace to edit.")
            return None

        return self.workspaces[row]

    def edit_workspace(self) -> None:
        original_workspace = self.get_selected_workspace()
        if original_workspace is None:
            return

        workspace_editor = WorkspaceEditor(original_workspace)
        result = workspace_editor.exec()

        if result != QDialog.DialogCode.Accepted:
            return

        workspace = workspace_editor.get_workspace()
        if workspace["name"] == "":
            QMessageBox.warning(self, "Warning", "Workspace name cannot be empty.")
            return

        try:
            save_workspace(workspace, original_name=original_workspace["name"])
        except FileExistsError as e:
            QMessageBox.warning(self, "Warning", str(e))
            return

        self.refresh_workspaces()

    def delete_selected_workspace(self) -> None:
        workspace = self.get_selected_workspace()

        if workspace is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete Workspace",
            f"Are you sure you want to delete the workspace '{workspace['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        delete_workspace(workspace["name"])
        self.refresh_workspaces()
