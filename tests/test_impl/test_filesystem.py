from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from magic_storage.impl import Filesystem

from .test_base import FullIOSuiteBase


class TestFilesystem(FullIOSuiteBase):

    storage: Filesystem

    def setup_method(
        self,
    ) -> None:
        # configure self.attribute
        self.temp_dir = TemporaryDirectory()
        self.storage = Filesystem(self.temp_dir.name)

    def teardown_method(self, *_: Any) -> None:
        # tear down self.attribute
        self.temp_dir.cleanup()

    def test_root_form_file(self) -> None:
        fs = Filesystem(__file__)
        assert fs._data_dir == Path(__file__).parent / "data"

    def test_root_form_directory(self, tmp_path: Path) -> None:
        fs = Filesystem(tmp_path)
        assert fs._data_dir == tmp_path / "data"

    def test_root_form_directory_no_suffix(self, tmp_path: Path) -> None:
        fs = Filesystem(tmp_path, subdir=None)
        assert fs._data_dir == tmp_path

    def test_root_form_stack(self) -> None:
        fs = Filesystem()
        assert fs._data_dir == Path(__file__).parent / "data"

    def test_configure(self) -> None:
        default_cache = self.storage._cache

        self.storage.configure(encoding="latin1")
        assert self.storage._encoding == "latin1"
        assert self.storage._cache is default_cache

        self.storage.configure(cache=None)
        assert self.storage._cache is None
