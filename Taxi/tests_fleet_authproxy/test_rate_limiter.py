# pylint: disable=import-error

import pytest

SESSION_HEADERS = {
    'Cookie': 'Session_id=session1',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-IP': 'test_ip',
}

SESSION_HEADERS_2 = {
    'Cookie': 'Session_id=session2',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-IP': 'test_ip',
}

SESSION_HEADERS_3 = {
    'Cookie': 'Session_id=session3',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-IP': 'test_ip',
}

SESSION_HEADERS_TEAM = {
    'Cookie': 'Session_id=session1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
}

URL_AUTH = 'fleet/v1/auth'

REMOTE_RESPONSE = {'response': 42}

FLEET_AUTHPROXY_ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/fleet/'},
        'proxy': {'server-hosts': ['*']},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]
FLEET_AUTHPROXY_ACCESS_RULES = [
    {
        'prefix': '/fleet/',
        'access_rules': [
            {'path': '/fleet/v1/auth', 'method': 'GET'},
            {'path': '/fleet/v1/auth', 'method': 'POST'},
            {'path': '/fleet/v1/auth/0', 'method': 'POST'},
            {'path': '/fleet/v1/auth/1', 'method': 'POST'},
            {'path': '/fleet/v1/auth/2', 'method': 'POST'},
            {'path': '/fleet/v1/auth/3', 'method': 'POST'},
            {'path': '/fleet/v1/auth/4', 'method': 'POST'},
            {'path': '/fleet/v1/auth/5', 'method': 'POST'},
            {'path': '/fleet/v1/auth/6', 'method': 'POST'},
            {'path': '/fleet/v1/auth/7', 'method': 'POST'},
        ],
    },
]


async def do_test_ok(_mock_remote, _request, url_path, headers, method='POST'):
    handler = _mock_remote(url_path=url_path, method=method)
    response = await _request(
        url_path=url_path, headers=headers, method=method,
    )

    assert handler.has_calls
    assert response.status_code == 200
    assert response.json() == REMOTE_RESPONSE


