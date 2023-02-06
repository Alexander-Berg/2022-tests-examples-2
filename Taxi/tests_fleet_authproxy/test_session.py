# pylint: disable=import-error

import datetime

import pytest

from client_blackbox import mock_blackbox  # noqa: F403 F401, I100, I202

SESSION_HEADERS = {
    'Cookie': 'Session_id=session1',
    'X-Ya-User-Ticket-Provider': 'yandex',
}

SESSION_HEADERS_TEAM = {
    'Cookie': 'Session_id=session1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
}

LARAVEL_TOKEN = (
    'eyJpdiI6Ijd0OU9keDBvb1pPOE5DQVhoUjhIakE9PSIsInZhbHVlIjoibk5hcDA4T2FnQnNW'
    'VUpua1lVSEJRRjQrMFVVYXpnVyszY29lcVFpdWFNUmoxelV5bGUrOFFqMERHODcxMWFCRkhP'
    'TnByWnE5S210bUFCNnB5cXNZczErRW1VTm83Rmd3d0RvcDZBTHFjVE9pb0QwcmN5SVpySVZN'
    'S0VPRXlMVDJjV0dNS3hYMGVxQ3dGRE43cGVIdEFtZnBLaFwvQjBkeGp3K1NsVUtnaStOTT0i'
    'LCJtYWMiOiI0NzVlZjJhNjkwM2VjZTM4M2M3YTBlYjBiZWVhNWI1NWJjZTAxMzY4NTdjNTNm'
    'ZTMyNTBmODcyZTY3N2ZlZTE3In0='
)
TOKEN = 'AgAAAADuyyxgAAAQXG95Nfdbp03-sGEKpz8mVH4'

TOKEN_HEADERS = {
    'Cookie': 'oauth_token=' + LARAVEL_TOKEN,
    'X-Ya-User-Ticket-Provider': 'yandex',
}

TOKEN_HEADERS_TEAM = {
    'Cookie': 'oauth_token=' + LARAVEL_TOKEN,
    'X-Ya-User-Ticket-Provider': 'yandex_team',
}

TOKEN_BEARER_HEADERS = {
    'Authorization': 'Bearer ' + TOKEN,
    'X-Ya-User-Ticket-Provider': 'yandex',
}

EMPTY_HEADERS = {'X-Ya-User-Ticket-Provider': 'yandex'}

FLEET_USERS_CONFIRM_REQUEST = {
    'phone': '+111111',
    'passport_uid': '100',
    'passport_name': 'John Smith',
}

BLACKBOX_NAME_RESPONSE = {
    'users': [
        {
            'uid': {'value': '100'},
            'login': 'login',
            'attributes': {'27': 'John', '28': 'Smith'},
        },
    ],
}

URL_AUTH = 'fleet/v1/auth'
URL_NOAUTH = 'fleet/v1/noauth'
URL_AUTH_PARK_ID_REQUIRED = 'fleet/v1/auth/park-id-required'
URL_NOAUTH_PARK_ID_REQUIRED = 'fleet/v1/noauth/park-id-required'
URL_NOTCONFIGURED = 'fleet/v1/notconfigured'

# TODO: copy paste
REMOTE_RESPONSE = {'response': 42}


async def do_test_ok(
        _mock_remote,
        _request,
        url_path,
        headers,
        provider='yandex',
        park='park',
        forwarded_permissions=None,
):
    handler = _mock_remote(url_path=url_path)
    response = await _request(url_path=url_path, headers=headers)

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    assert response_headers['X-Ya-User-Ticket-Provider'] == provider
    assert response_headers['X-Ya-User-Ticket'] == 'test_user_ticket'
    assert response_headers['X-Yandex-UID'] == '100'
    assert response_headers['X-Yandex-Login'] == 'login'
    if 'X-Park-Id' in headers:
        assert response_headers['X-Park-Id'] == park
    else:
        assert 'X-Park-Id' not in response_headers
    if forwarded_permissions is not None:
        assert (
            response_headers['X-YaTaxi-Fleet-Permissions']
            == forwarded_permissions
        )

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


