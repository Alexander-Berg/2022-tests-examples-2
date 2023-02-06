# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_authproxy_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.

import pytest
import aiohttp
import testsuite
from client_blackbox.mock_blackbox import make_phone

PHONE_NUMBER = '+71234567890'
PHONE_NUMBER_ID = 'phone_number_id'
STAFF_LOGIN = 'my_staff_login'
USER_TICKET = 'user_ticket'
BB_PHONES = [
    make_phone(PHONE_NUMBER, is_bank=True),
    make_phone('+70000000000'),
]

CONFIG = [
    {
        'input': {'http-path-prefix': '/'},
        'output': {
            'upstream': {'$mockserver': ''},
            'tvm-service': 'bank-authproxy',
        },
        'proxy': {'server-hosts': ['*']},
    },
    {
        'input': {'http-path-prefix': '/auth'},
        'output': {
            'upstream': {'$mockserver': ''},
            'tvm-service': 'bank-authproxy',
        },
        'proxy': {'only-passport-auth': True, 'server-hosts': ['*']},
    },
    {
        'input': {'http-path-prefix': '/unauth'},
        'output': {'upstream': {'$mockserver': ''}},
        'proxy': {'proxy-401': True, 'server-hosts': ['*']},
    },
    {
        'input': {'http-path-prefix': '/unauth/check_bank_auth'},
        'output': {
            'upstream': {'$mockserver': ''},
            'tvm-service': 'bank-authproxy',
        },
        'proxy': {
            'proxy-401': True,
            'only-passport-auth': False,
            'server-hosts': ['*'],
            'cookie-allow-list': ['allow_cookie'],
        },
    },
    {
        'input': {
            'http-path-prefix': '/domains_route',
            'domains': ['bank.yandex.ru'],
        },
        'output': {
            'upstream': {'$mockserver': '/bank.yandex.ru'},
            'tvm-service': 'bank-authproxy',
        },
        'proxy': {
            'proxy-401': True,
            'only-passport-auth': False,
            'server-hosts': ['*'],
        },
    },
    {
        'input': {
            'http-path-prefix': '/domains_route',
            'domains': ['fintech.yandex.ru'],
        },
        'output': {
            'upstream': {'$mockserver': '/fintech.yandex.ru'},
            'tvm-service': 'bank-authproxy',
        },
        'proxy': {
            'proxy-401': True,
            'only-passport-auth': False,
            'server-hosts': ['*'],
        },
    },
    {
        'input': {
            'http-path-prefix': '/several_domains_route',
            'domains': ['fintech.yandex.ru', 'bank.yandex.ru'],
        },
        'output': {
            'upstream': {'$mockserver': '/yandex.ru'},
            'tvm-service': 'bank-authproxy',
        },
        'proxy': {
            'proxy-401': True,
            'only-passport-auth': False,
            'server-hosts': ['*'],
        },
    },
]


def get_session_uuid_headers():
    return [
        {'X-YaBank-SessionUUID': '123'},
        {'Cookie': 'yabank-sessionuuid=123'},
    ]


SESSION_ALLOWED_STATUSES = {'items': ['ok']}


def get_default_headers_with_oauth(token, session_uuid=None):
    if session_uuid is None:
        session_uuid = {'X-YaBank-SessionUUID': '123'}
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/90.0.4430.212 '
            'YaBrowser/21.5.3.753 (beta) Yowser/2.5 Safari/537.36'
        ),
        'Accept-Language': 'en',
        'X-Remote-IP': '127.0.0.13',
        'Authorization': 'Bearer ' + token,
    }
    headers.update(session_uuid)
    return headers


# Proxying unauthorized requests is forbidden by default
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_request_no_authorization(taxi_bank_authproxy, mock_remote):
    backend = mock_remote('/abc')
    response = await taxi_bank_authproxy.get('/abc')
    assert not backend.has_calls
    assert response.status_code == 401


# Proxying unauthorized requests is allowed by config
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_request_no_authorization_ok(taxi_bank_authproxy, mock_remote):
    # all these headers must be removed befor proxying requests to the upstream
    internal_headers = {
        'X-YaBank-SessionStatus': 'ok',
        'X-YaBank-AuthorizedByAuthproxy': 'yes',
        'X-Yandex-BUID': '123',
        'X-Yandex-UID': '100',
        'X-YaBank-PhoneID': PHONE_NUMBER_ID,
        'X-YaTaxi-Pass-Flags': 'bank-account',
        'X-YaBank-Yandex-Team-Login': 'amatveyev',
        'X-Yandex-Auth-Status': 'VALID',
        'X-YaBank-ChannelType': 'WEB',
    }
    backend = mock_remote('/unauth')
    response = await taxi_bank_authproxy.get(
        '/unauth', headers=internal_headers,
    )
    assert backend.has_calls
    assert response.status_code == 200
    headers = backend.next_call()['request'].headers
    assert 'X-YaBank-SessionUUID' not in headers
    for key in internal_headers:
        assert key not in headers or headers[key] != internal_headers[key]


