from pathlib import Path

from magic_storage import FilesystemStorage, MagicStorage


class TestMagicStorage:
    def test_filesystem_with_cache(self, tmp_path: Path) -> None:
        fs = MagicStorage().filesystem(tmp_path)
        assert isinstance(fs, FilesystemStorage)

    def test_filesystem_without_cache(self, tmp_path: Path) -> None:
        fs = MagicStorage().filesystem_no_cache(tmp_path)
        assert isinstance(fs, FilesystemStorage)
