from __future__ import annotations

from typing import Any

from magic_storage import InMemory

from .test_base import FullIOSuiteBase


class TestInMemory(FullIOSuiteBase):
    def setup_method(
        self,
    ) -> None:
        # configure self.attribute
        self.storage = InMemory()

    def teardown_method(self, *_: Any) -> None:
        # tear down self.attribute
        del self.storage
