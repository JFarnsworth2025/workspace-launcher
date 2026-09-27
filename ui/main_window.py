from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    QLabel,
)

from PySide6.QtCore import QTimer, Qt

from services.launcher_service import (
    launch_workspace,
    end_workspace,
    get_active_workspace_name,
    request_application_close,
    get_running_applications,
    active_session,
)

from config import APP_NAME, PROJECT_ROOT
from PySide6.QtGui import QIcon
from ui.history_window import HistoryWindow, format_record
from ui.header_panel import HeaderPanel
from ui.workspace_card import WorkspaceCard
from ui.workspace_window import WorkspaceWindow
from ui.settings_window import SettingsWindow
from services.settings_service import load_settings
from services.history_service import load_history
from services.workspace_service import load_workspaces


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.close_checks = 0
        self.close_timer = QTimer(self)
        self.close_timer.setInterval(250)
        self.close_timer.timeout.connect(self.check_application_close)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(PROJECT_ROOT / "assets/icons/app.png")))
        self.resize(1000, 700)

        central_widget = QWidget()

        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        greeting_name = ""
        settings_error = False
        try:
            settings = load_settings()
            greeting_name = settings["greeting_name"]
        except (OSError, ValueError):
            settings_error = True

        self.header = HeaderPanel(greeting_name)
        self.header.setStyleSheet(
            (PROJECT_ROOT / "styles/header.qss").read_text(encoding="utf-8")
        )
        layout.addWidget(self.header)
        self.header.workspace_action_button.clicked.connect(self.toggle_workspace)
        self.header.end_workspace_button.clicked.connect(self.end_active_workspace)
        if settings_error:
            self.header.greeting_label.setText(
                "Settings could not be loaded. Open Settings for details."
            )

        self.workspace_list = QListWidget()
        self.workspace_cards = []
        self.workspace_manager = None
        self.workspace_list.setSpacing(8)
        card_styles = (PROJECT_ROOT / "styles/workspace_cards.qss").read_text(encoding="utf-8")
        card_styles += (PROJECT_ROOT / "styles/typography.qss").read_text(encoding="utf-8")
        self.workspace_list.setStyleSheet(card_styles)
        layout.addWidget(self.workspace_list)
        self.workspace_list.currentRowChanged.connect(self.refresh_session_status)

        self.workspace_load_warning = QLabel()
        self.workspace_load_warning.setTextFormat(Qt.TextFormat.PlainText)
        self.workspace_load_warning.setWordWrap(True)
        self.workspace_load_warning.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.workspace_load_warning)

        reload_button = QPushButton("Reload Workspaces")
        reload_button.clicked.connect(self.refresh_workspaces)
        layout.addWidget(reload_button)

        manager_button = QPushButton("Manage Workspaces")
        layout.addWidget(manager_button)
        manager_button.clicked.connect(self.show_workspace_manager)

        history_button = QPushButton("View History")
        layout.addWidget(history_button)
        history_button.clicked.connect(self.show_history)

        settings_button = QPushButton("Settings")
        layout.addWidget(settings_button)
        settings_button.clicked.connect(self.show_settings)

        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self.refresh_session_status)
        self.session_timer.start()

        self.refresh_workspaces()
        self.refresh_last_workspace()
        self.refresh_session_status()

    def toggle_workspace(self) -> None:
        if get_active_workspace_name() is None:
            self.launch_selected_workspace()
        else:
            self.toggle_pause()

    def show_workspace_manager(self) -> None:
        if self.workspace_manager is None:
            self.workspace_manager = WorkspaceWindow(self)
            self.workspace_manager.workspaces_changed.connect(self.refresh_workspaces)
        else:
            self.workspace_manager.reload_workspaces()
        self.workspace_manager.show()
        self.workspace_manager.raise_()
        self.workspace_manager.activateWindow()

    def select_workspace_card(self, workspace: dict) -> None:
        if get_active_workspace_name() is not None:
            return
        for row in range(len(self.workspaces)):
            if self.workspaces[row]["name"] == workspace["name"]:
                self.workspace_list.setCurrentRow(row)
                return

    def refresh_last_workspace(self) -> None:
        try:
            records = load_history()
        except (OSError, ValueError):
            self.header.last_workspace_label.setText("History unavailable")
            self.header.last_workspace_time.setText("Open View History for details")
            return

        for record in reversed(records):
            try:
                name, start, end, duration = format_record(record)
            except (ValueError, OverflowError):
                continue
            self.header.set_last_workspace(name, duration)
            return

    def show_history(self) -> None:
        history_window = HistoryWindow(self)
        history_window.exec()

    def show_settings(self) -> None:
        try:
            settings = load_settings()
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Could Not Load Settings", str(error))
            return

        settings_window = SettingsWindow(settings, self)
        if settings_window.exec() == QDialog.DialogCode.Accepted:
            self.header.set_greeting_name(settings_window.settings["greeting_name"])

    def refresh_workspaces(self) -> None:
        errors = []
        workspaces = load_workspaces(errors=errors)
        self.workspace_cards = []
        self.workspace_list.clear()
        self.workspaces = workspaces
        for workspace in self.workspaces:
            card = WorkspaceCard(workspace)
            card.clicked.connect(self.select_workspace_card)
            item = QListWidgetItem()
            item.setSizeHint(card.sizeHint())
            self.workspace_list.addItem(item)
            self.workspace_list.setItemWidget(item, card)
            self.workspace_cards.append(card)
        if errors:
            message = "Some workspaces could not be loaded. Files were not changed. "
            message += "Fix the listed files, then click Reload Workspaces.\n\n"
            message += "\n".join(errors)
            self.workspace_load_warning.setText(message)
            self.workspace_load_warning.show()
        else:
            self.workspace_load_warning.clear()
            self.workspace_load_warning.hide()
        self.refresh_session_status()

    def get_selected_workspace(self) -> dict | None:
        row = self.workspace_list.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", "Please select a workspace first.")
            return None

        return self.workspaces[row]

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

        row = self.workspace_list.currentRow()
        selected_name = name
        if name is None and row >= 0:
            selected_name = self.workspaces[row]["name"]
        for card in self.workspace_cards:
            card.set_selected(card.workspace["name"] == selected_name)
            card.set_locked(name is not None)

        if name is None:
            row = self.workspace_list.currentRow()
            if row >= 0:
                self.header.set_selected_workspace(self.workspaces[row]["name"])
            else:
                self.header.clear_workspace_selection()
        else:
            self.header.workspace_started(name)
            self.header.update_workspace_timer(active_session.get_elapsed_time())
            if active_session.paused:
                self.header.workspace_paused()

        self.header.end_workspace_button.setEnabled(not closing)

        if closing:
            self.header.workspace_action_button.setEnabled(False)
            self.header.workspace_action_button.setText("Closing...")
            self.statusBar().showMessage("Closing Applications... Please wait")
            return

        if name is None:
            self.statusBar().showMessage("No active workspace.")
        elif not active_session.active:
            self.header.workspace_action_button.setEnabled(False)
            self.header.workspace_action_button.setText("History not saved")
            self.statusBar().showMessage(
                f"History not saved: {name} | Click End to retry."
            )
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

        if not active_session.active:
            self.finish_workspace()
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

        default_choice = QMessageBox.StandardButton.No
        try:
            settings = load_settings()
            if settings["close_applications_on_end"]:
                default_choice = QMessageBox.StandardButton.Yes
        except (OSError, ValueError) as error:
            QMessageBox.warning(
                self,
                "Could Not Load Settings",
                "The default choice will leave applications open.\n\n" + str(error),
            )

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
            default_choice,
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
            self.refresh_session_status()
            return

        self.finish_workspace()

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
            self.finish_workspace()
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

    def finish_workspace(self) -> None:
        try:
            end_workspace()
        except (OSError, ValueError) as e:
            self.refresh_session_status()
            QMessageBox.warning(
                self,
                "History Not Saved",
                "The session timer has stopped, but its history could not be saved.\n\n"
                "The record is kept in memory while this app stays open. After resolving the problem, click End to retry.\n\n"
                f"{e}",
            )
            return

        self.refresh_last_workspace()
        self.refresh_session_status()
