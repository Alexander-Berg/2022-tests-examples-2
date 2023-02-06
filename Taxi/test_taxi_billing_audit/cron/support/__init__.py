import typing

from .markers import Markers  # noqa


def has_line(line: str, lines: typing.List[str]) -> bool:
    return any(line in x for x in lines)


def task_disabled(lines: typing.List[str]):
    return has_line('Task disabled by fallback config', lines)


def finished_with_issues(lines: typing.List[str]):
    return has_line('check finished with issues', lines)


def finished_with_no_issues(lines: typing.List[str]):
    return has_line('check finished with no issues', lines)
