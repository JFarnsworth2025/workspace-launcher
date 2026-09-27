from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtGui import QPixmap
from config import PROJECT_ROOT
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class SplashWindow(QWidget):

    transition_finished = Signal()

    def __init__(self):
        super().__init__()

        self._progress = 0
        self.progress_animation = None
        self.logo_animation = None
        self.fade_animation = None
        self.flying_logo = None

        self.setObjectName("splashWindow")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(620, 440)

        self.logo = QLabel()
        self.logo.setObjectName("splashLogo")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(str(PROJECT_ROOT / "assets/icons/app.png"))
        self.logo.setPixmap(
            pixmap.scaled(
                245,
                245,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        self.status_label = QLabel("Starting Workspace Launcher…")
        self.status_label.setObjectName("splashStatus")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("splashProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")
        self.progress_bar.setTextVisible(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 38, 64, 42)
        layout.setSpacing(14)
        layout.addStretch()
        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        layout.addSpacing(6)
        layout.addWidget(self.progress_bar)
        layout.addStretch()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center() - self.rect().center())

    def get_progress(self) -> int:
        return self._progress

    def set_progress_value(self, value: int) -> None:
        self._progress = value
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{value}%")

    progress = Property(int, get_progress, set_progress_value)

    def update_progress(self, value: int, message: str) -> None:
        self.status_label.setText(message)

        if self.progress_animation:
            self.progress_animation.stop()

        self.progress_animation = QPropertyAnimation(self, b"progress", self)
        self.progress_animation.setDuration(320)
        self.progress_animation.setStartValue(self._progress)
        self.progress_animation.setEndValue(value)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_animation.start()

        QApplication.processEvents()

    def finish_loading(self, main_window) -> None:
        self.status_label.setText("Ready")

        if self.progress_animation:
            self.progress_animation.stop()

        self.progress_animation = QPropertyAnimation(self, b"progress", self)
        self.progress_animation.setDuration(420)
        self.progress_animation.setStartValue(self._progress)
        self.progress_animation.setEndValue(100)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_animation.finished.connect(
            lambda: self.animate_logo_to_header(main_window)
        )
        self.progress_animation.start()

    def animate_logo_to_header(self, main_window) -> None:
        main_window.show()
        QApplication.processEvents()

        header_logo = main_window.header.logo
        header_effect = QGraphicsOpacityEffect(header_logo)
        header_effect.setOpacity(0)
        header_logo.setGraphicsEffect(header_effect)

        source_top_left = self.logo.mapToGlobal(self.logo.rect().topLeft())
        source_rect = QRect(source_top_left, self.logo.size())

        target_top_left = header_logo.mapToGlobal(header_logo.rect().topLeft())
        target_rect = QRect(target_top_left, header_logo.size())

        self.flying_logo = QLabel()
        self.flying_logo.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.flying_logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.flying_logo.setPixmap(self.logo.pixmap())
        self.flying_logo.setScaledContents(True)
        self.flying_logo.setGeometry(source_rect)
        self.flying_logo.show()
        self.logo.hide()

        splash_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(splash_effect)

        self.logo_animation = QPropertyAnimation(self.flying_logo, b"geometry", self)
        self.logo_animation.setDuration(760)
        self.logo_animation.setStartValue(source_rect)
        self.logo_animation.setEndValue(target_rect)
        self.logo_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.fade_animation = QPropertyAnimation(splash_effect, b"opacity", self)
        self.fade_animation.setDuration(480)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.logo_animation.finished.connect(
            lambda: self.complete_transition(header_effect)
        )
        self.fade_animation.start()
        self.logo_animation.start()

    def complete_transition(self, header_effect) -> None:
        header_effect.setOpacity(1)
        if self.flying_logo:
            self.flying_logo.close()
            self.flying_logo.deleteLater()
        self.close()
        self.transition_finished.emit()
