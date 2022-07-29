from pathlib import Path

import pytest

from .cli_toggle import register_toggle

collect_ignore_glob = ["data/*"]


def pytest_addoption(parser: pytest.Parser) -> None:  # pragma: no cover
    register_toggle.pytest_addoption(parser)


def pytest_configure(config: pytest.Config) -> None:  # pragma: no cover
    register_toggle.pytest_configure(config)


def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:  # pragma: no cover
    register_toggle.pytest_collection_modifyitems(session, config, items)


@pytest.fixture(scope="session")
def test_dir() -> Path:  # pragma: no cover
    return Path(__file__).parent


@pytest.fixture(scope="session")
def repo_dir() -> Path:  # pragma: no cover
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def source_dir(repo_dir: Path) -> Path:  # pragma: no cover
    return repo_dir / "source"


@pytest.fixture(scope="session")
def package_dir(source_dir: Path) -> Path:  # pragma: no cover
    return source_dir / "magic_storage"
