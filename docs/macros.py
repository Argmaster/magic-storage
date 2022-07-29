import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typings import MacrosEnvironment


def define_env(env: "MacrosEnvironment") -> None:  # noqa: FNE008 CFQ004
    @env.macro
    def include_partial(source: str, line_begin: int, line_end: int) -> str:
        with open(source) as file:
            return "".join(file.readlines()[line_begin:line_end])

    @env.macro
    def include_regex(source: str, regex: str, flags: int = 0) -> str:
        with open(source) as file:
            if match := re.search(regex, file.read(), flags):
                if len(match.groups()):
                    return match.group(1)
                else:
                    return match.group(0)
            else:
                return "<<<Not found>>>"
