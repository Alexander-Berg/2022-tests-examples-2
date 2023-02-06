import pytest

from taxi_corp import settings


@pytest.mark.parametrize(
    [
        'passport_mock',
        'idempotency_token',
        'post_content',
        'created_long_task',
        'status_code',
    ],
    [
        pytest.param(
            'client3',
            'not_existed_idempotency_token',
            {'cost_centers_id': 'cost_center_1', 'users': {'all_users': True}},
            {
                'idempotency_token': 'not_existed_idempotency_token',
                'task_name': settings.STQ_QUEUE_CORP_UPDATE_USERS_COST_CENTERS,
                'task_args': {
                    'client_id': 'client3',
                    'cost_centers_id': 'cost_center_1',
                    'users': {'all_users': True},
                },
                'status': 'waiting',
            },
            200,
            id='put new task',
        ),
        pytest.param(
            'client3',
            'idempotency_token_complete',
            {'cost_centers_id': 'cost_center_1', 'users': {'all_users': True}},
            None,
            200,
            id='existed task',
        ),
        pytest.param(
            'client3',
            'not_existed_idempotency_token',
            {
                'cost_centers_id': 'invalid_cost_centers_id',
                'users': {'all_users': True},
            },
            None,
            400,
            id='invalid cost_centers_id',
        ),
        pytest.param(
            'client3',
            'not_existed_idempotency_token',
            {
                'cost_centers_id': 'cost_center_1',
                'users': {'user_ids': ['test_user_1', 'test_user_2']},
            },
            None,
            403,
            id='user from another dep',
        ),
        pytest.param(
            'client1',
            'not_existed_idempotency_token',
            {
                'cost_centers_id': 'cost_center_1',
                'users': {'user_ids': ['test_user_1']},
            },
            None,
            403,
            id='user from another client',
        ),
        pytest.param(
            'client3',
            'not_existed_idempotency_token',
            {
                'cost_centers_id': 'cost_center_1',
                'users': {'user_ids': ['test_user_1', 'not_existed_user']},
            },
            None,
            404,
            id='not existed user',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_update_users_cost_centers_create_task(
        patch,
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        idempotency_token,
        post_content,
        created_long_task,
        status_code,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_corp_real_auth_client.post(
        '/2.0/bulk/users-cost-centers',
        json=post_content,
        headers={'X-Idempotency-Token': idempotency_token},
    )
    assert response.status == status_code

    response_json = await response.json()
    if response.status == 200:
        task_id = response_json['_id']

        if created_long_task:
            db_item = await db.corp_long_tasks.find_one(
                {'_id': task_id, 'idempotency_token': idempotency_token},
            )
            assert db_item

            for key, value in created_long_task.items():
                assert db_item[key] == value

            assert _put.calls
        else:
            assert not _put.calls
    else:
        assert not _put.calls


@pytest.mark.parametrize(
    [
        'passport_mock',
        'idempotency_token',
        'post_content',
        'created_long_task',
        'status_code',
    ],
    [
        pytest.param(
            'client3',
            'not_existed_idempotency_token',
            {
                'limits': [{'limit_id': 'limit3_2', 'service': 'taxi'}],
                'services': ['taxi'],
                'users': {'all_users': True},
            },
            {
                'idempotency_token': 'not_existed_idempotency_token',
                'task_name': settings.STQ_QUEUE_CORP_UPDATE_USERS_LIMITS,
                'task_args': {
                    'client_id': 'client3',
                    'limits': [{'limit_id': 'limit3_2', 'service': 'taxi'}],
                    'services': ['taxi'],
                    'users': {'all_users': True},
                },
                'status': 'waiting',
            },
            200,
            id='put new task',
        ),
        pytest.param(
            'client3',
            'not_existed_idempotency_token',
            {
                'limits': [{'limit_id': 'limit3_2', 'service': 'taxi'}],
                'services': [],
                'users': {'all_users': True},
            },
            None,
            400,
            id='put new task',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_update_users_limits_create_task(
        patch,
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        idempotency_token,
        post_content,
        created_long_task,
        status_code,
):
    """
    other test cases are the same as in test_update_users_cost_centers
    """

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    response = await taxi_corp_real_auth_client.post(
        '/2.0/bulk/users-limits',
        json=post_content,
        headers={'X-Idempotency-Token': idempotency_token},
    )

    if response.status == 200:
        response_json = await response.json()

        if created_long_task:
            task_id = response_json['_id']
            db_item = await db.corp_long_tasks.find_one(
                {'_id': task_id, 'idempotency_token': idempotency_token},
            )
            assert db_item
            for key, value in created_long_task.items():
                assert db_item[key] == value

            assert _put.calls
        else:
            assert not _put.calls
    else:
        assert not _put.calls


@pytest.mark.parametrize(
    ['passport_mock', 'task_id', 'expected_response', 'status_code'],
    [
        pytest.param(
            'client3',
            'task_waiting',
            {'status': 'waiting'},
            200,
            id='waiting task',
        ),
        pytest.param(
            'client3',
            'task_running',
            {'status': 'running', 'progress': 50},
            200,
            id='complete task',
        ),
        pytest.param(
            'client3',
            'task_complete',
            {'status': 'complete', 'result': 10},
            200,
            id='complete task',
        ),
        pytest.param('client3', 'task_unknown', None, 404, id='unknown task'),
        pytest.param(
            'client1',
            'task_complete',
            None,
            403,
            id='task is inaccessible for client',
        ),
        pytest.param(
            'client3', 'task_error_locked', None, 423, id='locked task',
        ),
        pytest.param(
            'client3', 'task_error_failed', None, 500, id='failed task',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_update_users_cost_centers_get_task(
        taxi_corp_real_auth_client,
        passport_mock,
        task_id,
        expected_response,
        status_code,
):
    """
    same tests for /2.0/bulk/users-limits/{task_id}
    """

    response = await taxi_corp_real_auth_client.get(
        '/2.0/bulk/users-cost-centers/{}'.format(task_id),
    )

    response_json = await response.json()
    assert response.status == status_code

    if response.status == 200:
        assert response_json == expected_response
    if response.status == 500:
        assert response_json['code'] == 'TASK_FATAL_ERROR'
        assert response_json['details'] == {
            'processed_size': 33,
            'total_size': 100,
        }
