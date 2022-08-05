from __future__ import annotations

import pytest

from magic_storage.base import DeleterBase


class DeleterImpl(DeleterBase):
    def _delete(self, __uid: str, /, *, missing_ok: bool = False) -> None:
        if not missing_ok:
            raise RuntimeError


class DeleterImpl2(DeleterBase):
    def _delete(self, __uid: str, /, *, missing_ok: bool = False) -> None:
        raise RuntimeError


class TestDeleterBase:
    def test_delete_no_suppress(self) -> None:
        with pytest.raises(KeyError):
            DeleterImpl().delete("")

    def test_delete_suppress(self) -> None:
        DeleterImpl().delete("", missing_ok=True)

    def test_delete_suppress_discard_exception(self) -> None:
        DeleterImpl2().delete("", missing_ok=True)
