from __future__ import annotations

from pathlib import Path

import pytest

from magic_storage._utils import (
    compress,
    decompress,
    get_random_sha256,
    this_file,
    this_uid,
    uid,
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


@pytest.mark.parametrize(
    ("args", "expect"),
    [
        (
            ("key"),
            "2c70e12b7a0646f92279f427c7b38e7334d8e5389cff167a1dc30e73f826b683",
        ),
        (
            ("key", "value"),
            "b4bfe7c31fb4b7cd245e74ab89fdb66f2286dc6831b57f112239e0b6131d321c",
        ),
        (
            ("key", "value", "foo"),
            "5c835b06e7b5eb341de3c6bab98ac008522d1990d8d21a89e022912d704b4d9d",
        ),
    ],
)
def test_generate_uid(args: tuple[str, ...], expect: str) -> None:
    assert uid(*args) == expect
    # this second one uses cache lookup
    assert uid(*args) == expect


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
