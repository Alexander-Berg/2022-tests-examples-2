# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import personal


@pytest.fixture
def login_info_mock(patch):
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


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected_pd_calls', 'pd_doc_fields'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'fullname': 'Jeffrey',
                'yandex_login': 'jeffrey',
                'phone': '+79291112205',
            },
            {
                personal.PERSONAL_TYPE_YANDEX_LOGINS: 'jeffrey',
                personal.PERSONAL_TYPE_PHONES: '+79291112205',
            },
            ['yandex_login_id', 'phone_id'],
        ),
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            {'fullname': 'Jeffrey', 'yandex_login': 'jeffrey'},
            {personal.PERSONAL_TYPE_YANDEX_LOGINS: 'jeffrey'},
            ['yandex_login_id'],
        ),
    ],
)
async def test_personal_post(
        taxi_corp_admin_client,
        patch,
        db,
        login_info_mock,
        client_id,
        post_content,
        expected_pd_calls,
        pd_doc_fields,
):
    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    response = await taxi_corp_admin_client.post(
        '/v1/clients/{}/managers'.format(client_id), json=post_content,
    )

    assert response.status == 200
    response_json = await response.json()

    store_calls = {
        call['data_type']: call['request_value'] for call in _store.calls
    }

    assert store_calls == expected_pd_calls

    db_item = await db.corp_managers.find_one({'_id': response_json['id']})

    for expected_field in pd_doc_fields:
        assert expected_field in db_item


@pytest.mark.parametrize(
    [
        'client_id',
        'manager_id',
        'put_content',
        'expected_pd_calls',
        'pd_doc_fields',
    ],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            '2bc4124acc5341019d6821d5fc1beab0',
            {'fullname': 'Bill Jones', 'yandex_login': 'bill'},
            {personal.PERSONAL_TYPE_YANDEX_LOGINS: 'bill'},
            ['yandex_login_id'],
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
                personal.PERSONAL_TYPE_YANDEX_LOGINS: 'jeffrey',
                personal.PERSONAL_TYPE_PHONES: '+79291112205',
            },
            ['yandex_login_id', 'phone_id'],
        ),
    ],
)
async def test_single_put(
        login_info_mock,
        taxi_corp_admin_client,
        patch,
        db,
        client_id,
        manager_id,
        put_content,
        expected_pd_calls,
        pd_doc_fields,
):
    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    response = await taxi_corp_admin_client.put(
        '/v1/clients/{}/managers/{}'.format(client_id, manager_id),
        json=put_content,
    )

    assert response.status == 200
    assert await response.json() == {}

    store_calls = {
        call['data_type']: call['request_value'] for call in _store.calls
    }

    assert store_calls == expected_pd_calls

    db_item = await db.corp_managers.find_one({'_id': manager_id})

    for expected_field in pd_doc_fields:
        assert expected_field in db_item
