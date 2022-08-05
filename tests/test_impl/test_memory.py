from __future__ import annotations

import json

from magic_storage import InMemoryStorage, StoreType

from ..data import ITEM_0, ITEM_1, ITEM_BYTES_0, ITEM_TEXT_0, UIDS

UID = UIDS[0]


class TestInMemoryStorage:
    def test_io_text(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_TEXT_0
        impl = InMemoryStorage()
        # Begin with store
        impl.store_as(StoreType.TEXT, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.TEXT, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    def test_io_json(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_0
        impl = InMemoryStorage()
        # Begin with store
        impl.store_as(StoreType.JSON, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.JSON, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    class Jsonable:

        _dict = {"val": 32}

        def json(self) -> str:
            return json.dumps(self._dict)

    def test_io_json_with_json_conversion(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = self.Jsonable()
        impl = InMemoryStorage()
        # Begin with store
        impl.store_as(StoreType.JSON, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.JSON, uid=UID)
        # And after load should remain in same form
        assert json.loads(item.json()) == ld_item

    def test_io_bytes(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_BYTES_0
        impl = InMemoryStorage()
        # Begin with store
        impl.store_as(StoreType.BINARY, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.BINARY, uid=UID)
        # And after load should remain in same form
        assert item == ld_item

    def test_io_pickle(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_1
        impl = InMemoryStorage()
        # Begin with store
        impl.store_as(StoreType.PICKLE, uid=UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_as(StoreType.PICKLE, uid=UID)
        # And after load should remain in same form
        assert item == ld_item
