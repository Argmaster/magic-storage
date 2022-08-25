from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from unittest.mock import sentinel

from cachetools import Cache, RRCache, cachedmethod

from magic_storage._atomic_file import AtomicFile
from magic_storage._base import StorageIOBase
from magic_storage._utils import this_file
from magic_storage.mixins import FullyFeaturedMixin

__all__ = ["Filesystem"]


class Filesystem(StorageIOBase, FullyFeaturedMixin):
    """Implementation of storage class which operates on filesystem items to
    preserve saved items between sessions. Loading procedures can optionally
    use caching, they do by default, therefore without disabling it you can't
    rely on loads being always instantly up to date with stores.

    Encoding used to read text files, as well as cache can be changed
    using .configure() method.

    Parameters
    ----------
    root : str | Path
        root dir for fs storage, if root points to file, parent directory of
        this file will be used.
    subdir : Optional[str], optional
        nested directory to use for file storage, when None, data will be stored
        directly in root, by default "data". When root is file, subdirectory
        in root parent directory will be used.

    Example
    -------
    ```
    >>> tmp = getfixture('tmp_path')
    >>> from magic_storage import Mode
    >>> fs = Filesystem(tmp)
    >>> example_item = {"foo": 32}
    >>> UID = "EXAMPLE UID"
    >>> fs.store(UID, example_item, mode=Mode.JSON)
    'EXAMPLE UID'
    >>> fs.is_available(UID)
    True
    >>> fs.load(UID, mode=Mode.JSON)
    {'foo': 32}
    >>>
    ```
    """

    def __init__(
        self, root: str | Path | None = None, *, subdir: Optional[str] = "data"
    ) -> None:
        if root is None:
            # Move to fourth frame in call stack including this_file() call
            root = this_file(ascend=3)

        root = Path(root)
        # When pointing to file, eg. when __file__ was used, replace it with parent dir
        if root.is_file():
            root = root.parent

        if subdir is not None:
            self._data_dir = root / subdir
        else:
            self._data_dir = root

        self._data_dir.mkdir(0o777, True, True)

        self._cache: Optional[RRCache] = RRCache(maxsize=128)
        self._encoding = "utf-8"
        super().__init__()

    def _filepath(self, identifier: str) -> Path:
        assert isinstance(identifier, str)

        return self._data_dir / identifier

    def _get_cache(self) -> Optional[Cache]:
        return self._cache

    def _is_available(self, identifier: str) -> bool:
        fname = self._filepath(identifier)
        return fname.exists() and fname.is_file()

    @cachedmethod(_get_cache)
    def _read_bytes(self, identifier: str) -> bytes:
        with AtomicFile(self._filepath(identifier)) as file:
            return file.read_bytes()

    def _write_bytes(self, identifier: str, item: bytes) -> None:
        with AtomicFile(self._filepath(identifier)) as file:
            file.write_bytes(item)

    def _delete(self, identifier: str) -> None:
        self._filepath(identifier).unlink()

    def configure(
        self,
        *,
        encoding: str | sentinel = sentinel,
        cache: Optional[Cache] | sentinel = sentinel,
    ) -> None:
        """Configure FileStorage instance.

        Parameters
        ----------
        encoding : str | sentinel, optional
            Change encoding used to read/write text, when sentinel, old value is kept, by default "utf-8"
        cache : Optional[Cache] | sentinel, optional
            Change cache instance used for caching, set to None to disable caching, when sentinel, old value is kept, by default RRCache(maxsize=128)
        """
        if encoding is not sentinel:
            self._encoding = encoding
            logging.debug(f"Changed encoding of FileStorage to {encoding}.")

        if cache is not sentinel:
            self._cache = cache  # type: ignore
            logging.debug(f"Changed cache of FileStorage to {cache}.")
