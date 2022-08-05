from typing import Any

from magic_storage import MagicStorage


def very_expensive_get() -> Any:
    ...


response = (
    MagicStorage()
    .filesystem(__file__)
    .cache_if_missing("Nice thing", lambda: very_expensive_get())
)
