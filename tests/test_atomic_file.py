from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pathlib import Path

from magic_storage._atomic_file import AtomicFile
from magic_storage._utils import get_random_sha256

from .data import ITEM_BYTES_0


class TestAtomicFile:
    def test_atomic_io_bytes(self, tmp_path: Path) -> None:
        tmp_file = tmp_path / get_random_sha256()

        with AtomicFile(tmp_file, "w+") as file:
            file.write(ITEM_BYTES_0)
            file.seek(0)
            assert file.read() == ITEM_BYTES_0

        with AtomicFile(tmp_file, "r") as file:
            assert file.read() == ITEM_BYTES_0

    def test_collision_access(self, tmp_path: Path) -> None:
        tmp_file = tmp_path / get_random_sha256()

        repeat_times = 2048

        with ProcessPoolExecutor(max_workers=32) as executor:
            executor.map(process_main, repeat(tmp_file, repeat_times))

        with AtomicFile(tmp_file, "r+") as file:
            content = file.read()
            ob = json.loads(content)

        assert len(ob["key"]) == repeat_times - 1


COLLISION_BASE_OBJECT: dict[str, list[str]] = {"key": []}


def process_main(tmp_file: Path) -> None:
    with AtomicFile(tmp_file, "r+") as file:
        content = file.read()

        if not content:
            serialized = json.dumps(COLLISION_BASE_OBJECT)
            file.write(serialized.encode("utf-8"))

        else:
            deserialized: dict[str, list[str]] = json.loads(content)
            file.seek(0)
            file.truncate(0)
            deserialized["key"].append(get_random_sha256())
            serialized = json.dumps(deserialized)
            file.write(serialized.encode("utf-8"))
