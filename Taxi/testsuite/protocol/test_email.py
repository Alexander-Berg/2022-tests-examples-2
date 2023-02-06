import json

import pytest

from protocol import brands
from user_api_switch_parametrize import PROTOCOL_SWITCH_TO_USER_API


class PersonalContext(object):
    def __init__(self, store_func, retrieve_func):
        self.store_func = store_func
        self.retrieve_func = retrieve_func

    @property
    def store_times_called(self):
        return self.store_func.times_called

    @property
    def retrieve_times_called(self):
        return self.retrieve_func.times_called


@pytest.fixture
def dummy_personal(mockserver):
    @mockserver.json_handler('/personal/v1/emails/store')
    def mock_emails_store(request):
        value = json.loads(request.get_data())['value']
        return {'id': 'personal_' + value, 'value': value}

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def mock_emails_retrieve(request):
        personal_id = json.loads(request.get_data())['id']
        assert personal_id.startswith('personal_')
        return {'id': personal_id, 'value': personal_id[9:]}

    return PersonalContext(mock_emails_store, mock_emails_retrieve)


def check_personal_user_email(db, user_id, brand_name, email):
    user = db.users.find_one({'_id': user_id})
    user_email = db.user_emails.find_one(
        {'phone_id': user['phone_id'], 'brand_name': brand_name},
    )
    assert user_email is not None
    assert user_email['email'] == email
    assert user_email['email_domain'] == email[email.find('@') + 1 :]
    assert user_email['personal_email_id'] == 'personal_' + email
    return (user, user_email)


@PROTOCOL_SWITCH_TO_USER_API
@pytest.mark.parametrize(
    'user_id, phone_id, yandex_uid',
    [
        ('abcd0000000000000000000000000001', '558af6684794b3f8d9c00001', None),
        (
            'abcd0000000000000000000000000002',
            '558af6684794b3f8d9c00002',
            '4003500002',
        ),
        (
            'abcd0000000000000000000000000003',
            '558af6684794b3f8d9c00003',
            '4003500003',
        ),
    ],
)
@pytest.mark.parametrize('send_major_version', [True, False])
def test_set_email_request(
        taxi_protocol,
        mockserver,
        user_id,
        phone_id,
        yandex_uid,
        send_major_version,
        user_api_switch_on,
        config,
        mock_stq_agent,
):
    @mockserver.json_handler('/user-api/user_emails/set')
    def mock_user_api_user_emails_set(request):
        expected_request = {
            'phone_id': phone_id,
            'email': 'test@mail.org',
            'brand_name': 'yango',
        }
        if yandex_uid is not None:
            expected_request['yandex_uid'] = yandex_uid
        assert request.json == expected_request

        return {
            'id': '1587d1254794b3f8d9cb87a5',
            'phone_id': phone_id,
            'yandex_uid': yandex_uid,
            'personal_email_id': 'test_personal_email_id',
            'confirmed': False,
            'confirmation_code': 'test_confirmation_code',
            'updated': '2019-11-25T18:18:18Z',
            'created': '2019-11-25T18:18:18Z',
        }

    @mockserver.json_handler('/user-api/users/get')
    def mock_user_api_user_get(request):
        assert request.json == {
            'id': user_id,
            'lookup_uber': False,
            'primary_replica': False,
        }
        resp = {
            'id': user_id,
            'authorized': True,
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
            'phone_id': phone_id,
        }
        if yandex_uid is not None:
            resp['yandex_uid'] = yandex_uid
            resp['yandex_uid_type'] = (
                'phonish' if yandex_uid == '4003500002' else 'portal'
            )

        return resp

    config.set(YANDEX_GO_USE_MAJOR_VERSION_AT_SET_EMAIL=send_major_version)
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/email',
        {'id': user_id, 'action': 'set', 'email': 'test@mail.org'},
        headers=brands.yango.android.headers,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'confirmation_sent'}

    assert mock_user_api_user_emails_set.times_called == 1

    task = mock_stq_agent.get_tasks('send_confirmation_email')
    sent_application = (
        'yango_android:3' if send_major_version else 'yango_android'
    )

    assert task[0].args == [
        {'$oid': '1587d1254794b3f8d9cb87a5'},
        sent_application,
        'en',
    ]
    if user_api_switch_on:
        assert mock_user_api_user_get.times_called == 1
    else:
        assert mock_user_api_user_get.times_called == 0


