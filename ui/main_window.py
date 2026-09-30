from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QScrollArea,
    QLabel,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QPushButton,
)

from PySide6.QtCore import QTimer, Qt, QUrl

from services.launcher_service import (
    launch_workspace,
    end_workspace,
    get_active_workspace_name,
    request_application_close,
    get_running_applications,
    active_session,
)

from config import APP_NAME, APP_VERSION, PROJECT_ROOT, GITHUB_OWNER, GITHUB_REPOSITORY
from PySide6.QtGui import QIcon, QAction, QDesktopServices
from ui.history_window import HistoryWindow, format_record
from ui.header_panel import HeaderPanel
from ui.workspace_card import WorkspaceCard
from ui.workspace_window import WorkspaceWindow
from ui.settings_window import SettingsWindow
from services.settings_service import load_settings
from services.history_service import load_history
from services.workspace_service import load_workspaces
from services.bible_services import get_daily_verse
from ui.verse_card import VerseCard
from services.quote_service import get_daily_quotes
from ui.quote_card import QuoteCard
from services.power_event_service import PowerEventService
from ui.update_worker import UpdateWorker


WORKSPACES_PER_ROW = 3


class MainWindow(QMainWindow):

    def __init__(self, progress_callback=None) -> None:
        super().__init__()
        self.progress_callback = progress_callback
        self.report_progress(12, "Loading settings...")

        self.is_quitting = False
        self.close_checks = 0
        self.close_timer = QTimer(self)
        self.close_timer.setInterval(250)
        self.close_timer.timeout.connect(self.check_application_close)

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(PROJECT_ROOT / "assets/icons/app.png")))
        self.resize(1000, 700)

        central_widget = QWidget()
        central_widget.setObjectName("mainDashboard")

        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        greeting_name = ""
        settings = {"bible_verse": False, "motivation_quote": False}
        settings_error = False
        try:
            settings = load_settings()
            greeting_name = settings["greeting_name"]
        except (OSError, ValueError):
            settings_error = True

        self.settings = settings
        self.close_to_tray = settings.get("close_to_tray", False)
        self.report_progress(28, "Building the dashboard...")
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

        self.report_progress(42, "Loading daily content...")
        self.quotes_verses = QHBoxLayout()
        layout.addLayout(self.quotes_verses)
        self.verse_card = None
        self.refresh_verse(settings)
        self.quote_card = None
        self.refresh_quote(settings)

        self.report_progress(65, "Creating workspace controls...")
        self.workspace_cards = []
        self.selected_row = -1
        self.workspace_manager = None
        self.workspace_container = QFrame()
        self.workspace_container.setFrameShape(QFrame.Shape.NoFrame)
        self.button_layout = QGridLayout(self.workspace_container)
        self.button_layout.setHorizontalSpacing(20)
        self.button_layout.setVerticalSpacing(20)
        self.button_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        for column in range(WORKSPACES_PER_ROW):
            self.button_layout.setColumnStretch(column, 1)
        card_styles = (PROJECT_ROOT / "styles/workspace_cards.qss").read_text(encoding="utf-8")
        card_styles += (PROJECT_ROOT / "styles/typography.qss").read_text(encoding="utf-8")
        self.workspace_container.setStyleSheet(card_styles)
        self.workspace_scroll = QScrollArea()
        self.workspace_scroll.setWidgetResizable(True)
        self.workspace_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.workspace_scroll.setWidget(self.workspace_container)
        self.empty_workspace_state = self.create_empty_workspace_state()
        layout.addWidget(self.empty_workspace_state, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.workspace_scroll)

        self.workspace_load_warning = QLabel()
        self.workspace_load_warning.setTextFormat(Qt.TextFormat.PlainText)
        self.workspace_load_warning.setWordWrap(True)
        self.workspace_load_warning.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.workspace_load_warning)

        self.create_navbar()
        self.create_tray_icon()

        self.session_timer = QTimer(self)
        self.session_timer.setInterval(1000)
        self.session_timer.timeout.connect(self.refresh_session_status)
        self.session_timer.start()

        self.report_progress(80, "Loading workspaces and history...")
        self.refresh_workspaces()
        self.refresh_last_workspace()
        self.refresh_session_status()
        self.setup_power_events()
        self.report_progress(95, "Finishing startup...")

    def report_progress(self, value: int, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(value, message)

    def setup_power_events(self) -> None:
        self.automatic_pause_reasons = set()
        self.automatically_paused_start = None
        self.power_events_registered = False
        self.power_event_service = PowerEventService()
        self.power_event_service.suspending.connect(self.handle_system_suspend)
        self.power_event_service.resumed.connect(self.handle_system_resume)
        self.power_event_service.locked.connect(self.handle_system_lock)
        self.power_event_service.unlocked.connect(self.handle_system_unlock)
        app = QApplication.instance()
        app.installNativeEventFilter(self.power_event_service)
        app.aboutToQuit.connect(self.cleanup_power_events)
        try:
            self.power_event_service.register_window(int(self.winId()))
            self.power_events_registered = True
        except OSError as error:
            QMessageBox.warning(self, "Automatic Lock Pause Unavailable", str(error))

    def cleanup_power_events(self) -> None:
        if self.power_events_registered:
            self.power_event_service.unregister_window(int(self.winId()))
            self.power_events_registered = False
        QApplication.instance().removeNativeEventFilter(self.power_event_service)

    def add_automatic_pause_reason(self, reason: str) -> None:
        self.automatic_pause_reasons.add(reason)
        if not active_session.active or active_session.paused:
            return
        self.automatically_paused_start = active_session.start_time
        active_session.pause()
        self.refresh_session_status()

    def remove_automatic_pause_reason(self, reason: str) -> None:
        self.automatic_pause_reasons.discard(reason)
        if self.automatic_pause_reasons:
            return
        if (active_session.active and active_session.paused
                and active_session.start_time == self.automatically_paused_start):
            active_session.resume()
        self.automatically_paused_start = None
        self.refresh_session_status()

    def handle_system_suspend(self) -> None:
        self.add_automatic_pause_reason("sleeping")

    def handle_system_resume(self) -> None:
        self.remove_automatic_pause_reason("sleeping")

    def handle_system_lock(self) -> None:
        self.add_automatic_pause_reason("locked")

    def handle_system_unlock(self) -> None:
        self.remove_automatic_pause_reason("locked")

    def create_empty_workspace_state(self) -> QFrame:
        empty_state = QFrame()
        empty_state.setObjectName("emptyWorkspaceState")
        empty_state.setMinimumWidth(560)
        empty_state.setMaximumWidth(680)
        empty_state.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        empty_layout = QVBoxLayout(empty_state)
        empty_layout.setContentsMargins(38, 28, 38, 26)
        empty_layout.setSpacing(8)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("＋")
        icon.setObjectName("emptyWorkspaceIcon")
        icon.setFixedSize(52, 52)
        icon.setContentsMargins(0, 0, 0, 3)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Create your first workspace")
        title.setObjectName("emptyWorkspaceTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(
            "Group the applications, files, folders, and websites you use together."
        )
        description.setObjectName("emptyWorkspaceDescription")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        create_button = QPushButton("Create Workspace")
        create_button.setObjectName("emptyWorkspacePrimaryButton")
        create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_button.clicked.connect(self.create_first_workspace)

        manager_button = QPushButton("Open Workspace Manager")
        manager_button.setObjectName("emptyWorkspaceManagerButton")
        manager_button.setCursor(Qt.CursorShape.PointingHandCursor)
        manager_button.clicked.connect(self.show_workspace_manager)

        empty_layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignCenter)
        empty_layout.addSpacing(12)
        empty_layout.addWidget(title)
        empty_layout.addWidget(description)
        empty_layout.addSpacing(8)
        empty_layout.addWidget(create_button, 0, Qt.AlignmentFlag.AlignCenter)
        empty_layout.addSpacing(2)
        empty_layout.addWidget(manager_button, 0, Qt.AlignmentFlag.AlignCenter)

        return empty_state

    def create_first_workspace(self) -> None:
        self.show_workspace_manager()
        self.workspace_manager.add_workspace()

    def create_navbar(self) -> None:
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.workspace_menu = self.menu_bar.addMenu("Workspaces")
        self.help_menu = self.menu_bar.addMenu("Help")

        self.settings_action = self.file_menu.addAction("Settings")
        self.settings_action.triggered.connect(self.show_settings)
        self.file_menu.addSeparator()
        self.exit_action = self.file_menu.addAction("Exit Workspace Launcher")
        self.exit_action.triggered.connect(self.quit_application)

        self.manager_action = self.workspace_menu.addAction("Manage Workspaces")
        self.manager_action.triggered.connect(self.show_workspace_manager)
        self.history_action = self.workspace_menu.addAction("Workspace History")
        self.history_action.triggered.connect(self.show_history)

        self.updates = self.help_menu.addAction("Check for Updates")
        self.updates.triggered.connect(self.check_for_updates)
        self.help_menu.addSeparator()
        self.about_action = self.help_menu.addAction("About Workspace Launcher")
        self.about_action.triggered.connect(self.show_about)

    def create_tray_icon(self) -> None:
        self.tray_icon = QSystemTrayIcon(self.windowIcon(), self)
        self.tray_icon.setToolTip("Workspace Launcher")

        self.tray_menu = QMenu()

        self.tray_open_action = QAction("Open Workspace Launcher", self)
        self.tray_pause_action = QAction("Pause Workspace", self)
        self.tray_end_action = QAction("End Workspace", self)
        self.tray_exit_action = QAction("Exit Workspace Launcher", self)

        self.tray_pause_action.setEnabled(False)
        self.tray_end_action.setEnabled(False)

        self.tray_menu.addAction(self.tray_open_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.tray_pause_action)
        self.tray_menu.addAction(self.tray_end_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.tray_exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)

        self.tray_open_action.triggered.connect(self.show_from_tray)
        self.tray_pause_action.triggered.connect(self.toggle_pause)
        self.tray_end_action.triggered.connect(self.end_active_workspace)
        self.tray_icon.activated.connect(self.handle_tray_activation)
        self.tray_exit_action.triggered.connect(self.quit_application)

        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon.show()

    def show_from_tray(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def handle_tray_activation(
        self,
        reason: QSystemTrayIcon.ActivationReason,
    ) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self.show_from_tray()

    def quit_application(self) -> None:
        self.show_from_tray()
        self.is_quitting = True
        self.close()
        self.is_quitting = False

    def closeEvent(self, event) -> None:
        if not self.is_quitting and self.close_to_tray and QSystemTrayIcon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Workspace Launcher",
                "Workspace Launcher is still running in the system tray.",
                QSystemTrayIcon.MessageIcon.Information,
                2500,
            )
            return
        if get_active_workspace_name() is not None:
            QMessageBox.information(
                self,
                "Workspace Still Active",
                "End the current workspace before exiting so its session history can be saved.",
            )
            event.ignore()
            return
        if hasattr(self, "update_worker") and self.update_worker.isRunning():
            QMessageBox.information(self, "Update Check Running", "Please wait for the update check to finish, then exit again.")
            event.ignore()
            return
        self.tray_icon.hide()
        self.cleanup_power_events()
        if self.workspace_manager is not None:
            self.workspace_manager.close()
        event.accept()

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "About Workspace Launcher",
            "<h3>Workspace Launcher</h3>"
            f"<p>Version {APP_VERSION}</p>"
            "<p style='color:#8B71FF;'><b>A Pariven product</b></p>"
            "<p>Launch and track focused groups of applications from one place.</p>"
            "<p style='color:#176BEA;'>Created and maintained by "
            "<span style='color:#9A7CFF;'><b>Pariven</b></span>.</p>"
            "<p>Copyright © 2026 Jacob Farnsworth. All rights reserved.</p>"
            "<p>Third-party components remain subject to their respective licenses.</p>",
        )

    def toggle_workspace(self) -> None:
        if get_active_workspace_name() is None:
            self.launch_selected_workspace()
        else:
            self.toggle_pause()

    def refresh_verse(self, settings: dict) -> None:
        if self.verse_card is not None:
            self.quotes_verses.removeWidget(self.verse_card)
            self.verse_card.deleteLater()
            self.verse_card = None

        if settings["bible_verse"]:
            daily_verse = get_daily_verse()
            self.verse_card = VerseCard(daily_verse)
            self.quotes_verses.insertWidget(0, self.verse_card, 2)

    def show_workspace_manager(self) -> None:
        if self.workspace_manager is None:
            self.workspace_manager = WorkspaceWindow(self)
            self.workspace_manager.workspaces_changed.connect(self.refresh_workspaces)
        else:
            self.workspace_manager.reload_workspaces()
        self.workspace_manager.show()
        self.workspace_manager.raise_()
        self.workspace_manager.activateWindow()

    def refresh_quote(self, settings: dict) -> None:
        if self.quote_card is not None:
            self.quotes_verses.removeWidget(self.quote_card)
            self.quote_card.deleteLater()
            self.quote_card = None

        if settings["motivation_quote"]:
            daily_quote = get_daily_quotes()
            self.quote_card = QuoteCard(daily_quote)
            self.quotes_verses.addWidget(self.quote_card, 1)

    def select_workspace_card(self, workspace: dict) -> None:
        if get_active_workspace_name() is not None:
            return
        for row in range(len(self.workspaces)):
            if self.workspaces[row]["name"] == workspace["name"]:
                self.selected_row = row
                self.refresh_session_status()
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
            self.settings = settings_window.settings
            self.close_to_tray = settings_window.settings["close_to_tray"]
            self.header.set_greeting_name(settings_window.settings["greeting_name"])
            self.refresh_verse(settings_window.settings)
            self.refresh_quote(settings_window.settings)

    def check_for_updates(self) -> None:
        self.start_update_check(automatic=False)

    def check_for_updates_automatic(self) -> None:
        if self.settings.get("check_for_updates", False):
            self.start_update_check(automatic=True)

    def start_update_check(self, automatic: bool) -> None:
        if hasattr(self, "update_worker") and self.update_worker.isRunning():
            return
        self.update_check_is_automatic = automatic
        self.update_worker = UpdateWorker(GITHUB_OWNER, GITHUB_REPOSITORY)
        self.update_worker.result_ready.connect(self.handle_update_result)
        self.update_worker.start()

    def handle_update_result(self, result: dict) -> None:
        if self.update_check_is_automatic:
            if "error" in result or not result["available"]:
                return

        self.show_update_result(result)

    def show_update_result(self, result: dict) -> None:
        if "error" in result:
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Icon.Warning)
            message.setWindowTitle("Unable to Check for Updates")
            message.setText("Workspace Launcher could not contact GitHub.")
            message.setInformativeText(
                "Check your internet connection and try again in a moment."
            )
            message.setDetailedText(result["error"])
            message.setStandardButtons(QMessageBox.StandardButton.Ok)
            message.exec()
            return

        if not result["available"]:
            QMessageBox.information(
                self,
                "Workspace Launcher Is Up to Date",
                f"You are using the latest version ({result['current_version']}).",
            )
            return

        message = QMessageBox(self)
        message.setIcon(QMessageBox.Icon.Information)
        message.setWindowTitle("Workspace Launcher Update Available")
        message.setText(f"Version {result['latest_version']} is available.")
        message.setInformativeText(
            f"You currently have version {result['current_version']}."
        )

        if result["release_notes"]:
            message.setDetailedText(result["release_notes"])

        open_button = message.addButton(
            "Open Release",
            QMessageBox.ButtonRole.AcceptRole,
        )
        message.addButton(QMessageBox.StandardButton.Close)
        message.exec()

        if message.clickedButton() is open_button:
            QDesktopServices.openUrl(QUrl(result["release_url"]))

    def refresh_workspaces(self) -> None:
        errors = []
        workspaces = load_workspaces(errors=errors)
        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            item.widget().hide()
            item.widget().deleteLater()
        self.workspace_cards = []
        self.selected_row = -1
        self.workspaces = workspaces
        for index, workspace in enumerate(self.workspaces):
            card = WorkspaceCard(workspace)
            card.clicked.connect(self.select_workspace_card)
            row = index // WORKSPACES_PER_ROW
            column = index % WORKSPACES_PER_ROW
            self.button_layout.addWidget(card, row, column, Qt.AlignmentFlag.AlignTop)
            self.workspace_cards.append(card)
        self.empty_workspace_state.setVisible(not workspaces and not errors)
        self.workspace_scroll.setVisible(bool(workspaces) or bool(errors))
        if errors:
            message = "Some workspaces could not be loaded. Files were not changed. "
            message += "Fix the listed files, then restart Workspace Launcher.\n\n"
            message += "\n".join(errors)
            self.workspace_load_warning.setText(message)
            self.workspace_load_warning.show()
        else:
            self.workspace_load_warning.clear()
            self.workspace_load_warning.hide()
        self.refresh_session_status()

    def get_selected_workspace(self) -> dict | None:
        row = self.selected_row
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
        self.tray_pause_action.setEnabled(name is not None and active_session.active and not closing)
        self.tray_end_action.setEnabled(name is not None and not closing)
        if active_session.paused:
            self.tray_pause_action.setText("Resume Workspace")
        else:
            self.tray_pause_action.setText("Pause Workspace")

        row = self.selected_row
        selected_name = name
        if name is None and row >= 0:
            selected_name = self.workspaces[row]["name"]
        for card in self.workspace_cards:
            card.set_selected(card.workspace["name"] == selected_name)
            card.set_locked(name is not None)

        if name is None:
            row = self.selected_row
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

        close_applications = False
        try:
            settings = load_settings()
            close_applications = settings["close_applications_on_end"]
        except (OSError, ValueError) as error:
            QMessageBox.warning(
                self,
                "Could Not Load Settings",
                "Applications will be left open.\n\n" + str(error),
            )

        if close_applications:
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

        if self.automatic_pause_reasons:
            return
        self.automatically_paused_start = None

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
