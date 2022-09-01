from pathlib import Path

from magic_storage import Filesystem, MagicStorage


class TestMagicStorage:
    def test_filesystem(self, tmp_path: Path) -> None:
        fs = MagicStorage().filesystem(tmp_path)
        assert isinstance(fs, Filesystem)
