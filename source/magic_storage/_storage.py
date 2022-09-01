from ._io_base import JsonIO, PickleIO
from .extensions import StoreIfAbsentMixin, UIDProxyMixin


class StorageIOBase(JsonIO, PickleIO, StoreIfAbsentMixin, UIDProxyMixin):
    def configure(self) -> None:
        """Configure resource storage access."""
