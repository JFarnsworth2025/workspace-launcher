from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Signal, Qt

from services.workspace_service import load_workspaces, delete_workspace, save_workspace
from config import PROJECT_ROOT
from ui.workspace_editor import WorkspaceEditor


class WorkspaceWindow(QMainWindow):

    workspaces_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workspaces = []

        self.setup_window()
        self.create_widgets()
        self.create_layouts()
        self.setStyleSheet(
            (PROJECT_ROOT / "styles/workspace_manager.qss").read_text(encoding="utf-8")
        )
        self.reload_workspaces()

    def setup_window(self) -> None:
        self.setObjectName("workspaceManagerWindow")
        self.setWindowTitle("Workspace Launcher | Workspace Manager")
        self.resize(860, 560)
        self.setMinimumSize(680, 440)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

    def create_widgets(self) -> None:
        self.title_label = QLabel("Workspace Manager")
        self.title_label.setObjectName("workspaceManagerTitle")

        self.subtitle_label = QLabel(
            "View your workspaces and the applications assigned to them."
        )
        self.subtitle_label.setObjectName("workspaceManagerSubtitle")

        self.workspace_list = QListWidget()
        self.workspace_list.setObjectName("workspaceManagerList")
        self.workspace_list.setMinimumWidth(210)
        self.workspace_list.setMaximumWidth(280)
        self.workspace_list.setSpacing(5)

        self.details_frame = QFrame()
        self.details_frame.setObjectName("workspaceManagerDetails")

        self.workspace_name = QLabel("Select a workspace")
        self.workspace_name.setTextFormat(Qt.TextFormat.PlainText)
        self.workspace_name.setObjectName("workspaceManagerName")

        self.applications = QTreeWidget()
        self.applications.setObjectName("workspaceManagerApplications")
        self.applications.setHeaderLabels(["Workspace Item", "Path"])
        self.applications.header().setStretchLastSection(True)

        self.add_button = QPushButton("Add Workspace")
        self.edit_button = QPushButton("Edit Workspace")
        self.remove_button = QPushButton("Remove Workspace")
        self.close_button = QPushButton("Close")
        self.reload_button = QPushButton("Reload")
        self.reload_button.setObjectName("secondaryButton")
        self.reload_button.clicked.connect(self.reload_workspaces)
        self.load_warning = QLabel()
        self.load_warning.setWordWrap(True)
        self.load_warning.setTextFormat(Qt.TextFormat.PlainText)

        self.add_button.setObjectName("primaryButton")
        self.edit_button.setObjectName("secondaryButton")
        self.remove_button.setObjectName("secondaryButton")
        self.close_button.setObjectName("secondaryButton")

        self.edit_button.setEnabled(False)
        self.remove_button.setEnabled(False)
        self.add_button.setEnabled(True)

        self.close_button.clicked.connect(self.close)
        self.add_button.clicked.connect(self.add_workspace)
        self.workspace_list.currentRowChanged.connect(self.show_workspace)
        self.edit_button.clicked.connect(self.edit_workspace)
        self.remove_button.clicked.connect(self.remove_workspace)

    def create_layouts(self) -> None:
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 18, 20, 18)
        main_layout.setSpacing(10)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addWidget(self.load_warning)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)
        content_layout.addWidget(self.workspace_list, 1)

        details_layout = QVBoxLayout(self.details_frame)
        details_layout.setContentsMargins(14, 14, 14, 14)
        details_layout.setSpacing(8)
        details_layout.addWidget(self.workspace_name)
        details_layout.addWidget(self.applications)

        content_layout.addWidget(self.details_frame, 2)
        main_layout.addLayout(content_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.reload_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    def reload_workspaces(self) -> None:
        errors = []
        self.workspaces = load_workspaces(errors=errors)
        self.load_warning.setText("\n".join(errors))
        self.load_warning.setVisible(bool(errors))
        self.display_workspaces()

    def display_workspaces(self) -> None:
        self.workspace_list.clear()

        for workspace in self.workspaces:
            self.workspace_list.addItem(workspace["name"])

        if self.workspaces:
            self.workspace_list.setCurrentRow(0)

    def show_workspace(self, row: int) -> None:
        self.applications.clear()

        if row == -1:
            self.workspace_name.setText("Select a workspace")
            self.edit_button.setEnabled(False)
            self.remove_button.setEnabled(False)
            return

        workspace = self.workspaces[row]
        self.workspace_name.setText(workspace["name"])

        for application in workspace["applications"]:
            self.applications.addTopLevelItem(self.create_application_item(application))

        self.applications.resizeColumnToContents(0)
        self.edit_button.setEnabled(True)
        self.remove_button.setEnabled(True)

    def create_application_item(self, application: dict) -> QTreeWidgetItem:
        return QTreeWidgetItem([application["name"], application["path"]])

    def add_workspace(self) -> None:
        editor = WorkspaceEditor()
        result = editor.exec()

        if result == QDialog.DialogCode.Accepted:
            try:
                save_workspace(editor.get_workspace())
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, "Could Not Save Workspace", str(error))
                return
            self.reload_workspaces()
            self.workspaces_changed.emit()

    def edit_workspace(self) -> None:
        row = self.workspace_list.currentRow()

        if row == -1:
            return

        workspace = self.workspaces[row]
        editor = WorkspaceEditor(workspace)

        result = editor.exec()
        if result == QDialog.DialogCode.Accepted:
            try:
                save_workspace(editor.get_workspace(), original_name=workspace["name"])
            except (OSError, ValueError) as error:
                QMessageBox.warning(self, "Could Not Save Workspace", str(error))
                return
            self.reload_workspaces()
            self.workspaces_changed.emit()

    def remove_workspace(self) -> None:
        row = self.workspace_list.currentRow()

        if row == -1:
            return

        workspace_name = self.workspaces[row]["name"]

        confirmation = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the workspace '{workspace_name}'?",
            QMessageBox.StandardButtons(QMessageBox.Yes | QMessageBox.No),
            QMessageBox.StandardButton(QMessageBox.No),
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_workspace(workspace_name)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Could Not Delete Workspace", str(error))
            return
        self.reload_workspaces()
        self.workspaces_changed.emit()