async def do_test_fail(
        _mock_remote,
        _request,
        url_path,
        headers,
        expected_status_code=401,
        expected_json=None,
):
    handler = _mock_remote(url_path=url_path)
    response = await _request(url_path=url_path, headers=headers)

    assert not handler.has_calls
    assert response.status_code == expected_status_code
    assert not response.cookies
    if expected_json is not None:
        assert response.json() == expected_json
    return response


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_ok(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_ok(_mock_remote, _request, URL_AUTH, SESSION_HEADERS)


NEOPHONISH_PARAMS = [
    ('yandex', 'phonish', [], 0, 0, SESSION_HEADERS),
    ('yandex', 'neophonish', [], 0, 0, SESSION_HEADERS),
    (
        'yandex',
        'neophonish',
        [mock_blackbox.make_phone('+111111', secured=False)],
        0,
        0,
        SESSION_HEADERS,
    ),
    (
        'yandex',
        'neophonish',
        [mock_blackbox.make_phone('+111111', secured=True)],
        1,
        1,
        {**SESSION_HEADERS, 'X-Park-Id': 'park'},
    ),
    (
        'yandex',
        'neophonish',
        [mock_blackbox.make_phone('+111111', secured=True)],
        1,
        1,
        {**SESSION_HEADERS, 'X-Park-Id': 'park'},
    ),
    (
        'yandex',
        'phonish',
        [mock_blackbox.make_phone('+111111', secured=True)],
        0,
        1,
        {**SESSION_HEADERS, 'X-Park-Id': 'park'},
    ),
    ('yandex_team', 'phonish', [], 0, 0, SESSION_HEADERS_TEAM),
]


@pytest.mark.passport_team_session(session1={'uid': '100'})
@pytest.mark.parametrize(
    """provider, account_type, phones, times_called_fleet_users,
    times_called_dac_permissions, headers""",
    NEOPHONISH_PARAMS,
)
async def test_session_ok_neophonish(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        provider,
        account_type,
        phones,
        times_called_fleet_users,
        times_called_dac_permissions,
        headers,
        mockserver,
        dispatcher_access_control,
):
    blackbox_service.user_tickets['test_user_ticket'] = BLACKBOX_NAME_RESPONSE

    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        assert request.json == FLEET_USERS_CONFIRM_REQUEST
        return {}

    blackbox_service.set_sessionid_info(
        'session1', uid='100', phones=phones, account_type=account_type,
    )

    await do_test_ok(_mock_remote, _request, URL_AUTH, headers, provider)

    assert _mock_fleet_users.times_called == times_called_fleet_users
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == times_called_dac_permissions
    )


async def test_session_ok_portal_neophonish(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        mockserver,
        dispatcher_access_control,
):
    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        assert request.json == FLEET_USERS_CONFIRM_REQUEST
        return {}

    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        if request.query['method'] == 'user_ticket':
            assert request.query['attributes'] == '27,28'
            return BLACKBOX_NAME_RESPONSE

        return {
            'uid': {'value': '100'},
            'login': 'login',
            'status': {'value': 'VALID'},
            'aliases': {'21': 'abba', '1': 'portal'},
            'phones': [
                {'id': '0', 'attributes': {'108': '1', '102': '+111111'}},
            ],
            'user_ticket': 'test_user_ticket',
        }

    await do_test_ok(
        _mock_remote=_mock_remote,
        _request=_request,
        url_path=URL_AUTH,
        headers={**SESSION_HEADERS, 'X-Park-Id': 'park'},
    )

    assert _mock_fleet_users.times_called == 0
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_session_fail_neophonish(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        mockserver,
        dispatcher_access_control,
):
    blackbox_service.user_tickets['test_user_ticket'] = BLACKBOX_NAME_RESPONSE

    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        return mockserver.make_response(
            status=400, json={'code': 'user_was_not_found', 'message': ''},
        )

    blackbox_service.set_sessionid_info(
        'session1',
        uid='100',
        phones=[mock_blackbox.make_phone('+111111', secured=True)],
        account_type='neophonish',
    )

    await do_test_fail(
        _mock_remote=_mock_remote,
        _request=_request,
        url_path=URL_AUTH,
        headers={**SESSION_HEADERS, 'X-Park-Id': 'park'},
        expected_status_code=403,
    )

    assert _mock_fleet_users.times_called == 1
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 0
    )


