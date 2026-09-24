from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.history_service import load_history


def format_record(record: object) -> tuple[str, str, str, str]:
    """Validate a stored record before displaying it; never modify history."""
    if not isinstance(record, dict):
        raise ValueError("Invalid session record")

    name = record.get("workspace_name")
    duration = record.get("duration")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Invalid workspace name")
    if type(duration) is not int or duration < 0:
        raise ValueError("Invalid duration")

    timestamps = []
    for key in ("start_time", "end_time"):
        value = record.get(key)
        if not isinstance(value, str):
            raise ValueError("Invalid timestamp")
        timestamp = datetime.fromisoformat(value)
        # Keep the recorded offset; older records may have no timezone.
        timestamps.append(timestamp.isoformat(sep=" ", timespec="seconds"))

    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    return name, *timestamps, f"{hours:02}:{minutes:02}:{seconds:02}"


class HistoryWindow(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Workspace History")
        self.resize(950, 500)

        layout = QVBoxLayout(self)
        self.summary = QLabel()
        self.summary.setTextFormat(Qt.TextFormat.PlainText)
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Workspace", "Started", "Ended", "Active duration"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().hide()
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for column in range(1, 4):
            header.setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh)
        layout.addWidget(refresh_button)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.refresh()

    def refresh(self) -> None:
        self.table.setRowCount(0)
        try:
            records = load_history()
        except (OSError, ValueError) as error:
            self.summary.setText(f"Could not load history: {error}")
            return

        rows = []
        skipped = 0
        # History is appended on completion, so reverse for latest-saved first.
        for record in reversed(records):
            try:
                rows.append(format_record(record))
            except (ValueError, OverflowError):
                skipped += 1

        self.table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))

        message = (
            f"{len(rows)} completed session(s). Latest saved first. "
            "Active duration excludes pauses."
            if rows
            else "No completed sessions to display."
        )
        if skipped:
            message += f" Skipped {skipped} invalid record(s); the history file was not changed."
        self.summary.setText(message)
