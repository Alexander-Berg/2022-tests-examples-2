import datetime

import pytest


async def test_example_task(stq_runner):
    await stq_runner.example.call(
        task_id='task_id',
        args=('task_id', datetime.datetime(2019, 1, 1, 12, 0)),
    )
    await stq_runner.example.call(
        task_id='task_id',
        args=('task_id', datetime.datetime(2019, 1, 1, 12, 0)),
        kwargs={'param_2': 'optional_param'},
    )
    with pytest.raises(RuntimeError, match='Task \'example\' failed'):
        await stq_runner.example.call(
            task_id='task_id',
            args=('task_id', datetime.datetime(2019, 1, 1)),
            kwargs={'param_2': 'failing_param'},
        )


async def test_example_with_task_info_task(stq_runner):
    await stq_runner.example_with_task_info.call(
        task_id='task_id',
        args=('task_id', datetime.datetime(2019, 1, 1, 12, 0)),
        exec_tries=1,
    )
