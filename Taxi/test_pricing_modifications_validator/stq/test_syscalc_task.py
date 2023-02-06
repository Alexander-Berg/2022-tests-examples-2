# flake8: noqa
import pytest

from taxi.stq import async_worker_ng

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)
from pricing_modifications_validator.storage import validator
from pricing_modifications_validator.stq import syscalc


def _create_task_info(exec_tries=0):
    return async_worker_ng.TaskInfo(
        id='task_id', exec_tries=exec_tries, reschedule_counter=0, queue='',
    )


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.config(PMV_MAX_TASK_FAIL_RETRIES=1)
async def test_syscalc_stq_task_error(stq3_context, select_named):
    await syscalc.task(stq3_context, _create_task_info(1), check_id=1)
    checks_state = select_named('SELECT task_state FROM db.checks WHERE id=1')[
        0
    ]
    assert checks_state['task_state'] == 'Terminated'


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
async def test_syscalc_stq_task_good(stq3_context, select_named):
    await syscalc.task(stq3_context, _create_task_info(0), check_id=1)
    checks_state = select_named(
        'SELECT message, task_state FROM db.checks WHERE id=1',
    )[0]
    assert checks_state['task_state'] == 'Finished'
