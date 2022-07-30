from __future__ import annotations

from typing import TypeVar

from cachetools import RRCache, cached

from ._local import LocalStorage

__all__ = ["MagicStorage"]


T = TypeVar("T", bound="MagicStorage")


class MagicStorage:
    """This class instantiated and caches loaders which can be acquired with
    dedicated methods.

    Resource storages are neither guaranteed to be cached, nor to be
    always newly created.
    """

    def local(self, current_file: str) -> LocalStorage:
        """Return local cache storage for current file. Storage object may be
        cached for future use.

        Parameters
        ----------
        current_file : str
            expects __file__ variable to be used. Providing different string may cause unexpected results.

        Returns
        -------
        LocalStorage
            storage object.
        """
        return get_local_storage(current_file)


@cached(cache=RRCache(maxsize=32))
def get_local_storage(current_file: str) -> LocalStorage:
    return LocalStorage(current_file)
