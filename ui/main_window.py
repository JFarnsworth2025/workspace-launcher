from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QWidget,
    QListWidget,
)

from PySide6.QtCore import QTimer

from services.launcher_service import (
    launch_workspace,
    end_workspace,
    get_active_workspace_name,
    request_application_close,
    get_running_applications,
    active_session,
)

from config import APP_NAME
from ui.workspace_editor import WorkspaceEditor
from services.workspace_service import save_workspace, load_workspaces, delete_workspace


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.close_checks = 0
        self.close_timer = QTimer(self)
        self.close_timer.setInterval(250)
        self.close_timer.timeout.connect(self.check_application_close)

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

        launch_workspace_button = QPushButton("Launch Workspace")
        layout.addWidget(launch_workspace_button)
        launch_workspace_button.clicked.connect(self.launch_selected_workspace)

        end_workspace_button = QPushButton("End Workspace")
        layout.addWidget(end_workspace_button)
        end_workspace_button.clicked.connect(self.end_active_workspace)

        self.pause_button = QPushButton("Pause")
        layout.addWidget(self.pause_button)
        self.pause_button.clicked.connect(self.toggle_pause)

        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self.refresh_session_status)
        self.session_timer.start()

        self.refresh_workspaces()
        self.refresh_session_status()

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
            QMessageBox.warning(self, "Warning", "Please select a workspace first.")
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

    def launch_selected_workspace(self) -> None:
        workspace = self.get_selected_workspace()

        if workspace is None:
            return

        if not workspace["applications"]:
            QMessageBox.information(
                self,
                "Empty Workspace",
                "Add an item to the workspace before launching.",
            )
            return

        try:
            successful_launches, launch_errors = launch_workspace(workspace)
        except ValueError as e:
            QMessageBox.warning(self, "Workspace Active Already", str(e))
            return

        self.refresh_session_status()

        message = f"Opened {successful_launches} item(s) successfully."

        if launch_errors:
            message += "\n\nCould not start:\n" + "\n".join(launch_errors)
            QMessageBox.warning(self, "Launch Errors", message)
            return

        QMessageBox.information(self, "Launch Successful", message)

    def refresh_session_status(self) -> None:
        name = get_active_workspace_name()
        closing = self.close_timer.isActive()

        self.pause_button.setEnabled(name is not None and not closing)
        self.pause_button.setText("Resume" if active_session.paused else "Pause")

        if closing:
            self.statusBar().showMessage("Closing Applications... Please wait")
            return

        if name is None:
            self.statusBar().showMessage("No active workspace.")
        else:
            state = "Paused" if active_session.paused else "Active"
            elapsed = active_session.get_elapsed_time()
            self.statusBar().showMessage(f"{state}: {name} | {elapsed}")

    def end_active_workspace(self) -> None:

        if self.close_timer.isActive():
            QMessageBox.information(
                self,
                "Closing Applications",
                "Please wait for the applications to close before ending the workspace.",
            )
            return

        name = get_active_workspace_name()

        if name is None:
            QMessageBox.information(
                self, "No Active Workspace", "There is no active workspace to end."
            )
            return

        answer = QMessageBox.question(
            self,
            "End Workspace",
            f'End "{name}"? You can choose whether to close its applications next.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        close_choice = QMessageBox.question(
            self,
            "Close Applications",
            "Force-stop tracked applications? Unsaved work may be lost.\n"
            "Files, folders, and websites will remain open.\n\n"
            "Yes: force-stop applications.\n"
            "No: leave applications open.\n"
            "Cancel: keep the workspace active.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.No,
        )

        if close_choice == QMessageBox.StandardButton.Cancel:
            return

        if close_choice == QMessageBox.StandardButton.Yes:
            close_errors = request_application_close()

            if close_errors:
                QMessageBox.warning(
                    self,
                    "Close Errors",
                    "Some applications could not be closed:\n"
                    + "\n".join(close_errors),
                )

            self.close_checks = 0
            self.close_timer.start()
            self.statusBar().showMessage("Closing applications... Please wait.")
            return

        end_workspace()
        self.refresh_session_status()

    def check_application_close(self) -> None:
        self.close_checks += 1

        try:
            running_apps = get_running_applications()
        except OSError as e:
            self.close_timer.stop()
            self.refresh_session_status()
            QMessageBox.warning(
                self,
                "Error Checking Applications",
                f"An error occurred while checking running applications: {e}",
            )
            return

        if not running_apps:
            self.close_timer.stop()
            end_workspace()
            self.refresh_session_status()
            return

        if self.close_checks >= 20:
            self.close_timer.stop()
            self.refresh_session_status()
            QMessageBox.warning(
                self,
                "Applications Still Running",
                "The workspace remains active. You can retry ending it.\n\n"
                + "\n".join(running_apps),
            )

    def toggle_pause(self) -> None:
        if self.close_timer.isActive() or not active_session.active:
            return

        if active_session.paused:
            active_session.resume()
        else:
            active_session.pause()

        self.refresh_session_status()
