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
    def is_available(self, __uid: str, /) -> bool:
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
        __uid = make_uid(__uid)
        assert isinstance(__uid, str), __uid

        status = self._is_available(__uid)
        logging.debug(f"Availability status of {__uid} is {status}.")

        return status

    @abstractmethod
    def _is_available(self, __uid: str, /) -> bool:
        ...

    def load_as(  # noqa: FNE004
        self,
        store_type: StoreType,
        uid: str,
        **load_kw: Any,
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
        return self._load_as(store_type, uid=uid, **load_kw)

    def _load_as(  # noqa: FNE004
        self,
        store_type: StoreType,
        /,
        *,
        uid: str,
        **load_kw: Any,
    ) -> Any:
        uid = make_uid(uid)
        assert isinstance(uid, str), uid
        logging.debug(f"Loading '{uid}' as {store_type}.")

        # We can't check if retval is not None as anything can be stored, including None
        retval = self._LOAD_MAP[store_type](self, uid, **load_kw)

        logging.debug(f"Successfully loaded {uid} as {store_type}")
        return retval

    def _load_text(self, uid: str) -> str:  # noqa: FNE004
        value = self._read_text(uid)
        assert isinstance(value, str)

        return value

    @abstractmethod
    def _read_text(self, __uid: str, /) -> str:
        ...

    def _load_json(self, uid: str, **load_kw: Any) -> Any:  # noqa: FNE004
        raw_value = self._read_text(uid)
        assert isinstance(raw_value, str)

        value = json.loads(raw_value, **load_kw)
        return value

    def _load_bytes(self, uid: str) -> bytes:  # noqa: FNE004
        value = self._read_bytes(uid)
        assert isinstance(value, bytes), value

        return value

    @abstractmethod
    def _read_bytes(self, __uid: str, /) -> bytes:
        ...

    def _load_pickle(  # noqa: FNE004
        self, uid: str, **pickle_load_kw: Any
    ) -> Any:
        source = self._read_bytes(uid)
        assert isinstance(source, bytes)

        source = decompress(source)
        assert isinstance(source, bytes)

        ob = pickle.loads(source, **pickle_load_kw)
        return ob

    def load_text(self, uid: str, **load_kw: Any) -> Any:  # noqa: FNE004
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
        return self._load_as(StoreType.TEXT, uid=uid, **load_kw)

    def load_bytes(self, uid: str, **load_kw: Any) -> Any:  # noqa: FNE004
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
        return self._load_as(StoreType.BINARY, uid=uid, **load_kw)

    def load_json(self, uid: str, **load_kw: Any) -> Any:  # noqa: FNE004
        """Load object with specified identifier as json.

        This can be used with any object which can be decoded with json.loads()

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters are allowed,
            other are replaced with '_'.
        **load_kw: Any
            keyword argument passed to json.loads().

        Returns
        -------
        Any
            Loaded object.
        """
        return self._load_as(StoreType.JSON, uid=uid, **load_kw)

    def load_pickle(self, uid: str, **load_kw: Any) -> Any:  # noqa: FNE004
        """Load object with specified identifier as pickle.

        This can be used with any object which can be decoded with pickle.loads()

        Parameters
        ----------
        uid : str
            object unique identifier. Only Alphanumeric characters allowed,
            other are replaced with '_'.
        **load_kw: Any
            keyword argument passed to pickle.loads().

        Returns
        -------
        Any
            Loaded object.
        """
        return self._load_as(StoreType.PICKLE, uid=uid, **load_kw)

    _LOAD_MAP: dict[StoreType, Callable[[ReaderBase, str], Any]] = {
        StoreType.TEXT: _load_text,
        StoreType.BINARY: _load_bytes,
        StoreType.JSON: _load_json,
        StoreType.PICKLE: _load_pickle,
    }