async def test_session_fail(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_fail(_mock_remote, _request, URL_AUTH, SESSION_HEADERS)


async def test_no_session(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    headers = {
        'X-Park-Id': 'unknown_park',
        'X-Ya-User-Ticket-Provider': 'yandex',
    }
    await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.parametrize('url', [URL_AUTH, URL_AUTH_PARK_ID_REQUIRED])
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_park_id_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        url,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    await do_test_ok(_mock_remote, _request, url, headers)

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.parametrize('url', [URL_AUTH_PARK_ID_REQUIRED])
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_park_id_not_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        url,
):
    dispatcher_access_control.set_permissions([])

    headers = {**SESSION_HEADERS, 'X-Park-Id': 'unknown_park'}
    response = await do_test_fail(_mock_remote, _request, url, headers, 403)
    assert response.json() == {
        'code': 'no_permissions',
        'message': 'No permissions',
    }

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.parametrize(
    'account_2fa_on, account_sms_2fa_on', [('1', '0'), ('0', '1'), ('1', '1')],
)
async def test_session_park_id_multifactor_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        load_json,
        account_2fa_on,
        account_sms_2fa_on,
):
    blackbox_service.set_sessionid_info(
        'session1',
        uid='100',
        account_2fa_on=account_2fa_on,
        account_sms_2fa_on=account_sms_2fa_on,
    )
    dispatcher_access_control.set_users(
        load_json('dac_users_multifactor_auth.json'),
    )
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    await do_test_ok(_mock_remote, _request, URL_AUTH, headers)

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


MULTIFACTOR_BAD_PARAMS = [
    (
        [],
        {'code': 'unauthorized_no_phone_confirmed', 'message': 'Unauthorized'},
    ),
    (
        [
            mock_blackbox.make_phone(
                '+111111',
                confirmation_time=datetime.datetime.now(),
                secured=False,
            ),
        ],
        {'code': 'unauthorized_no_phone_confirmed', 'message': 'Unauthorized'},
    ),
    (
        [
            mock_blackbox.make_phone(
                '+111111',
                confirmation_time=datetime.datetime(2019, 1, 1),
                secured=True,
            ),
        ],
        {
            'code': 'unauthorized_phone_confirmation_timed_out',
            'message': 'Unauthorized',
        },
    ),
    (
        [
            mock_blackbox.make_phone(
                '+111111',
                confirmation_time=datetime.datetime.now(),
                secured=True,
            ),
        ],
        {
            'code': 'unauthorized_multi_factor_auth_disabled',
            'message': 'Unauthorized',
        },
    ),
]


@pytest.mark.parametrize('phones, expected_json', MULTIFACTOR_BAD_PARAMS)
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_multifactor_error(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        load_json,
        phones,
        expected_json,
):
    blackbox_service.set_sessionid_info(
        'session1',
        uid='100',
        account_2fa_on='0',
        account_sms_2fa_on='0',
        phones=phones,
    )
    dispatcher_access_control.set_users(
        load_json('dac_users_multifactor_auth.json'),
    )
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    await do_test_fail(
        _mock_remote,
        _request,
        URL_AUTH,
        headers,
        expected_status_code=403,
        expected_json=expected_json,
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_access_rules_notconfigured(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        mockserver,
):
    await do_test_fail(
        _mock_remote,
        _request,
        URL_NOTCONFIGURED,
        {**SESSION_HEADERS, 'X-Park-Id': 'park'},
        403,
    )


@pytest.mark.parametrize(
    'error_code', ['invalid_user_ticket', 'no_access', 'park_not_found'],
)
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_disp_access_control_not_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        error_code,
):
    dispatcher_access_control.set_error(
        http_code=400, error_code=error_code, message='error',
    )

    await do_test_fail(
        _mock_remote,
        _request,
        URL_AUTH_PARK_ID_REQUIRED,
        {**SESSION_HEADERS, 'X-Park-Id': 'park'},
        403,
    )

    assert dispatcher_access_control.parks_users_list.times_called == 1


