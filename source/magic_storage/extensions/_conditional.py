from __future__ import annotations

import logging
import warnings
from typing import Any, Callable, TypeVar

from magic_storage._io_base import IOBase
from magic_storage._mode import Mode

_R = TypeVar("_R")


class StoreIfAbsentMixin(IOBase):
    def store_if_absent(
        self,
        name: str,
        callback: Callable[[], _R],
        mode: Mode = Mode.PICKLE,
    ) -> _R:
        """Store and return object if not present in cache, otherwise load from
        cache and return.

        In case of load failure object cache is recreated.

        Parameters
        ----------
        name : str
            Object name used to find object in cache.
        callback : Callable[[], _R]
            Callback function which can create new object if object is not found in cache
        mode : Mode, optional
            Determines how object should be stored in cache, by default Mode.PICKLE

        Returns
        -------
        _R
            Object loaded from cache OR object created with callback and stored to cache.
        """
        logging.debug(f"Call to store_if_absent {name!r} {mode!r}.")
        if self.is_available(name):
            try:
                return self.load(name=name, mode=mode)  # type: ignore
            except Exception as e:
                logging.exception(e)

            self.delete(name)
            logging.warning(
                f"Failed to load '{name}' due to loading error. Cache will be recreated."
            )

        else:
            logging.debug(
                f"Resource '{name}' is NOT available thus will be created."
            )
        # If cache is not present OR if cache load failed
        default_item = callback()

        logging.debug(f"Default store uses {mode!r} for key {name!r}.")
        self.store(name=name, item=default_item, mode=mode)

        item = self.load(name=name, mode=mode)  # type: ignore
        return item  # type: ignore

    def cache_if_missing(self, *args: Any, **kwargs: Any) -> Any:
        warnings.warn(
            "cache_if_missing() is deprecated, use get_or_set_default()",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.store_if_absent(*args, **kwargs)
