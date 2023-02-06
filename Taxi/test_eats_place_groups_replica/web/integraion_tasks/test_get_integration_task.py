import pytest

from eats_place_groups_replica.internal import entities

VALID_TASK_UUID = 'task'


@pytest.mark.parametrize(
    'task_id, code', [(VALID_TASK_UUID, 200), ('wrong_id', 404)],
)
async def test_get_task(
        web_app_client,
        mock_eats_core_internal_integrations,
        web_context,
        task_id,
        code,
):
    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):
        return {}

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': task_id},
    )
    assert response.status == code
    assert not mock_integrations_post.has_calls


@pytest.mark.client_experiments3(
    consumer='eats_place_groups_replica/sync_with_core',
    config_name='eats_place_groups_replica_sync_with_core',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id'},
        {'name': 'brand_id', 'type': 'string', 'value': 'brand_id'},
        {
            'name': 'place_group_id',
            'type': 'string',
            'value': 'place_group_id',
        },
        {'name': 'type', 'type': 'string', 'value': 'price'},
    ],
    value={'is_active_sync_with_core': True},
)
async def test_get_task_set_status_failed_if_sync_error(
        web_app_client,
        mock_eats_core_internal_integrations,
        mockserver,
        web_context,
        pgsql,
):

    core_response_status = 404
    core_response_text = 'Bad task id'

    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):  # pylint: disable=W0612
        return mockserver.make_response(
            status=core_response_status, response=core_response_text,
        )

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': VALID_TASK_UUID},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['status'] == entities.StatusTask.FAILED.value
    assert str(core_response_status) in response_data['reason']
    assert core_response_text in response_data['reason']

    with pgsql['eats_place_groups_replica'].dict_cursor() as cursor:
        cursor.execute(
            f'select * from integration_tasks where id=\'{VALID_TASK_UUID}\'',
        )
        data = cursor.fetchone()
        assert data['status'] == entities.StatusTask.FAILED.value
        assert data['reason']
        assert data['stacktrace']


@pytest.mark.client_experiments3(
    consumer='eats_place_groups_replica/sync_with_core',
    config_name='eats_place_groups_replica_sync_with_core',
    args=[
        {'name': 'place_id', 'type': 'string', 'value': 'place_id'},
        {'name': 'brand_id', 'type': 'string', 'value': 'brand_id'},
        {
            'name': 'place_group_id',
            'type': 'string',
            'value': 'place_group_id',
        },
        {'name': 'type', 'type': 'string', 'value': 'price'},
    ],
    value={'is_active_sync_with_core': True},
)
async def test_get_task_raise_500(
        web_app_client,
        mock_eats_core_internal_integrations,
        mockserver,
        web_context,
):
    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):  # pylint: disable=W0612
        return mockserver.make_response(
            b'{"errors": [{"code": "500", "message": "Error message"}]}', 500,
        )

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': VALID_TASK_UUID},
    )
    assert response.status == 500
    data = await response.read()
    assert b'Error message' in data


async def test_get_task_return_200_if_sync_raise_409(
        web_app_client,
        mock_eats_core_internal_integrations,
        mockserver,
        web_context,
):
    @mock_eats_core_internal_integrations('/nomenclature-retail/v1/sync')
    async def mock_integrations_post(request):  # pylint: disable=W0612
        return mockserver.make_response(status=409)

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': VALID_TASK_UUID},
    )
    assert response.status == 200
    data = await response.json()
    assert data['status'] == entities.StatusTask.FINISHED.value


async def test_reason_converting(
        web_app_client, mock_eats_core_internal_integrations, web_context,
):

    response = await web_app_client.get(
        '/v1/tasks', params={'task_id': VALID_TASK_UUID},
    )
    assert response.status == 200
    data = await response.json()
    assert data['reason'] == 'Test fail error'
