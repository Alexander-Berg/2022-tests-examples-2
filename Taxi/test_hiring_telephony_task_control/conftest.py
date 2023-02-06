import pytest

import hiring_telephony_task_control.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_telephony_task_control.generated.cron import run_cron  # noqa: I100

pytest_plugins = [
    'hiring_telephony_task_control.generated.service.pytest_plugins',
]


@pytest.fixture
def run_tasks_states():
    async def _run_cron():
        argv = [
            'hiring_telephony_task_control.crontasks.tasks_state_pending',
            '-t',
            '0',
        ]
        await run_cron.main(argv)
        argv = [
            'hiring_telephony_task_control.crontasks.tasks_state_acquired',
            '-t',
            '0',
        ]
        await run_cron.main(argv)
        argv = [
            'hiring_telephony_task_control.crontasks.tasks_state_processed',
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron
