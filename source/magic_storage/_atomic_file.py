from __future__ import annotations

from inspect import Traceback
from pathlib import Path
from typing import IO, Optional, Type, cast

from filelock import BaseFileLock, FileLock

__all__ = ["AtomicFile"]


class AtomicFile:
    """File like object supporting writing and reading in quasi atomic manor.

    All reading and writing is done under lock and writing is done with
    temporary files and os.replace().

    Example
    -------
    ```
    >>> tmp = getfixture("tmp_path")
    >>> with AtomicFile(tmp / "some_file.txt", "w") as file:
    ...     file.write(b"Example content")
    ...
    15
    >>> with AtomicFile(tmp / "some_file.txt") as file:
    ...     file.read()
    ...
    b'Example content'
    >>>
    ```
    """

    _mode: str
    _file_path: Path
    _file_lock: Optional[BaseFileLock]

    def __init__(self, file: str | Path, mode: str = "r") -> None:
        assert "t" not in mode, f"Text mode not allowed, got {mode!r}"
        self._mode: str = mode + ("b" if "b" not in mode else "")
        self._file_path = Path(file).absolute()
        self._file_lock = None

    @property
    def name(self) -> str:
        """Return absolute path to file."""
        return str(self._file_path)

    def _acquire(self) -> None:
        if not self._file_path.exists():
            self._file_path.parent.mkdir(0o777, True, True)
            self._file_path.touch(0o777, True)

        lock_path = self._file_path.parent / f"{self._file_path.name}.lock"
        self._file_lock = FileLock(lock_path)
        self._file_lock.acquire()

    def __enter__(self) -> IO[bytes]:
        self._acquire()
        self._file_io = cast(IO[bytes], self._file_path.open(self._mode))
        return self._file_io

    def __exit__(
        self,
        _exception_type: Optional[Type[BaseException]],
        _exception_value: Optional[BaseException],
        _traceback: Traceback,
    ) -> None:
        self._file_io.flush()
        self._file_io.close()
        assert self._file_lock is not None, self._file_path
        self._file_lock.release()
