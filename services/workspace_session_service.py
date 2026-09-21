from time import monotonic
from datetime import datetime


class WorkspaceSession:

    def __init__(self) -> None:
        self.active = False
        self.paused = False
        self.accumulated_seconds = 0.0
        self.segment_start = 0.0
        self.start_time: datetime | None = None
        self.end_time: datetime | None = None

    def start(self) -> None:
        self.active = True
        self.paused = False
        self.accumulated_seconds = 0.0
        self.segment_start = monotonic()
        self.start_time = datetime.now().astimezone()
        self.end_time = None

    def pause(self) -> None:
        if not self.active or self.paused:
            return

        self.accumulated_seconds += monotonic() - self.segment_start
        self.paused = True

    def resume(self) -> None:
        if not self.active or not self.paused:
            return

        self.segment_start = monotonic()
        self.paused = False

    def end(self) -> None:
        if not self.active:
            return

        self.pause()
        self.active = False
        self.paused = False
        self.end_time = datetime.now().astimezone()

    def get_elapsed_seconds(self) -> float:
        elapsed = self.accumulated_seconds

        if self.active and not self.paused:
            elapsed += monotonic() - self.segment_start

        return elapsed

    def get_elapsed_time(self) -> str:

        total_seconds = int(self.get_elapsed_seconds())

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def to_dict(self, workspace_name: str) -> dict:
        if self.start_time is None or self.end_time is None:
            raise ValueError("Only completed sessions can be saved to history.")
        return {
            "workspace_name": workspace_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration": int(self.get_elapsed_seconds()),
        }
