from __future__ import annotations

from ._atomic_file import AtomicFile
from ._magic import MagicStorage
from ._mode import Mode
from ._utils import this_uid
from .impl import InMemory
from .impl._filesystem import Filesystem

__all__ = [
    "MagicStorage",
    "Mode",
    "Filesystem",
    "InMemory",
    "AtomicFile",
    "this_uid",
]

__version__: str = "1.1.0"
