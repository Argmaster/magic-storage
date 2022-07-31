import pickle

import pytest
from pytest_mock import MockerFixture

from magic_storage import StoreType
from magic_storage.base._writer import WriterBase

from .data import ITEM_0, ITEM_1, ITEM_TEXT_0, ITEM_TEXT_1, UIDS


class WriterImpl(WriterBase):

    dumped_text: dict[str, str]
    dumped_bytes: dict[str, bytes]

    def __init__(self) -> None:
        self.dumped_text = {}
        self.dumped_bytes = {}

    def _write_text(self, uid: str, item: str) -> None:
        self.dumped_text[uid] = item

    def _write_bytes(self, uid: str, item: bytes) -> None:
        self.dumped_bytes[uid] = item


ITEMS_TEXT: list[str] = [
    ITEM_TEXT_0,
    ITEM_TEXT_1,
]
ITEMS_BYTES: list[bytes] = [pickle.dumps(ob) for ob in ITEMS_TEXT]

COMPLEX_OBJECT_STORE = [ITEM_0, ITEM_1]

TOTAL_ITEMS: int = len(ITEMS_TEXT)


class TestWriterBase:
    @pytest.mark.parametrize(
        ("uid", "item_index", "store_type"),
        [
            (id_, item_index, store_type)
            for id_ in UIDS
            for item_index in range(TOTAL_ITEMS)
            for store_type in (StoreType.TEXT, StoreType.JSON)
        ],
    )
    def test_store_str_store_json(
        self, uid: str, item_index: int, store_type: StoreType
    ) -> None:
        # Check that store_str() and store_json() correctly passes dump call to implementation
        # Prepare class implementing Dumper interface & resources
        impl = WriterImpl()
        item = ITEMS_TEXT[item_index]
        # Use interface while expecting it to call _write_text()
        if store_type == StoreType.TEXT:
            clean_id = impl.store_str(uid, item)
        elif store_type == StoreType.JSON:
            clean_id = impl.store_json(uid, item)
        else:  # pragma: no cover
            pytest.fail(
                "Only TEXT and JSON should appear, unless API changed."
            )
        # Ensure that call to implementation was correctly recorded.
        assert len(impl.dumped_text.keys()) == 1
        assert len(impl.dumped_bytes.keys()) == 0
        assert item in impl.dumped_text[clean_id]

    @pytest.mark.parametrize(
        ("uid", "item_index", "store_type"),
        [
            (id_, item_index, store_type)
            for id_ in UIDS
            for item_index in range(TOTAL_ITEMS)
            for store_type in (StoreType.BINARY, StoreType.PICKLE)
        ],
    )
    def test_store_bytes_store_pickle(
        self, uid: str, item_index: int, store_type: StoreType
    ) -> None:
        # Check that store_bytes() and store_pickle() correctly passes dump call to implementation
        # Prepare class implementing Dumper interface & resources
        impl = WriterImpl()
        item = ITEMS_BYTES[item_index]
        # Use interface while expecting it to call _write_bytes()
        if store_type == StoreType.BINARY:
            clean_id = impl.store_bytes(uid, item)
        elif store_type == StoreType.PICKLE:
            clean_id = impl.store_pickle(uid, item)
        else:  # pragma: no cover
            pytest.fail(
                "Only BINARY and PICKLE should appear, unless API changed."
            )
        # Ensure that call to implementation was correctly recorded.
        assert len(impl.dumped_text.keys()) == 0
        assert len(impl.dumped_bytes.keys()) == 1
        assert clean_id in impl.dumped_bytes
        assert len(impl.dumped_bytes[clean_id]) > 0

    @pytest.mark.parametrize(
        ("item_index"),
        range(len(COMPLEX_OBJECT_STORE)),
    )
    def test_store_json_complex_object(self, item_index: int) -> None:
        # Check that store_json() serializes complex objects at all.
        impl = WriterImpl()
        item = COMPLEX_OBJECT_STORE[item_index]

        clean_id = impl.store_json(str(item_index), item)

        assert len(impl.dumped_text.keys()) == 1
        assert len(impl.dumped_bytes.keys()) == 0
        assert clean_id in impl.dumped_text
        assert len(impl.dumped_text[clean_id]) > 0

    @pytest.mark.parametrize("store_type", (StoreType.iter_text()))
    def test_store_as_call_text(
        self,
        store_type: StoreType,
        mocker: MockerFixture,
    ) -> None:
        assert store_type.is_text() is True
        # mock _write_text to record calls to it
        _mock = mocker.patch.object(
            WriterImpl,
            "_write_text",
            return_value=None,
        )
        # ensure mocked correctly
        assert WriterImpl._write_text is _mock
        # Check if store_as calls correct implementation function
        impl = WriterImpl()

        impl.store_as(store_type, "1c0bf9d628003ee80dc7ac3d4d", "ANY ARG")

        assert _mock.called

    def test_store_as_call_binary(
        self,
        mocker: MockerFixture,
    ) -> None:
        # mock _write_bytes to record calls to it
        _mock = mocker.patch.object(
            WriterImpl,
            "_write_bytes",
            return_value=None,
        )
        # ensure mocked correctly
        assert WriterImpl._write_bytes is _mock
        # Check if store_as calls correct implementation function
        impl = WriterImpl()

        impl.store_as(
            StoreType.BINARY,
            "1c0bf9d628003ee80dc7ac3d4d",
            "ANY ARG",
            encoding="utf-8",
        )

        assert _mock.called

    def test_store_as_call_pickle(
        self,
        mocker: MockerFixture,
    ) -> None:
        # mock _write_bytes to record calls to it
        _mock = mocker.patch.object(
            WriterImpl,
            "_write_bytes",
            return_value=None,
        )
        # ensure mocked correctly
        assert WriterImpl._write_bytes is _mock
        # Check if store_as calls correct implementation function
        impl = WriterImpl()

        impl.store_as(
            StoreType.PICKLE,
            "1c0bf9d628003ee80dc7ac3d4d",
            "ANY ARG",
        )

        assert _mock.called
