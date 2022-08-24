from magic_storage import InMemory, this_uid


class TestCacheIfMissingMixin:
    class TestC2:
        def test_get_or_set_default(self) -> None:
            ob = InMemory().store_if_absent(this_uid(), lambda: {})
            assert ob == {}
