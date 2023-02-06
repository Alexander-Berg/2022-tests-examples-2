# pylint: disable=too-many-locals
import datetime

import bson
import pytest


NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)
MOCK_ROLE_ID = 'mock_role_id'
MOCK_LIMIT_ID = 'mock_limit_id'


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


@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79,
    CORP_DRIVE_USE_PRESTABLE=True,
)
@pytest.mark.parametrize(
    'passport_mock, put_content, expected_content',
    [
        pytest.param('client1', {}, {}, id='client_restore'),
        pytest.param(
            'client1',
            {
                'cost_centers': {
                    'required': False,
                    'format': 'text',
                    'values': [],
                },
            },
            {
                'cost_centers': {
                    'required': False,
                    'format': 'text',
                    'values': [],
                },
            },
            id='restore_with_cost_centers',
        ),
        pytest.param(
            'main_manager1',
            {
                'role': {'role_id': 'role2'},
                'services': {'eats2': {'is_active': True}},
            },
            {
                'role': {'role_id': 'role2'},
                'limits': [
                    {'service': 'taxi', 'limit_id': 'limit2.1'},
                    {'service': 'eats2', 'limit_id': 'limit2.2'},
                ],
            },
            id='manager_restore',
        ),
        pytest.param(
            'manager1',
            {'department_id': 'd1_1'},
            {'department_id': 'd1_1'},
            id='dept_manager_restore',
        ),
        pytest.param(
            'client1',
            {
                'services': {
                    'drive': {
                        'is_active': False,
                        'group_id': None,
                        'soft_limit': None,
                    },
                    'eats': {'is_active': False, 'codes': []},
                    'eats2': {
                        'is_active': True,
                        'limits': {
                            'monthly': {
                                'amount': '-1',
                                'no_specific_limit': True,
                            },
                        },
                    },
                },
            },
            {
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': False,
                        'group_id': 'example',
                        'soft_limit': None,
                        'hard_limit': None,
                    },
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'taxi': {'send_activation_sms': False},
                    'eats2': {'was_sms_sent': False},
                },
            },
            id='services_is_active_false',
        ),
        pytest.param(
            'client1',
            {
                'services': {
                    'drive': {'is_active': True, 'soft_limit': '1000'},
                    'eats': {'is_active': True, 'codes': ['BBB1', 'BBB2']},
                },
            },
            {
                'services': {
                    'drive': {
                        'drive_user_id': 'drive_user_id',
                        'is_active': True,
                        'group_id': 'example',
                        'soft_limit': '1000',
                        'hard_limit': '1000',
                    },
                    'eats': {'is_active': False, 'send_activation_sms': True},
                    'taxi': {'send_activation_sms': False},
                    'eats2': {'was_sms_sent': False},
                },
            },
            id='services_is_active_true',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_restore_user(
        taxi_corp_real_auth_client,
        pd_patch,
        drive_patch,
        db,
        patch,
        patch_doc,
        passport_mock,
        put_content,
        expected_content,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    drive = taxi_corp_real_auth_client.server.app.drive
    assert drive.base_url == '$mockserver/drive'

    base_content = {
        'fullname': 'Restore',
        'role': {'limit': 7000, 'classes': ['econom']},
        'email': 'restore@mail.com',
        'is_active': False,
    }
    base_expected_content = {
        'department_id': None,
        'cost_center': '',
        'email': 'restore@mail.com',
        'email_id': 'pd_id',
        'fullname': 'Restore',
        'is_active': True,
        'nickname': 'Restore',
        'phone': '+79291112210',
        'phone_id': bson.ObjectId('AAAAAAAAAAAAA79291112210'),
        'personal_phone_id': 'pd_id',
        'role': {'role_id': MOCK_ROLE_ID},
        'services': {
            'drive': {
                'drive_user_id': 'drive_user_id',
                'is_active': False,
                'group_id': 'example',
                'soft_limit': None,
                'hard_limit': None,
            },
            'eats': {'is_active': False, 'send_activation_sms': True},
            'taxi': {'send_activation_sms': False},
            'eats2': {'was_sms_sent': False},
        },
        'is_deleted': False,
        'yandex_uid': 'userRestore_uid',
    }

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

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch(
        'taxi_corp.api.common.services.eats2_service.'
        '_put_eats2_activation_sms_task',
    )
    async def _put_stq_task(*args, **kwargs):
        pass

    @patch('taxi_corp.api.common.v1_users.update.create_role_id')
    def _create_role_id():
        return MOCK_ROLE_ID

    put_content = patch_doc(base_content, put_content)
    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/client1/user/userRestore/restore', json=put_content,
    )

    response_json = await response.json()
    assert response_json == {}
    db_item = await db.corp_users.find_one({'_id': 'userRestore'})
    for field in ['_id', 'client_id', 'updated', 'created']:
        del db_item[field]
    if 'limits' not in expected_content:
        services = put_content.get('services', {})
        expected_limits_count = (
            1
            + int(services.get('drive', {}).get('is_active', False))
            + int(services.get('eats2', {}).get('is_active', False))
        )

        assert len(db_item.pop('limits')) == expected_limits_count
    assert db_item == patch_doc(base_expected_content, expected_content)

    put_services = put_content.get('services', {})
    if put_services.get('eats2', {}).get('is_active', False):
        assert _put_stq_task.calls


@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
@pytest.mark.parametrize(
    'passport_mock, user, data, error, code',
    [
        pytest.param(
            'client1',
            'user3',
            {'department_id': 'd1', 'role': {'role_id': 'role1'}},
            'user is not deleted',
            400,
            id='already_restored',
        ),
        pytest.param(
            'client2',
            'userX',
            {},
            'Access denied',
            403,
            id='another_clients_user',
        ),
        pytest.param(
            'manager2',
            'userX',
            {'department_id': 'd1_1', 'role.role_id': 'role1'},
            'Access denied',
            403,
            id='dept_manager_to_denied_department',
        ),
        pytest.param(
            'secretary2',
            'userX',
            {'department_id': 'd2', 'role.role_id': 'role1'},
            'Access denied',
            403,
            id='dept_secretary_denied',
        ),
        pytest.param(
            'client1',
            'userX',
            {'department_id': 'd2', 'role.role_id': 'role1'},
            'role_id should belong to this department_id',
            400,
            id='client_to_denied_group',
        ),
        pytest.param(
            'client1',
            'userX',
            {'cost_centers': {'required': 'invalid'}},
            '\'invalid\' is not of type \'boolean\'',
            400,
            id='wrong_cost_centers',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_restore_user_fail(
        taxi_corp_real_auth_client,
        pd_patch,
        patch_doc,
        data,
        passport_mock,
        user,
        error,
        code,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    doc = {
        'fullname': 'Hoe',
        'phone': '+79291112203"',
        'role': {'role_id': 'role1'},
        'email': 'hoe@mail.com',
        'is_active': True,
    }
    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/client1/user/{}/restore'.format(user),
        json=patch_doc(doc, data),
    )
    response_json = await response.json()
    assert response.status == code
    assert error == response_json['errors'][0]['text']
