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
TASK_ID_4 = 'task_4'
PLACE_ID_3 = 'place_id_3'
BRAND_ID = 'brand'


def rand_id():
    return uuid.uuid4().hex


@pytest.mark.client_experiments3(
    consumer='eats_place_groups_replica/sync_with_core',
    config_name='eats_place_groups_replica_sync_with_core',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id'},
        {'name': 'brand_id', 'type': 'string', 'value': 'brand'},
        {
            'name': 'place_group_id',
            'type': 'string',
            'value': 'place_group_id',
        },
        {'name': 'type', 'type': 'string', 'value': 'price'},
    ],
    value={'is_active_sync_with_core': True},
)
@pytest.mark.client_experiments3(
    consumer='eats_place_groups_replica/sync_with_core',
    config_name='eats_place_groups_replica_sync_with_core',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id_2'},
        {'name': 'type', 'type': 'string', 'value': 'availability'},
    ],
    value={'is_active_sync_with_core': True},
)
@pytest.mark.client_experiments3(
    consumer='eats_place_groups_replica/sync_with_core',
    config_name='eats_place_groups_replica_sync_with_core',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id_3'},
        {'name': 'brand_id', 'type': 'string', 'value': 'brand'},
        {
            'name': 'place_group_id',
            'type': 'string',
            'value': 'place_group_id',
        },
        {'name': 'type', 'type': 'string', 'value': 'stock'},
    ],
    value={'is_active_sync_with_core': True},
)
@pytest.mark.parametrize(
    'task_id, request_data, has_calls',
    [
        (TASK_ID, {'s3_link': S3_LINK}, True),
        (TASK_ID, None, True),
        (TASK_ID, {}, True),
        (TASK_ID_2, {'s3_link': S3_LINK}, False),
        (TASK_ID_2, None, False),
        (TASK_ID_2, {}, False),
        (TASK_ID_3, {'s3_link': S3_LINK}, True),
    ],
)
@pytest.mark.parametrize('push_model_enabled', [True, False])
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_SWITCH_TO_PUSH_MODEL={
        'brand_ids': [BRAND_ID],
        'place_ids': [PLACE_ID],
    },
)
async def test_success_request(
        stq,
        taxi_config,
        taxi_eats_place_groups_replica_web,
        mock_eats_core_internal_integrations,
        task_id,
        request_data,
        has_calls,
        push_model_enabled,
):
    synced = has_calls and push_model_enabled
    taxi_config.set(
        EATS_PLACE_GROUPS_REPLICA_SETTINGS={
            'is_active_switch_to_push_model': push_model_enabled,
        },
    )
    await taxi_eats_place_groups_replica_web.invalidate_caches()

    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):
        return {}

    with stq.flushing():
        response = await taxi_eats_place_groups_replica_web.post(
            f'/v1/processing-result-success?task_uuid={task_id}',
            json=request_data,
        )
        assert response.status == 200
        assert mock_integrations_post.has_calls == (
            request_data is not None
            and 's3_link' in request_data
            and push_model_enabled
        )
        assert (
            stq.eats_nomenclature_collector_task_status_updater.has_calls
            is synced
        )
        if synced:
            task = (
                stq.eats_nomenclature_collector_task_status_updater.next_call()
            )
            assert (
                task['args'][0] == task_id
            )  # required fields go to args list

    task_response = await taxi_eats_place_groups_replica_web.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 200

    task_info = json.loads(await task_response.read())

    assert task_info.get('status') == 'finished'
    request_s3_link = (
        request_data.get('s3_link') if request_data is not None else None
    )
    assert task_info.get('data_file_url') == request_s3_link


