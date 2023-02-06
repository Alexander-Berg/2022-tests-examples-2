# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
import datetime

import pytest

from taxi_corp.internal import consts
from .conftest import DELETE_FIELD

NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)
MOCK_ROLE_ID = 'mock_role_id'


CORP_USER_PHONES_SUPPORTED_79 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]
CORP_USER_PHONES_SUPPORTED_712 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+712', '+79'],
        'matches': ['^712', '^79'],
    },
]


@pytest.mark.translations(
    corp={
        'role.others_name': {'ru': 'role.others_name'},
        'sms.eats_activate_sms': {'ru': 'Еда подключена!'},
        'sms.create_user': {'ru': 'Всем такси!'},
    },
)
@pytest.mark.parametrize(
    ['client_id', 'user_id', 'put_content', 'expected_user', 'expected_role'],
    [
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {
                    'limit': 1000,
                    'classes': ['econom', 'non-existing'],
                    'period': 'week',
                    'orders': {'no_specific_limit': True},
                },
                'email': 'joe@mail.com',
                'is_active': True,
                'revision': 1,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'limit': 1000,
                'no_specific_limit': False,
                'period': 'week',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
                'classes': ['econom'],
            },
        ),
        pytest.param(
            'client1',
            'user5',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {
                    'limit': 200,
                    'classes': ['econom', 'non-existing'],
                    'period': 'week',
                    'orders': {'no_specific_limit': True},
                },
                'email': 'joe@mail.com',
                'is_active': True,
                'revision': 1,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'role_id': 'personal_group_for_user5'},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'limit': 200,
                'no_specific_limit': False,
                'period': 'week',
                'orders': {'limit': consts.INF, 'no_specific_limit': True},
                'classes': ['econom'],
            },
            id='user already was in personal_limit',
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {
                    'limit': '1000',
                    'classes': ['econom', 'non-existing'],
                },
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'role': {'role_id': MOCK_ROLE_ID},
                'phone': '+79291112204',
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {'limit': 1000, 'no_specific_limit': False, 'classes': ['econom']},
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'nickname': 'CleverJoe',
                'role': {'role_id': 'role1'},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'nickname': 'CleverJoe',
                'role': {'role_id': 'role1'},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            },
            None,
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'role': {'role_id': 'role1'},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'role': {'role_id': 'role1'},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            },
            None,
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'limit': None, 'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
            },
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {
                    'limit': consts.INF,
                    'classes': ['econom', 'non-existing'],
                },
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
            },
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            },
            {
                'limit': consts.INF,
                'no_specific_limit': True,
                'classes': ['econom'],
            },
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['123', ''],
                },
                'role': {'role_id': 'role4'},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['123'],
                },
                'role': {'role_id': 'role4'},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': None,
            },
            None,
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'role': {
                    'limit': 5000,
                    'classes': ['econom', 'unknown-class-name'],
                    'restrictions': [
                        {
                            'type': 'range_date',
                            'start_date': '2000-01-01T00:00:00',
                            'end_date': '2000-01-02T00:00:00',
                        },
                        {
                            'type': 'weekly_date',
                            'start_time': '03:10:10',
                            'end_time': '03:20:10',
                            'days': [],
                        },
                    ],
                },
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': None,
            },
            {
                'limit': 5000,
                'classes': ['econom'],
                'no_specific_limit': False,
                'restrictions': [
                    {
                        'type': 'range_date',
                        'end_date': '2000-01-02T00:00:00',
                        'start_date': '2000-01-01T00:00:00',
                    },
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': [],
                    },
                ],
            },
        ),
        (
            'client2',
            'userServicesNotActive',
            {
                'fullname': 'Joe',
                'phone': '+79291112205',
                'role': {'limit': 1000, 'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '1000',
                    },
                    'eats': {'is_active': True, 'codes': []},
                },
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112205',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '1000',
                        'hard_limit': '1000',
                    },
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'eats2': {'was_sms_sent': False},
                    'taxi': {'send_activation_sms': False},
                },
            },
            {'limit': 1000, 'no_specific_limit': False, 'classes': ['econom']},
        ),
        (
            'client2',
            'userServicesActive',
            {
                'fullname': 'Joe',
                'phone': '+79291112206',
                'role': {'limit': 1000, 'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': False,
                        'group_id': 'example',
                        'soft_limit': '100.00',
                    },
                    'eats': {'is_active': True, 'codes': ['BBB1', 'BBB2']},
                },
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112206',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': False,
                        'group_id': 'example',
                        'soft_limit': '100.00',
                        'hard_limit': '100.00',
                    },
                    'eats': {'is_active': True},
                    'eats2': {'was_sms_sent': False},
                    'taxi': {'send_activation_sms': False},
                },
            },
            {'limit': 1000, 'no_specific_limit': False, 'classes': ['econom']},
        ),
        pytest.param(
            'client2',
            'userServicesTheSameGroup',
            {
                'fullname': 'Joe',
                'phone': '+79291112207',
                'role': {'limit': 1000, 'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
                'yandex_login': 'user_login',
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '1000',
                    },
                    'eats': {'is_active': False, 'codes': []},
                },
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112207',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
                'yandex_uid': '4009429274',
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '1000',
                        'hard_limit': '1000',
                    },
                    'eats': {'is_active': True},
                    'eats2': {'was_sms_sent': False},
                    'taxi': {'send_activation_sms': False},
                },
            },
            {'limit': 1000, 'no_specific_limit': False, 'classes': ['econom']},
        ),
        (
            'client1',
            'new_inactive_user',
            {
                'fullname': 'Joe',
                'phone': '+79291112208',
                'role': {'limit': 1000, 'classes': ['econom', 'non-existing']},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112208',
                'personal_phone_id': 'pd_id',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {'limit': 1000, 'no_specific_limit': False, 'classes': ['econom']},
        ),
        (
            'client1',
            'user3',
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'role': {
                    'limit': 5000,
                    'classes': ['econom', 'unknown-class-name'],
                    'geo_restrictions': [
                        {
                            'source': 'geo_id_1',
                            'destination': 'geo_id_2',
                            'prohibiting_restriction': True,
                        },
                    ],
                },
                'email': 'joe@mail.com',
                'is_active': True,
            },
            {
                'fullname': 'Joe',
                'phone': '+79291112204',
                'cost_center': 'JoesProject',
                'role': {'role_id': MOCK_ROLE_ID},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': None,
            },
            {
                'limit': 5000,
                'classes': ['econom'],
                'no_specific_limit': False,
                'geo_restrictions': [
                    {
                        'source': 'geo_id_1',
                        'destination': 'geo_id_2',
                        'prohibiting_restriction': True,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_712,
    COST_CENTERS_VALUES_MAX_COUNT=2,
)
async def test_single_put(
        taxi_corp_auth_client,
        pd_patch,
        drive_patch,
        db,
        patch,
        client_id,
        user_id,
        put_content,
        expected_user,
        expected_role,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.drive.DriveClient.accounts_by_account_id')
    async def _accounts_by_account_id(account_id, **kwargs):
        assert account_id == 100
        return {
            'id': 100,
            'type_name': 'example',
            'soft_limit': 10000,
            'hard_limit': 10000,
            'is_active': True,
            'parent': {'id': 123},
        }

    @patch('taxi.clients.drive.DriveClient.get_user_id_by_yandex_uid')
    async def _get_user_id_by_yandex_uid(*args, **kwargs):
        return {'users': [{'12345': 'user_id'}]}

    @patch('taxi.clients.drive.DriveClient.descriptions')
    async def _descriptions(*args, **kwargs):
        return {
            'accounts': [
                {
                    'name': 'example',
                    'soft_limit': 0,
                    'hard_limit': 0,
                    'meta': {'parent_id': 123},
                },
            ],
        }

    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):
        return {'uid': '4009429274'}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(*args, **kwargs):
        return {'id': 'pd_id'}

    @patch(
        'taxi_corp.api.common.services.eats2_service.'
        '_put_eats2_activation_sms_task',
    )
    async def _put_eats2_stq_task(*args, **kwargs):
        pass

    @patch(
        'taxi_corp.api.common.services.taxi_service.'
        '_put_taxi_activation_sms_task',
    )
    async def _put_taxi_stq_task(*args, **kwargs):
        pass

    @patch('taxi_corp.api.common.v1_users.update.create_role_id')
    def _create_role_id():
        return MOCK_ROLE_ID

    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/user/{}'.format(client_id, user_id), json=put_content,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}
    db_item = await db.corp_users.find_one({'_id': user_id})
    for key, value in expected_user.items():
        assert db_item[key] == value

    if expected_role:
        db_role = await db.corp_roles.find_one({'user_id': user_id})
        for key, value in expected_role.items():
            assert db_role[key] == value

    put_services = put_content.get('services', {})
    if put_services.get('eats2', {}).get('is_active', False):
        assert _put_eats2_stq_task.calls
    if put_services.get('eats2', {}).get('is_active', False):
        assert _put_taxi_stq_task.calls


@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_712,
    COST_CENTERS_VALUES_MAX_COUNT=2,
)
@pytest.mark.parametrize(
    'method, url, passport_mock',
    [
        ('POST', '/1.0/client/client1/user', 'client1'),
        ('PUT', '/1.0/client/client1/user/user3', 'client1'),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'request_content, response_code, expected_errors',
    [
        ({'role': {'role_id': 'notfound'}}, 400, ['Role not found']),
        (
            {'phone': '+79291112202'},
            406,
            ['error.duplicate_user_phone_error_code'],
        ),
        (
            {'role.classes': DELETE_FIELD},
            400,
            ['{\'limit\': 100} is not valid under any of the given schemas'],
        ),
        (
            {'role.limit': 'invalid'},
            400,
            ['limit should be a positive int or None'],
        ),
        ({'role.limit': -50}, 400, ['limit should be a positive int or None']),
        (
            {'fullname': DELETE_FIELD},
            400,
            ['\'fullname\' is a required property'],
        ),
        (
            {'excess_field': 'value'},
            400,
            [
                'Additional properties are not allowed '
                '(\'excess_field\' was unexpected)',
            ],
        ),
        ({'department_id': 'invalid'}, 404, ['Department not found']),
        ({'role.limit': 10 ** 8}, 400, ['error.validate_max_limit']),
        (
            {'role': None},
            400,
            ['None is not valid under any of the given schemas'],
        ),
        (
            {
                'role.restrictions': [
                    {
                        'type': 'range_date',
                        'start_date': '0000-01-02T00:00:00',
                        'end_date': '2000-01-01T00:00:00',
                    },
                ],
            },
            400,
            ['invalid format for start_date'],
        ),
        (
            {
                'role.restrictions': [
                    {
                        'type': 'range_date',
                        'start_date': '2000-01-02T00:00:00',
                        'end_date': '2000-01-01T00:00:00',
                    },
                ],
            },
            400,
            ['\'start_date\' must be less than \'end_date\''],
        ),
        (
            {
                'role.restrictions': [
                    {
                        'type': 'weekly_date',
                        'start_time': '03:20:10',
                        'end_time': '03:10:10',
                        'days': ['mo'],
                    },
                ],
            },
            400,
            ['\'start_time\' must be less than \'end_time\''],
        ),
        (
            {
                'role.restrictions': [
                    {
                        'type': 'weekly_date',
                        'start_time': '03:10:10',
                        'end_time': '03:20:10',
                        'days': ['mo', 'mo'],
                    },
                ],
            },
            400,
            [
                '{\'limit\': 100, \'classes\': [\'econom\'], '
                '\'restrictions\': [{\'type\': \'weekly_date\', '
                '\'start_time\': \'03:10:10\', \'end_time\': \'03:20:10\', '
                '\'days\': [\'mo\', \'mo\']}]} '
                'is not valid under any of the given schemas',
            ],
        ),
        (
            {
                'role': {
                    'limit': 1000,
                    'no_specific_limit': True,
                    'classes': ['econom'],
                },
            },
            400,
            ['limit should be an infinite'],
        ),
        (
            {'role': {'role_id': 'role3'}, 'department_id': 'd2'},
            400,
            ['role_id should belong to this department_id'],
        ),
        (
            {
                'cost_centers': {
                    'required': 'invalid',
                    'format': 'invalid',
                    'values': 'invalid',
                },
            },
            400,
            [
                '\'invalid\' is not of type \'boolean\'',
                '\'invalid\' is not one of [\'select\', \'text\', \'mixed\']',
                '\'invalid\' is not of type \'array\'',
            ],
        ),
        pytest.param(
            {
                'cost_centers': {
                    'required': True,
                    'format': 'select',
                    'values': ['123', '456', '789'],
                },
            },
            400,
            ['error.cost_centers_max_count_error'],
            id='too_many_cost_centers_values',
        ),
        pytest.param(
            {
                'services': {
                    'drive': {
                        'is_active': True,
                        'group_id': None,
                        'soft_limit': None,
                    },
                },
            },
            400,
            ['error.drive_limits_required'],
            id='drive_no_limits',
        ),
        pytest.param(
            {
                'role.geo_restrictions': [
                    {'source': 'geo_id_1', 'destination': 'geo_id_not_found'},
                ],
            },
            400,
            ['source or destination points are not found'],
            id='geo_restriction_was_not_found',
        ),
    ],
)
async def test_single_edit_fail(
        taxi_corp_real_auth_client,
        pd_patch,
        drive_patch,
        patch,
        patch_doc,
        method,
        url,
        passport_mock,
        request_content,
        response_code,
        expected_errors,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    base_content = {
        'fullname': 'Boe',
        'phone': '+79291112204',
        'role': {'limit': 100, 'classes': ['econom']},
        'email': 'boe@mail.com',
        'is_active': False,
    }
    response = await taxi_corp_real_auth_client.request(
        method, url, json=patch_doc(base_content, request_content),
    )

    response_json = await response.json()
    assert response.status == response_code, response_json
    response_errors = [
        error['text'] for error in response_json.get('errors', [])
    ]
    assert response_errors == expected_errors


@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_single_edit_deleted(taxi_corp_auth_client, pd_patch):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    doc = {
        'fullname': 'UserX',
        'phone': '+79291112204',
        'role': {'limit': 5000, 'classes': ['econom']},
        'email': 'boe@mail.com',
        'is_active': True,
        'department_id': 'd1',
    }
    response = await taxi_corp_auth_client.put(
        '/1.0/client/client1/user/userX', json=doc,
    )
    response_json = await response.json()
    assert response.status == 400
    assert response_json == {
        'errors': [
            {'code': 'USER_IS_DELETED_ERROR', 'text': 'user is deleted'},
        ],
        'message': 'user is deleted',
        'code': 'USER_IS_DELETED_ERROR',
    }


@pytest.mark.parametrize(
    ['put_content', 'sms_sent'],
    [
        pytest.param(
            {
                'fullname': 'Boe',
                'phone': '+792922222222',
                'email': 'boe@mail.com',
                'is_active': True,
                'role': {'limit': 5000, 'classes': ['econom']},
            },
            True,
            id='send_updated',
        ),
        pytest.param(
            {
                'fullname': 'Boe',
                'phone': '+79291112214',
                'email': 'boe@mail.com',
                'is_active': False,
                'role': {'limit': 5000, 'classes': ['econom']},
            },
            False,
            id='not_is_active',
        ),
    ],
)
async def test_update_created(
        taxi_corp_auth_client,
        patch,
        drive_patch,
        put_content,
        sms_sent,
        pd_patch,
):
    @patch(
        'taxi_corp.api.common.services.taxi_service.'
        '_put_taxi_activation_sms_task',
    )
    async def _put_taxi_stq_task(*args, **kwargs):
        pass

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    create_doc = {
        'fullname': 'Boe',
        'phone': '+79291111111',
        'role': {'limit': 0, 'classes': []},
        'email': 'boe@mail.com',
        'is_active': False,
        'department_id': 'd1',
    }
    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/user', json=create_doc,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert list(_put_taxi_stq_task.calls) == []

    user_id = response_json['_id']
    response = await taxi_corp_auth_client.put(
        '/1.0/client/client1/user/{}'.format(user_id), json=put_content,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    _put_taxi_stq_task_calls = list(_put_taxi_stq_task.calls)
    assert len(_put_taxi_stq_task_calls) == sms_sent


@pytest.mark.parametrize(
    ['client_is_active', 'user_is_active'],
    [
        pytest.param(True, True, id='all_active'),
        pytest.param(True, False, id='user_inactive'),
        pytest.param(False, True, id='client_inactive'),
        pytest.param(False, False, id='all_inactive'),
    ],
)
async def test_drive_wallet_status(
        taxi_corp_auth_client,
        pd_patch,
        patch,
        db,
        client_is_active,
        user_is_active,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.drive.DriveClient.descriptions')
    async def _descriptions(*args, **kwargs):
        return {
            'accounts': [
                {
                    'name': 'example',
                    'soft_limit': 0,
                    'hard_limit': 0,
                    'meta': {'parent_id': 123},
                },
            ],
        }

    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):
        return {'uid': '12345'}

    @patch('taxi.clients.drive.DriveClient.get_user_id_by_yandex_uid')
    async def _get_user_id_by_yandex_uid(*args, **kwargs):
        return {'users': [{'12345': 'user_id'}]}

    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _account(*args, **kwargs):
        return {
            'id': 100,
            'type_name': 'example',
            'soft_limit': 100000,
            'hard_limit': 100000,
            'is_active': not user_is_active,
        }

    @patch('taxi.clients.drive.DriveClient.activate')
    async def _activate(accounts, is_active, **kwargs):
        assert is_active == user_is_active

    await db.corp_clients.find_one_and_update(
        {'_id': 'client1'},
        {'$set': {'services.drive.is_active': client_is_active}},
    )

    user = {
        'fullname': 'Boe',
        'phone': '+79291112214',
        'role': {'limit': 5000, 'classes': ['econom']},
        'email': 'boe@mail.com',
        'is_active': True,
        'yandex_login': '123',
        'services': {
            'drive': {
                'soft_limit': '1000',
                'hard_limit': '1000',
                'is_active': user_is_active,
                'group_id': 'example',
            },
        },
    }

    await taxi_corp_auth_client.put(
        '/1.0/client/client1/user/user1', json=user,
    )

    user = await db.corp_users.find_one({'_id': 'user1'})
    assert user['services']['drive']['is_active'] == user_is_active


@pytest.mark.parametrize(
    ['user_id'],
    [
        pytest.param(
            'userFromPersonalToRegularGroup',
            id='Change new style personal to common',
        ),
        pytest.param(
            'oldStylePersonal', id='Change new style personal to common',
        ),
    ],
)
async def test_put_personal_to_common_group(
        taxi_corp_auth_client, pd_patch, patch, db, user_id,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    target_role = 'role5'
    user = await db.corp_users.find_one({'_id': user_id})
    del user['_id']
    del user['phone_id']
    del user['client_id']
    user['role'] = {'role_id': target_role}

    response = await taxi_corp_auth_client.put(
        '/1.0/client/client4/user/{}'.format(user_id), json=user,
    )
    assert response.status == 200

    user = await db.corp_users.find_one({'_id': user_id})
    assert user['role']['role_id'] == target_role

    role = await db.corp_roles.find_one(
        {'client_id': 'client4', 'user_id': user_id},
    )
    assert role is None


@pytest.mark.parametrize(
    ['user_id', 'new_limits'],
    [
        pytest.param(
            'userFromRegularToPersonalGroup',
            {'limit': 400, 'classes': ['econom']},
            id='Change common group to new style personal',
        ),
    ],
)
async def test_put_common_to_personal_group(
        taxi_corp_auth_client, pd_patch, db, user_id, new_limits,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    user = await db.corp_users.find_one({'_id': user_id})
    del user['_id']
    del user['phone_id']
    del user['client_id']
    user['role'] = new_limits

    response = await taxi_corp_auth_client.put(
        '/1.0/client/client4/user/{}'.format(user_id), json=user,
    )
    assert response.status == 200

    user = await db.corp_users.find_one({'_id': user_id})
    new_role_id = user['role']['role_id']
    new_role = await db.corp_roles.find_one({'_id': new_role_id})
    assert new_role['user_id'] == user_id
    assert new_role['name'] == user_id

    for key, value in new_limits.items():
        assert new_role[key] == value
