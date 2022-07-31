from ._local import LocalStorage
from ._magic import MagicStorage
from ._store_type import StoreType
from .impl import InMemoryStorage

__all__ = ["MagicStorage", "StoreType", "LocalStorage", "InMemoryStorage"]

__version__: str = "1.0.0"
