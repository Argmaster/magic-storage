from __future__ import annotations

from pathlib import Path

import pytest

from magic_storage._atomic_file import AtomicFile, IndexFile

from .data import ITEM_BYTES_0, ITEM_TEXT_0


class TestAtomicFile:
    def test_atomic_read_write_text(self, tmp_path: Path) -> None:
        tmp_file = tmp_path / "some_file.txt"

        with AtomicFile(tmp_file) as file:
            file.write_text(ITEM_TEXT_0)
            assert file.read_text() == ITEM_TEXT_0

        with AtomicFile(tmp_file) as file:
            assert file.read_text() == ITEM_TEXT_0

    def test_atomic_read_write_bytes(self, tmp_path: Path) -> None:
        tmp_file = tmp_path / "some_file.txt"

        with AtomicFile(tmp_file) as file:
            file.write_bytes(ITEM_BYTES_0)
            assert file.read_bytes() == ITEM_BYTES_0

        with AtomicFile(tmp_file) as file:
            assert file.read_bytes() == ITEM_BYTES_0


class TestIndexFile:
    def test_enter_exit(self, tmp_path: Path) -> None:
        file = IndexFile(tmp_path / ".index.json")
        with file:
            assert file.index == {}

        assert file._index is None

        with pytest.raises(AssertionError):
            file.index

    def test_content_access(self, tmp_path: Path) -> None:
        file = IndexFile(tmp_path / ".index.json")

        with file as index:
            index["foo"] = "spam"
            index["bar"] = "maps"
            index["car"] = "claps"

            assert index["foo"] == "spam"
            assert index["bar"] == "maps"
            assert index["car"] == "claps"

            del index["bar"]

            with pytest.raises(KeyError):
                index["bar"]

        with file as index:
            assert len(index.keys()) == 2

            assert "foo" in index
            assert "car" in index

            assert index["foo"] == "spam"
            assert index["car"] == "claps"

            del index["car"]
            assert len(index.keys()) == 1

            with pytest.raises(KeyError):
                index["bar"]

        with file as index:
            index["foo"] = "spam"
            assert len(index.keys()) == 1

            with pytest.raises(KeyError):
                del index["car"]

            assert len(index.keys()) == 1

            index["far"] = "gnar"
            assert len(index.keys()) == 2

            with pytest.raises(KeyError):
                index["car"]

            with pytest.raises(KeyError):
                index["bar"]

            assert index.get("bar", "THG") == "THG"

        with file as index:
            assert len(index.keys()) == 2

    def test_load_broken(self, tmp_path: Path) -> None:  # noqa: FNE004
        file = IndexFile(tmp_path / ".index.json")

        file._lock.acquire()
        file.write_text("random")
        file._lock.release()

        with file as index:
            index["foo"] = "spam"

        with file as index:
            assert "foo" in index.keys()  # noqa: SIM118
