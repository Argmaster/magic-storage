import pytest

from magic_storage.base import DeleterBase


class DeleterImpl(DeleterBase):
    def _delete(self, __uid: str, /) -> None:
        raise RuntimeError()


class TestDeleterBase:
    def test_delete_no_suppress(self) -> None:
        with pytest.raises(RuntimeError):
            DeleterImpl().delete("")

    def test_delete_suppress(self) -> None:
        DeleterImpl().delete("", suppress_errors=True)
