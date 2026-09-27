import sys
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QMessageBox,
)
from ui.main_window import MainWindow
from config import PROJECT_ROOT
from ui.onboarding_window import OnboardingWindow
from services.settings_service import first_run_required, load_settings
from services.startup_service import sync_startup
from ui.splash_window import SplashWindow


def main() -> None:
    app = QApplication(sys.argv)

    stylesheet = ""
    for filename in [
        "global.qss",
        "typography.qss",
        "header.qss",
        "workspace_cards.qss",
        "buttons.qss",
        "inputs.qss",
        "scrollbars.qss",
        "dialogs.qss",
        "history.qss",
        "workspace_manager.qss",
        "settings.qss",
        "onboarding.qss",
        "verse_card.qss",
        "quote_card.qss",
        "menus.qss",
        "splash.qss",
    ]:
        with (PROJECT_ROOT / "styles" / filename).open(encoding="utf-8") as file:
            stylesheet += file.read() + "\n"
    app.setStyleSheet(stylesheet)
    splash = SplashWindow()
    splash.show()
    app.processEvents()

    try:
        needs_setup = first_run_required()
    except (OSError, ValueError) as error:
        splash.close()
        QMessageBox.warning(
            None,
            "Could Not Load Settings",
            "Startup stopped because settings could not be read. "
            "Your settings file was not changed.\n\n" + str(error),
        )
        return

    if needs_setup:
        splash.update_progress(6, "Preparing First-time Setup...")
        splash.hide()
        onboarding_window = OnboardingWindow()
        if onboarding_window.exec() != QDialog.DialogCode.Accepted:
            splash.close()
            return
        splash.show()
        app.processEvents()

    try:
        sync_startup(load_settings()["launch_on_startup"])
    except (OSError, ValueError) as error:
        splash.hide()
        QMessageBox.warning(None, "Startup Setting Could Not Be Applied", str(error))
        splash.show()

    window = MainWindow(progress_callback=splash.update_progress)
    splash.transition_finished.connect(window.check_for_updates_automatic)
    splash.finish_loading(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
