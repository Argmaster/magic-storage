import json
import logging
from typing import Any

import pytest

from magic_storage import Mode, StorageIOBase
from magic_storage._io_base import _IOMeta
from magic_storage._utils import get_random_sha256
from magic_storage.extensions import StoreIfAbsentMixin


class _Examples:

    name_short = "some name"
    item_string_short = "Lorem ipsum dolor sit amet"
    item_string_short_2 = "Sed ut perspiciatis unde omnis iste natus error"

    class Jsonable:

        _dict = {"val": 32}

        def json(self) -> str:
            return json.dumps(self._dict)


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
    @pytest.mark.parametrize(("mode"), _IOMeta.stores.keys())
    def test_store_small(self, mode: Mode) -> None:

        name = self.storage.store(
            _Examples.name_short,
            _Examples.item_string_short,
            mode=mode,
        )
        assert name == _Examples.name_short
        assert self.storage.is_available(_Examples.name_short) is True

    @pytest.mark.parametrize("mode", _IOMeta.loaders.keys())
    def test_load_small(self, mode: Mode) -> None:  # noqa: FNE004

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

    @pytest.mark.parametrize("mode", _IOMeta.stores.keys())
    def test_delete_small(self, mode: Mode) -> None:

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

    @pytest.mark.parametrize("mode", _IOMeta.stores.keys())
    def test_store_load_store_chain(self, mode: Mode) -> None:  # noqa: FNE004
        stage_1_name = "name_1"
        stage_1_content = [1523, 3466]

        self.storage.store(stage_1_name, stage_1_content, mode=mode)
        assert self.storage.is_available(stage_1_name) is True, stage_1_name

        loaded_content = self.storage.load(stage_1_name, mode=mode)
        assert loaded_content == stage_1_content, loaded_content

        stage_2_content = [*stage_1_content, 978798, 55]

        self.storage.store(stage_1_name, stage_2_content, mode=mode)
        assert self.storage.is_available(stage_1_name) is True, stage_1_name

        loaded_content = self.storage.load(stage_1_name, mode=mode)
        assert loaded_content == stage_2_content, loaded_content

        stage_3_content = get_random_sha256()

        self.storage.store(stage_1_name, stage_3_content, mode=mode)
        assert self.storage.is_available(stage_1_name) is True, stage_1_name

        loaded_content = self.storage.load(stage_1_name, mode=mode)
        assert loaded_content == stage_3_content, loaded_content


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

    def test_store_json_custom(self) -> None:
        self.storage.store_json(_Examples.name_short, _Examples.Jsonable())
        assert self.storage.is_available(_Examples.name_short) is True

    def test_load_json_custom(self) -> None:  # noqa: FNE004
        self.storage.store_json(_Examples.name_short, _Examples.Jsonable())

        item = self.storage.load_json(_Examples.name_short)
        assert item == _Examples.Jsonable()._dict

    def test_store_json_incompatible(self) -> None:
        class Arbitrary:
            pass

        with pytest.raises(TypeError):
            self.storage.store_json(_Examples.name_short, Arbitrary())

    def test_load_json_incompatible(self) -> None:  # noqa: FNE004
        self.storage.store_pickle(
            _Examples.name_short, _Examples.item_string_short
        )

        with pytest.raises(UnicodeDecodeError):
            self.storage.load_json(_Examples.name_short)


class PickleIOSuiteBase(IOSuiteBase):
    def test_store_pickle(self) -> None:
        self.storage.store_pickle(
            _Examples.name_short, _Examples.item_string_short
        )
        assert self.storage.is_available(_Examples.name_short) is True

    def test_load_pickle(self) -> None:  # noqa: FNE004
        self.storage.store_pickle(
            _Examples.name_short, _Examples.item_string_short
        )

        item = self.storage.load_pickle(_Examples.name_short)
        assert item == _Examples.item_string_short


class StoreIfAbsentSuiteBase:

    storage: StoreIfAbsentMixin

    @pytest.mark.parametrize("mode", _IOMeta.stores.keys())
    def test_store_if_absent(self, mode: Mode) -> None:
        assert self.storage.is_available(_Examples.name_short) is False

        item = self.storage.store_if_absent(
            _Examples.name_short,
            lambda: _Examples.item_string_short,
            mode=mode,
        )

        assert self.storage.is_available(_Examples.name_short) is True
        assert _Examples.item_string_short == item

    @pytest.mark.parametrize("mode", _IOMeta.stores.keys())
    def test_store_if_absent_present(self, mode: Mode) -> None:
        self.storage.store(
            _Examples.name_short,
            _Examples.item_string_short,
            mode=mode,
        )
        assert self.storage.is_available(_Examples.name_short) is True

        item = self.storage.store_if_absent(
            _Examples.name_short,
            lambda: _Examples.item_string_short,
            mode=mode,
        )
        assert self.storage.is_available(_Examples.name_short) is True
        assert _Examples.item_string_short == item

    @pytest.mark.parametrize("mode", _IOMeta.stores.keys())
    def test_store_if_absent_present_load_fails(  # noqa: FNE004
        self, mode: Mode
    ) -> None:
        # Always select different one to make it impossible to load correctly
        store_mode = Mode.PICKLE if mode != Mode.PICKLE else Mode.JSON

        # this one should succeed to store resource
        self.storage.store(
            _Examples.name_short,
            _Examples.item_string_short,
            mode=store_mode,
        )
        logging.debug(f"First store {_Examples.name_short!r} {store_mode!r}")
        assert self.storage.is_available(_Examples.name_short) is True
        # This load will fail because of different data type
        # And it will recreate this resource with different data type
        item = self.storage.store_if_absent(
            _Examples.name_short,
            lambda: _Examples.item_string_short_2,
            mode=mode,
        )
        logging.debug(f"Second store {_Examples.name_short!r} {mode!r}")
        assert self.storage.is_available(_Examples.name_short) is True
        assert item == _Examples.item_string_short_2

        # After load failure stored resource should be overwritten
        item2 = self.storage.load(_Examples.name_short, mode=mode)
        assert item2 == _Examples.item_string_short_2


class MixinSuiteBase(StoreIfAbsentSuiteBase):
    pass


class FullIOSuiteBase(
    StorageIOSuiteBase, JsonIOSuiteBase, PickleIOSuiteBase, MixinSuiteBase
):
    pass
