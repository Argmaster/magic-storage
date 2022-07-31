from __future__ import annotations

import json
import pickle
from typing import Any

from pytest_mock import MockerFixture

from magic_storage import StoreType
from magic_storage._utils import compress
from magic_storage.base import ReaderBase

from .data import ITEM_0, ITEM_BYTES_0, ITEM_TEXT_0, UIDS

MOCK_MSG = "This method requires mocking!"


_TESTING_UID = UIDS[0]


class ReaderImpl(ReaderBase):
    def _is_available(self, __uid: str, /) -> bool:
        raise AssertionError(MOCK_MSG)

    def _read_text(self, __uid: str, /) -> str:
        raise AssertionError(MOCK_MSG)

    def _read_bytes(self, __uid: str, /) -> bytes:
        raise AssertionError(MOCK_MSG)


class TestReaderBase:
    def test_load_text(self, mocker: MockerFixture) -> None:  # noqa: FNE004
        # Check that load_text() correctly calls reading calls.
        item = ITEM_TEXT_0
        impl, _ = self.prepare_text(mocker, item)
        value = impl.load_text(_TESTING_UID)
        assert value == item

    def prepare_text(
        self, mocker: MockerFixture, retval: Any
    ) -> tuple[ReaderImpl, MockerFixture]:
        # Prepare environment for testing functions calling _read_bytes()
        impl = ReaderImpl()
        # mock _read_text to record calls to it
        _mock = mocker.patch.object(
            ReaderImpl,
            "_read_text",
            return_value=retval,
        )
        # ensure mocked correctly
        assert ReaderImpl._read_text is _mock
        assert impl._read_text is _mock
        # Check actual call
        return impl, mocker

    def test_load_json(self, mocker: MockerFixture) -> None:  # noqa: FNE004
        # Check that load_json() correctly calls reading calls & loads object.
        item = ITEM_0
        impl, _ = self.prepare_text(mocker, json.dumps(item))
        value = impl.load_json(_TESTING_UID)
        assert value == item

    def test_load_bytes(self, mocker: MockerFixture) -> None:  # noqa: FNE004
        # Check that load_bytes() correctly calls reading calls.
        item = ITEM_BYTES_0
        impl, _ = self.prepare_bytes(mocker, item)
        value = impl.load_bytes(_TESTING_UID)
        assert value == item

    def prepare_bytes(
        self, mocker: MockerFixture, retval: Any
    ) -> tuple[ReaderImpl, MockerFixture]:
        # Prepare environment for testing functions calling _read_bytes()
        impl = ReaderImpl()
        # mock _read_bytes to record calls to it
        _mock = mocker.patch.object(
            ReaderImpl,
            "_read_bytes",
            return_value=retval,
        )
        # ensure mocked correctly
        assert ReaderImpl._read_bytes is _mock
        assert impl._read_bytes is _mock
        # Check actual call
        return impl, mocker

    def test_load_pickle(self, mocker: MockerFixture) -> None:  # noqa: FNE004
        # Check that load_pickle() correctly calls reading calls & loads object.
        item = ITEM_BYTES_0
        impl, _ = self.prepare_bytes(mocker, compress(pickle.dumps(item)))
        value = impl.load_pickle(_TESTING_UID)
        assert value == item

    def test_load_as(self, mocker: MockerFixture) -> None:  # noqa: FNE004
        # Check that load_as() correctly calls reading calls.
        item = ITEM_TEXT_0
        impl, _ = self.prepare_text(mocker, item)
        value = impl.load_as(StoreType.TEXT, _TESTING_UID)
        assert value == item
