# pylint: disable=too-many-locals
import datetime

import pytest

from taxi.clients import integration_api

from test_taxi_corp import request_util as util

_NOW = datetime.datetime(2016, 3, 19, 12, 40)


@pytest.mark.parametrize(
    'post_content',
    [
        # plane case
        (
            {
                'fullname': 'Boe',
                'phone': '+79291234567',
                'role': {'role_id': 'role1'},
                'email': 'boe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            }
        ),
        # nested departments
        (
            {
                'fullname': 'Boe',
                'phone': '+79291234567',
                'role': {'role_id': 'role1_1_1'},
                'email': 'boe@mail.com',
                'is_active': True,
                'department_id': 'd1_1_1',
            }
        ),
        # role "others" == no role_id
        (
            {
                'fullname': 'Heh',
                'phone': '+79291234567',
                'role': {'classes': ['business']},
                'email': 'boe@mail.com',
                'is_active': True,
                'department_id': 'd1',
            }
        ),
        # no role_id, no dept
        (
            {
                'fullname': 'Heh',
                'phone': '+79291234567',
                'role': {'classes': ['business']},
                'email': 'boe@mail.com',
                'is_active': True,
            }
        ),
    ],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_add_user(
        taxi_corp_auth_client, pd_patch, db, patch, post_content,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient.send_sms_to_user',
    )
    async def _send_message(personal_phone_id, text, intent):
        assert personal_phone_id == 'pd_id'
        assert text == 'sms.create_user'
        assert intent == 'taxi_corp_taxi_account_created'

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    # get counters before create user
    dept_id = post_content.get('department_id')

    if dept_id:
        dept_usercount = (
            await db.corp_departments.find_one({'_id': dept_id})
        )['counters']['users']

        ancestors = (await db.corp_departments.find_one({'_id': dept_id}))[
            'ancestors'
        ]
        anc_counter = {}
        for anc_id in ancestors:
            anc_counter[anc_id] = (
                (await db.corp_departments.find_one({'_id': anc_id}))
                .get('counters', {})
                .get('users', 0)
            )

    role_id = post_content['role'].get('role_id')

    role_usercount = (
        role_id
        and (await db.corp_roles.find_one({'_id': role_id}))['counters'][
            'users'
        ]
    )

    # create user
    response = await taxi_corp_auth_client.post(
        '/1.0/client/client1/user', json=post_content,
    )

    assert response.status == 200

    # check all counters increased by 1
    if role_id:
        role = await db.corp_roles.find_one({'_id': role_id})
        limit = await db.corp_limits.find_one(
            {'role_id': role_id, 'service': 'taxi'},
        )
        assert role['counters']['users'] == role_usercount + 1
        assert role['counters']['users'] == limit['counters']['users']

    if dept_id:
        dept = await db.corp_departments.find_one({'_id': dept_id})
        assert dept['counters']['users'] == dept_usercount + 1

        for anc_id in ancestors:
            updated_anc = await db.corp_departments.find_one({'_id': anc_id})
            assert updated_anc['counters']['users'] == anc_counter[anc_id] + 1


@pytest.mark.parametrize(
    ['passport_mock', 'client_id', 'post_content'],
    [
        # department manager
        (
            'manager1',
            'client1',
            util.make_order_request(
                city='unknown_city_id', phone='+71231234567', zone_name=None,
            ),
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+7'],
            'matches': ['^7'],
        },
    ],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_add_user_via_order(
        taxi_corp_real_auth_client,
        pd_patch,
        load_json,
        db,
        patch,
        passport_mock,
        client_id,
        post_content,
):
    app = taxi_corp_real_auth_client.server.app
    await app.phones.refresh_cache()

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi_corp.clients.protocol.ProtocolClient.geosearch')
    async def _geosearch(*args, **kwargs):
        return [
            {
                'short_text': 'short text',
                'short_text_from': 'short text from',
                'short_text_to': 'short text to',
            },
        ]

    @patch('taxi.clients.integration_api.IntegrationAPIClient.profile')
    async def _order_profile(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'user_id': 'user_id'}, headers={},
        )

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_draft')
    async def _order_draft(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'orderid': 'SomeOrderId'}, headers={},
        )

    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch(
        'taxi_corp.clients.corp_integration_api.'
        'CorpIntegrationApiClient.corp_paymentmethods',
    )
    async def _corp_paymentmethods(*args, **kwargs):
        return {
            'methods': [
                {
                    'id': 'corp-{}'.format(client_id),
                    'can_order': True,
                    'zone_available': True,
                },
            ],
        }

    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_estimate')
    async def _order_estimate(*args, **kwargs):
        return integration_api.APIResponse(
            status=200, data={'offer': 'offer_id'}, headers={},
        )

    department_id = None
    yandex_uid = passport_mock + '_uid'
    for access_data in load_json('mock_access_data.json'):
        if access_data['yandex_uid'] == yandex_uid:
            department_id = access_data['department_id']

    dept_usercount = (
        await db.corp_departments.find_one({'_id': department_id})
    )['counters']['users']

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/order'.format(client_id),
        json=post_content,
        headers={'X-Real-IP': '127.0.0.1', 'User-Agent': ''},
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    upd_dept_usercount = (
        await db.corp_departments.find_one({'_id': department_id})
    )['counters']['users']

    assert upd_dept_usercount == dept_usercount + 1
    assert len(_put.calls) == 1


@pytest.mark.parametrize(
    'passport_mock, user_id',
    [('client1', 'user1'), ('client1', 'user3')],  # nested depts
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_delete_user(
        taxi_corp_real_auth_client,
        pd_patch,
        db,
        passport_mock,
        user_id,
        patch,
):
    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _get_account(*args, **kwargs):
        return None

    # get counters before delete user
    user = await db.corp_users.find_one({'_id': user_id})

    role_id = user['role']['role_id']
    old_role_usercount = (await db.corp_roles.find_one({'_id': role_id}))[
        'counters'
    ]['users']

    dept_id = user['department_id']
    old_dept_usercount = (
        await db.corp_departments.find_one({'_id': dept_id})
    )['counters']['users']
    ancestors = (
        await db.corp_departments.find_one({'_id': user['department_id']})
    )['ancestors']
    anc_counter = {}
    for anc_id in ancestors:
        anc_counter[anc_id] = (
            (await db.corp_departments.find_one({'_id': anc_id}))
            .get('counters', {})
            .get('users', 0)
        )

    # delete user
    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/client1/user/{}'.format(user_id),
    )

    assert response.status == 200

    # check all counters decreased by 1
    role = await db.corp_roles.find_one({'_id': role_id})
    limit = await db.corp_limits.find_one(
        {'role_id': role_id, 'service': 'taxi'},
    )
    assert role['counters']['users'] == old_role_usercount - 1
    assert role['counters']['users'] == limit['counters']['users']

    role = await db.corp_departments.find_one({'_id': dept_id})
    assert role['counters']['users'] == old_dept_usercount - 1

    for anc_id in ancestors:
        updated_anc = await db.corp_departments.find_one({'_id': anc_id})
        assert updated_anc['counters']['users'] == anc_counter[anc_id] - 1


@pytest.mark.parametrize(
    'client_id, phone_id, patch_content',
    [
        (
            'client1',
            'AAAAAAAAAAAAA79291112201',
            {
                'phone': '+79291112201',
                'role': {'role_id': 'role2'},
                'is_active': True,
                'fullname': 'Zoe',
                'email': 'test@email.com',
                'nickname': 'ZoeTheCoolest',
                'cost_center': 'ZoeCostCenter',
                'department_id': 'd2',
            },
        ),
        # from nested departments to plain dept
        (
            'client1',
            'AAAAAAAAAAAAA79291112204',
            {
                'phone': '+79291112204',
                'role': {'role_id': 'role2'},
                'is_active': True,
                'fullname': 'Eoe',
                'email': 'doe@mail.com',
                'nickname': 'Eoe',
                'cost_center': 'EoeCenter',
                'department_id': 'd2',
            },
        ),
        # from  plain dept to nested one
        (
            'client1',
            'AAAAAAAAAAAAA79291112202',
            {
                'phone': '+79291112202',
                'role': {'role_id': 'role1_1_1'},
                'is_active': True,
                'fullname': 'Zoe',
                'email': 'test@email.com',
                'nickname': 'ZoeTheCoolest',
                'cost_center': 'ZoeCostCenter',
                'department_id': 'd1_1_1',
            },
        ),
    ],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_modify_user_via_patch(
        taxi_corp_auth_client,
        pd_patch,
        db,
        patch,
        client_id,
        phone_id,
        patch_content,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _get_account(*args, **kwargs):
        return None

    old_user = await db.corp_users.find_one({'phone_id': phone_id})
    if old_user:
        old_role_id = old_user['role']['role_id']
        old_role_usercount_before_upd = (
            await db.corp_roles.find_one({'_id': old_role_id})
        )['counters']['users']

    if old_user:
        old_dept_id = old_user['department_id']
        old_dept_usercount_before_upd = (
            await db.corp_departments.find_one({'_id': old_dept_id})
        )['counters']['users']

        old_ancestors = (
            await db.corp_departments.find_one({'_id': old_dept_id})
        )['ancestors']
        old_anc_counter = {}
        for anc_id in old_ancestors:
            old_anc_counter[anc_id] = (
                (await db.corp_departments.find_one({'_id': anc_id}))
                .get('counters', {})
                .get('users', 0)
            )

    new_dept_id = patch_content['department_id']
    new_ancestors = (await db.corp_departments.find_one({'_id': new_dept_id}))[
        'ancestors'
    ]
    new_anc_counter = {}
    for anc_id in new_ancestors:
        new_anc_counter[anc_id] = (
            (await db.corp_departments.find_one({'_id': anc_id}))
            .get('counters', {})
            .get('users', 0)
        )

    new_role_usercount_before_upd = (
        await db.corp_roles.find_one({'_id': patch_content['role']['role_id']})
    )['counters']['users']

    new_dept_usercount_before_upd = (
        await db.corp_departments.find_one({'_id': new_dept_id})
    )['counters']['users']

    # update user == change role and dept
    response = await taxi_corp_auth_client.patch(
        '/1.0/client/{}/user'.format(client_id), json=patch_content,
    )
    response_json = await response.json()

    assert response.status == 200

    patched_user = await db.corp_users.find_one({'_id': response_json['_id']})

    if old_user:
        old_role = await db.corp_roles.find_one({'_id': old_role_id})
        old_limit = await db.corp_limits.find_one(
            {'role_id': old_role_id, 'service': 'taxi'},
        )
        assert old_role['counters']['users'] == (
            old_role_usercount_before_upd - 1
        )
        assert old_role['counters']['users'] == old_limit['counters']['users']

    new_role = await db.corp_roles.find_one(
        {'_id': patched_user['role']['role_id']},
    )
    new_limit = await db.corp_limits.find_one(
        {'role_id': patch_content['role']['role_id'], 'service': 'taxi'},
    )
    assert new_role['counters']['users'] == new_role_usercount_before_upd + 1
    assert new_role['counters']['users'] == new_limit['counters']['users']

    if old_user:
        old_dept = await db.corp_departments.find_one({'_id': old_dept_id})
        assert old_dept['counters']['users'] == (
            old_dept_usercount_before_upd - 1
        )

    new_dept = await db.corp_departments.find_one(
        {'_id': patched_user['department_id']},
    )
    assert new_dept['counters']['users'] == new_dept_usercount_before_upd + 1

    if old_user:
        for anc_id in old_ancestors:
            updated_anc = await db.corp_departments.find_one({'_id': anc_id})
            assert updated_anc['counters']['users'] == (
                old_anc_counter[anc_id] - 1
            )

    for anc_id in new_ancestors:
        updated_anc = await db.corp_departments.find_one({'_id': anc_id})
        assert updated_anc['counters']['users'] == new_anc_counter[anc_id] + 1


@pytest.mark.parametrize(
    'client_id, user_id, put_content',
    [
        (
            'client1',
            'user1',
            {
                'fullname': 'Joe',
                'phone': '+79291112201',
                'role': {'role_id': 'role2'},
                'email': 'joe@mail.com',
                'is_active': True,
                'department_id': 'd2',
            },
        ),
    ],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_modify_user_via_put(
        taxi_corp_auth_client,
        pd_patch,
        db,
        patch,
        client_id,
        user_id,
        put_content,
):
    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _get_account(*args, **kwargs):
        return None

    old_user = await db.corp_users.find_one({'_id': user_id})
    old_role_id = old_user['role']['role_id']
    old_role_usercount_before_upd = (
        await db.corp_roles.find_one({'_id': old_role_id})
    )['counters']['users']
    new_role_usercount_before_upd = (
        await db.corp_roles.find_one({'_id': put_content['role']['role_id']})
    )['counters']['users']

    old_dept_id = old_user['department_id']
    old_dept_usercount_before_upd = (
        await db.corp_departments.find_one({'_id': old_dept_id})
    )['counters']['users']
    new_dept_usercount_before_upd = (
        await db.corp_departments.find_one(
            {'_id': put_content['department_id']},
        )
    )['counters']['users']

    # update user == change role and dept
    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/user/{}'.format(client_id, user_id), json=put_content,
    )
    assert response.status == 200

    modified_user = await db.corp_users.find_one({'_id': user_id})

    old_role = await db.corp_roles.find_one({'_id': old_role_id})
    old_limit = await db.corp_limits.find_one(
        {'role_id': old_role_id, 'service': 'taxi'},
    )
    assert old_role['counters']['users'] == old_role_usercount_before_upd - 1
    assert old_role['counters']['users'] == old_limit['counters']['users']

    new_role = await db.corp_roles.find_one(
        {'_id': modified_user['role']['role_id']},
    )
    new_limit = await db.corp_limits.find_one(
        {'role_id': modified_user['role']['role_id'], 'service': 'taxi'},
    )
    assert new_role['counters']['users'] == new_role_usercount_before_upd + 1
    assert new_role['counters']['users'] == new_limit['counters']['users']

    old_dept = await db.corp_departments.find_one({'_id': old_dept_id})
    assert old_dept['counters']['users'] == old_dept_usercount_before_upd - 1

    new_dept = await db.corp_departments.find_one(
        {'_id': modified_user['department_id']},
    )
    assert new_dept['counters']['users'] == new_dept_usercount_before_upd + 1


@pytest.mark.parametrize(
    'passport_mock, role_id, put_content',
    [
        (
            'client1',
            'role_many_users',
            {
                'name': 'managers',
                'limit': 9000,
                'classes': ['econom', 'non-existing'],
                'department_id': 'd1_1',
            },
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_modify_role_via_put(
        patch, taxi_corp_auth_client, db, passport_mock, role_id, put_content,
):
    old_role = await db.corp_roles.find_one({'_id': role_id})
    role_usercount = old_role['counters']['users']

    # get usercount of original dept and it's parent dept
    old_dept_id = old_role['department_id']
    old_dept = await db.corp_departments.find_one({'_id': old_dept_id})
    old_dept_usercount = old_dept['counters']['users']

    old_parent_id = old_dept['parent_id']
    old_parent = await db.corp_departments.find_one({'_id': old_parent_id})
    old_parent_usercount = old_parent['counters']['users']

    new_dept_id = put_content['department_id']
    new_dept = await db.corp_departments.find_one({'_id': new_dept_id})
    new_dept_usercount = new_dept['counters']['users']

    new_parent_id = new_dept['parent_id']
    new_parent = await db.corp_departments.find_one({'_id': new_parent_id})
    new_parent_usercount = new_parent['counters']['users']

    # send modifying response
    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/role/{}'.format(passport_mock, role_id),
        json=put_content,
    )
    response_json = await response.json()

    assert response.status == 200, 'Response is %s' % response_json

    # get usercount of mofidied dept and it's modified parent dept
    upd_old_dept = await db.corp_departments.find_one({'_id': old_dept_id})
    upd_old_dept_usercount = upd_old_dept['counters']['users']

    upd_old_parent = await db.corp_departments.find_one({'_id': old_parent_id})
    upd_old_parent_usercount = upd_old_parent['counters']['users']

    upd_new_dept = await db.corp_departments.find_one({'_id': new_dept_id})
    upd_new_dept_usercount = upd_new_dept['counters']['users']

    upd_new_parent = await db.corp_departments.find_one({'_id': new_parent_id})
    upd_new_parent_usercount = upd_new_parent['counters']['users']

    assert upd_old_dept_usercount == old_dept_usercount - role_usercount
    assert upd_old_parent_usercount == old_parent_usercount - role_usercount
    assert upd_new_dept_usercount == new_dept_usercount + role_usercount
    assert upd_new_parent_usercount == new_parent_usercount + role_usercount


@pytest.mark.parametrize(
    'client_id, role_id', [('client1', 'role_many_users')],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True)
async def test_delete_role(
        patch, taxi_corp_auth_client, db, client_id, role_id,
):
    role = await db.corp_roles.find_one({'_id': role_id})

    # get usercount of original dept and it's parent dept
    dept_id = role['department_id']
    dept = await db.corp_departments.find_one({'_id': dept_id})
    dept_usercount = dept['counters']['users']

    parent_id = dept['parent_id']
    parent = await db.corp_departments.find_one({'_id': parent_id})
    parent_usercount = parent['counters']['users']

    # send deleting response
    response = await taxi_corp_auth_client.delete(
        '/1.0/client/{}/role/{}'.format(client_id, role_id),
    )
    response_json = await response.json()
    assert response.status == 200, 'Response is %s' % response_json

    # get usercount of mofidied dept and it's modified parent dept
    upd_dept = await db.corp_departments.find_one({'_id': dept_id})
    upd_dept_usercount = upd_dept['counters']['users']

    upd_parent = await db.corp_departments.find_one({'_id': parent_id})
    upd_parent_usercount = upd_parent['counters']['users']

    assert upd_dept_usercount == dept_usercount
    assert upd_parent_usercount == parent_usercount


@pytest.mark.parametrize(
    'passport_mock, user_id, put_content',
    [
        pytest.param(
            'client1',
            'to_restore',
            {'department_id': 'd1_1_1', 'role': {'role_id': 'role1_1_1'}},
            id='restore_user',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(
    CORP_COUNTERS_ENABLED=True,
    CORP_USER_PHONES_SUPPORTED=[
        {
            'min_length': 11,
            'max_length': 11,
            'prefixes': ['+7'],
            'matches': ['^7'],
        },
    ],
)
async def test_restore_user(
        taxi_corp_real_auth_client,
        pd_patch,
        db,
        patch,
        patch_doc,
        put_content,
        passport_mock,
        user_id,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi_corp.api.common.drive.DriveAccountManager.get_account')
    async def _get_account(*args, **kwargs):
        return None

    base_content = {
        'fullname': 'Joe',
        'phone': '+79291112299',
        'email': 'joe@mail.com',
        'is_active': True,
    }
    # get counters restoring create user
    dept_id = put_content.get('department_id')

    if dept_id:
        dept_usercount = (
            await db.corp_departments.find_one({'_id': dept_id})
        )['counters']['users']

        ancestors = (await db.corp_departments.find_one({'_id': dept_id}))[
            'ancestors'
        ]
        anc_counter = {}
        for anc_id in ancestors:
            anc_counter[anc_id] = (
                (await db.corp_departments.find_one({'_id': anc_id}))
                .get('counters', {})
                .get('users', 0)
            )

    role_id = put_content['role'].get('role_id')

    role_usercount = (
        role_id
        and (await db.corp_roles.find_one({'_id': role_id}))['counters'][
            'users'
        ]
    )

    # restore user
    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/user/{}/restore'.format(passport_mock, user_id),
        json=patch_doc(base_content, put_content),
    )

    assert response.status == 200

    # check all counters increased by 1
    if role_id:
        role = await db.corp_roles.find_one({'_id': role_id})
        limit = await db.corp_limits.find_one(
            {'role_id': role_id, 'service': 'taxi'},
        )
        assert role['counters']['users'] == role_usercount + 1
        assert role['counters']['users'] == limit['counters']['users']

    if dept_id:
        dept = await db.corp_departments.find_one({'_id': dept_id})
        assert dept['counters']['users'] == dept_usercount + 1

        for anc_id in ancestors:
            updated_anc = await db.corp_departments.find_one({'_id': anc_id})
            assert updated_anc['counters']['users'] == anc_counter[anc_id] + 1
