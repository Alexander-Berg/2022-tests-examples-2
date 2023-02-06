import pytest

from taxi.util import decorators


async def _foo(items, count):
    items.append(1)
    if len(items) < count:
        raise decorators.IntervalError
    return items


async def test_retry_with_intervals():
    items = []

    items2 = await (
        decorators.retry_with_intervals([0.01, 0.01, 0.01])(_foo)(items, 3)
    )

    assert items == items2 == [1, 1, 1]


async def test_fail_retry_with_intervals():
    items = []
    with pytest.raises(decorators.IntervalError):
        await decorators.retry_with_intervals([])(_foo)(items, 3)
    assert items == [1]

    items = []
    with pytest.raises(decorators.IntervalError):
        await decorators.retry_with_intervals([0.1])(_foo)(items, 3)
    assert items == [1, 1]
