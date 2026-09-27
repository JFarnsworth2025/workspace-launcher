from pathlib import Path

from PySide6.QtCore import QFileInfo
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileIconProvider

_icon_cache = {}
_icon_provider = QFileIconProvider()


def get_application_icon(exe_path: str) -> QPixmap | None:

    if exe_path in _icon_cache:
        return _icon_cache[exe_path]

    path = Path(exe_path)

    if not path.exists():
        return None

    file_info = QFileInfo(str(path))

    icon = _icon_provider.icon(file_info)

    pixmap = icon.pixmap(20, 20)

    if pixmap.isNull():
        return None

    _icon_cache[exe_path] = pixmap

    return pixmap
