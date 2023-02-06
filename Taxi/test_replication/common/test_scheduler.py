import pytest

from replication.common import scheduler


@pytest.mark.parametrize(
    'tasks, expected',
    [
        ({0: 'running', 1: 'ready'}, None),
        ({0: 'not_ready', 1: 'not_ready'}, None),
        ({0: 'not_ready', 1: 'running'}, None),
        ({0: 'ready', 1: 'ready'}, 0),
        ({0: 'not_ready', 1: 'ready'}, 1),
        ({0: 'ready', 1: 'ready', 2: 'ready'}, 0),
        ({0: 'not_ready', 1: 'ready', 2: 'ready'}, 1),
        ({0: 'not_ready', 1: 'not_ready', 2: 'ready'}, 2),
        ({0: 'not_ready', 1: 'not_ready', 2: 'running'}, None),
        ({0: 'running', 1: 'not_ready', 2: 'ready'}, None),
        ({0: 'not_ready', 1: 'running', 2: 'ready'}, None),
        ({0: 'not_ready', 1: 'not_ready', 2: 'not_ready'}, None),
    ],
)
async def test_scheduler(tasks, expected):
    class Task(scheduler.BaseTask):
        async def is_running(self) -> bool:
            return tasks[self.task_id] == 'running'

        async def is_ready(self) -> bool:
            return tasks[self.task_id] == 'ready'

        async def resolve_conflict(self) -> bool:
            return False

    to_schedule = [Task(task) for task in sorted(tasks.keys())]
    assert await scheduler.check_has_ready(to_schedule) == (
        'ready' in tasks.values()
    ), str(tasks)
    assert await scheduler.schedule(to_schedule) == expected, str(tasks)