@pytest.mark.parametrize('push_model_enabled', [True, False])
@pytest.mark.parametrize('is_active_sync_with_core', [True, False])
@pytest.mark.config(
    EATS_PLACE_GROUPS_REPLICA_SWITCH_TO_PUSH_MODEL={
        'brand_ids': [BRAND_ID],
        'place_ids': [PLACE_ID],
    },
)
async def test_sync_with_core_matter(
        client_experiments3,
        stq,
        taxi_config,
        taxi_eats_place_groups_replica_web,
        mock_eats_core_internal_integrations,
        push_model_enabled,
        is_active_sync_with_core,
):
    client_experiments3.add_record(
        consumer='eats_place_groups_replica/sync_with_core',
        config_name='eats_place_groups_replica_sync_with_core',
        args=[
            {'name': 'place_id', 'type': 'string', 'value': 'place_id'},
            {'name': 'brand_id', 'type': 'string', 'value': 'brand'},
            {
                'name': 'place_group_id',
                'type': 'string',
                'value': 'place_group_id',
            },
            {'name': 'type', 'type': 'string', 'value': 'price'},
        ],
        value={'is_active_sync_with_core': is_active_sync_with_core},
    )
    task_id = TASK_ID
    request_data = {'s3_link': S3_LINK}
    taxi_config.set(
        EATS_PLACE_GROUPS_REPLICA_SETTINGS={
            'is_active_switch_to_push_model': push_model_enabled,
        },
    )
    await taxi_eats_place_groups_replica_web.invalidate_caches()

    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):
        return {}

    with stq.flushing():
        response = await taxi_eats_place_groups_replica_web.post(
            f'/v1/processing-result-success?task_uuid={task_id}',
            json=request_data,
        )
        assert response.status == 200
        assert mock_integrations_post.has_calls == (
            is_active_sync_with_core and push_model_enabled
        )
        assert (
            stq.eats_nomenclature_collector_task_status_updater.has_calls
            == push_model_enabled
        )

    task_response = await taxi_eats_place_groups_replica_web.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 200

    task_info = json.loads(await task_response.read())

    assert task_info.get('status') == 'finished'
    request_s3_link = (
        request_data.get('s3_link') if request_data is not None else None
    )
    assert task_info.get('data_file_url') == request_s3_link


@pytest.mark.parametrize(
    'task_id, request_data, has_calls',
    [(TASK_ID_4, {'s3_link': S3_LINK}, True)],
)
async def test_success_request_restaurant(
        stq,
        taxi_config,
        taxi_eats_place_groups_replica_web,
        mock_eats_core_internal_integrations,
        task_id,
        request_data,
        has_calls,
):
    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):
        return {}

    with stq.flushing():
        response = await taxi_eats_place_groups_replica_web.post(
            f'/v1/processing-result-success?task_uuid={task_id}',
            json=request_data,
        )
        assert response.status == 200
        assert not mock_integrations_post.has_calls


@pytest.mark.client_experiments3(
    consumer='eats_place_groups_replica/sync_with_core',
    config_name='eats_place_groups_replica_sync_with_core',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id'},
        {'name': 'brand_id', 'type': 'string', 'value': 'brand'},
        {
            'name': 'place_group_id',
            'type': 'string',
            'value': 'place_group_id',
        },
        {'name': 'type', 'type': 'string', 'value': 'price'},
    ],
    value={'is_active_sync_with_core': True},
)
@pytest.mark.parametrize(
    'task_id, request_data, code', [(TASK_ID, {'s3_link': None}, 400)],
)
async def test_fail_request(web_app_client, task_id, request_data, code):
    response = await web_app_client.post(
        f'/v1/processing-result-success?task_uuid={task_id}',
        json=request_data,
    )
    assert response.status == code

    task_response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 200

    task_info = json.loads(await task_response.read())

    assert task_info.get('status') in ('created', 'started')
    assert task_info.get('data_file_url') == DEFAULT_S3_LINK


@pytest.mark.parametrize(
    'task_id, request_data', [(WRONG_TASK_ID, {'s3_link': S3_LINK})],
)
async def test_wrong_task_id(web_app_client, stq, task_id, request_data):
    with stq.flushing():
        response = await web_app_client.post(
            f'/v1/processing-result-success?task_uuid={task_id}',
            json=request_data,
        )
        assert response.status == 404
        assert (
            not stq.eats_nomenclature_collector_task_status_updater.has_calls
        )

    task_response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert task_response.status == 404
