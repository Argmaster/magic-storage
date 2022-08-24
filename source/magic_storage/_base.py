from __future__ import annotations

import json
import logging
import pickle
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar

from magic_storage._mode import Mode
from magic_storage._utils import compress, decompress

__all__ = ["PickleIO", "JsonIO", "StorageIOBase"]

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

LoadMapT: TypeAlias = dict[Mode, Callable[["IOBase", str], Any]]
StoreMapT: TypeAlias = dict[Mode, Callable[["IOBase", str, Any], Any]]


class _IOMeta(ABCMeta):

    loaders: ClassVar[LoadMapT] = {}
    stores: ClassVar[StoreMapT] = {}

    if TYPE_CHECKING:
        extend_loaders: dict[Mode, str]
        extend_stores: dict[Mode, str]

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> _IOMeta:
        instance = super().__new__(cls, name, bases, namespace, **kwargs)
        assert isinstance(instance, _IOMeta)

        if "extend_loaders" in namespace:
            _IOMeta._update_deferred(
                _IOMeta.loaders, instance.extend_loaders, instance
            )
        if "extend_stores" in namespace:
            _IOMeta._update_deferred(
                _IOMeta.stores, instance.extend_stores, instance
            )

        return instance

    @staticmethod
    def _update_deferred(
        collection: dict[Mode, Any], extend: dict[Mode, Any], instance: Any
    ) -> None:
        for key, value in extend.items():
            collection[key] = getattr(instance, value)


class IOBase(metaclass=_IOMeta):

    if TYPE_CHECKING:
        loaders: ClassVar[LoadMapT]
        stores: ClassVar[StoreMapT]

    extend_loaders: dict[Mode, str] = {}
    extend_stores: dict[Mode, str] = {}

    def is_available(self, name: str) -> bool:
        """Check if object with specified name and store type is present in
        cache.

        Parameters
        ----------
        name : str
            object name.

        Returns
        -------
        bool
            True when object is present, False otherwise.
        """
        assert isinstance(name, str), name

        status = self._is_available(name)
        logging.debug(f"Availability status of {name} is {status}.")

        return status

    @abstractmethod
    def _is_available(self, name: str) -> bool:
        ...

    def load(  # noqa: FNE004
        self,
        name: str,
        mode: Mode = Mode.PICKLE,
        **load_kw: Any,
    ) -> Any:
        """Load object from cache in format selected by parameter store.

        Parameters
        ----------
        mode : StoreType, optional
            store type from enum.
        name : str
            object name.

        Returns
        -------
        str
            Loaded object._read_bytes
        """
        return self._load(name=name, mode=mode, **load_kw)

    def _load(  # noqa: FNE004
        self, *, name: str, mode: Mode, **load_kw: Any
    ) -> Any:
        assert isinstance(name, str), name
        logging.debug(f"Loading '{name}' as {mode}.")
        # We can't check if retval is not None as anything can be stored, including None
        retval = _IOMeta.loaders[mode](self, name, **load_kw)
        logging.debug(f"Successfully loaded {name} as {mode}")

        return retval

    @abstractmethod
    def _read_bytes(self, name: str, /) -> bytes:
        ...

    def store(
        self,
        name: str,
        item: Any,
        mode: Mode = Mode.PICKLE,
        **dump_kw: Any,
    ) -> str:
        """Dump object to cache in format selected by parameter store.

        Parameters
        ----------
        mode : StoreType
            store type from enum
        name : str
            object name.
        item : Any
            item to store, constraints depend on storage type.

        Returns
        -------
        str
            name after cleanup and tagging (real used name).
        """
        return self._store(name=name, mode=mode, item=item, **dump_kw)

    def _store(
        self,
        name: str,
        mode: Mode,
        item: Any,
        **dump_kw: Any,
    ) -> str:
        assert isinstance(name, str), name
        logging.debug(f"Dumping '{name}' as {mode}.")

        retval = _IOMeta.stores[mode](self, name, item, **dump_kw)
        assert retval is None, retval

        logging.debug(f"Successfully dumped {name} as {mode}")
        return name

    @abstractmethod
    def _write_bytes(self, __name: str, __item: bytes, /) -> None:
        ...

    def delete(self, name: str, /, *, missing_ok: bool = False) -> None:
        """Delete object with specified object name.

        Attempt to delete non-existing object KeyError will be raised unless missing_ok=True.

        Parameters
        ----------
        name : str
            object name.
        missing_ok : bool, optional
            ignores missing key errors, by default False
        """
        try:
            self._delete(name, missing_ok=missing_ok)
        except Exception as e:
            if not missing_ok:
                raise KeyError(f"Couldn't delete {name}.") from e

    @abstractmethod
    def _delete(self, name: str, /, *, missing_ok: bool = False) -> None:
        ...


