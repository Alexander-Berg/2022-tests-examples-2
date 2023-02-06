import aiohttp
import pytest

from taxi_corp_admin import settings

MOCK_ID = 'some_id'

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(
        corp={
            'error.users.csv_content_type': {
                'ru': 'Загруженный файл не является CSV файлом',
            },
        },
    ),
]


@pytest.mark.parametrize(
    [
        'client_id',
        'idempotency_token',
        'created_long_task',
        'expected_task_status',
        'status_code',
    ],
    [
        pytest.param(
            'client3',
            'non_existent_idempotency_token',
            {
                'idempotency_token': 'non_existent_idempotency_token',
                'task_name': settings.STQ_QUEUE_CORP_GENERATE_USERS_EXPORT,
                'task_args': {'client_id': 'client3'},
                'status': 'waiting',
            },
            'waiting',
            200,
            id='put new task',
        ),
        pytest.param(
            'client3',
            'idempotency_token_complete',
            None,
            'complete',
            200,
            id='export users with existing task',
        ),
        pytest.param(
            'client3',
            'idempotency_token_failed',
            None,
            None,
            500,
            id='failed task',
        ),
    ],
)
async def test_export_users(
        patch,
        db,
        taxi_corp_admin_client,
        client_id,
        idempotency_token,
        created_long_task,
        expected_task_status,
        status_code,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_corp_admin_client.post(
        '/v1/users/csv/export',
        headers={'X-Idempotency-Token': idempotency_token},
        params={'client_id': client_id},
    )
    assert response.status == status_code
    response_json = await response.json()
    if response.status == 200:
        assert response_json['status'] == expected_task_status

        if created_long_task:
            db_item = await db.corp_long_tasks.find_one(
                {'idempotency_token': idempotency_token},
            )
            for key, value in created_long_task.items():
                assert db_item[key] == value

            assert _put.calls
        else:
            assert not _put.calls
    else:
        assert not _put.calls
        if response.status == 500:
            assert response_json['code'] == 'TASK_FATAL_ERROR'


@pytest.mark.parametrize(
    [
        'client_id',
        'idempotency_token',
        'created_long_task',
        'expected_task_status',
        'status_code',
    ],
    [
        pytest.param(
            'client3',
            'non_existent_idempotency_token',
            {
                'idempotency_token': 'non_existent_idempotency_token',
                'task_name': settings.STQ_QUEUE_EXPORT_AUXILIARY_DICTIONARY,
                'task_args': {'client_id': 'client3'},
                'status': 'waiting',
            },
            'waiting',
            200,
            id='put new task',
        ),
        pytest.param(
            'client3',
            'idempotency_token_complete',
            None,
            'complete',
            200,
            id='export users with existing task',
        ),
        pytest.param(
            'client3',
            'idempotency_token_failed',
            None,
            None,
            500,
            id='failed task',
        ),
    ],
)
async def test_export_auxiliary(
        patch,
        db,
        taxi_corp_admin_client,
        client_id,
        idempotency_token,
        created_long_task,
        expected_task_status,
        status_code,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_corp_admin_client.post(
        '/v1/users/csv/export/auxiliary',
        headers={'X-Idempotency-Token': idempotency_token},
        params={'client_id': client_id},
    )
    assert response.status == status_code
    response_json = await response.json()
    if response.status == 200:
        assert response_json['status'] == expected_task_status

        if created_long_task:
            db_item = await db.corp_long_tasks.find_one(
                {'idempotency_token': idempotency_token},
            )
            for key, value in created_long_task.items():
                assert db_item[key] == value

            assert _put.calls
        else:
            assert not _put.calls
    else:
        assert not _put.calls
        if response.status == 500:
            assert response_json['code'] == 'TASK_FATAL_ERROR'


@pytest.mark.parametrize(
    ['task_id', 'expected_task_status', 'progress', 'status_code'],
    [
        pytest.param(
            'task_complete',
            'complete',
            100,
            200,
            id='get status of an existing task',
        ),
        pytest.param(
            'task_error_failed',
            'error',
            None,
            500,
            id='status of a failed task',
        ),
        pytest.param(
            'non_existent_task', 'error', None, 400, id='non existent task',
        ),
    ],
)
async def test_status_check(
        db,
        taxi_corp_admin_client,
        task_id,
        expected_task_status,
        status_code,
        progress,
):

    response = await taxi_corp_admin_client.get(
        '/v1/users/csv/status', params={'task_id': task_id},
    )
    assert response.status == status_code

    response_json = await response.json()
    assert progress == response_json.get('progress')

    if response.status == 200:
        assert response_json['status'] == expected_task_status

    else:
        if response.status == 500:
            assert response_json['code'] == 'TASK_FATAL_ERROR'


@pytest.mark.parametrize(
    ['task_id', 'expected_task_status', 'progress', 'status_code'],
    [
        pytest.param(
            'task_complete',
            'complete',
            100,
            200,
            id='get status of an existing task',
        ),
        pytest.param(
            'task_error_failed',
            'error',
            None,
            400,
            id='status of a failed task',
        ),
        pytest.param(
            'non_existent_task', 'error', None, 400, id='non existent task',
        ),
    ],
)
async def test_download(
        db,
        taxi_corp_admin_client,
        task_id,
        expected_task_status,
        status_code,
        progress,
):

    response = await taxi_corp_admin_client.get(
        '/v1/users/csv/result', params={'task_id': task_id},
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['client_id', 'idempotency_token', 'file_name', 'status_code', 'expected'],
    [
        pytest.param(
            'client1',
            'non_existent_idempotency_token',
            'import_create.csv',
            200,
            {'task_id': 'some_id', 'status': 'waiting'},
            id='valid_file',
        ),
        pytest.param(
            'client3',
            'idempotency_token_complete',
            'import_create.csv',
            200,
            {'task_id': 'task_complete', 'status': 'complete'},
            id='completed_task',
        ),
        pytest.param(
            'client1',
            'non_existent_idempotency_token',
            'excel_file.xlsx',
            400,
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'Загруженный файл не является CSV файлом',
                'details': {},
            },
            id='invalid_file',
        ),
    ],
)
async def test_import_users(
        db,
        taxi_corp_admin_client,
        idempotency_token,
        client_id,
        load_binary,
        status_code,
        monkeypatch,
        file_name,
        expected,
        patch,
):
    monkeypatch.setattr('uuid.UUID.hex', MOCK_ID)

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        return 'mds_key'

    form = aiohttp.FormData()
    form.add_field(
        name='file',
        value=load_binary(file_name),
        filename='result.csv',
        content_type='text/csv',
    )

    response = await taxi_corp_admin_client.post(
        '/v1/users/csv/import',
        data=form,
        headers={'X-Idempotency-Token': idempotency_token},
        params={'client_id': client_id},
    )
    response_json = await response.json()
    assert response_json == expected
    assert response.status == status_code
