from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

from magic_storage._store_type import StoreType
from magic_storage._utils import make_uid

from ._reader import ReaderBase
from ._writer import WriterBase

__all__ = ["StorageIOBase"]


_R = TypeVar("_R")


class StorageIOBase(ReaderBase, WriterBase):
    def __init__(self) -> None:
        self.configure()

    def cache_if_missing(
        self,
        uid: str,
        callback: Callable[[], _R],
        store_as: StoreType = StoreType.PICKLE,
    ) -> _R:
        """Store and return object if not present in cache, otherwise load from
        cache and return.

        In case of load failure object cache is recreated.

        Parameters
        ----------
        uid : str
            Object identifier used to find object in cache.
        callback : Callable[[], _R]
            Callback function which can create new object if object is not found in cache
        store_as : StoreType, optional
            Determines how object should be stored in cache, by default StoreType.PICKLE

        Returns
        -------
        _R
            Object loaded from cache OR object created with callback and stored to cache.
        """
        uid = make_uid(uid)

        if self.is_available(uid):
            logging.debug(f"'{uid}' is available and will be loaded.")
            try:
                return self._load_from_cache(uid, store_as)  # type: ignore
            except Exception as e:
                logging.exception(e)
            logging.warning(
                f"Failed to load '{uid}' due to loading error. Cache will be recreated."
            )

        else:
            logging.debug(
                f"Resource '{uid}' is NOT available thus will be created."
            )
        # If cache is not present OR if cache load failed
        return self._create_cache(uid, callback, store_as)

    def _load_from_cache(
        self,
        identifier: str,
        stored_as: StoreType = StoreType.PICKLE,
    ) -> Any:
        item = self.load_as(stored_as, identifier)
        return item  # type: ignore

    def _create_cache(
        self,
        identifier: str,
        callback: Callable[[], _R],
        stored_as: StoreType = StoreType.PICKLE,
    ) -> _R:
        item = callback()
        self.store_as(stored_as, identifier, item)
        return item  # type: ignore

    def configure(self) -> None:
        """Configure resource storage access."""
