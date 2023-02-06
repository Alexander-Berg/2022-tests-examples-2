import typing as tp

_T = tp.TypeVar('_T')  # type: ignore


def symmetric_lists_diff(
        first: tp.List[_T], second: tp.List[_T],
) -> tp.List[_T]:
    first = list(first)  # make a mutable copy
    result: tp.List[_T] = []
    for elem in second:
        try:
            first.remove(elem)
        except ValueError:
            result.append(elem)
    return result + first
