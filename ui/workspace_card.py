from services.icon_service import get_application_icon

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)


class WorkspaceCard(QFrame):

    clicked = Signal(dict)

    def __init__(self, workspace):
        super().__init__()

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        self.workspace = workspace
        self.application_labels = []
        self.locked = False

        self.build_ui()

    def build_ui(self) -> None:

        self.setObjectName("workspaceCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(28, 16, 28, 16)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(6)

        # Applications
        self.apps_layout = QVBoxLayout()
        self.apps_layout.setSpacing(4)

        self.main_layout.addLayout(self.info_layout)
        self.main_layout.addSpacing(8)
        self.main_layout.addLayout(self.apps_layout)

        self.build_title()
        self.build_subtitle()
        self.build_applications()

        self.main_layout.activate()
        self.setFixedHeight(self.main_layout.sizeHint().height() + 10)

    def build_title(self) -> None:

        self.title = QLabel(self.workspace["name"])
        self.title.setTextFormat(Qt.TextFormat.PlainText)
        self.title.setObjectName("workspaceTitle")
        self.info_layout.addWidget(self.title)

    def build_subtitle(self) -> None:
        item_count = len(self.workspace["applications"])
        item_word = "item" if item_count == 1 else "items"
        self.subtitle = QLabel(f"{item_count} {item_word} will open")
        self.subtitle.setObjectName("workspaceSubtitle")
        self.info_layout.addWidget(self.subtitle)

    def build_applications(self) -> None:

        for app in self.workspace["applications"]:

            row = QHBoxLayout()
            row.setSpacing(8)

            icon_label = QLabel()
            icon_label.setFixedSize(20, 20)

            pixmap = get_application_icon(app["path"])

            if pixmap is not None:
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("•")
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text_label = QLabel(app["name"])
            text_label.setTextFormat(Qt.TextFormat.PlainText)
            text_label.setObjectName("workspaceApplication")

            row.addWidget(icon_label)
            row.addWidget(text_label)
            row.addStretch()

            self.apps_layout.addLayout(row)

    def mousePressEvent(self, event):

        if self.locked:
            return

        self.clicked.emit(self.workspace)
        super().mousePressEvent(event)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_locked(self, locked: bool) -> None:
        self.locked = locked
        self.setProperty("locked", locked)

        if locked:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.style().unpolish(self)
        self.style().polish(self)
