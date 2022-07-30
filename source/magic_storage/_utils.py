from __future__ import annotations

import lzma
from hashlib import sha256
from random import random
from typing import Any

from cachetools import RRCache, cached

__all__ = ["make_uid", "decompress", "compress", "get_random_sha256"]


LZMA_KWARGS: dict[str, Any] = {
    "format": lzma.FORMAT_XZ,
    "check": lzma.CHECK_CRC64,
    "preset": 6,
    "filters": None,
}


@cached(cache=RRCache(maxsize=64))
def make_uid(string: str) -> str:
    return "".join(x if x.isalnum() else "_" for x in string)


def decompress(ob: bytes) -> bytes:
    return lzma.decompress(
        ob,
        format=LZMA_KWARGS["format"],
        filters=LZMA_KWARGS["filters"],
    )


def compress(ob: bytes) -> bytes:
    return lzma.compress(
        ob,
        **LZMA_KWARGS,
    )


def get_random_sha256() -> str:
    return sha256(str(random()).encode("utf-8")).hexdigest()
