from __future__ import annotations

import os
import tempfile
from inspect import Traceback
from pathlib import Path
from typing import Any, Optional, Type

from filelock import FileLock

__all__ = ["AtomicFile"]


class AtomicFile:
    def __init__(self, file_path: str | Path) -> None:
        file_path = Path(file_path)
        self._file = file_path
        self._lock_file = file_path.parent / f"{file_path.name}.lock"
        self._lock = FileLock(self._lock_file)

    def __enter__(self) -> AtomicFile:
        self._file.touch(0o777, True)
        self._lock.acquire()
        return self

    def read_text(self, **kwargs: Any) -> str:
        assert self._lock.is_locked
        return self._file.read_text(**kwargs)

    def write_text(self, content: str, **kwargs: Any) -> None:
        assert self._lock.is_locked
        temp = tempfile.NamedTemporaryFile(
            mode="wt",
            delete=False,
            suffix=self._file.name,
            dir=self._file.parent,
            encoding="utf-8",
        )
        temp.write(content)
        temp.flush()
        temp.close()
        os.replace(temp.name, self._file)

    def read_bytes(self, **kwargs: Any) -> bytes:
        assert self._lock.is_locked
        return self._file.read_bytes(**kwargs)

    def write_bytes(self, content: bytes, **kwargs: Any) -> None:
        assert self._lock.is_locked
        temp = tempfile.NamedTemporaryFile(
            mode="wb",
            delete=False,
            suffix=self._file.name,
            dir=self._file.parent,
        )
        temp.write(content)
        temp.flush()
        temp.close()
        os.replace(temp.name, self._file)

    def __exit__(
        self,
        _exception_type: Optional[Type[BaseException]],
        _exception_value: Optional[BaseException],
        _traceback: Traceback,
    ) -> None:
        self._lock.release()
