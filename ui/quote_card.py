from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)


class QuoteCard(QFrame):

    def __init__(self, quote):
        super().__init__()

        self.setMinimumHeight(150)
        self.setMinimumWidth(360)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )

        self.quote = quote

        self.build_ui()

    def build_ui(self) -> None:

        self.setObjectName("quoteCard")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        self.build_title()
        self.build_quote()
        self.main_layout.setSpacing(10)
        self.build_author()
        self.source_label = QLabel('Quotes provided by <a href="https://zenquotes.io/">ZenQuotes API</a>')
        self.source_label.setOpenExternalLinks(True)
        self.source_label.setWordWrap(True)
        self.main_layout.addWidget(self.source_label)

    def build_title(self) -> None:

        self.title = QLabel("Today's Quote")
        self.main_layout.addWidget(self.title)
        self.title.setObjectName("quoteTitle")

    def build_quote(self) -> None:

        self.quote_text = QLabel(self.quote["quote"])
        self.quote_text.setTextFormat(Qt.TextFormat.PlainText)
        self.main_layout.addWidget(self.quote_text)
        self.quote_text.setObjectName("quoteText")

        self.quote_text.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.quote_text.setWordWrap(True)

    def build_author(self) -> None:

        self.quote_author = QLabel(f"—{self.quote['author']}")
        self.main_layout.addWidget(self.quote_author)
        self.quote_author.setObjectName("quoteAuthor")
        self.quote_author.setTextFormat(Qt.TextFormat.PlainText)
