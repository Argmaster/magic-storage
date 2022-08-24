from __future__ import annotations

from pathlib import Path

import pytest

from magic_storage import Mode
from magic_storage.impl import Filesystem

from ..data import ITEM_0, ITEM_1, UIDS

UID = UIDS[0]


class TestFileStorage:
    def test_root_dir(self, tmp_path: Path) -> None:
        fs = Filesystem(__file__)
        assert fs._data_dir == Path(__file__).parent / "data"

        fs = Filesystem(tmp_path)
        assert fs._data_dir == tmp_path / "data"

        fs = Filesystem(tmp_path, subdir=None)
        assert fs._data_dir == tmp_path

    def test_configure(self) -> None:
        fs = Filesystem(__file__)
        default_cache = fs._cache

        fs.configure(encoding="latin1")
        assert fs._encoding == "latin1"
        assert fs._cache is default_cache

        fs.configure(cache=None)
        assert fs._cache is None

    def test_io_json(self, tmp_path: Path) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_0
        impl = Filesystem(tmp_path)
        # Begin with store
        impl.store(UID, mode=Mode.JSON, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load(UID, mode=Mode.JSON)
        # And after load should remain in same form
        assert item == ld_item

    def test_io_pickle(self, tmp_path: Path) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_1
        impl = Filesystem(tmp_path)
        # Begin with store
        impl.store(name=UID, mode=Mode.PICKLE, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load(UID, Mode.PICKLE)
        # And after load should remain in same form
        assert item == ld_item

    def test_delete_existing(self, tmp_path: Path) -> None:
        # Check that delete works correctly for uid which is available
        item = ITEM_1
        impl = Filesystem(tmp_path)
        impl.store(name=UID, mode=Mode.PICKLE, item=item)
        impl.delete(UID)

    def test_delete_non_existing(self, tmp_path: Path) -> None:
        # Check that delete works correctly for uid which is not available
        impl = Filesystem(tmp_path)
        with pytest.raises(KeyError):
            impl.delete(UID)

    def test_delete_non_existing_missing_ok(self, tmp_path: Path) -> None:
        # Check that delete works correctly for uid which is not available
        impl = Filesystem(tmp_path)
        impl.delete(UID, missing_ok=True)
