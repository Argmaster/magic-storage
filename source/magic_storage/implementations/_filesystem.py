from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from unittest.mock import sentinel

from magic_storage._atomic_file import AtomicFile
from magic_storage._storage import StorageIOBase
from magic_storage._utils import slugify_encode, this_file
from magic_storage.extensions import FullyFeaturedMixin

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

        root = root.absolute()

        if subdir is not None:
            self._data_dir = root / subdir
        else:
            self._data_dir = root

        self._data_dir.mkdir(0o777, True, True)

        self._encoding = "utf-8"
        super().__init__()

    def _filepath(self, name: str) -> Path:
        assert isinstance(name, str), name
        name = slugify_encode(name)
        logging.debug(f"Slugified name into {name!r}")

        return self._data_dir / name

    def _is_available(self, name: str) -> bool:
        fname = self._filepath(name)
        return fname.exists() and fname.is_file()

    def _read_bytes(self, name: str) -> bytes:
        logging.debug(f"Filesystem read bytes {name!r}")

        location = self._filepath(name)
        logging.debug(f"Store to location {location}")

        with AtomicFile(location, "r") as file:
            retval = file.read()

        logging.debug(f"Filesystem read bytes {len(retval)}B.")
        assert isinstance(retval, bytes), retval

        logging.debug(f"Loaded {retval!r}")
        return retval

    def _write_bytes(self, name: str, item: bytes) -> None:
        logging.debug(f"Filesystem write bytes {name!r} {len(item)}B.")
        logging.debug(f"Stored {item!r}")

        location = self._filepath(name)
        logging.debug(f"Store to location {location}")

        with AtomicFile(location, "w") as file:
            count = file.write(item)

        logging.debug(f"Filesystem write bytes {count}B.")

    def _delete(self, name: str) -> None:
        self._filepath(name).unlink()

    def configure(
        self,
        *,
        encoding: str | sentinel = sentinel,
    ) -> None:
        """Configure FileStorage instance.

        Parameters
        ----------
        encoding : str | sentinel, optional
            Change encoding used to read/write text, when sentinel, old value is kept, by default "utf-8"
        """
        if encoding is not sentinel:
            self._encoding = encoding
            logging.debug(f"Changed encoding of FileStorage to {encoding}.")
