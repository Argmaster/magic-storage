from __future__ import annotations

from enum import Enum

__all__ = ["Mode"]


class Mode(Enum):
    JSON = 1
    PICKLE = 2

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Mode.{self.name}"
