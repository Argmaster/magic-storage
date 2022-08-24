from __future__ import annotations

import json

import pytest

from magic_storage import InMemory, Mode

from ..data import ITEM_0, ITEM_1, UIDS

UID = UIDS[0]


class TestInMemoryStorage:
    def test_io_json(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_0
        impl = InMemory()
        # Begin with store
        impl.store(UID, mode=Mode.JSON, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load(UID, mode=Mode.JSON)
        # And after load should remain in same form
        assert item == ld_item

    class Jsonable:

        _dict = {"val": 32}

        def json(self) -> str:
            return json.dumps(self._dict)

    def test_io_json_with_json_conversion(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = self.Jsonable()
        impl = InMemory()
        # Begin with store
        impl.store_json(UID, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load_json(UID)
        # And after load should remain in same form
        assert json.loads(item.json()) == ld_item

    def test_io_pickle(self) -> None:
        # Check that object can be stored, then appears available and can re loaded.
        item = ITEM_1
        impl = InMemory()
        # Begin with store
        impl.store(UID, mode=Mode.PICKLE, item=item)
        # Just created, should be available
        assert impl.is_available(UID) is True
        # As is available, should be loadable
        ld_item = impl.load(
            UID,
            mode=Mode.PICKLE,
        )
        # And after load should remain in same form
        assert item == ld_item

    def test_delete_existing(self) -> None:
        impl = InMemory()
        item = ITEM_1
        impl.store(UID, mode=Mode.PICKLE, item=item)
        impl.delete(UID)

    def test_delete_not_existing(self) -> None:
        impl = InMemory()
        with pytest.raises(KeyError):
            impl.delete(UID)

    def test_delete_not_existing_missing_ok(self) -> None:
        impl = InMemory()
        impl.delete(UID, missing_ok=True)
