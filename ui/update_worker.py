from PySide6.QtCore import QThread, Signal
from services.update_service import check_for_updates


class UpdateWorker(QThread):
    result_ready = Signal(dict)

    def __init__(self, owner: str, repository: str):
        super().__init__()
        self.owner = owner
        self.repository = repository

    def run(self):
        result = check_for_updates(self.owner, self.repository)
        self.result_ready.emit(result)
