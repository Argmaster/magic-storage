from __future__ import annotations

from pathlib import Path

import pytest

from magic_storage import StoreType
from magic_storage.impl import FilesystemStorage

from ..data import ITEM_0, ITEM_1, ITEM_BYTES_0, ITEM_TEXT_0, UIDS

UID = UIDS[0]


class TestFileStorage:
    def test_root_dir(self, tmp_path: Path) -> None:
        fs = FilesystemStorage(__file__)
        assert fs._data_dir == Path(__file__).parent / "data"

        fs = FilesystemStorage(tmp_path)
        assert fs._data_dir == tmp_path / "data"

        fs = FilesystemStorage(tmp_path, subdir=None)
        assert fs._data_dir == tmp_path

    def test_configure(self) -> None:
        fs = FilesystemStorage(__file__)
        default_cache = fs._cache

        fs.configure(encoding="latin1")
        assert fs._encoding == "latin1"
        assert fs._cache is default_cache

        fs.configure(cache=None)
        assert fs._cache is None

    def test_io_text_with_cache(self, tmp_path: Path) -> None:
        impl = FilesystemStorage(tmp_path)
        self._io_text(tmp_path, impl)

    def _io_text(self, tmp_path: Path, impl: FilesystemStorage) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_TEXT_0
        # Begin with store
        impl.store_as(StoreType.TEXT, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.TEXT, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    def test_io_text_no_cache(self, tmp_path: Path) -> None:
        impl = FilesystemStorage(tmp_path)
        impl.configure(cache=None)
        self._io_text(tmp_path, impl)

    def test_io_json(self, tmp_path: Path) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_0
        impl = FilesystemStorage(tmp_path)
        # Begin with store
        impl.store_as(StoreType.JSON, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.JSON, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    def test_io_bytes(self, tmp_path: Path) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_BYTES_0
        impl = FilesystemStorage(tmp_path)
        # Begin with store
        impl.store_as(StoreType.BINARY, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.BINARY, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    def test_io_pickle(self, tmp_path: Path) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_1
        impl = FilesystemStorage(tmp_path)
        # Begin with store
        impl.store_as(StoreType.PICKLE, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.PICKLE, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    def test_delete_existing(self, tmp_path: Path) -> None:
        # Check that delete works correctly for uid which is available
        item = ITEM_1
        impl = FilesystemStorage(tmp_path)
        impl.store_as(StoreType.PICKLE, uid=UID, item=item)
        impl.delete(UID)

    def test_delete_non_existing(self, tmp_path: Path) -> None:
        # Check that delete works correctly for uid which is not available
        impl = FilesystemStorage(tmp_path)
        with pytest.raises(KeyError):
            impl.delete(UID)

    def test_delete_non_existing_missing_ok(self, tmp_path: Path) -> None:
        # Check that delete works correctly for uid which is not available
        impl = FilesystemStorage(tmp_path)
        impl.delete(UID, missing_ok=True)
