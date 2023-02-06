import copy

import pytest

from taxi_corp.stq import create_users

CORP_USER_PHONES_SUPPORTED = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]

USER = {
    'fullname': 'base_name',
    'phone': '+79997778877',
    'is_active': True,
    'email': 'example@yandex.ru',
    'department_id': 'dep1',
    'limits': [
        {'limit_id': 'limit3_2', 'service': 'taxi'},
        {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
        {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
    ],
    'cost_centers_id': 'cost_center_1',
    'cost_center': 'default',
    'nickname': 'custom ID',
    'is_deleted': False,
}
USER2 = copy.deepcopy(USER)
USER2['phone'] = '+79997778878'

USER_BAD_PHONE = copy.deepcopy(USER)
USER_BAD_PHONE['phone'] = 'xxx'


@pytest.mark.parametrize(
    ['task_args', 'expected_task_result', 'expected_stored_users'],
    [
        pytest.param(
            {'client_id': 'client3', 'users': [USER, USER2]},
            {
                'response_data': {'result': 2},
                'progress': {'processed_size': 2, 'total_size': 2},
                'status': 'complete',
            },
            [USER, USER2],
        ),
        pytest.param(
            {'client_id': 'client3', 'users': [USER, USER_BAD_PHONE]},
            {
                'response_data': {'result': {'errors': '2'}},
                'progress': {'processed_size': 1, 'total_size': 2},
                'status': 'error',
            },
            [USER],
        ),
    ],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_main(
        pd_patch,
        patch,
        taxi_corp_app_stq,
        db,
        task_args,
        expected_task_result,
        expected_stored_users,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    task_id = 'task0'

    await db.corp_long_tasks.update_one(
        {'_id': task_id}, {'$set': {'task_args': task_args}},
    )

    task_kwargs = {
        'task_id': task_id,
        'request_info': {
            'login': 'corp-test',
            'uid': '4010776088',
            'method': 'POST',
            'user_ip': '2a02:6b8:c0f:4:0:42d5:a437:0',
            'locale': 'ru',
        },
    }

    await taxi_corp_app_stq.phones.refresh_cache()

    await create_users(taxi_corp_app_stq, **task_kwargs)

    for user in expected_stored_users:
        user_doc = await db.corp_users.find_one({'phone': user['phone']})
        assert user_doc

    task = await db.corp_long_tasks.find_one({'_id': task_id})

    for k, val in expected_task_result.items():
        assert task[k] == val
