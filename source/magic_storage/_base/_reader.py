from __future__ import annotations

import json
import logging
import pickle
from abc import ABC, abstractmethod
from typing import Any, Callable

from magic_storage._store_type import StoreType
from magic_storage._utils import decompress, make_uid

__all__ = ["ReaderBase"]


class ReaderBase(ABC):
    def is_available(self, uid: str) -> bool:
        """Check if object with specified identifier and store type is present
        in cache.

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters allowed,
            other are replaced with '_'.

        Returns
        -------
        bool
            True when object is present, False otherwise.
        """
        uid = make_uid(uid)

        status = self._is_available(uid)
        logging.debug(f"Availability status of {uid} is {status}.")

        return status

    @abstractmethod
    def _is_available(self, identifier: str) -> bool:
        ...

    @abstractmethod
    def _read_text(self, identifier: str) -> str:
        ...

    @abstractmethod
    def _read_bytes(self, identifier: str) -> bytes:
        ...

    def read_text(self, uid: str) -> str:
        """Load object with specified identifier as text.

        This is only suitable for str and str-like objects.

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters are allowed,
            other are replaced with '_'.

        Returns
        -------
        str
            Loaded object.
        """
        uid = make_uid(uid)

        ob = self._read_text(uid)
        logging.debug(f"Successfully loaded {uid} as TEXT")

        return ob

    def read_bytes(self, uid: str) -> bytes:
        """Load object with specified identifier as binary.

        This is only suitable for bytes and bytes-like objects.

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters allowed,
            other are replaced with '_'.

        Returns
        -------
        bytes
            Loaded object.
        """
        uid = make_uid(uid)

        ob = self._read_bytes(uid)
        ob = decompress(ob)
        logging.debug(f"Successfully loaded {uid} as BINARY")

        return ob

    def read_json(self, uid: str, **json_load_kw: Any) -> Any:
        """Load object with specified identifier as json.

        This can be used with any object which can be decoded with json.loads()

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters are allowed,
            other are replaced with '_'.

        Returns
        -------
        Any
            Loaded object.
        """
        uid = make_uid(uid)

        source = self._read_text(uid)
        ob = json.loads(source, **json_load_kw)
        logging.debug(f"Successfully loaded {uid} as JSON")

        return ob

    def read_pickle(self, uid: str, **pickle_load_kw: Any) -> Any:
        """Load object with specified identifier as pickle.

        This can be used with any object which can be decoded with pickle.loads()

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters allowed,
            other are replaced with '_'.

        Returns
        -------
        Any
            Loaded object.
        """
        uid = make_uid(uid)

        source = self._read_bytes(uid)
        source = decompress(source)
        ob = pickle.loads(source, **pickle_load_kw)
        logging.debug(f"Successfully loaded {uid} as PICKLE")

        return ob

    def read_as(  # noqa: FNE004
        self,
        store_type: StoreType,
        uid: str,
        **load_kwargs: Any,
    ) -> Any:
        """Load object from cache in format selected by parameter store_as.

        Parameters
        ----------
        store_type : StoreType, optional
            store type from enum.
        uid : str
            object unique identifier. Only Alphanumeric characters allowed,
            other are replaced with '_'.
        """
        uid = make_uid(uid)

        logging.debug(f"Loading '{uid}' as {store_type}.")

        return self._LOAD_MAP[store_type](self, uid, **load_kwargs)

    _LOAD_MAP: dict[StoreType, Callable[[ReaderBase, str], Any]] = {
        StoreType.TEXT: read_text,
        StoreType.BINARY: read_bytes,
        StoreType.JSON: read_json,
        StoreType.PICKLE: read_pickle,
    }
