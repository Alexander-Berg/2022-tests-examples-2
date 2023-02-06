# pylint: disable=redefined-outer-name
import copy

import pytest

from taxi_corp import settings
from test_taxi_corp import corp_users_util

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(
        corp={
            'error.users.validation': {
                'ru': 'Ошибка в столбце {} в строке {}',
            },
            'error.users.validation_api': {'ru': 'Ошибка в столбце {}'},
            'error.required_field.csv_validation': {
                'ru': 'Нет обязательного поля {} на строке {}',
            },
            'error.required_field.api_validation': {
                'ru': 'Нет обязательного поля {}',
            },
            'error.departments.csv_validation': {
                'ru': 'Ошибка валидации департаментов на строке {}',
            },
            'error.departments.api_validation': {
                'ru': 'Ошибка валидации департаментов',
            },
            'error.cost_center.csv_validation': {
                'ru': 'Неправильно указан центр затрат на строке {}',
            },
            'error.cost_center.api_validation': {
                'ru': 'Неправильно указан центр затрат',
            },
            'error.user_creation.csv_validation': {
                'ru': 'Ошибка при создании сотрудника на строке {}',
            },
            'error.ids.csv_validation': {
                'ru': 'Ошибка. Такого id не существует на строке {}',
            },
            'error.duplicate_phone.csv_validation': {
                'ru': (
                    'Ошибка. Обнаружен дубликат'
                    ' телефонного номера на строке {}'
                ),
            },
            'error.duplicate_phone.api_validation': {
                'ru': ('Ошибка. Обнаружен дубликат' ' телефонного номера'),
            },
            'error.deleted_user.csv_validation': {
                'ru': (
                    'Ошибка. Попытка изменить или создать'
                    ' удаленного сотрудника на строке {}'
                ),
            },
            'error.duplicate_id.csv_validation': {
                'ru': 'Ошибка. Обнаружен дубликат id на строке {}',
            },
            'error.limits.csv_validation': {
                'ru': 'Ошибка при валидации лимитов на строке {}',
            },
            'error.limits.api_validation': {
                'ru': 'Ошибка при валидации лимитов',
            },
            'error.users.csv_parse': {'ru': 'Ошибка в структуре csv файла'},
        },
    ),
]


_v2 = corp_users_util.v2_user_doc  # pylint: disable=invalid-name

CORP_USER_PHONES_SUPPORTED = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]

NEW_USER = _v2(corp_users_util.EXTENDED_USER_REQUEST)

NEW_USER2 = copy.deepcopy(NEW_USER)
NEW_USER2['phone'] = '+79997778878'

NEW_USER_EMPTY_COST_CENTER = copy.deepcopy(NEW_USER)
NEW_USER_EMPTY_COST_CENTER['cost_center'] = ''

NEW_USER_NO_COST_CENTER = copy.deepcopy(NEW_USER)
NEW_USER_NO_COST_CENTER.pop('cost_center')

NEW_USER_SAME_PHONE = copy.deepcopy(NEW_USER)
NEW_USER_SAME_PHONE['phone'] = '+79654646546'

NEW_USER_SAME_PHONE_BAD_EMAIL = copy.deepcopy(NEW_USER_SAME_PHONE)
NEW_USER_SAME_PHONE_BAD_EMAIL['email'] = 'xxx'

NEW_USER_EMPTY_PHONE = copy.deepcopy(NEW_USER)
NEW_USER_EMPTY_PHONE['phone'] = ''

NEW_USER_NO_PHONE = copy.deepcopy(NEW_USER)
NEW_USER_NO_PHONE.pop('phone')

NEW_USER_BAD_PHONE1 = copy.deepcopy(NEW_USER)
NEW_USER_BAD_PHONE1['phone'] = 'xxx'

NEW_USER_BAD_PHONE2 = copy.deepcopy(NEW_USER)
NEW_USER_BAD_PHONE2['phone'] = '+81231909911'

NEW_USER_BAD_TAXI_LIMIT_ID = copy.deepcopy(NEW_USER)
NEW_USER_BAD_TAXI_LIMIT_ID['limits'][0]['limit_id'] = 'xxx'

NEW_USER_BAD_DEP_ID = copy.deepcopy(NEW_USER)
NEW_USER_BAD_DEP_ID['department_id'] = 'xxx'

NEW_USER_BAD_COST_CENTERS_ID = copy.deepcopy(NEW_USER)
NEW_USER_BAD_COST_CENTERS_ID['cost_centers_id'] = 'xxx'

NEW_USER_BAD_FULLNAME = copy.deepcopy(NEW_USER)
NEW_USER_BAD_FULLNAME['fullname'] = '!!!'

NEW_USER_BAD_NICKNAME = copy.deepcopy(NEW_USER)
NEW_USER_BAD_NICKNAME['nickname'] = '!!!'


