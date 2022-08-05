from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Set, Type

import pytest


@dataclass(frozen=True, order=True)
class ToggleBase:
    cli_flag: str
    pytest_mark_name: str
    cli_flag_doc: str
    pytest_mark_doc: str

    @property
    def cli_flag_string(self) -> str:
        return f"--{self.cli_flag}"

    def get_skip_mark(self) -> pytest.MarkDecorator:
        return pytest.mark.skip(reason=self.pytest_mark_doc)

    def skip_item(self, item: pytest.Item) -> None:
        item.add_marker(self.get_skip_mark())

    def handle_marked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        raise NotImplementedError

    def handle_unmarked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        raise NotImplementedError


@dataclass(frozen=True, order=True)
class ToggleIncludeWhenFlag(ToggleBase):
    def handle_marked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        if not is_flag_present:
            self.skip_item(item)

    def handle_unmarked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        pass


@dataclass(frozen=True, order=True)
class ToggleExcludeWhenFlag(ToggleBase):
    def handle_marked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        if is_flag_present:
            self.skip_item(item)

    def handle_unmarked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        pass


@dataclass(frozen=True, order=True)
class ToggleIncludeWhenFlagAndExcludeOthers(ToggleBase):
    def handle_marked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        if not is_flag_present:
            self.skip_item(item)

    def handle_unmarked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        if is_flag_present:
            self.skip_item(item)


@dataclass(frozen=True, order=True)
class ToggleExcludeWhenFlagAndIncludeOthers(ToggleBase):
    def handle_marked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        if is_flag_present:
            self.skip_item(item)

    def handle_unmarked_item(
        self, is_flag_present: bool, item: pytest.Item
    ) -> None:
        if not is_flag_present:
            self.skip_item(item)


class Behavior:
    INCLUDE_WHEN_FLAG: Type[ToggleBase] = ToggleIncludeWhenFlag
    EXCLUDE_WHEN_FLAG: Type[ToggleBase] = ToggleExcludeWhenFlag
    INCLUDE_WHEN_FLAG_AND_EXCLUDE_OTHERS: Type[
        ToggleBase
    ] = ToggleIncludeWhenFlagAndExcludeOthers
    EXCLUDE_WHEN_FLAG_AND_INCLUDE_OTHERS: Type[
        ToggleBase
    ] = ToggleExcludeWhenFlagAndIncludeOthers


@dataclass
class ToggleCache:

    toggles: Set[ToggleBase] = field(default_factory=set)

    def __call__(
        self,
        *,
        cli_flag: str,
        pytest_mark_name: str,
        cli_flag_doc: Optional[str] = "",
        pytest_mark_doc: Optional[str] = "",
        flag_behavior: Optional[Type[ToggleBase]] = Behavior.INCLUDE_WHEN_FLAG,
    ) -> None:
        flag_behavior = (
            flag_behavior
            if flag_behavior is not None
            else Behavior.INCLUDE_WHEN_FLAG
        )
        self.toggles.add(
            flag_behavior(
                cli_flag,
                pytest_mark_name,
                cli_flag_doc if cli_flag_doc is not None else "",
                pytest_mark_doc if pytest_mark_doc is not None else "",
            )
        )

    def pytest_addoption(self, parser: pytest.Parser) -> None:
        for toggle in self.toggles:
            parser.addoption(
                toggle.cli_flag_string,  # type: ignore
                action="store_true",
                default=False,
                help=toggle.cli_flag_doc,
            )

    def pytest_configure(self, config: pytest.Config) -> None:
        for toggle in self.toggles:
            config.addinivalue_line(
                "markers",
                (f"{toggle.pytest_mark_name}: {toggle.pytest_mark_doc}"),
            )

    def pytest_collection_modifyitems(
        self,
        _: pytest.Session,
        config: pytest.Config,
        items: list[pytest.Item],
    ) -> None:
        for toggle in self.toggles:
            is_flagged = config.getoption(toggle.cli_flag_string)  # type: ignore
            for test_item in items:
                if toggle.pytest_mark_name in test_item.keywords:
                    toggle.handle_marked_item(is_flagged, test_item)  # type: ignore
                else:
                    toggle.handle_unmarked_item(is_flagged, test_item)  # type: ignore


register_toggle = ToggleCache()
