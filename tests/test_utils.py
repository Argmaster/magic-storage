from __future__ import annotations

from magic_storage._utils import compress, decompress, get_random_sha256


def test_compress_decompress() -> None:
    source = b"ghyq3452hq45w"
    cmp_source = compress(source)
    assert decompress(cmp_source) == source


def test_get_random_sha256() -> None:
    for _ in range(16):
        sha = get_random_sha256()
        assert isinstance(sha, str)
        assert len(sha) == 64
