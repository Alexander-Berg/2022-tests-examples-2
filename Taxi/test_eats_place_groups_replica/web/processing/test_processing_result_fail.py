# pylint: disable=import-only-modules

import json
import uuid

import pytest


TASK_ID = 'task'
TASK_ID_2 = 'task_2'
WRONG_TASK_ID = 'wrong_task'
PLACE_ID = 'place_id'
PLACE_ID_2 = 'place_id_2'
S3_LINK = 'integration/collector/nomenclature/nomenclature_task.json'
DEFAULT_S3_LINK = 'test_data_file_url'
TASK_ID_3 = 'task_3'
PLACE_ID_3 = 'place_id_3'
BRAND_ID = 'brand'


def rand_id():
    return uuid.uuid4().hex


@pytest.mark.parametrize(
    'task_id, request_data, reason, has_calls',
    [
        (
            TASK_ID,
            {'error_code': 200, 'error_text': 'Parser error: Reason'},
            'Reason',
            True,
        ),
        (
            TASK_ID,
            {
                'error_code': 200,
                'error_text': 'Parser error: Processing error: Reason',
            },
            'Not found parser name to processing',
            True,
        ),
        (TASK_ID, {'error_code': 200}, '', True),
        (
            TASK_ID_2,
            {'error_code': 200, 'error_text': 'Parser error: Reason'},
            'Reason',
            False,
        ),
        (
            TASK_ID_2,
            {
                'error_code': 200,
                'error_text': 'Parser error: Processing error: Reason',
            },
            'Not found parser name to processing',
            False,
        ),
        (TASK_ID_2, {'error_code': 200}, '', False),
        (
            TASK_ID_3,
            {'error_code': 200, 'error_text': 'Parser error: Reason'},
            'Reason',
            True,
        ),
    ],
)
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_SETTINGS={
        'is_active_switch_to_push_model': True,
    },
)
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_SWITCH_TO_PUSH_MODEL={
        'brand_ids': [BRAND_ID],
        'place_ids': [PLACE_ID],
    },
)
async def test_success_request(
        web_app_client, stq, task_id, request_data, reason, has_calls,
):
    with stq.flushing():
        response = await web_app_client.post(
            f'/v1/processing-result-fail?task_uuid={task_id}',
            json=request_data,
        )
        assert response.status == 200
        assert (
            stq.eats_nomenclature_collector_task_status_updater.has_calls
            is has_calls
        )
        if has_calls:
            task = (
                stq.eats_nomenclature_collector_task_status_updater.next_call()
            )
            assert (
                task['args'][0] == task_id
                and task['kwargs']['reason'] == reason
            )  # required fields go to args list

    task_response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 200

    task_info = await task_response.json()

    assert task_info.get('status') == 'failed'
    assert task_info.get('reason') == reason


@pytest.mark.parametrize(
    'task_id, request_data, code', [(TASK_ID, None, 400), (TASK_ID, {}, 400)],
)
async def test_fail_request(web_app_client, task_id, request_data, code):
    response = await web_app_client.post(
        f'/v1/processing-result-fail?task_uuid={task_id}', json=request_data,
    )
    assert response.status == code

    task_response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 200

    task_info = json.loads(await task_response.read())

    assert task_info.get('status') in ('created', 'started')
    assert task_info.get('reason') is None


@pytest.mark.parametrize(
    'task_id, request_data',
    [(WRONG_TASK_ID, {'error_code': 200, 'error_text': 'Parser error'})],
)
async def test_wrong_task_id(web_app_client, task_id, request_data):
    response = await web_app_client.post(
        f'/v1/processing-result-fail?task_uuid={task_id}', json=request_data,
    )
    assert response.status == 404

    task_response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 404