@pytest.mark.config(FLEET_ACCESS_CONTROL_ENABLED=False)
@pytest.mark.parametrize('url', [URL_AUTH_PARK_ID_REQUIRED])
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_fleet_access_control_disabled(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        url,
):

    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    await do_test_ok(_mock_remote, _request, url, headers)
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 0
    )


@pytest.mark.parametrize('url', [URL_AUTH, URL_AUTH_PARK_ID_REQUIRED])
@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_session_yandex_team_park_id_all_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        mockserver,
        dispatcher_access_control,
        url,
):
    headers = {**SESSION_HEADERS_TEAM, 'X-Park-Id': 'park'}
    await do_test_ok(
        _mock_remote,
        _request,
        url,
        headers,
        provider='yandex_team',
        park='park',
    )


async def test_noauth_ok(_mock_remote, _request, taxi_fleet_authproxy):
    handler = _mock_remote(url_path=URL_NOAUTH)
    response = await _request(url_path=URL_NOAUTH, headers=EMPTY_HEADERS)

    assert handler.has_calls
    response_headers = handler.next_call()['request'].headers
    # 'X-Ya-User-Ticket-Provider' is ignored
    assert 'X-Ya-User-Ticket' not in response_headers
    assert 'X-Yandex-UID' not in response_headers
    assert 'X-Yandex-Login' not in response_headers

    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE
    assert not response.cookies


