import collections

import pytest

from taxi.util import itertools_ext


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'tasks_args,max_lap',
    [
        (
            (
                ('first', 5),
                ('second', 8),
                ('third', 4),
                ('fourth', 1),
                ('fifth', 0),
                ('sixth', 3),
            ),
            8,
        ),
        ((('first', 7),), 7),
    ],
)
async def test_azip_longest(tasks_args, max_lap):
    async def _task(num_results):
        for curr in range(num_results):
            yield curr

    def get_tasks():
        return [_task(args[1]) for args in tasks_args]

    nothing = object()
    laps = 0

    tasks = get_tasks()
    collected = collections.defaultdict(list)
    collected_nothings = collections.defaultdict(int)
    async for results in itertools_ext.azip_longest(tasks, nothing=nothing):
        laps += 1
        assert len(results) == len(tasks)
        for (name, _), result in zip(tasks_args, results):
            if result is nothing:
                collected_nothings[name] += 1
            else:
                collected[name].append(result)

    assert laps == max_lap
    collected = dict(collected)
    assert collected == {
        key: list(range(num)) for key, num in tasks_args if num
    }
    assert collected_nothings == {
        key: max_lap - num for key, num in tasks_args if max_lap - num
    }

    collected2 = collections.defaultdict(list)
    for (name, _), task in zip(tasks_args, get_tasks()):
        async for result in task:
            collected2[name].append(result)

    assert dict(collected2) == collected