class JsonIO(IOBase):

    extend_loaders = {Mode.JSON: "_load_json"}
    extend_stores = {Mode.JSON: "_store_json"}

    def load_json(self, name: str, **load_kw: Any) -> Any:  # noqa: FNE004
        """Load object with specified name as json.

        This can be used with any object which can be decoded with json.loads()

        Parameters
        ----------
        name : str
            object name. Only Alphanumeric characters are allowed,
            other are replaced with '_'.
        **load_kw: Any
            keyword argument passed to json.loads().

        Returns
        -------
        Any
            Loaded object.
        """
        return self._load(name=name, mode=Mode.JSON, **load_kw)

    def _load_json(self, name: str, **load_kw: Any) -> Any:  # noqa: FNE004
        bytes_value = self._read_bytes(name)
        assert isinstance(bytes_value, bytes)

        string_value = bytes_value.decode("utf-8")
        loaded_value = json.loads(string_value, **load_kw)
        return loaded_value

    def store_json(self, name: str, item: Any, **json_dumps_kw: Any) -> str:
        """Dump object to cache in form of json encoded text.

        Parameters
        ----------
        name : str
            object name.
        item : str
            item to store, any object which can be encoded with json.dumps().

        Returns
        -------
        str
            name after cleanup and tagging (real used name).
        """
        return self._store(
            name=name, mode=Mode.JSON, item=item, **json_dumps_kw
        )

    def _store_json(self, name: str, item: Any, **json_dumps_kw: Any) -> None:
        try:
            serialized_value = json.dumps(item, **json_dumps_kw)
        except TypeError:
            if hasattr(item, "json") and callable(item.json):
                serialized_value = item.json()
            else:
                raise
        assert isinstance(serialized_value, str), serialized_value

        encoded_value = serialized_value.encode("utf-8")
        retval = self._write_bytes(name, encoded_value)
        assert retval is None, retval

        return retval


class PickleIO(IOBase):

    extend_loaders = {Mode.PICKLE: "_load_pickle"}
    extend_stores = {Mode.PICKLE: "_store_pickle"}

    def load_pickle(self, name: str, **load_kw: Any) -> Any:  # noqa: FNE004
        """Load object with specified name as pickle.

        This can be used with any object which can be decoded with pickle.loads()

        Parameters
        ----------
        name : str
            object name.
        **load_kw: Any
            keyword argument passed to pickle.loads().

        Returns
        -------
        Any
            Loaded object.
        """
        return self._load(name=name, mode=Mode.PICKLE, **load_kw)

    def _load_pickle(  # noqa: FNE004
        self, name: str, **pickle_load_kw: Any
    ) -> Any:
        source = self._read_bytes(name)
        assert isinstance(source, bytes)

        source = decompress(source)
        assert isinstance(source, bytes)

        ob = pickle.loads(source, **pickle_load_kw)
        return ob

    def store_pickle(self, name: str, item: Any, **pickle_dump_kw: Any) -> str:
        """Dump object to cache in form of pickled binary.

        Because pickle is a binary format, it is always compressed with lzma algorithm.

        Parameters
        ----------
        name : str
            object name.
        item : str
            item to store, any object which can be encoded with pickle.dumps().


        Returns
        -------
        str
            name after cleanup and tagging (real used name).
        """
        return self._store(
            name=name, mode=Mode.PICKLE, item=item, **pickle_dump_kw
        )

    def _store_pickle(
        self, name: str, item: Any, **pickle_dump_kw: Any
    ) -> None:
        raw_value = pickle.dumps(item, **pickle_dump_kw)
        assert isinstance(raw_value, bytes)

        raw_value = compress(raw_value)
        assert isinstance(raw_value, bytes), raw_value

        retval = self._write_bytes(name, raw_value)
        assert retval is None, retval

        logging.debug(f"Successfully dumped {name} as PICKLE")
        return retval


class StorageIOBase(JsonIO, PickleIO):
    def configure(self) -> None:
        """Configure resource storage access."""
