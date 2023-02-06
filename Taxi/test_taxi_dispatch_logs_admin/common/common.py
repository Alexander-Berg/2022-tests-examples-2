import typing as tp


def compare_queries(actual: str, expected: str):
    equals = strip_spaces(actual) == strip_spaces(expected)
    if not equals:
        print(f'actual:   {actual}')
        print(f'expected: {expected}')
    return equals


def strip_spaces(string: str):
    return ' '.join(string.replace('\n', ' ').split())


def remove_duplicates_ordered(values: tp.Iterable[str]) -> tp.List[str]:
    result = []
    passed: set = set()
    for val in values:
        if val not in passed:
            result.append(val)
            passed.add(val)
    return result