@pytest.mark.parametrize(
    [
        'passport_mock',
        'post_content',
        'expected_status',
        'expected_errors',
        'expected_is_correct',
    ],
    [
        pytest.param('client3', [NEW_USER], 200, [[]], True),
        pytest.param('client3', [NEW_USER_EMPTY_COST_CENTER], 200, [[]], True),
        pytest.param(
            'client3',
            [NEW_USER_NO_COST_CENTER],
            200,
            [
                [
                    {
                        'text': 'Ошибка в столбце ',
                        'field': '',
                        'error_type': 'validation_error',
                    },
                    {
                        'text': 'Нет обязательного поля cost_center',
                        'field': 'cost_center',
                        'error_type': 'missed_required_field',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER, NEW_USER],
            200,
            [
                [],
                [
                    {
                        'field': 'phone',
                        'text': (
                            'Ошибка. Обнаружен дубликат телефонного номера'
                        ),
                        'error_type': 'duplicate_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_SAME_PHONE],
            200,
            [
                [
                    {
                        'text': (
                            'Ошибка. Обнаружен дубликат телефонного номера'
                        ),
                        'field': 'phone',
                        'error_type': 'duplicate_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_SAME_PHONE_BAD_EMAIL],
            200,
            [
                [
                    {
                        'text': 'Ошибка в столбце email',
                        'field': 'email',
                        'error_type': 'validation_error',
                    },
                    {
                        'text': (
                            'Ошибка. Обнаружен дубликат телефонного номера'
                        ),
                        'field': 'phone',
                        'error_type': 'duplicate_error',
                    },
                ],
            ],
            False,
            id='email_err',
        ),
        pytest.param(
            'client3',
            [NEW_USER_EMPTY_PHONE],
            200,
            [
                [
                    {
                        'text': 'Ошибка в столбце phone',
                        'field': 'phone',
                        'error_type': 'validation_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_BAD_PHONE1],
            200,
            [
                [
                    {
                        'text': 'Ошибка в столбце phone',
                        'field': 'phone',
                        'error_type': 'validation_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_BAD_PHONE2],
            200,
            [
                [
                    {
                        'text': 'Ошибка в столбце phone',
                        'field': 'phone',
                        'error_type': 'validation_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param('client3', [NEW_USER_NO_PHONE], 400, None, None),
        pytest.param(
            'client3',
            [NEW_USER_BAD_TAXI_LIMIT_ID],
            200,
            [
                [
                    {
                        'field': 'limit_taxi_id',
                        'text': 'Ошибка при валидации лимитов',
                        'error_type': 'wrong_value',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_BAD_DEP_ID],
            200,
            [
                [
                    {
                        'field': 'department_id',
                        'text': 'Ошибка валидации департаментов',
                        'error_type': 'wrong_value',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_BAD_COST_CENTERS_ID],
            200,
            [
                [
                    {
                        'field': 'cost_centers_id',
                        'text': 'Неправильно указан центр затрат',
                        'error_type': 'wrong_value',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_BAD_FULLNAME],
            200,
            [
                [
                    {
                        'field': 'fullname',
                        'text': 'Ошибка в столбце fullname',
                        'error_type': 'validation_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_BAD_NICKNAME],
            200,
            [
                [
                    {
                        'field': 'nickname',
                        'text': 'Ошибка в столбце nickname',
                        'error_type': 'validation_error',
                    },
                ],
            ],
            False,
        ),
        pytest.param(
            'client3',
            [NEW_USER_SAME_PHONE, NEW_USER_BAD_PHONE1],
            200,
            [
                [
                    {
                        'field': 'phone',
                        'text': (
                            'Ошибка. Обнаружен дубликат телефонного номера'
                        ),
                        'error_type': 'duplicate_error',
                    },
                ],
                [
                    {
                        'field': 'phone',
                        'text': 'Ошибка в столбце phone',
                        'error_type': 'validation_error',
                    },
                ],
            ],
            False,
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_bulk_users_check(
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        post_content,
        expected_status,
        expected_errors,
        expected_is_correct,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.post(
        '/2.0/bulk/users/check', json={'users': post_content},
    )
    assert response.status == expected_status
    if expected_status == 200:
        response_data = await response.json()

        for i, user in enumerate(response_data['users']):
            assert user.get('errors', '') == expected_errors[i]

        assert response_data['is_correct'] == expected_is_correct


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
            [NEW_USER, NEW_USER2],
            {
                'idempotency_token': 'not_existed_idempotency_token',
                'task_name': settings.STQ_QUEUE_CREATE_USERS,
                'task_args': {
                    'client_id': 'client3',
                    'users': [
                        {
                            'fullname': 'base_name',
                            'phone': '+79997778877',
                            'is_active': True,
                            'email': 'example@yandex.ru',
                            'department_id': 'dep1',
                            'limits': [
                                {'limit_id': 'limit3_2', 'service': 'taxi'},
                                {
                                    'limit_id': 'limit3_2_eats2',
                                    'service': 'eats2',
                                },
                                {
                                    'limit_id': 'limit3_2_tanker',
                                    'service': 'tanker',
                                },
                            ],
                            'cost_centers_id': 'cost_center_1',
                            'cost_center': 'default',
                            'nickname': 'custom ID',
                            'is_deleted': False,
                        },
                        {
                            'fullname': 'base_name',
                            'phone': '+79997778878',
                            'is_active': True,
                            'email': 'example@yandex.ru',
                            'department_id': 'dep1',
                            'limits': [
                                {'limit_id': 'limit3_2', 'service': 'taxi'},
                                {
                                    'limit_id': 'limit3_2_eats2',
                                    'service': 'eats2',
                                },
                                {
                                    'limit_id': 'limit3_2_tanker',
                                    'service': 'tanker',
                                },
                            ],
                            'cost_centers_id': 'cost_center_1',
                            'cost_center': 'default',
                            'nickname': 'custom ID',
                            'is_deleted': False,
                        },
                    ],
                },
                'status': 'waiting',
            },
            200,
            id='put new task',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_create_users(
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
        '/2.0/bulk/users',
        json={'users': post_content},
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
    ['passport_mock', 'task_id', 'expected_response', 'status_code'],
    [
        pytest.param(
            'client3',
            'task_complete',
            {'status': 'complete', 'result': 10},
            200,
            id='complete task',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_get_task(
        taxi_corp_real_auth_client,
        passport_mock,
        task_id,
        expected_response,
        status_code,
):
    response = await taxi_corp_real_auth_client.get(
        '/2.0/bulk/users/{}'.format(task_id),
    )

    response_json = await response.json()
    assert response.status == status_code
    if response.status == 200:
        assert response_json == expected_response