# Proxying unauthorized requests is allowed by config
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('session_info_code', (404, 400))
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
async def test_request_no_authorization_but_check_bank_auth(
        taxi_bank_authproxy,
        mockserver,
        blackbox_service,
        mock_remote,
        session_info_code,
        session_uuid_header,
):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_session_info',
    )
    def _session_info_handler(request):
        return mockserver.make_response(status=session_info_code, json={})

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_id',
    )
    def _phone_id_handler(request):
        assert request.headers.get('X-Yandex-UID')
        assert not request.headers.get('X-Yandex-BUID')
        return {'phone_id': PHONE_NUMBER_ID}

    url = 'unauth/check_bank_auth'
    backend = mock_remote(url)
    session_uuid = 'session_uuid'
    headers = session_uuid_header
    headers['Cookie'] = (
        headers.get('Cookie', '')
        + f';Session_id={session_uuid}'
        + ';allow_cookie=allow_data;blocked_cookie=blocked_data'
    )

    blackbox_service.set_sessionid_info(
        sessionid=session_uuid,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )

    response = await taxi_bank_authproxy.get(url, headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert 'X-Yandex-BUID' not in headers
    assert 'X-YaBank-SessionStatus' not in headers
    assert headers['X-Yandex-Auth-Status'] == 'VALID'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'no'
    assert headers['X-YaBank-SessionUUID'] == '123'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    assert response.status_code == 200
    assert headers['Cookie'] == 'allow_cookie=allow_data'


# Proxying unauthorized requests is forbidden by default
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('yandex_uid', [None, 'bad_yandex_uid'])
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
async def test_request_not_authorized_bad_session_yandex_uid(
        taxi_bank_authproxy,
        blackbox_service,
        bank_service,
        mock_remote,
        yandex_uid,
        session_uuid_header,
):
    url = '/abc'
    bank_service.set_session_info(
        bank_uid='123', yandex_uid=yandex_uid, bank_phone_id=PHONE_NUMBER_ID,
    )
    session_uuid = 'session_uuid'
    blackbox_service.set_sessionid_info(
        sessionid=session_uuid,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    backend = mock_remote(url)

    headers = session_uuid_header
    headers['Cookie'] = (
        headers.get('Cookie', '') + f';Session_id={session_uuid}'
    )

    response = await taxi_bank_authproxy.get(url, headers=headers)
    assert not backend.has_calls
    assert response.status_code == 401


# Proxying unauthorized requests is forbidden by default
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
async def test_request_not_authorized_no_bank_phone_id(
        taxi_bank_authproxy,
        blackbox_service,
        bank_service,
        mock_remote,
        session_uuid_header,
):
    url = '/abc'
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    session_uuid = 'session_uuid'
    blackbox_service.set_sessionid_info(
        sessionid=session_uuid,
        uid='100',
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    backend = mock_remote(url)
    headers = session_uuid_header
    headers['Cookie'] = (
        headers.get('Cookie', '') + f';Session_id={session_uuid}'
    )

    response = await taxi_bank_authproxy.get(url, headers=headers)
    assert not backend.has_calls
    assert response.status_code == 401


# Proxying requests with valid passport authorization via a session id cookie
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
async def test_request_valid_passport_session_auth(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        session_uuid_header,
):
    backend = mock_remote('/abc')
    session_uuid = 'session_uuid'
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/90.0.4430.212 '
            'YaBrowser/21.5.3.753 (beta) Yowser/2.5 Safari/537.36'
        ),
        'Accept-Language': 'en',
    }
    headers.update(session_uuid_header)
    headers['Cookie'] = (
        headers.get('Cookie', '') + f';Session_id={session_uuid}'
    )

    blackbox_service.set_sessionid_info(
        sessionid=session_uuid,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-Yandex-Auth-Status'] == 'VALID'
    assert headers['X-YaBank-SessionUUID'] == '123'
    assert headers['X-YaBank-SessionStatus'] == 'ok'
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'yes'
    assert headers['X-Yandex-BUID'] == '123'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-Request-Language'] == 'en'
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    # Compare ignoring key-value pair order
    assert set(headers['X-Request-Application'].split(',')) == set(
        'app_brand=yataxi,app_name=web,app_ver1=2'.split(','),
    )
    assert response.status_code == 200


# Proxying requests with an invalid Passport session cookie is forbidden
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_request_invalid_passport_session_auth(
        taxi_bank_authproxy, mock_remote, blackbox_service,
):
    backend = mock_remote('/abc')
    headers = {'Cookie': 'Session_id=invalid'}
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert not backend.has_calls
    assert response.status_code == 401


# Proxying requests with valid passport authorization via an OAuth token
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('session_uuid_headers', get_session_uuid_headers())
async def test_request_valid_passport_token_auth(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        session_uuid_headers,
):
    backend = mock_remote('/abc')
    token = 'token'
    headers = get_default_headers_with_oauth(token, session_uuid_headers)

    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert 'X-Yandex-Auth-Status' not in headers
    assert headers['X-YaBank-SessionUUID'] == '123'
    assert headers['X-YaBank-SessionStatus'] == 'ok'
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'yes'
    assert headers['X-Yandex-BUID'] == '123'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-Request-Language'] == 'en'
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    # Compare ignoring key-value pair order
    assert set(headers['X-Request-Application'].split(',')) == set(
        'app_brand=yataxi,app_name=web,app_ver1=2'.split(','),
    )
    assert response.status_code == 200


# Proxying requests with valid passport authorization via an OAuth token
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
async def test_request_valid_passport_token_auth_bad_session_status(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        session_uuid_header,
):
    backend = mock_remote('/abc')
    token = 'token'
    headers = get_default_headers_with_oauth(token, session_uuid_header)
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123',
        yandex_uid='100',
        bank_phone_id=PHONE_NUMBER_ID,
        status='nOk',
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert not backend.has_calls
    assert response.status_code == 401


# Proxying requests with valid passport authorization via an OAuth token
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
async def test_request_valid_passport_token_auth_bad_session_status_allow_401(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        session_uuid_header,
):
    url = '/unauth/check_bank_auth'
    backend = mock_remote(url)
    token = 'token'
    headers = get_default_headers_with_oauth(token, session_uuid_header)
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123',
        yandex_uid='100',
        bank_phone_id=PHONE_NUMBER_ID,
        status='nOk',
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get(url, headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-YaBank-SessionUUID'] == '123'
    assert headers['X-YaBank-SessionStatus'] == 'nOk'
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'no'
    assert headers['X-Yandex-BUID'] == '123'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-Request-Language'] == 'en'
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    # Compare ignoring key-value pair order
    assert set(headers['X-Request-Application'].split(',')) == set(
        'app_brand=yataxi,app_name=web,app_ver1=2'.split(','),
    )
    assert response.status_code == 200


# Proxying requests with a valid passport authorization but no bank authorization
# Requests to any path except /auth should be blocked
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_request_valid_passport_no_bank_401(
        taxi_bank_authproxy, mock_remote, blackbox_service,
):
    backend = mock_remote('/abc')
    token = 'token'
    headers = {'Authorization': 'Bearer ' + token}
    blackbox_service.set_token_info(
        token=token, uid='100', strict_phone_attributes=True,
    )
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert not backend.has_calls
    assert response.status_code == 401


# Same as above, but now we request an authorization from the bank,
# this call should be proxied with only passport auth checked
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_request_valid_passport_no_bank_auth_ok(
        taxi_bank_authproxy, mock_remote, blackbox_service, bank_service,
):
    backend = mock_remote('/auth')
    token = 'token'
    headers = {'Authorization': 'Bearer ' + token}
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    response = await taxi_bank_authproxy.get('/auth', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'yes'
    assert 'X-Yandex-BUID' not in headers
    assert 'X-YaBank-PhoneID' not in headers
    assert 'X-YaBank-SessionStatus' not in headers
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    assert headers['X-Yandex-UID'] == '100'
    assert response.status_code == 200


# Same as above, but the passport account now contains a bank phone
# It should be proxied along with the rest of authinfo
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_request_valid_passport_with_phone_no_bank_auth_ok(
        taxi_bank_authproxy, mock_remote, blackbox_service, bank_service,
):
    backend = mock_remote('/auth')
    token = 'token'
    headers = {'Authorization': 'Bearer ' + token}
    blackbox_service.set_token_info(
        token=token, uid='100', phones=BB_PHONES, strict_phone_attributes=True,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/auth', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'yes'
    assert 'X-Yandex-BUID' not in headers
    assert 'X-YaBank-SessionStatus' not in headers
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert response.status_code == 200


# Checks whether the request to the phone_id handle is cached correctly
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_bank_phone_id_cache(
        mockserver,
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_id',
    )
    def _phone_id_handler(request):
        assert request.headers.get('X-Yandex-UID')
        assert request.headers.get('X-Yandex-BUID')
        return {'phone_id': PHONE_NUMBER_ID}

    backend = mock_remote('/abc')
    token = 'token'
    headers = {
        'X-YaBank-SessionUUID': '123',
        'Authorization': 'Bearer ' + token,
    }
    blackbox_service.set_token_info(
        token=token, uid='100', phones=BB_PHONES, strict_phone_attributes=True,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )

    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert response.status_code == 200

    headers['X-YaBank-SessionUUID'] = '345'
    bank_service.set_session_info(
        bank_uid='567', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )

    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert backend.times_called == 2
    assert bank_service.session_info_handler.times_called == 2
    assert _phone_id_handler.times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize('account_type', ['phonish', 'portal'])
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_phonish_to_flag_ytpf(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        account_type,
):
    backend = mock_remote('/abc')
    token = 'token'
    headers = get_default_headers_with_oauth(token)
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        account_type=account_type,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-Remote-IP'] == '127.0.0.13'
    assert headers['X-YaBank-SessionStatus'] == 'ok'
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'yes'
    assert headers['X-Yandex-BUID'] == '123'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-Request-Language'] == 'en'
    assert headers['X-YaTaxi-Pass-Flags'] == f'{account_type},bank-account'
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    # Compare ignoring key-value pair order
    assert set(headers['X-Request-Application'].split(',')) == set(
        'app_brand=yataxi,app_name=web,app_ver1=2'.split(','),
    )
    assert response.status_code == 200


def config_add_to_pcidss_router(config, config_vars):
    config['components_manager']['components']['handler-router'][
        'is_in_pcidss_scope'
    ] = True


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.uservice_oneshot(config_hooks=[config_add_to_pcidss_router])
@pytest.mark.parametrize('url', ['/unauth', '/abc'])
async def test_uconfig_ignored(taxi_bank_authproxy, mock_remote, url):
    backend = mock_remote(url)
    response = await taxi_bank_authproxy.get(url)
    assert not backend.has_calls
    assert response.status_code == 404


@pytest.mark.uservice_oneshot(config_hooks=[config_add_to_pcidss_router])
async def test_hardcoded_route_unauthorized(taxi_bank_authproxy, mock_remote):
    backend = mock_remote('/v1/card/do_smth')
    response = await taxi_bank_authproxy.get('/v1/card/do_smth')
    assert not backend.has_calls
    assert response.status_code == 401


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize(
    'token_scopes,required_scopes,status_code',
    [
        ('yabank:read', 'yabank:read passport:bind_phone', 401),
        ('yabank:read passport:bind_phone', 'yabank:read', 200),
        (
            'yabank:read passport:bind_phone',
            'yabank:read passport:bind_phone',
            200,
        ),
    ],
)
async def test_scopes(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        token_scopes,
        required_scopes,
        status_code,
        taxi_config,
):
    taxi_config.set_values(
        {'BANK_AUTHPROXY_PASSPORT_SCOPES': required_scopes.split()},
    )
    backend = mock_remote('/abc')
    token = 'token'
    headers = get_default_headers_with_oauth(token)
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
        scope=token_scopes,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert response.status_code == status_code
    if status_code == 200:
        assert backend.has_calls


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize(
    'domain', ['bank.yandex.ru', 'fintech.yandex.ru', 'unknown'],
)
async def test_domain_routing(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        domain,
):
    mock_url = ('' if domain == 'unknown' else domain) + '/domains_route'
    backend = mock_remote(mock_url)
    token = 'token'
    headers = get_default_headers_with_oauth(token)
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    headers['Host'] = domain
    response = await taxi_bank_authproxy.get('/domains_route', headers=headers)
    assert response.status_code == 200
    assert backend.has_calls


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.parametrize(
    'domain', ['bank.yandex.ru', 'fintech.yandex.ru', 'unknown'],
)
async def test_domain_routing_2(
        taxi_bank_authproxy,
        mock_remote,
        blackbox_service,
        bank_service,
        domain,
):
    mock_url = (
        '' if domain == 'unknown' else 'yandex.ru'
    ) + '/several_domains_route'
    backend = mock_remote(mock_url)
    token = 'token'
    headers = get_default_headers_with_oauth(token)
    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    headers['Host'] = domain
    response = await taxi_bank_authproxy.get(
        '/several_domains_route', headers=headers,
    )
    assert response.status_code == 200
    assert backend.has_calls


@pytest.mark.parametrize(
    'response_code,expected_message',
    [
        (200, 'message'),
        (400, 'BadRequest'),
        (401, 'NotAuthorized'),
        (404, 'NotFound'),
        (409, 'Conflict'),
    ],
)
@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
async def test_replace_error_message(
        taxi_bank_authproxy, mock_remote, response_code, expected_message,
):
    backend = mock_remote(
        '/unauth',
        response_code=response_code,
        response_body={'code': 'code', 'message': 'message'},
    )
    response = await taxi_bank_authproxy.get('/unauth')
    assert backend.has_calls
    assert response.status_code == response_code
    expected_code = 'code' if response_code == 200 else str(response_code)
    assert response.json() == {
        'code': expected_code,
        'message': expected_message,
    }


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_session_uuid_both_cookie_and_header(
        taxi_bank_authproxy, mock_remote, blackbox_service, bank_service,
):
    backend = mock_remote('/abc')
    token = 'token'
    headers = get_default_headers_with_oauth(token)
    headers.update({'Cookie': 'yabank-sessionuuid=456'})

    blackbox_service.set_token_info(
        token=token,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
    )
    bank_service.set_session_info(
        bank_uid='123', yandex_uid='100', bank_phone_id=PHONE_NUMBER_ID,
    )
    bank_service.set_phone_id_dict({PHONE_NUMBER: PHONE_NUMBER_ID})
    response = await taxi_bank_authproxy.get('/abc', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-YaBank-SessionUUID'] == '456'
    assert headers['X-YaBank-SessionStatus'] == 'ok'
    assert headers['X-YaBank-AuthorizedByAuthproxy'] == 'yes'
    assert headers['X-Yandex-BUID'] == '123'
    assert headers['X-Yandex-UID'] == '100'
    assert headers['X-YaBank-PhoneID'] == PHONE_NUMBER_ID
    assert headers['X-Request-Language'] == 'en'
    assert headers['X-YaBank-Yandex-Team-Login'] == STAFF_LOGIN
    assert headers['X-Ya-User-Ticket'] == USER_TICKET
    # Compare ignoring key-value pair order
    assert set(headers['X-Request-Application'].split(',')) == set(
        'app_brand=yataxi,app_name=web,app_ver1=2'.split(','),
    )
    assert response.status_code == 200


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
async def test_proxy_invalid_cookie_status(
        taxi_bank_authproxy, blackbox_service, mock_remote,
):
    backend = mock_remote('/unauth')
    headers = {'Cookie': 'Session_id=invalid_cookie'}
    await taxi_bank_authproxy.get('/unauth', headers=headers)
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-Yandex-Auth-Status'] == 'NOAUTH'


@pytest.mark.config(BANK_AUTHPROXY_ROUTE_RULES=CONFIG)
@pytest.mark.config(
    BANK_AUTHPROXY_USER_SESSION_ALLOWED_STATUSES=SESSION_ALLOWED_STATUSES,
)
@pytest.mark.parametrize('yandex_uid', [None, 'bad_yandex_uid'])
@pytest.mark.parametrize('session_uuid_header', get_session_uuid_headers())
@pytest.mark.parametrize('cookie_status', ['VALID', 'NEED_RESET'])
async def test_request_uid_mismatch_proxy_auth_status(
        taxi_bank_authproxy,
        blackbox_service,
        bank_service,
        mock_remote,
        yandex_uid,
        session_uuid_header,
        cookie_status,
):
    backend = mock_remote('/unauth')
    bank_service.set_session_info(
        bank_uid='123', yandex_uid=yandex_uid, bank_phone_id=PHONE_NUMBER_ID,
    )
    session_uuid = 'session_uuid'
    blackbox_service.set_sessionid_info(
        sessionid=session_uuid,
        uid='100',
        phones=BB_PHONES,
        strict_phone_attributes=True,
        staff_login=STAFF_LOGIN,
        user_ticket=USER_TICKET,
        status=cookie_status,
    )

    headers = session_uuid_header
    headers['Cookie'] = (
        headers.get('Cookie', '') + f';Session_id={session_uuid}'
    )

    response = await taxi_bank_authproxy.get('/unauth', headers=headers)
    assert response.status_code == 200
    assert backend.has_calls
    headers = backend.next_call()['request'].headers
    assert headers['X-Yandex-Auth-Status'] == cookie_status
