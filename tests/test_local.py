from pathlib import Path

import pytest

from magic_storage import FilesystemStorage
from magic_storage._utils import get_random_sha256

IDENTIFIER = get_random_sha256()
TEST_ITEM_TEXT = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
TEST_ITEM_BYTES = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
TEST_ITEM_JSON = {"any": 234}


class TestLocalStorage:
    def get_local_storage(self, tmp_path: Path) -> FilesystemStorage:
        file_path = f"{tmp_path}/__not_important__.py"
        return FilesystemStorage(file_path)

    @pytest.mark.skip()
    def test__dump_as_text_to(self, tmp_path: Path) -> None:
        storage = self.get_local_storage(tmp_path)
        storage._write_text(IDENTIFIER, TEST_ITEM_TEXT)

    def test_is_available_not_present(self, tmp_path: Path) -> None:
        storage = self.get_local_storage(tmp_path)
        assert storage.is_available(IDENTIFIER) is False

    @pytest.mark.skip()
    def test_is_available_after_insert(self, tmp_path: Path) -> None:
        storage = self.get_local_storage(tmp_path)
        storage.store_json(IDENTIFIER, TEST_ITEM_JSON)
        assert storage.is_available(IDENTIFIER) is True
