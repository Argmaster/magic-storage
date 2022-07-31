from __future__ import annotations

from pathlib import Path

from cachetools import Cache, RRCache, cachedmethod

from .base import StorageIOBase

__all__ = ["LocalStorage"]


class LocalStorage(StorageIOBase):
    def __init__(self, current_file: str | Path) -> None:
        self._current_file = Path(current_file)
        self._current_dir = self._current_file.parent
        self._current_data = self._current_dir / "data"
        self._current_data.mkdir(0o777, True, True)
        self._cache: RRCache = RRCache(maxsize=128)
        super().__init__()

    def _get_cache(self) -> Cache:
        return self._cache

    def _is_available(self, uid: str) -> bool:
        file = self._current_data / uid
        if file.is_dir():
            raise RuntimeError(
                f"{file.absolute()} is a directory, was expected to be a file."
            )
        return file.exists()

    @cachedmethod(_get_cache)
    def _read_text(self, uid: str) -> str:
        return (self._current_data / uid).read_text(encoding=self._encoding)

    @cachedmethod(_get_cache)
    def _read_bytes(self, uid: str) -> bytes:
        return (self._current_data / uid).read_bytes()

    def _write_text(self, uid: str, item: str) -> None:
        file = self._current_data / uid
        with file.open("wt", encoding=self._encoding) as io:
            io.write(item)

    def _write_bytes(self, uid: str, item: bytes) -> None:
        file = self._current_data / uid
        with file.open("wb") as io:
            io.write(item)

    def configure(self, encoding: str = "utf-8") -> None:
        self._encoding = encoding
