from __future__ import annotations

import inspect
import logging
import lzma
import re
from contextlib import suppress
from hashlib import sha256
from pathlib import Path
from random import random
from typing import Any

from cachetools import RRCache

__all__ = [
    "uid",
    "decompress",
    "compress",
    "get_random_sha256",
    "slugify_encode",
    "slugify_decode",
    "this_uid",
    "this_file",
]


LZMA_KWARGS: dict[str, Any] = {
    "format": lzma.FORMAT_XZ,
    "check": lzma.CHECK_CRC64,
    "preset": 6,
    "filters": None,
}


_UID_CACHE: RRCache = RRCache(maxsize=64)


def uid(*__source: str) -> str:
    key = "".join(__source)
    assert isinstance(key, str)

    with suppress(KeyError):
        value = _UID_CACHE[key]
        assert isinstance(value, str)

        logging.debug("Cache hit for UID from {key!r}")

        return value

    uid_value = sha256(key.encode("utf-8")).hexdigest()
    assert isinstance(uid_value, str)

    _UID_CACHE[key] = uid_value

    return uid_value


def decompress(ob: bytes | bytearray) -> bytes:
    return lzma.decompress(
        ob,
        format=LZMA_KWARGS["format"],
        filters=LZMA_KWARGS["filters"],
    )


def compress(ob: bytes | bytearray) -> bytes:
    return lzma.compress(
        ob,
        **LZMA_KWARGS,
    )


def get_random_sha256() -> str:
    return sha256(str(random()).encode("utf-8")).hexdigest()


def this_uid(*extra: str, ascend: int = 2) -> str:
    """Return UID based of name of function which called this_uid().

    Parameters
    ----------
    ascend : int, optional
        Ascension of stack, can be used to refer to functions
        higher in stack, by default 2

    Returns
    -------
    str
        Unique identifier created.
    """
    frame = _frame(ascend)
    return uid(frame.function, *extra)


def _frame(ascend: int) -> inspect.FrameInfo:
    frames = inspect.stack()
    return frames[ascend]


def this_file(ascend: int = 2) -> Path:
    frame = _frame(ascend)
    return Path(frame.filename)


def slugify_encode(__string: str) -> str:
    return str.join(
        "",
        (_FS_ENCODE_ESCAPES[i] for i in __string.encode("utf-8")),
    )


_FS_ENCODE_ESCAPES = {
    i: (f"_{i}_" if not c.isalnum() else c)
    for i, c in zip(range(0, 256), map(chr, range(0, 256)))
}


_FS_DECODE_ESCAPES = {v: k for k, v in _FS_ENCODE_ESCAPES.items()}
_FS_DECODE_PATTERN = re.compile(r"_\d+_")


def slugify_decode(__string: str) -> str:
    escapes: set[str] = set(_FS_DECODE_PATTERN.findall(__string))
    source = __string.encode("utf-8")

    for escape in escapes:
        source = source.replace(
            escape.encode("utf-8"),
            _FS_DECODE_ESCAPES[escape].to_bytes(1, "little"),
        )

    return source.decode("utf-8")
