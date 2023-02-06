import dataclasses
from typing import Callable
from typing import Sequence

import pytest


@dataclasses.dataclass
class Params:
    pytest_id: str


def parametrize(params: Sequence[Params]) -> Callable:
    for param in params:
        assert ' ' not in param.pytest_id, 'spaces in "%s"' % param.pytest_id

    return pytest.mark.parametrize(
        'params',
        [pytest.param(param, id=param.pytest_id) for param in params],
    )
