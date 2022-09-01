from __future__ import annotations

from ._atomic_file import AtomicFile
from ._magic import MagicStorage
from ._mode import Mode
from ._storage import StorageIOBase
from ._utils import this_uid
from .implementations import InMemory
from .implementations._filesystem import Filesystem

__all__ = [
    "StorageIOBase",
    "MagicStorage",
    "Mode",
    "Filesystem",
    "InMemory",
    "AtomicFile",
    "this_uid",
]

__version__: str = "2.0.0"
