import ctypes
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, QObject, Signal

WM_POWERBROADCAST = 0x0218
PBT_APMSUSPEND = 0x0004
PBT_APMRESUMEAUTOMATIC = 0x0012

WM_WTSSESSION_CHANGE = 0x02B1
WTS_SESSION_LOCK = 0x0007
WTS_SESSION_UNLOCK = 0x0008


class PowerEventService(QObject, QAbstractNativeEventFilter):

    suspending = Signal()
    resumed = Signal()
    locked = Signal()
    unlocked = Signal()
    NOTIFY_FOR_THIS_SESSION = 0

    def __init__(self) -> None:
        QObject.__init__(self)
        QAbstractNativeEventFilter.__init__(self)
        ctypes.windll.wtsapi32.WTSRegisterSessionNotification.argtypes = [wintypes.HWND, wintypes.DWORD]
        ctypes.windll.wtsapi32.WTSRegisterSessionNotification.restype = wintypes.BOOL
        ctypes.windll.wtsapi32.WTSUnRegisterSessionNotification.argtypes = [wintypes.HWND]
        ctypes.windll.wtsapi32.WTSUnRegisterSessionNotification.restype = wintypes.BOOL

    def nativeEventFilter(self, event_type, message):

        if event_type not in (
            b"windows_generic_MSG",
            b"windows_dispatcher_MSG",
        ):
            return False

        try:
            windows_message = ctypes.cast(
                int(message),
                ctypes.POINTER(wintypes.MSG),
            ).contents
        except (TypeError, ValueError):
            return False

        if windows_message.message == WM_POWERBROADCAST:

            if windows_message.wParam == PBT_APMSUSPEND:
                self.suspending.emit()

            elif windows_message.wParam == PBT_APMRESUMEAUTOMATIC:
                self.resumed.emit()

        elif windows_message.message == WM_WTSSESSION_CHANGE:

            if windows_message.wParam == WTS_SESSION_LOCK:
                self.locked.emit()

            elif windows_message.wParam == WTS_SESSION_UNLOCK:
                self.unlocked.emit()

        return False

    def register_window(self, window_id: int) -> None:
        registered = ctypes.windll.wtsapi32.WTSRegisterSessionNotification(
            window_id,
            self.NOTIFY_FOR_THIS_SESSION,
        )

        if not registered:
            raise ctypes.WinError()

    def unregister_window(self, window_id: int) -> None:
        ctypes.windll.wtsapi32.WTSUnRegisterSessionNotification(window_id)
