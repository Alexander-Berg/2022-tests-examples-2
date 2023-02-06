# pylint: disable=redefined-outer-name
import datetime

import pytest


@pytest.fixture
def passport_mock(patch):
    data = {
        'emily': 'emily_uid',
        'bill': 'bill_uid',
        'john': 'john_uid',
        'boris': 'boris_uid',
        'jeffrey': 'jeffrey_uid',
        'innokentiy': 'existing_uid',
    }
    from taxi.clients import passport

    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):

        if kwargs['login'] in data:
            return {'uid': data[kwargs['login']]}
        raise passport.InvalidLoginError()


@pytest.fixture
def personal_mock(patch):
    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}


@pytest.mark.parametrize(
    ['client_id', 'url_args', 'expected_result', 'expected_find_pd_calls'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {},
            {
                'amount': 3,
                'sorting_direction': 1,
                'limit': 100,
                'skip': 0,
                'sorting_field': 'fullname',
                'items': [
                    {
                        'id': '2bc4124acc5341019d6821d5fc1beab0',
                        'fullname': 'Bill',
                        'yandex_login': 'bill',
                        'phone': '+79291112202',
                    },
                    {
                        'id': '710979d98be74a3a82732adc7483a8a2',
                        'fullname': 'Emily',
                        'yandex_login': 'emily',
                        'phone': '+79291112201',
                    },
                    {
                        'id': '95a4304486854d7dbf46037e38aca369',
                        'fullname': 'John',
                        'yandex_login': 'john',
                    },
                ],
            },
            5,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'sorting_direction': '-1', 'limit': '1', 'skip': '1'},
            {
                'amount': 3,
                'sorting_direction': -1,
                'limit': 1,
                'skip': 1,
                'sorting_field': 'fullname',
                'items': [
                    {
                        'id': '710979d98be74a3a82732adc7483a8a2',
                        'fullname': 'Emily',
                        'yandex_login': 'emily',
                        'phone': '+79291112201',
                    },
                ],
            },
            2,
        ),
    ],
)
async def test_general_get(
        taxi_corp_admin_client,
        patch,
        client_id,
        url_args,
        expected_result,
        expected_find_pd_calls,
):
    @patch('taxi_corp_admin.util.personal_data.find_pd_by_condition')
    async def _mock_find_pd(app, item, field, *args, **kwargs):
        return item[field]

    response = await taxi_corp_admin_client.get(
        '/v1/clients/{}/managers'.format(client_id), params=url_args,
    )

    assert response.status == 200
    assert await response.json() == expected_result

    assert len(_mock_find_pd.calls) == expected_find_pd_calls


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected_result'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Jeffrey',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
            {
                'fullname': 'Jeffrey',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
                'yandex_uid': 'jeffrey_uid',
                'role': 'manager',
            },
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'fullname': 'Jeffrey', 'yandex_login': 'jeffrey'},
            {
                'fullname': 'Jeffrey',
                'yandex_login': 'jeffrey',
                'yandex_uid': 'jeffrey_uid',
                'role': 'manager',
            },
        ),
    ],
)
async def test_general_post(
        patch,
        taxi_corp_admin_client,
        db,
        personal_mock,
        client_id,
        post_content,
        expected_result,
        passport_mock,
):

    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )

    assert response.status == 200
    response_json = await response.json()

    db_item = await db.corp_managers.find_one({'_id': response_json['id']})
    for key, value in expected_result.items():
        assert db_item[key] == value

    acl_item = await db.corp_acl_common.find_one(
        {'yandex_uid': expected_result['yandex_uid']},
    )
    assert acl_item['role'] == 'manager'


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'response_code'],
    [
        # this manager already exists
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': '  Billy  ',
                'yandex_login': '  bill  ',
                'phone': ' +79291112202 ',
            },
            406,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Chloe',
                'yandex_login': 'chloe',
                'phone': 79291112202,
            },
            400,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Billy',
                'yandex_login': 'bill',
                'phone': '+79291112202',
                'excess_field': 'value',
            },
            400,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Anonymous',
                'yandex_login': 'anonymous',
                'phone': '+79291112202',
            },
            400,
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.duplicate_manager_login_error_code': {'ru': 'duplicate login'},
    },
)
async def test_general_post_fail(
        taxi_corp_admin_client,
        personal_mock,
        client_id,
        post_content,
        response_code,
        passport_mock,
):
    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )
    response_json = await response.json()
    assert response.status == response_code, response_json


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected_result', 'response_code'],
    [
        # this id already corresponds to an existing role
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Innokentiy',
                'yandex_login': 'innokentiy',
                'phone': '+79291112205',
            },
            {'yandex_uid': 'existing_uid'},
            400,
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.duplicate_manager_login_error_code': {'ru': 'duplicate login'},
    },
)
async def test_no_records_if_role_exists(
        taxi_corp_admin_client,
        db,
        personal_mock,
        passport_mock,
        client_id,
        post_content,
        response_code,
        expected_result,
):
    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )
    response_json = await response.json()
    assert response.status == response_code, response_json

    db_item = await db.corp_managers.find_one(
        {'fullname': post_content['fullname']},
    )
    assert db_item is None

    acl_item = await db.corp_acl_common.find_one(
        {'yandex_uid': expected_result['yandex_uid']},
    )
    assert acl_item['role'] != 'manager'


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected_result', 'response_code'],
    [
        # this manager already exists
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Emily',
                'yandex_login': 'emily',
                'phone': '+79291112201',
            },
            {'yandex_uid': 'emily_uid'},
            406,
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.duplicate_manager_login_error_code': {'ru': 'duplicate login'},
    },
)
async def test_no_records_if_mang_exists(
        taxi_corp_admin_client,
        db,
        personal_mock,
        passport_mock,
        client_id,
        post_content,
        response_code,
        expected_result,
):
    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )
    response_json = await response.json()
    assert response.status == response_code, response_json

    db_item = await db.corp_managers.find_one(
        {'fullname': post_content['fullname']},
    )
    assert db_item

    acl_item = await db.corp_acl_common.find_one(
        {'yandex_uid': expected_result['yandex_uid']},
    )
    assert acl_item is None