async def do_test_fail(
        _mock_remote,
        _request,
        url_path,
        headers,
        expected_status_code=429,
        expected_json=None,
        method='POST',
):
    handler = _mock_remote(url_path=url_path, method=method)
    response = await _request(
        url_path=url_path, headers=headers, method=method,
    )

    assert not handler.has_calls
    assert response.status_code == expected_status_code
    assert not response.cookies
    if expected_json is not None:
        assert response.json() == expected_json
    return response


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'services': {
            '__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
        },
    },
)
async def test_service_default(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {'__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}]},
    },
)
async def test_park_default(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'urls': {'__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}]},
    },
)
async def test_url_default(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'users': {'__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}]},
    },
)
async def test_user_default(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {'park': [{'by': 'park_id', 'rate': 2, 'unit': 10}]},
    },
)
async def test_park_concrete(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {
            'park1': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
            'park2': [{'by': 'park_id', 'rate': 3, 'unit': 10}],
        },
    },
)
async def test_park_many(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park1'}

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)

    headers['X-Park-Id'] = 'park2'
    for i in range(0, 4):
        if i < 3:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)

    headers['X-Park-Id'] = 'park3'
    for i in range(0, 4):
        await do_test_ok(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {
            '__default__': [{'by': 'park_id', 'rate': 6, 'unit': 10}],
            'park1': [{'by': 'park_id', 'rate': 3, 'unit': 10}],
        },
        'urls': {
            '__default__': [{'by': 'park_id', 'rate': 4, 'unit': 10}],
            '/'
            + URL_AUTH
            + '@POST': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
        },
    },
    FLEET_AUTHPROXY_ACCESS_RULES=FLEET_AUTHPROXY_ACCESS_RULES,
    FLEET_AUTHPROXY_ROUTE_RULES=FLEET_AUTHPROXY_ROUTE_RULES,
)
async def test_hard_config(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park1'}
    for i in range(0, 4):
        url = URL_AUTH + '/' + str(i)
        if i < 3:
            await do_test_ok(_mock_remote, _request, url, headers)
        else:
            await do_test_fail(_mock_remote, _request, url, headers)

    headers['X-Park-Id'] = 'park2'
    for i in range(0, 7):
        url = URL_AUTH + '/' + str(i)
        if i < 6:
            await do_test_ok(_mock_remote, _request, url, headers)
        else:
            await do_test_fail(_mock_remote, _request, url, headers)

    headers['X-Park-Id'] = 'park3'
    for i in range(0, 4):
        url = URL_AUTH + '/' + str(i)
        await do_test_ok(_mock_remote, _request, url, headers)

    headers['X-Park-Id'] = 'park4'
    for i in range(0, 3):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {'__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}]},
    },
)
async def test_limit_recovery(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        mocked_time,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    for _ in range(0, 2):
        await do_test_ok(_mock_remote, _request, URL_AUTH, headers)

    mocked_time.sleep(5)
    await taxi_fleet_authproxy.invalidate_caches()

    await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
    await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {
            '__default__': [
                {'by': 'park_id', 'rate': 2, 'unit': 10},
                {'by': 'park_id', 'rate': 4, 'unit': 1000},
            ],
        },
    },
)
async def test_periods(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        mocked_time,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)

    mocked_time.sleep(10)
    await taxi_fleet_authproxy.invalidate_caches()

    for i in range(0, 4):
        if i < 1:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'urls': {
            '/'
            + URL_AUTH
            + '@GET': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
            '/'
            + URL_AUTH
            + '@POST': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
        },
    },
    FLEET_AUTHPROXY_ACCESS_RULES=FLEET_AUTHPROXY_ACCESS_RULES,
    FLEET_AUTHPROXY_ROUTE_RULES=FLEET_AUTHPROXY_ROUTE_RULES,
)
async def test_urls_methods(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
        mocked_time,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    for i in range(0, 4):
        if i < 2:
            await do_test_ok(
                _mock_remote, _request, URL_AUTH, headers, method='GET',
            )
        else:
            await do_test_fail(
                _mock_remote, _request, URL_AUTH, headers, method='GET',
            )

    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'}, session2={'uid': '200'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'services': {
            '__default__': [{'by': 'passport_uid', 'rate': 2, 'unit': 10}],
        },
    },
)
async def test_by_user(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)

    headers = {**SESSION_HEADERS_2, 'X-Park-Id': 'park'}
    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(
    session1={'uid': '100'}, session2={'uid': '200'}, session3={'uid': '300'},
)
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'parks': {'park': [{'by': 'passport_uid', 'rate': 4, 'unit': 10}]},
    },
)
async def test_by_user_2(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    for _ in range(0, 2):
        headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
        for __ in range(0, 2):
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)

        headers = {**SESSION_HEADERS_2, 'X-Park-Id': 'park'}
        for __ in range(0, 2):
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)

        headers = {**SESSION_HEADERS_3, 'X-Park-Id': 'park'}
        for __ in range(0, 2):
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'services': {'__default__': [{'by': 'ip', 'rate': 2, 'unit': 10}]},
    },
)
async def test_by_ip(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    for i in range(0, 4):
        if i < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': False,
        'services': {
            '__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
        },
    },
)
async def test_config_disabled(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS, 'X-Park-Id': 'park'}
    for _ in range(0, 4):
        await do_test_ok(_mock_remote, _request, URL_AUTH, headers)


@pytest.mark.passport_team_session(session1={'uid': '100'})
@pytest.mark.config(
    FLEET_AUTHPROXY_RATE_LIMITER={
        'is_enabled': True,
        'services': {
            '__default__': [{'by': 'park_id', 'rate': 2, 'unit': 10}],
        },
    },
)
async def test_yandex_team(
        _mock_remote,
        _request,
        taxi_fleet_authproxy,
        blackbox_service,
        dispatcher_access_control,
):
    headers = {**SESSION_HEADERS_TEAM, 'X-Park-Id': 'park'}
    for _ in range(0, 4):
        if _ < 2:
            await do_test_ok(_mock_remote, _request, URL_AUTH, headers)
        else:
            await do_test_fail(_mock_remote, _request, URL_AUTH, headers)
