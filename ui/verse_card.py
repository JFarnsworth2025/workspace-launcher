from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)


class VerseCard(QFrame):

    def __init__(self, verse):
        super().__init__()

        self.setMinimumHeight(150)
        self.setMinimumWidth(250)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        self.verse = verse

        self.build_ui()

    def build_ui(self) -> None:

        self.setObjectName("verseCard")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        self.build_title()
        self.build_reference()
        self.build_verse()

    def build_title(self) -> None:

        self.title = QLabel("Today's Verse")
        self.main_layout.addWidget(self.title)

        self.title.setObjectName("verseTitle")

    def build_reference(self) -> None:

        self.verse_reference = QLabel(self.verse["reference"])
        self.verse_reference.setTextFormat(Qt.TextFormat.PlainText)
        self.main_layout.addWidget(self.verse_reference)

        self.verse_reference.setObjectName("verseReference")

    def build_verse(self) -> None:

        self.verse_text = QLabel(self.verse["text"])
        self.verse_text.setTextFormat(Qt.TextFormat.PlainText)
        self.main_layout.addWidget(self.verse_text)

        self.verse_text.setWordWrap(True)
        self.verse_text.setObjectName("verseText")