@pytest.mark.parametrize(
    ['client_id', 'post_content'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Jeffrey',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
        ),
    ],
)
async def test_general_time_fields_post(
        taxi_corp_admin_client,
        db,
        personal_mock,
        passport_mock,
        client_id,
        post_content,
):
    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )
    assert response.status == 200
    response_json = await response.json()

    db_item = await db.corp_managers.find_one({'_id': response_json['id']})
    assert 'created' in db_item and 'updated' in db_item
    assert isinstance(db_item['created'], datetime.datetime)
    assert isinstance(db_item['updated'], datetime.datetime)


@pytest.mark.parametrize(
    ['client_id', 'manager_id', 'expected_result'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'id': '2bc4124acc5341019d6821d5fc1beab0',
                'fullname': 'Bill',
                'yandex_login': 'bill',
                'phone': '+79291112202',
            },
        ),
    ],
)
async def test_single_get(
        taxi_corp_admin_client, patch, client_id, manager_id, expected_result,
):
    @patch('taxi_corp_admin.util.personal_data.find_pd_by_condition')
    async def _mock_find_pd(app, item, field, *args, **kwargs):
        return item[field]

    response = await taxi_corp_admin_client.get(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
    )

    assert response.status == 200
    assert await response.json() == expected_result
    assert len(_mock_find_pd.calls) == 2


@pytest.mark.parametrize(
    ['client_id', 'manager_id', 'response_code'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '04d78450765541979fee25430f75d59a',
            404,
        ),
        (
            'c95ea8013cab47fc8ba1da87af1b2107',
            '2bc4124acc5341019d6821d5fc1beab0',
            404,
        ),
    ],
)
async def test_single_get_fail(
        taxi_corp_admin_client, client_id, manager_id, response_code,
):
    response = await taxi_corp_admin_client.get(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
    )
    response_json = await response.json()
    assert response.status == response_code, response_json


@pytest.mark.parametrize(
    ['client_id', 'manager_id'],
    [('7ff7900803534212a3a66f4d0e114fc2', '2bc4124acc5341019d6821d5fc1beab0')],
)
async def test_single_delete(
        taxi_corp_admin_client, db, client_id, manager_id,
):
    yandex_uid = await db.corp_managers.find_one({'_id': manager_id})

    response = await taxi_corp_admin_client.delete(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
    )

    assert response.status == 200
    assert (await db.corp_managers.find_one({'_id': manager_id})) is None
    assert (
        await db.corp_acl_common.find_one(
            {'role': 'manager', 'yandex_uid': yandex_uid},
        )
    ) is None


@pytest.mark.parametrize(
    ['client_id', 'manager_id'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '3c5c40a3cfc14447805e3c69f59aec2c',
        ),
        (
            'e5defdc1c4e54439b4b6fc40b5da46d8',
            '2bc4124acc5341019d6821d5fc1beab0',
        ),
    ],
)
async def test_single_delete_fail(
        taxi_corp_admin_client, client_id, manager_id,
):
    response = await taxi_corp_admin_client.delete(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
    )
    response_json = await response.json()
    assert response.status == 404, response_json


