import random
import string
import typing as tp


class Sentinel:
    pass


def fields(data: dict, selected=None, as_tuple=False) -> tp.Union[dict, tuple]:
    selected = selected or data.keys()
    if as_tuple:
        return tuple(data[field] for field in selected)
    return {field: data[field] for field in selected}


def random_string(length: int = 10) -> str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


def add_random_prefix(input_string: str) -> str:
    return input_string + random_string()
