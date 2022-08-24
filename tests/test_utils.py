from __future__ import annotations

from pathlib import Path

from magic_storage._utils import (
    compress,
    decompress,
    get_random_sha256,
    this_file,
    this_uid,
)


def test_compress_decompress() -> None:
    source = b"ghyq3452hq45w"
    cmp_source = compress(source)
    assert decompress(cmp_source) == source


def test_get_random_sha256() -> None:
    for _ in range(16):
        sha = get_random_sha256()
        assert isinstance(sha, str)
        assert len(sha) == 64


def test_this_uid() -> None:
    uid = this_uid()

    assert (
        uid
        == "3d3692a480575320c859d723e2f105ae625fe5f7fb77fb80961047aa3c9e2427"
    )


def test_this_file() -> None:
    file_path = this_file()

    assert isinstance(file_path, Path)
    assert str(file_path).endswith("tests/test_utils.py")
