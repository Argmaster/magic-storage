from pathlib import Path

from magic_storage._atomic_file import AtomicFile

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
