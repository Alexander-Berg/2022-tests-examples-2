# pylint: disable=redefined-outer-name
# flake8: noqa
import pytest
from typing import Any, Dict, List

from taxi.stq import async_worker_ng

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)
from pricing_modifications_validator.storage import validator
from pricing_modifications_validator.stq import nantest


def _create_task_info(exec_tries=0):
    return async_worker_ng.TaskInfo(
        id='task_id', exec_tries=exec_tries, reschedule_counter=0, queue='',
    )


def fetch_stq_args(stq) -> List[Dict[str, Any]]:
    result = []
    while stq.has_calls:
        syscalc = stq.next_call()
        result.append(syscalc['kwargs'])
    return result


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.config(PMV_MAX_TASK_FAIL_RETRIES=1)
async def test_nantest_stq_task_error(stq3_context, select_named):
    await nantest.task(stq3_context, _create_task_info(1), test_task_id=1)

    task_state = select_named(
        'SELECT task_state FROM db.script_tasks WHERE id=1',
    )
    checks_state = select_named(
        'SELECT task_state FROM db.checks WHERE script_id=1',
    )
    assert task_state[0]['task_state'] == 'Terminated'
    assert checks_state
    assert all(
        check_state['task_state'] == 'Terminated'
        for check_state in checks_state
    )


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.config(PMV_MULTITASK_EVALUATION_ENABLED=True)
@pytest.mark.parametrize(
    'task_id, expected_messages_file',
    [(2, 'messages/simple.json'), (3, 'messages/discount.json')],
)
async def test_nantest_task_split(
        stq3_context,
        select_named,
        stq,
        mock_pricing_admin,
        load_json,
        task_id,
        expected_messages_file,
):
    expected_messages = load_json(expected_messages_file)
    mock_pricing_admin.set_variables_response(load_json('variable_types.json'))
    await stq3_context.backend_variables_schema_cache.refresh_cache()
    with stq.flushing():
        await nantest.task(
            stq3_context, _create_task_info(0), test_task_id=task_id,
        )
        stq_args = fetch_stq_args(stq.price_validator_syscalc)
        assert stq_args
        check_ids = set(arg['check_id'] for arg in stq_args)
        assert len(check_ids) == len(expected_messages)
        checks = select_named(
            f'SELECT id, task_state, message FROM db.checks WHERE script_id = {task_id}',
        )
        assert all(check['task_state'] == 'InProgress' for check in checks)
        assert set(check['message'] for check in checks) == set(
            expected_messages,
        )

        task = select_named(
            f'SELECT task_state, message FROM db.script_tasks WHERE id = {task_id}',
        )[0]
        assert task['task_state'] == 'Finished'


@pytest.mark.pgsql('pricing_modifications_validator', files=['state.sql'])
@pytest.mark.config(PMV_MULTITASK_EVALUATION_ENABLED=False)
async def test_nantest_single_task_processing(
        stq3_context, select_named, stq, mock_pricing_admin, load_json,
):
    mock_pricing_admin.set_variables_response(load_json('variable_types.json'))
    await stq3_context.backend_variables_schema_cache.refresh_cache()
    with stq.flushing():
        await nantest.task(stq3_context, _create_task_info(0), test_task_id=2)
        stq_args = fetch_stq_args(stq.price_validator_syscalc)
        assert not stq_args
        checks = select_named(
            'SELECT task_state, message FROM db.checks WHERE script_id  = 2',
        )
        assert all(check['task_state'] == 'Finished' for check in checks)
        assert set(check['message'] for check in checks) == set(
            [
                'Detected access to uninitialized optional variable *(fix.discount).restrictions',
                'Detected division by zero in variable 0',
            ],
        )
        task = select_named(
            'SELECT task_state, message FROM db.script_tasks WHERE id = 2',
        )[0]
        assert task['task_state'] == 'Finished'