async def test_noauth_fail(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_fail(_mock_remote, _request, URL_AUTH, EMPTY_HEADERS)


PASSPORT_TOKEN_KWARGS = {TOKEN: {'uid': '100', 'scope': 'taxi_fleet:all'}}

PASSPORT_TOKEN_WRONG_SCOPE_KWARGS = {TOKEN: {'uid': '100'}}


@pytest.mark.passport_token(**PASSPORT_TOKEN_KWARGS)
async def test_bearer_token(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_ok(_mock_remote, _request, URL_AUTH, TOKEN_BEARER_HEADERS)


@pytest.mark.passport_token(**PASSPORT_TOKEN_WRONG_SCOPE_KWARGS)
async def test_bearer_token_wrong_scope(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_fail(_mock_remote, _request, URL_AUTH, TOKEN_BEARER_HEADERS)


async def test_bearer_token_invalid(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_fail(_mock_remote, _request, URL_AUTH, TOKEN_BEARER_HEADERS)


@pytest.mark.passport_token(**PASSPORT_TOKEN_KWARGS)
async def test_laravel_token(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_ok(_mock_remote, _request, URL_AUTH, TOKEN_HEADERS)


@pytest.mark.passport_token(**PASSPORT_TOKEN_WRONG_SCOPE_KWARGS)
async def test_laravel_token_wrong_scope(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_fail(_mock_remote, _request, URL_AUTH, TOKEN_HEADERS)


async def test_laravel_token_fail(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_fail(_mock_remote, _request, URL_AUTH, TOKEN_HEADERS)


@pytest.mark.parametrize('url', [URL_AUTH, URL_AUTH_PARK_ID_REQUIRED])
@pytest.mark.passport_token(**PASSPORT_TOKEN_KWARGS)
async def test_laravel_token_park_id_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        url,
):
    headers = {**TOKEN_HEADERS, 'X-Park-Id': 'park'}
    await do_test_ok(_mock_remote, _request, url, headers)

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.parametrize('url', [URL_AUTH_PARK_ID_REQUIRED])
@pytest.mark.passport_token(**PASSPORT_TOKEN_KWARGS)
async def test_laravel_token_park_id_not_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        url,
):
    dispatcher_access_control.set_permissions([])

    headers = {**TOKEN_HEADERS, 'X-Park-Id': 'unknown_park'}
    response = await do_test_fail(_mock_remote, _request, url, headers, 403)
    assert response.json() == {
        'code': 'no_permissions',
        'message': 'No permissions',
    }

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_token(**PASSPORT_TOKEN_KWARGS)
async def test_laravel_token_park_id_missing(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        mockserver,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _dispatcher_access_control(request):
        assert False

    await do_test_fail(
        _mock_remote, _request, URL_AUTH_PARK_ID_REQUIRED, TOKEN_HEADERS, 400,
    )


@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_provider_yandex_team(
        _mock_remote, _request, taxi_fleet_authproxy, blackbox_service,
):
    await do_test_ok(
        _mock_remote,
        _request,
        URL_AUTH,
        SESSION_HEADERS_TEAM,
        provider='yandex_team',
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_yandex_with_chatterbox_ticket_all_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        mockserver,
        dispatcher_access_control,
):
    headers = {
        **SESSION_HEADERS,
        'X-Park-Id': 'park',
        'X-Chatterbox-Ticket-id': 'some_ticket',
    }
    await do_test_ok(_mock_remote, _request, URL_AUTH, headers)

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_session_yandex_team_with_chatterbox_ticket_all_ok(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        mockserver,
        dispatcher_access_control,
):
    headers = {
        **SESSION_HEADERS_TEAM,
        'X-Park-Id': 'park',
        'X-Chatterbox-Ticket-Id': 'some_ticket',
    }
    await do_test_ok(
        _mock_remote, _request, URL_AUTH, headers, provider='yandex_team',
    )

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session_yandex_forwarded_permissions(
        _mock_remote, _request, blackbox_service, dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    await do_test_ok(
        _mock_remote,
        _request,
        URL_AUTH_PARK_ID_REQUIRED,
        headers,
        forwarded_permissions='one,two',
    )

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_session_yandex_team_forwarded_permissions(
        _mock_remote, _request, blackbox_service, dispatcher_access_control,
):
    headers = {**SESSION_HEADERS_TEAM, 'X-Park-Id': 'park'}
    await do_test_ok(
        _mock_remote,
        _request,
        URL_AUTH_PARK_ID_REQUIRED,
        headers,
        provider='yandex_team',
        forwarded_permissions='one,two',
    )

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_token(**PASSPORT_TOKEN_KWARGS)
async def test_token_yandex_forwarded_permissions(
        _mock_remote, _request, blackbox_service, dispatcher_access_control,
):
    headers = {**TOKEN_HEADERS, 'X-Park-Id': 'park'}
    await do_test_ok(
        _mock_remote,
        _request,
        URL_AUTH_PARK_ID_REQUIRED,
        headers,
        forwarded_permissions='one,two',
    )

    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


NEOPHONISH_PARAMS = [
    ('yandex', 'phonish', [], 0, 0, TOKEN_HEADERS),
    ('yandex', 'neophonish', [], 0, 0, TOKEN_HEADERS),
    (
        'yandex',
        'neophonish',
        [mock_blackbox.make_phone('+111111', secured=False)],
        0,
        0,
        TOKEN_HEADERS,
    ),
    (
        'yandex',
        'neophonish',
        [mock_blackbox.make_phone('+111111', secured=True)],
        1,
        1,
        {**TOKEN_HEADERS, 'X-Park-Id': 'park'},
    ),
    (
        'yandex',
        'neophonish',
        [mock_blackbox.make_phone('+111111', secured=True)],
        1,
        1,
        {**TOKEN_HEADERS, 'X-Park-Id': 'park'},
    ),
    (
        'yandex',
        'phonish',
        [mock_blackbox.make_phone('+111111', secured=True)],
        0,
        1,
        {**TOKEN_HEADERS, 'X-Park-Id': 'park'},
    ),
    ('yandex_team', 'phonish', [], 0, 0, TOKEN_HEADERS_TEAM),
]


@pytest.mark.passport_team_token(**PASSPORT_TOKEN_KWARGS)
@pytest.mark.parametrize(
    """provider, account_type, phones, times_called_fleet_users,
    times_called_dac_permissions, headers""",
    NEOPHONISH_PARAMS,
)
async def test_token_neophonish(
        _mock_remote,
        _request,
        blackbox_service,
        provider,
        account_type,
        phones,
        headers,
        times_called_fleet_users,
        times_called_dac_permissions,
        mockserver,
        dispatcher_access_control,
):
    blackbox_service.user_tickets['test_user_ticket'] = BLACKBOX_NAME_RESPONSE

    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        assert request.json == FLEET_USERS_CONFIRM_REQUEST
        return {}

    blackbox_service.set_token_info(
        token=TOKEN,
        uid='100',
        scope='taxi_fleet:all',
        phones=phones,
        account_type=account_type,
    )

    await do_test_ok(_mock_remote, _request, URL_AUTH, headers, provider)

    assert _mock_fleet_users.times_called == times_called_fleet_users
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == times_called_dac_permissions
    )


async def test_token_portal_neophonish(
        _mock_remote, _request, mockserver, dispatcher_access_control,
):
    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        assert request.json == FLEET_USERS_CONFIRM_REQUEST
        return {}

    @mockserver.json_handler('/blackbox')
    def _blackbox(request):
        if request.query['method'] == 'user_ticket':
            assert request.query['attributes'] == '27,28'
            return BLACKBOX_NAME_RESPONSE

        return {
            'uid': {'value': '100'},
            'login': 'login',
            'oauth': {
                'scope': 'taxi_fleet:all',
                'issue_time': '2018-05-30 12:34:56',
                'client_id': '',
            },
            'status': {'value': 'VALID'},
            'aliases': {'21': 'abba', '1': 'portal'},
            'phones': [
                {'id': '0', 'attributes': {'108': '1', '102': '+111111'}},
            ],
            'user_ticket': 'test_user_ticket',
        }

    await do_test_ok(
        _mock_remote=_mock_remote,
        _request=_request,
        url_path=URL_AUTH,
        headers={**TOKEN_HEADERS, 'X-Park-Id': 'park'},
    )

    assert _mock_fleet_users.times_called == 0
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )


@pytest.mark.passport_team_token(**PASSPORT_TOKEN_KWARGS)
async def test_token_fail_neophonish(
        _mock_remote,
        _request,
        blackbox_service,
        mockserver,
        dispatcher_access_control,
):
    blackbox_service.user_tickets['test_user_ticket'] = BLACKBOX_NAME_RESPONSE

    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        return mockserver.make_response(
            status=400, json={'code': 'user_was_not_found', 'message': ''},
        )

    blackbox_service.set_token_info(
        token=TOKEN,
        uid='100',
        scope='taxi_fleet:all',
        phones=[mock_blackbox.make_phone('+111111', secured=True)],
        account_type='neophonish',
    )

    await do_test_fail(
        _mock_remote=_mock_remote,
        _request=_request,
        url_path=URL_AUTH,
        headers={**TOKEN_HEADERS, 'X-Park-Id': 'park'},
        expected_status_code=403,
    )

    assert _mock_fleet_users.times_called == 1
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 0
    )


NEOPHONISH_CONFIG = {'is_neophonish_enabled': False}


@pytest.mark.config(FLEET_AUTHPROXY_NEOPHONISH_AUTHORIZATION=NEOPHONISH_CONFIG)
@pytest.mark.passport_team_session(session1={'uid': '100'})
async def test_neophonish_disable(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        mockserver,
        dispatcher_access_control,
):
    @mockserver.json_handler('fleet-users/v1/users/confirm')
    def _mock_fleet_users(request):
        assert request.json == FLEET_USERS_CONFIRM_REQUEST
        return {}

    blackbox_service.set_sessionid_info(
        'session1',
        uid='100',
        phones=[mock_blackbox.make_phone('+111111', secured=True)],
        account_type='neophonish',
    )
    await do_test_ok(
        _mock_remote=_mock_remote,
        _request=_request,
        url_path=URL_AUTH,
        headers={**SESSION_HEADERS, 'X-Park-Id': 'park'},
    )

    assert _mock_fleet_users.times_called == 0
    assert (
        dispatcher_access_control.parks_users_permissions_list.times_called
        == 1
    )