@pytest.mark.parametrize(
    ['post_content', 'expected_response'],
    [
        (
            {
                'managers': [
                    {'id': '62ac07f288a04f87bc044343928372f5'},
                    {'id': '95a4304486854d7dbf46037e38aca369'},
                ],
            },
            {'managers_deleted_count': 2},
        ),
        (
            {
                'managers': [
                    {'id': 'no such a manager'},
                    {'id': '95a4304486854d7dbf46037e38aca369'},
                ],
            },
            {'managers_deleted_count': 1},
        ),
        (
            {'managers': [{'id': 'no such a manager'}]},
            {'managers_deleted_count': 0},
        ),
    ],
)
async def test_bulk_remove(
        taxi_corp_admin_client, db, post_content, expected_response,
):
    # find acl roles in db
    managers_ids = [manager['id'] for manager in post_content['managers']]
    managers_query = {'_id': {'$in': managers_ids}}
    managers = await db.corp_managers.find(managers_query).to_list(None)
    ya_uids = [manager['yandex_uid'] for manager in managers]

    response = await taxi_corp_admin_client.post(
        '/v1/managers/bulk-remove', json=post_content,
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
    assert (await db.corp_managers.count(managers_query)) == 0
    assert (
        await db.corp_acl_common.count({'yandex_uid': {'$in': ya_uids}})
    ) == 0


@pytest.mark.parametrize(
    ['client_id', 'manager_id', 'put_content', 'expected_result'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {'fullname': 'Bill Jones', 'yandex_login': 'bill'},
            {
                'fullname': 'Bill Jones',
                'yandex_login': 'bill',
                'yandex_uid': 'bill_uid',
            },
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'fullname': 'Jeffrey Lebowski',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
            {
                'fullname': 'Jeffrey Lebowski',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
                'yandex_uid': 'jeffrey_uid',
            },
        ),
    ],
)
async def test_single_put(
        passport_mock,
        personal_mock,
        taxi_corp_admin_client,
        db,
        patch,
        client_id,
        manager_id,
        put_content,
        expected_result,
):
    @patch('taxi_corp_admin.util.personal_data.find_pd_by_condition')
    async def _mock_find_pd(app, item, field, *args, **kwargs):
        return item[field]

    response = await taxi_corp_admin_client.put(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
        json=put_content,
    )

    assert response.status == 200
    assert await response.json() == {}
    db_item = await db.corp_managers.find_one({'_id': manager_id})
    for key, value in expected_result.items():
        assert db_item[key] == value

    assert len(_mock_find_pd.calls) == 1


@pytest.mark.parametrize(
    ['client_id', 'manager_id', 'put_content', 'yandex_uid'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'fullname': 'Jeffrey Lebowski',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
            'jeffrey_uid',
        ),
    ],
)
async def test_acl_single_put(
        passport_mock,
        personal_mock,
        taxi_corp_admin_client,
        db,
        client_id,
        manager_id,
        put_content,
        yandex_uid,
):
    manager = await db.corp_managers.find_one({'_id': manager_id})
    old_uid = manager['yandex_uid']

    await taxi_corp_admin_client.put(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
        json=put_content,
    )

    manager = await db.corp_managers.find_one({'_id': manager_id})
    new_uid = manager['yandex_uid']

    old_acl_item = await db.corp_acl_common.find_one({'yandex_uid': old_uid})
    assert old_acl_item is None

    new_acl_item = await db.corp_acl_common.find_one({'yandex_uid': new_uid})
    assert new_acl_item['role'] == 'manager'


@pytest.mark.parametrize(
    ['client_id', 'manager_id', 'put_content', 'response_code'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'fullname': 'Billy',
                'yandex_login': 'emily',
                'phone': '+79291112202',
            },
            406,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'fullname': 'Chloe',
                'yandex_login': 'chloe',
                'phone': 79291112202,
            },
            400,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {'fullname': 'Chloe', 'yandex_login': 'chloe'},
            400,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'fullname': 'Billy',
                'yandex_login': 'bill',
                'phone': '+79291112202',
                'excess_field': 'value',
            },
            400,
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {
                'fullname': 'Anonymous',
                'yandex_login': 'anonymous',
                'phone': '+79291112202',
            },
            400,
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.duplicate_manager_login_error_code': {'ru': 'duplicate login'},
    },
)
async def test_single_put_fail(
        passport_mock,
        taxi_corp_admin_client,
        personal_mock,
        client_id,
        manager_id,
        put_content,
        response_code,
):
    response = await taxi_corp_admin_client.put(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
        json=put_content,
    )
    response_json = await response.json()
    assert response.status == response_code, response_json


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'put_content'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Jeffrey',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
            {
                'fullname': 'Jeffrey Lebowski',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
        ),
    ],
)
async def test_single_updated_field_put(
        taxi_corp_admin_client,
        db,
        personal_mock,
        passport_mock,
        client_id,
        post_content,
        put_content,
):
    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )
    assert response.status == 200
    response_json = await response.json()

    db_item = await db.corp_managers.find_one({'_id': response_json['id']})
    manager_id = db_item['_id']
    prev_created = db_item['created']
    prev_updated = db_item['updated']

    response = await taxi_corp_admin_client.put(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
        json=put_content,
    )
    assert response.status == 200
    assert await response.json() == {}
    fresh_item = await db.corp_managers.find_one({'_id': manager_id})
    assert fresh_item['created'] == prev_created
    assert fresh_item['updated'] > prev_updated
