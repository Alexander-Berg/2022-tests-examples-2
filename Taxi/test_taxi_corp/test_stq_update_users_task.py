import pytest

from taxi_corp.internal import consts
from taxi_corp.internal import users_helper
from taxi_corp.stq import update_users_task
from taxi_corp.util import long_tasks_helper


@pytest.mark.parametrize(
    ['task_id', 'is_func_called', 'error_code'],
    [
        pytest.param(
            'task1',
            False,
            'TASK_CURRENTLY_LOCKED',
            id='task is locked -> func is not called',
        ),
        pytest.param(
            'task2', True, None, id='task is not locked -> func is called',
        ),
        pytest.param(
            'task3',
            True,
            None,
            id='another client, task is not locked -> func is called',
        ),
        pytest.param(
            'task4',
            False,
            'TASK_CURRENTLY_LOCKED',
            id='another stq task, task is  locked -> func is not called',
        ),
        pytest.param(
            'task5',
            True,
            None,
            id='second try of stq execution -> func is called',
        ),
        pytest.param(
            'task6',
            False,
            'TASK_FATAL_ERROR',
            id='max tries of stq execution -> func is not called',
        ),
    ],
)
async def test_check_lock_decorator(
        patch, taxi_corp_app_stq, db, task_id, is_func_called, error_code,
):
    @long_tasks_helper.check_lock
    async def stq_update_users(stq_app, task_id, request_info):
        return True, consts.LongTaskStatus.COMPLETE

    task_kwargs = {'task_id': task_id, 'request_info': {}}

    return_result = await stq_update_users(  # return None if locked
        taxi_corp_app_stq, **task_kwargs,
    )

    db_item = await db.corp_long_tasks.find_one({'_id': task_id})

    if is_func_called:
        assert return_result
        assert db_item['status'] == 'complete'
    else:
        assert return_result is None
        assert db_item['status'] == 'error'
        assert db_item['error_code'] == error_code


@pytest.mark.parametrize(
    ['users'],
    [
        pytest.param({'user_ids': ['test_user_1', 'test_user_3']}),
        pytest.param({'department_id': 'dep1'}),
        pytest.param({'all_users': True}),
    ],
)
async def test_update_users_cost_centers(patch, taxi_corp_app_stq, db, users):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    client_id = 'client3'
    task_id = 'task0'
    await db.corp_long_tasks.update_one(
        {'_id': task_id}, {'$set': {'task_args.users': users}},
    )
    task_kwargs = {'task_id': task_id, 'request_info': {}}
    await update_users_task.update_users_cost_centers(
        taxi_corp_app_stq, **task_kwargs,
    )

    query = await users_helper.get_query_by_users_update_field(
        db, client_id, users,
    )

    users_list = await db.corp_users.find(
        query, projection=['cost_centers_id'],
    ).to_list(None)
    assert all(
        [user['cost_centers_id'] == 'cost_centers1' for user in users_list],
    )

    db_item = await db.corp_long_tasks.find_one({'_id': task_id})
    assert db_item['status'] == 'complete'
    assert db_item['response_data']['result'] == len(users_list)
    assert db_item['exec_tries'] == 1
    assert len(_put.calls) == 1


