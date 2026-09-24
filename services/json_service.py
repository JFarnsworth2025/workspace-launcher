import json
import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


logger = logging.getLogger(__name__)


def save_json(path: Path, data: object) -> None:
    """Replace a JSON file only after its new contents are fully written.

    The parent directory must exist. This does not coordinate concurrent writers.
    """
    content = json.dumps(data, indent=4, ensure_ascii=False)
    temporary_path: Path | None = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            file.write(content)
            file.flush()
            os.fsync(file.fileno())

        # Close the temporary file first so replacement works on Windows.
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                # Preserve the original save error if cleanup also fails.
                logger.warning(
                    "Could not remove temporary file %s", temporary_path, exc_info=True
                )
