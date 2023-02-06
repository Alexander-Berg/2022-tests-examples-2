import json
import uuid

import pytest

from generated.models import crm_scheduler as crm_scheduler_models

from crm_hub.logic import action_utils
from crm_hub.logic.schedule import action


@pytest.mark.config(
    CRM_HUB_DAEMON_SETTINGS={'worker_timeout': 3600, 'workers_per_cpu': 1},
)
@pytest.mark.parametrize(
    'first_task_id, second_task_id, do_calls_expected, action_result',
    [(1337, 1338, 2, {'data': 'data'}), (1339, 1339, 1, {'data': 'data'})],
)
async def test_action_idempotency(
        cron_context,
        patch,
        first_task_id,
        second_task_id,
        do_calls_expected,
        action_result,
):
    sending_id = uuid.UUID('00000000000000000000000000000001')
    properties = []

    do_calls_counter = 0

    @patch('crm_hub.logic.schedule.action.SendAction')
    class _DummySendAction(action.SendAction):
        _ACTION_TYPE = 'send'

        @action_utils.idempotent_action()
        async def _do_action(self):
            nonlocal do_calls_counter
            do_calls_counter += 1
            self.action_result.update(action_result)

        async def _notify_scheduler(self, error_string, task_state):
            assert self.action_result == action_result

    first_action = action.SendAction(
        cron_context,
        crm_scheduler_models.TaskListItem(
            id=first_task_id,
            sending_id=sending_id,
            task_properties=properties,
            time_delay_ms=200,
        ),
    )
    await first_action.perform()

    async with cron_context.pg.master_pool.acquire() as conn:
        idempotency = await conn.fetchrow(
            f'SELECT * FROM crm_hub.action_idempotency '
            f'WHERE id = {first_task_id}',
        )
    assert json.loads(idempotency['result']) == action_result

    second_action = action.SendAction(
        cron_context,
        crm_scheduler_models.TaskListItem(
            id=second_task_id,
            sending_id=sending_id,
            task_properties=properties,
            time_delay_ms=200,
        ),
    )
    await second_action.perform()

    assert do_calls_counter == do_calls_expected