@pytest.mark.parametrize(
    ['task_args', 'expected_stq_calls'],
    [
        pytest.param(
            {
                'client_id': 'client3',
                'limits': [],
                'services': ['taxi', 'eats2', 'drive', 'tanker'],
                'users': {'user_ids': ['test_user_1', 'test_user_3']},
            },
            2,
            id='reset limits',
        ),
        pytest.param(
            {
                'client_id': 'client3',
                'limits': [
                    {'limit_id': 'limit3_2', 'service': 'taxi'},
                    {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                ],
                'services': ['taxi', 'eats2', 'drive', 'tanker'],
                'users': {'user_ids': ['test_user_1', 'test_user_3']},
            },
            4,
            id='success path',
        ),
        pytest.param(
            {
                'client_id': 'client3',
                'limits': [{'limit_id': 'limit3_dep1_1', 'service': 'taxi'}],
                'services': ['taxi', 'eats2', 'drive', 'tanker'],
                'users': {'user_ids': ['test_user_1', 'test_user_3']},
            },
            3,
            id='limit from low department',
        ),
    ],
)
async def test_update_users_limits_replace_all_services(
        patch, taxi_corp_app_stq, db, task_args, expected_stq_calls,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    client_id = task_args['client_id']
    limits = task_args['limits']
    users = task_args['users']
    task_id = 'task0'

    await db.corp_long_tasks.update_one(
        {'_id': task_id}, {'$set': {'task_args': task_args}},
    )
    task_kwargs = {'task_id': task_id, 'request_info': {'locale': None}}
    await update_users_task.update_users_limits(
        taxi_corp_app_stq, **task_kwargs,
    )
    query = await users_helper.get_query_by_users_update_field(
        taxi_corp_app_stq.db, client_id, users,
    )

    users_list = await db.corp_users.find(
        query, projection=['limits'],
    ).to_list(None)
    assert all(user['limits'] == limits for user in users_list)

    db_item = await db.corp_long_tasks.find_one({'_id': task_id})
    assert db_item['status'] == 'complete'
    assert db_item['response_data']['result'] == len(users_list)
    assert db_item['exec_tries'] == 1

    assert len(_put.calls) == expected_stq_calls


@pytest.mark.parametrize(
    ['old_limits', 'task_args', 'expected_limits'],
    [
        pytest.param(
            [
                {'limit_id': 'limit3_2', 'service': 'taxi'},
                {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                {'limit_id': 'drive_limit', 'service': 'drive'},
            ],
            {
                'client_id': 'client3',
                'limits': [{'limit_id': 'limit3_1', 'service': 'taxi'}],
                'services': ['taxi', 'eats2', 'drive'],
                'users': {'user_ids': ['test_user_1']},
            },
            [{'limit_id': 'limit3_1', 'service': 'taxi'}],
        ),
        pytest.param(
            [
                {'limit_id': 'limit3_2', 'service': 'taxi'},
                {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                {'limit_id': 'drive_limit', 'service': 'drive'},
            ],
            {
                'client_id': 'client3',
                'limits': [{'limit_id': 'limit3_1', 'service': 'taxi'}],
                'services': ['taxi'],
                'users': {'user_ids': ['test_user_1']},
            },
            [
                {'limit_id': 'limit3_1', 'service': 'taxi'},
                {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                {'limit_id': 'drive_limit', 'service': 'drive'},
            ],
        ),
        pytest.param(
            [
                {'limit_id': 'limit3_2', 'service': 'taxi'},
                {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
            ],
            {
                'client_id': 'client3',
                'limits': [],
                'services': ['eats2'],
                'users': {'user_ids': ['test_user_1']},
            },
            [{'limit_id': 'limit3_2', 'service': 'taxi'}],
        ),
        pytest.param(
            [],
            {
                'client_id': 'client3',
                'limits': [],
                'services': ['eats2'],
                'users': {'user_ids': ['test_user_1']},
            },
            [],
        ),
    ],
)
async def test_update_users_limits_replace_some_services(
        patch, taxi_corp_app_stq, db, old_limits, task_args, expected_limits,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    task_id = 'task0'
    user_id = 'test_user_1'

    await db.corp_users.update_one(
        {'_id': user_id}, {'$set': {'limits': old_limits}},
    )
    await db.corp_long_tasks.update_one(
        {'_id': task_id}, {'$set': {'task_args': task_args}},
    )

    task_kwargs = {'task_id': task_id, 'request_info': {'locale': None}}
    await update_users_task.update_users_limits(
        taxi_corp_app_stq, **task_kwargs,
    )

    db_user = await db.corp_users.find_one({'_id': user_id})
    assert db_user['limits'] == expected_limits


@pytest.mark.parametrize(
    ['task_args', 'expected_limits_counters'],
    [
        pytest.param(
            {
                'client_id': 'client3',
                'limits': [{'limit_id': 'limit3_1', 'service': 'taxi'}],
                'services': ['taxi', 'eats2', 'drive'],
                'users': {'user_ids': ['test_user_1', 'test_user_3']},
            },
            {
                # old user limits
                'limit3_2_with_users': 1,  # value before stq: 3
                'limit3_2_eats2': 0,  # value before stq: 1
                'drive_limit': 0,  # value before stq: 1
                'limit3_2_tanker': 1,  # value before stq: 1
                # new user limits
                'limit3_1': 2,  # value before stq: 0
            },
        ),
    ],
)
async def test_update_users_limits_counters(
        patch, taxi_corp_app_stq, db, task_args, expected_limits_counters,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    task_id = 'task0'
    await db.corp_long_tasks.update_one(
        {'_id': task_id}, {'$set': {'task_args': task_args}},
    )
    task_kwargs = {'task_id': task_id, 'request_info': {'locale': None}}
    await update_users_task.update_users_limits(
        taxi_corp_app_stq, **task_kwargs,
    )

    limits = await db.corp_limits.find(
        {'_id': {'$in': list(expected_limits_counters.keys())}},
    ).to_list(None)

    for limit in limits:
        user_counters = limit.get('counters', {}).get('users', 0)
        assert user_counters == expected_limits_counters[limit['_id']]
