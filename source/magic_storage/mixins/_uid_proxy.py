from abc import ABC
from typing import Any, Callable, TypeVar

from magic_storage._base import StorageIOBase
from magic_storage._utils import uid

T = TypeVar("T")


class _UIDProxy:
    def __init__(self, storage: StorageIOBase) -> None:
        self._storage = storage

    def __getattribute__(self, __name: str) -> Any:
        attrib = getattr(self._storage, __name)
        if __name.startswith("load") or __name.startswith("store"):
            return self._uid_getter(attrib)
        return attrib

    def _uid_getter(
        self, attrib: Callable[[str, Any], Any]
    ) -> Callable[[str, Any], Any]:
        def wrapper(name: str, *args: Any, **kwargs: Any) -> Any:
            return attrib(name=uid(name), *args, **kwargs)  # type: ignore

        return wrapper


class UIDProxyMixin(ABC):
    """This is a mixin class which provides you with .uid property.

    When using methods through uid property, all names will be
    automatically converted to uid's.
    """

    @property
    def UID(self: T) -> T:
        """This is a UID proxy which will convert all names to uids."""
        return _UIDProxy(self)  # type: ignore
