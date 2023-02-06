import datetime

import pytest

from scripts.lib.models import async_check_queue as acq_models

NOW = datetime.datetime.utcnow()


def _test_dict_by_fields(dict_to_check: dict, check_data: dict):
    for key, val in check_data.items():
        assert key in dict_to_check
        assert dict_to_check[key] == val


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.parametrize(
    'check_queue_task, script_extras',
    [
        pytest.param(None, {}, id='no check item'),
        pytest.param(
            acq_models.QueueItem(
                status=acq_models.common.Status.in_progress,
                script_id='test-get-script',
                created=NOW,
                updated=NOW,
                error_messages=[],
                warn_messages=[],
            ),
            {},
            id='non-completed-task',
        ),
        pytest.param(
            acq_models.QueueItem(
                status=acq_models.common.Status.success,
                script_id='test-get-script',
                created=NOW,
                updated=NOW,
                error_messages=[],
                warn_messages=[],
            ),
            {},
            id='success-task',
        ),
        pytest.param(
            acq_models.QueueItem(
                status=acq_models.common.Status.success,
                script_id='test-get-script',
                created=NOW,
                updated=NOW,
                error_messages=[],
                warn_messages=['some interesting warning'],
            ),
            {'warning_messages': ['some interesting warning']},
            id='success-task-with-warnings',
        ),
        pytest.param(
            acq_models.QueueItem(
                status=acq_models.common.Status.failed,
                script_id='test-get-script',
                created=NOW,
                updated=NOW,
                error_messages=['some-check: big failure'],
                warn_messages=[],
                error_reason={'code': 'FAIL', 'message': 'big failure'},
            ),
            {
                'error_messages': [
                    'FAIL: big failure',
                    'some-check: big failure',
                ],
            },
            id='failed-task-with-errors',
        ),
    ],
)
async def test_get_script(
        scripts_client,
        patch,
        insert_many_acq_tasks,
        check_queue_task,
        script_extras,
):
    if check_queue_task:
        await insert_many_acq_tasks(check_queue_task)

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def _get_draft_mock(*args, **kwargs):
        return {
            'created_by': 'test-login',
            'id': 1234,
            'description': 'aaaa',
            'approvals': [],
            'status': 'applying',
            'run_manually': False,
        }

    response = await scripts_client.get(
        '/test-get-script/', headers={'X-Yandex-Login': 'somebody'},
    )
    assert response.status == 200
    result = await response.json()
    _test_dict_by_fields(
        result,
        {
            'id': 'test-get-script',
            'created_by': 'test-login',
            'status': 'execute_wait',
            'error_messages': [],
            'warning_messages': [],
            **script_extras,
        },
    )
