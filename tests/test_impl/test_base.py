import json
from typing import Any, Callable

import pytest

from magic_storage import Mode, StorageIOBase
from magic_storage._base import _IOMeta


class _Examples:

    name_short = "some name"
    item_string_short = "item"


class IOSuiteBase:

    storage: StorageIOBase

    def setup_method(
        self,
    ) -> None:
        # configure self.attribute
        pass

    def teardown_method(self, *_: Any) -> None:
        # tear down self.attribute
        pass


class StorageIOSuiteBase(IOSuiteBase):
    @pytest.mark.parametrize(("mode", "function"), _IOMeta.stores.items())
    def test_store_small(
        self, mode: Mode, function: Callable[["StorageIOBase", str, Any], Any]
    ) -> None:

        name = self.storage.store(
            _Examples.name_short,
            _Examples.item_string_short,
            mode=mode,
        )
        assert name == _Examples.name_short
        assert self.storage.is_available(_Examples.name_short) is True

    @pytest.mark.parametrize(("mode", "function"), _IOMeta.loaders.items())
    def test_load_small(  # noqa: FNE004
        self, mode: Mode, function: Callable[["StorageIOBase", str, Any], Any]
    ) -> None:

        self.storage.store(
            _Examples.name_short,
            _Examples.item_string_short,
            mode=mode,
        )

        item = self.storage.load(
            _Examples.name_short,
            mode=mode,
        )

        assert item == _Examples.item_string_short

    @pytest.mark.parametrize(("mode", "function"), _IOMeta.stores.items())
    def test_delete_small(
        self, mode: Mode, function: Callable[["StorageIOBase", str, Any], Any]
    ) -> None:

        name = self.storage.store(
            _Examples.name_short,
            _Examples.item_string_short,
            mode=mode,
        )
        self.storage.delete(name, missing_ok=False)
        assert self.storage.is_available(name) is False

    def test_delete_non_existing_missing_ok(self) -> None:
        # Check that delete works correctly for uid which is not available
        self.storage.delete(_Examples.name_short, missing_ok=True)

    def test_delete_non_existing(self) -> None:
        # Check that delete works correctly for uid which is not available
        with pytest.raises(StorageIOBase.DeletionError):
            self.storage.delete(_Examples.name_short, missing_ok=False)


class JsonIOSuiteBase(IOSuiteBase):
    def test_store_json_small(self) -> None:
        self.storage.store_json(
            _Examples.name_short, _Examples.item_string_short
        )
        assert self.storage.is_available(_Examples.name_short) is True

    def test_load_json_small(self) -> None:  # noqa: FNE004
        self.storage.store_json(
            _Examples.name_short, _Examples.item_string_short
        )

        item = self.storage.load_json(_Examples.name_short)
        assert item == _Examples.item_string_short

    class Jsonable:

        _dict = {"val": 32}

        def json(self) -> str:
            return json.dumps(self._dict)

    def test_store_json_custom(self) -> None:
        self.storage.store_json(_Examples.name_short, self.Jsonable())
        assert self.storage.is_available(_Examples.name_short) is True

    def test_load_json_custom(self) -> None:  # noqa: FNE004
        self.storage.store_json(_Examples.name_short, self.Jsonable())

        item = self.storage.load_json(_Examples.name_short)
        assert item == self.Jsonable()._dict

    def test_store_json_incompatible(self) -> None:
        class Arbitrary:
            pass

        with pytest.raises(TypeError):
            self.storage.store_json(_Examples.name_short, Arbitrary())


class PickleIOSuiteBase(IOSuiteBase):
    def test_store_pickle(self) -> None:
        self.storage.store_json(
            _Examples.name_short, _Examples.item_string_short
        )
        assert self.storage.is_available(_Examples.name_short) is True

    def test_load_pickle(self) -> None:  # noqa: FNE004
        self.storage.store_pickle(
            _Examples.name_short, _Examples.item_string_short
        )

        item = self.storage.load_pickle(_Examples.name_short)
        assert item == _Examples.item_string_short


class FullIOSuiteBase(StorageIOSuiteBase, JsonIOSuiteBase, PickleIOSuiteBase):
    pass
