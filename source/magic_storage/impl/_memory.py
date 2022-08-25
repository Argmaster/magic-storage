from __future__ import annotations

from magic_storage._base import StorageIOBase
from magic_storage.mixins import FullyFeaturedMixin


class InMemory(StorageIOBase, FullyFeaturedMixin):
    """Implementation of storage class which operates only in RAM and thus will
    be lost after garbage collection.

    However it is much faster than any other cache type.
    """

    def __init__(self) -> None:
        self.__storage: dict[str, str | bytes] = {}

    def _is_available(self, name: str) -> bool:
        return name in self.__storage

    def _read_bytes(self, name: str) -> bytes:
        value = self.__storage[name]
        assert isinstance(value, bytes)

        return value

    def _write_bytes(self, name: str, item: bytes) -> None:
        self.__storage[name] = item

    def _delete(self, name: str) -> None:
        self.__storage.pop(name)