@pytest.mark.parametrize(
    'user_id, user_api_request, confirmed',
    [
        (
            'abcd0000000000000000000000000001',
            {'phone_ids': ['558af6684794b3f8d9c00001']},
            False,
        ),
        (
            'abcd0000000000000000000000000002',
            {'yandex_uids': ['4003500002']},
            True,
        ),
        (
            'abcd0000000000000000000000000003',
            {'yandex_uids': ['4003500003']},
            False,
        ),
    ],
)
def test_get_email_request(
        taxi_protocol, mockserver, user_id, user_api_request, confirmed,
):
    @mockserver.json_handler('/user-api/user_emails/get')
    def mock_user_api_user_emails_get(request):
        expected_request = {
            'brand_name': 'yango',
            'fields': [
                'yandex_uid',
                'personal_email_id',
                'confirmed',
                'confirmation_code',
            ],
            'primary_replica': True,
        }
        expected_request.update(user_api_request)
        assert request.json == expected_request
        return {
            'items': [
                {
                    'personal_email_id': 'test_personal_email_id',
                    'confirmed': confirmed,
                    'confirmation_code': 'test_confirmation_code',
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def mock_personal_emails_retrieve(request):
        personal_email_id = json.loads(request.get_data())['id']
        assert personal_email_id == 'test_personal_email_id'
        return {'id': personal_email_id, 'value': 'test@mail.org'}

    response = taxi_protocol.post(
        '3.0/email',
        {'id': user_id, 'action': 'get'},
        headers=brands.yango.android.headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'email': 'test@mail.org',
        'status': 'ok' if confirmed else 'not_confirmed',
    }

    assert mock_user_api_user_emails_get.times_called == 1
    assert mock_personal_emails_retrieve.times_called == 1


def test_get_email_request_not_found(taxi_protocol, mockserver):
    @mockserver.json_handler('/user-api/user_emails/get')
    def mock_user_api_user_emails_get(request):
        return {'items': []}

    response = taxi_protocol.post(
        '3.0/email',
        {'id': 'abcd0000000000000000000000000001', 'action': 'get'},
        headers=brands.yango.android.headers,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'user_id, confirmation_code, user_api_request',
    [
        (
            'abcd0000000000000000000000000001',
            None,
            {'phone_id': '558af6684794b3f8d9c00001'},
        ),
        (
            'abcd0000000000000000000000000002',
            None,
            {'yandex_uids': ['4003500002']},
        ),
        (
            'abcd0000000000000000000000000003',
            None,
            {'yandex_uids': ['4003500003']},
        ),
        (
            None,
            'test_confirmation_code',
            {'confirmation_code': 'test_confirmation_code'},
        ),
    ],
)
def test_unset_email_request(
        taxi_protocol,
        mockserver,
        user_id,
        confirmation_code,
        user_api_request,
):
    @mockserver.json_handler('/user-api/user_emails/remove')
    def mock_user_api_user_emails_remove(request):
        expected_request = {}
        if confirmation_code is None:
            expected_request.update({'brand_name': 'yango'})
        expected_request.update(user_api_request)
        assert request.json == expected_request

    request_data = {'action': 'unset'}
    if user_id is not None:
        request_data['id'] = user_id
    if confirmation_code is not None:
        request_data['confirmation_code'] = confirmation_code

    response = taxi_protocol.post(
        '3.0/email', request_data, headers=brands.yango.android.headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}

    assert mock_user_api_user_emails_remove.times_called == 1


def test_unset_email_request_not_found(taxi_protocol, mockserver):
    @mockserver.json_handler('/user-api/user_emails/remove')
    def mock_user_api_user_emails_remove(request):
        return mockserver.make_response(status=404)

    response = taxi_protocol.post(
        '3.0/email',
        {'id': 'abcd0000000000000000000000000001', 'action': 'unset'},
        headers=brands.yango.android.headers,
    )
    assert response.status_code == 404


def test_confirm_email_request(taxi_protocol, mockserver):
    @mockserver.json_handler('/user-api/user_emails/confirm')
    def mock_user_api_user_emails_confirm(request):
        assert request.json == {
            'personal_email_id': 'test_personal_email_id',
            'confirmation_code': 'test_confirmation_code',
        }

    @mockserver.json_handler('/personal/v1/emails/store')
    def mock_personal_emails_store(request):
        assert json.loads(request.get_data())['value'] == 'test@mail.org'
        return {'id': 'test_personal_email_id', 'value': 'test@mail.org'}

    response = taxi_protocol.post(
        '3.0/email',
        {
            'email': 'test@mail.org',
            'confirmation_code': 'test_confirmation_code',
            'action': 'confirm',
        },
        headers=brands.yango.android.headers,
    )
    assert response.status_code == 200

    assert mock_user_api_user_emails_confirm.times_called == 1
    assert mock_personal_emails_store.times_called == 1


def test_confirm_email_request_not_found(taxi_protocol, mockserver):
    @mockserver.json_handler('/user-api/user_emails/confirm')
    def mock_user_api_user_emails_confirm(request):
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/personal/v1/emails/store')
    def mock_personal_emails_store(request):
        assert json.loads(request.get_data())['value'] == 'test@mail.org'
        return {'id': 'test_personal_email_id', 'value': 'test@mail.org'}

    response = taxi_protocol.post(
        '3.0/email',
        {
            'email': 'test@mail.org',
            'confirmation_code': 'test_confirmation_code',
            'action': 'confirm',
        },
        headers=brands.yango.android.headers,
    )
    assert response.status_code == 406


@pytest.mark.parametrize(
    'user_id, action', [('ab1d0000000000000000000000000111', 'get')],
)
@pytest.mark.config(PERSONAL_EMAILS_RETRIEVE_CPP_ENABLED=True)
def test_get_email_not_exist(user_id, action, taxi_protocol, dummy_personal):
    response = taxi_protocol.post(
        '3.0/email', {'id': user_id, 'action': action},
    )
    assert response.status_code == 401
    data = response.json()
    assert data['error']['text'] == 'Authorized user not found'
    assert dummy_personal.store_times_called == 0
    assert dummy_personal.retrieve_times_called == 0


@pytest.mark.parametrize(
    'user_id, action', [('ab1d0000000000000000000000000012', 'get')],
)
@pytest.mark.config(PERSONAL_EMAILS_RETRIEVE_CPP_ENABLED=True)
def test_get_email_no_authorized(
        user_id, action, taxi_protocol, dummy_personal,
):
    response = taxi_protocol.post(
        '3.0/email', {'id': user_id, 'action': action},
    )
    assert response.status_code == 401
    data = response.json()
    assert data['error']['text'] == 'User not authorized'
    assert dummy_personal.store_times_called == 0
    assert dummy_personal.retrieve_times_called == 0


@pytest.mark.parametrize(
    'user_id, confirmation_code, email',
    [
        (
            'ab1d0000000000000000000000000000',
            'f35c2b0f6ae027aaf7e3f3be0165ed4f14a228' '12b46e6f9452b6dcd2',
            'mknaumenko@yandex-team.ru',
        ),
    ],
)
@pytest.mark.config(PERSONAL_EMAILS_RETRIEVE_CPP_ENABLED=True)
def test_bad_request(
        user_id, confirmation_code, email, taxi_protocol, dummy_personal,
):
    response = taxi_protocol.post(
        '3.0/email', {'action': 'get'}, bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email', {'action': 'set'}, bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email', {'action': 'set', 'email': email}, bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email', {'action': 'set', 'id': user_id}, bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email',
        {
            'action': 'unset',
            'id': user_id,
            'confirmation_code': confirmation_code,
        },
        bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email', {'action': 'unset'}, bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email',
        {'action': 'confirm', 'email': email},
        bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email',
        {'action': 'confirm', 'confirmation_code': confirmation_code},
        bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email', {'action': 'confirm'}, bearer='test_token',
    )
    assert response.status_code == 400
    response = taxi_protocol.post(
        '3.0/email',
        {
            'action': 'confirm',
            'confirmation_code': confirmation_code,
            'email': 'fdsfsf@treter.111',
        },
        bearer='test_token',
    )
    assert response.status_code == 400
