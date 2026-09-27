from services.greeting_service import get_time_based_greeting
from config import PROJECT_ROOT

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)


class HeaderPanel(QFrame):

    def __init__(self, greeting_name: str):
        super().__init__()

        self.greeting_name = greeting_name
        self.setFixedHeight(130)

        self.current_workspace = None

        self.build_ui()

    def build_ui(self) -> None:

        self.setObjectName("headerPanel")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(22, 8, 22, 8)
        self.main_layout.setSpacing(16)

        # ---------- Frames ----------
        self.left_frame = QFrame()
        self.center_frame = QFrame()
        self.right_frame = QFrame()

        self.left_frame.setObjectName("headerLeft")
        self.center_frame.setObjectName("headerCenter")
        self.right_frame.setObjectName("headerRight")

        # ---------- Left ----------
        self.left_layout = QVBoxLayout(self.left_frame)
        self.left_layout.setSpacing(4)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.greeting_layout = QVBoxLayout()
        self.greeting_layout.setSpacing(2)

        self.last_workspace_layout = QVBoxLayout()
        self.last_workspace_layout.setSpacing(0)

        self.left_layout.addLayout(self.greeting_layout)
        self.left_layout.addLayout(self.last_workspace_layout)

        # ---------- Center ----------
        self.center_layout = QVBoxLayout(self.center_frame)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.center_layout.setSpacing(0)

        # ---------- Right ----------
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.right_layout.setSpacing(0)

        self.build_greeting()
        self.build_last_workspace()
        self.build_logo()
        self.build_current_workspace()

        self.main_layout.addWidget(self.left_frame, 3)
        self.main_layout.addWidget(self.center_frame, 1)
        self.main_layout.addWidget(self.right_frame, 3)

    def build_logo(self) -> None:

        self.logo = QLabel()

        pixmap = QPixmap(str(PROJECT_ROOT / "assets/icons/app.png"))

        self.logo.setPixmap(
            pixmap.scaled(
                95,
                95,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        self.logo.setObjectName("headerLogo")

        self.center_layout.addWidget(self.logo)

    def build_greeting(self) -> None:

        self.greeting_label = QLabel(get_time_based_greeting(self.greeting_name))
        self.greeting_label.setTextFormat(Qt.TextFormat.PlainText)
        self.greeting_label.setObjectName("headerGreeting")

        self.greeting_layout.addWidget(self.greeting_label)

    def set_greeting_name(self, greeting_name: str) -> None:
        self.greeting_name = greeting_name
        self.greeting_label.setText(get_time_based_greeting(greeting_name))

    def set_last_workspace(self, workspace_name: str, elapsed_time: str) -> None:
        self.last_workspace_label.setText(workspace_name)
        self.last_workspace_time.setText(f"Used for {elapsed_time}")

    def build_last_workspace(self) -> None:

        self.last_workspace_title = QLabel("LAST WORKSPACE")
        self.last_workspace_title.setObjectName("headerLastWorkspaceTitle")

        self.last_workspace_label = QLabel("None Yet")
        self.last_workspace_label.setTextFormat(Qt.TextFormat.PlainText)
        self.last_workspace_label.setObjectName("headerLastWorkspace")

        self.last_workspace_time = QLabel("")
        self.last_workspace_time.setObjectName("headerLastWorkspaceTime")

        self.last_workspace_layout.addWidget(self.last_workspace_title)
        self.last_workspace_layout.addWidget(self.last_workspace_label)
        self.last_workspace_layout.addWidget(self.last_workspace_time)

    def build_current_workspace(self) -> None:

        self.current_title = QLabel("CURRENT WORKSPACE")
        self.current_title.setObjectName("headerCurrentTitle")

        self.current_workspace_label = QLabel("No Workspace Running")
        self.current_workspace_label.setTextFormat(Qt.TextFormat.PlainText)
        self.current_workspace_label.setObjectName("headerCurrentWorkspace")
        self.current_workspace_label.setProperty("state", "idle")

        self.current_timer_label = QLabel("")
        self.current_timer_label.setObjectName("headerCurrentTimer")

        self.workspace_action_button = QPushButton("Select a Workspace")
        self.workspace_action_button.setObjectName("workspaceActionButton")
        self.workspace_action_button.setProperty("actionState", "disabled")
        self.workspace_action_button.setEnabled(False)

        self.end_workspace_button = QPushButton("End")
        self.end_workspace_button.setObjectName("endWorkspaceButton")
        self.end_workspace_button.setVisible(False)

        self.workspace_controls_layout = QHBoxLayout()
        self.workspace_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.workspace_controls_layout.setSpacing(8)
        self.workspace_controls_layout.addWidget(self.workspace_action_button, 1)
        self.workspace_controls_layout.addWidget(self.end_workspace_button)

        self.right_layout.addWidget(self.current_title)
        self.right_layout.addWidget(self.current_workspace_label)
        self.right_layout.addWidget(self.current_timer_label)
        self.right_layout.addSpacing(6)
        self.right_layout.addLayout(self.workspace_controls_layout)

    def set_selected_workspace(self, workspace_name: str) -> None:

        self.current_workspace = workspace_name

        self.current_workspace_label.setText(workspace_name)
        self.current_timer_label.clear()

        self.current_workspace_label.setProperty("state", "selected")
        self.style().unpolish(self.current_workspace_label)
        self.style().polish(self.current_workspace_label)

        self.workspace_action_button.setText(f"Start {workspace_name}")
        self.workspace_action_button.setProperty("actionState", "start")
        self.workspace_action_button.setEnabled(True)
        self.end_workspace_button.setVisible(False)
        self.style().unpolish(self.workspace_action_button)
        self.style().polish(self.workspace_action_button)

    def clear_workspace_selection(self) -> None:
        self.current_workspace = None
        self.current_workspace_label.setText("No Workspace Running")
        self.current_timer_label.clear()

        self.current_workspace_label.setProperty("state", "idle")
        self.workspace_action_button.setText("Select a Workspace")
        self.workspace_action_button.setProperty("actionState", "disabled")
        self.workspace_action_button.setEnabled(False)
        self.end_workspace_button.setVisible(False)

        self.style().unpolish(self.current_workspace_label)
        self.style().polish(self.current_workspace_label)
        self.style().unpolish(self.workspace_action_button)
        self.style().polish(self.workspace_action_button)

    def workspace_started(self, workspace_name: str) -> None:

        self.current_workspace = workspace_name

        self.current_workspace_label.setText(workspace_name)

        self.current_workspace_label.setProperty("state", "running")
        self.style().unpolish(self.current_workspace_label)
        self.style().polish(self.current_workspace_label)

        self.workspace_action_button.setText(f"Pause {workspace_name}")
        self.workspace_action_button.setProperty("actionState", "pause")
        self.workspace_action_button.setEnabled(True)
        self.end_workspace_button.setVisible(True)
        self.style().unpolish(self.workspace_action_button)
        self.style().polish(self.workspace_action_button)

    def workspace_paused(self) -> None:
        self.current_workspace_label.setProperty("state", "paused")
        self.style().unpolish(self.current_workspace_label)
        self.style().polish(self.current_workspace_label)

        self.workspace_action_button.setText(f"Resume {self.current_workspace}")
        self.workspace_action_button.setProperty("actionState", "resume")
        self.style().unpolish(self.workspace_action_button)
        self.style().polish(self.workspace_action_button)

    def workspace_resumed(self) -> None:
        self.current_workspace_label.setProperty("state", "running")
        self.style().unpolish(self.current_workspace_label)
        self.style().polish(self.current_workspace_label)

        self.workspace_action_button.setText(f"Pause {self.current_workspace}")
        self.workspace_action_button.setProperty("actionState", "pause")
        self.style().unpolish(self.workspace_action_button)
        self.style().polish(self.workspace_action_button)

    def workspace_stopped(self, elapsed_time: str) -> None:

        self.set_last_workspace(self.current_workspace, elapsed_time)
        self.clear_workspace_selection()

    def update_workspace_timer(self, elapsed_time: str) -> None:

        self.current_timer_label.setText(elapsed_time)
