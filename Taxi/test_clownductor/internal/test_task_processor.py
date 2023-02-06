# pylint: disable=protected-access
import pytest

from clownductor.internal.tasks import processor


@pytest.mark.parametrize(
    'result',
    [
        pytest.param(
            [1],
            marks=[
                pytest.mark.pgsql(
                    'clownductor', files=['base.sql', 'non_started_job.sql'],
                ),
            ],
        ),
        pytest.param(
            [2],
            marks=[
                pytest.mark.pgsql(
                    'clownductor', files=['base.sql', 'started_job.sql'],
                ),
            ],
        ),
        pytest.param(
            [1],
            marks=[
                pytest.mark.pgsql(
                    'clownductor', files=['base.sql', 'task_succeeded.sql'],
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_TASK_PROCESSOR_JOBS_QOS={
                        'enabled': False,
                        'default_job': {
                            'priority': 1000,
                            'at_most_amount': 50,
                        },
                        'jobs': [],
                    },
                ),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_TASK_PROCESSOR_JOBS_QOS={
                        'enabled': True,
                        'default_job': {
                            'priority': 1000,
                            'at_most_amount': 50,
                        },
                        'jobs': [],
                    },
                ),
            ],
        ),
    ],
)
async def test_get_next_task_to_process(patch, web_context, result):
    tasks = []

    @patch('clownductor.internal.tasks.processor._try_update_task')
    async def _try_update_task(context, conn, task_id):
        tasks.append(task_id)

    await processor._update_tasks(web_context)

    assert tasks == result
