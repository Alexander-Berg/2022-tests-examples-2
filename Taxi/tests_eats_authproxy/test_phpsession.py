import json

import aiohttp
import pytest


USER_AGENT_NATIVE = 'ios-eats(0.0.1)'
SESSION_TYPE_NATIVE = 'native'
APPLICATION_NAME_NATIVE = 'web'
BRAND_NATIVE = 'yataxi'
DEVICE_ID = 'default_device_id'


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test',
            'priority': 100,
            'rule_name': '/test',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/test401',
            'priority': 100,
            'rule_name': '/test401',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/test401',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/401',
            'priority': 100,
            'rule_name': '/401',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/401',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/proxy401',
            'priority': 100,
            'rule_name': '/proxy401',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/proxy401',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': True,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/nonewsession',
            'priority': 100,
            'rule_name': '/nonewsession',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/nonewsession',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


SESSION_ID_RULES = [{'session_id': 'undefined', 'error_code': '403'}]


@pytest.mark.eater(
    i10={'id': '10', 'personal_phone_id': 'p10', 'personal_email_id': 'e10'},
)
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize('device_id', ['', DEVICE_ID])
@pytest.mark.parametrize(
    'name,session,eats_user_id,partner_id,new_external_session',
    [
        ('New session', 'abcdef', '10', None, '123'),
        ('Logged in', 'abcdef', '10', None, '123'),
        ('Logged in', 'abcdef', None, '10', '123'),
        ('Logged in', 'abcdef', '10', '10', '123'),
        ('no session', None, '10', None, '123'),
    ],
)
async def test_session(
        taxi_eats_authproxy,
        mockserver,
        mock_core_eater,
        eats_user_id,
        partner_id,
        name,
        new_external_session,
        session,
        device_id,
        request,
):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        assert req.json == {
            'outer_session_id': session or '',
            'no_new_session': True,
        }
        assert req.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        assert req.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert req.headers['X-Device-Id'] == device_id
        data = {
            'inner_session_id': 'internal',
            'outer_session_id': new_external_session,
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }
        if session:
            if eats_user_id:
                data['eater_id'] = eats_user_id
            if partner_id:
                data['partner_user_id'] = partner_id
        data['bound_sessions'] = ['bound-session-1', 'bound-session-2']
        return data

    @mockserver.json_handler('test/123')
    def _mock_backend(req):
        assert req.headers['X-YaTaxi-Proxy'] == 'eats-authproxy'
        assert req.headers['X-YaTaxi-Session'] == 'eats:internal'
        assert req.headers['X-Eats-Session'] == 'internal'
        assert req.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
        assert (
            req.headers['X-YaTaxi-Bound-Sessions']
            == 'eats:bound-session-1,eats:bound-session-2'
        )
        assert req.cookies['PHPSESSID'] == 'internal'
        values = set()
        if eats_user_id or partner_id:
            if partner_id:
                values.add('eats_partner_user_id=' + str(partner_id))
            elif eats_user_id:
                values.add('eats_user_id=' + str(eats_user_id))
            for marker in request.node.iter_markers('eater'):
                data = marker.kwargs.get(
                    'i' + str(partner_id if partner_id else eats_user_id),
                )
                if data is not None:
                    personal_phone_id = data.get('personal_phone_id')
                    personal_email_id = data.get('personal_email_id')
                    if personal_phone_id:
                        values.add(
                            'personal_phone_id=' + str(personal_phone_id),
                        )
                    if personal_email_id:
                        values.add(
                            'personal_email_id=' + str(personal_email_id),
                        )
        if values:
            assert set(req.headers['X-YaTaxi-User'].split(',')) == values
            values = set(
                entry if not entry.startswith('eats_') else entry[5:]
                for entry in values
            )

            if 'user_id=' + str(eats_user_id) in values:
                values.add('eater_uuid=' + str(eats_user_id))

            if 'partner_user_id=' + str(partner_id) in values:
                values.add('eater_uuid=' + str(partner_id))

            assert set(req.headers['X-Eats-User'].split(',')) == values
            assert (
                req.headers['X-YaTaxi-Pass-Flags']
                == 'credentials=eats-session'
            )
        else:
            assert 'X-YaTaxi-User' not in req.headers
            assert 'X-Eats-User' not in req.headers
            assert set(req.headers['X-YaTaxi-Pass-Flags'].split(',')) == {
                'no-login',
                'credentials=eats-session',
            }

        headers = {'Set-Cookie': 'PHPSESSID=malformed'}
        body = {'id': '123'}
        return aiohttp.web.json_response(body, status=200, headers=headers)

    headers = {'X-Host': 'localhost', 'User-Agent': USER_AGENT_NATIVE}
    if device_id:
        headers['X-Device-Id'] = device_id
    if session:
        headers['Cookie'] = 'PHPSESSID=' + session

    response = await taxi_eats_authproxy.post(
        'test/123', data=json.dumps({}), headers=headers,
    )
    if not session:
        assert response.status_code == 401
    else:
        assert response.status_code == 200
        assert response.json() == {'id': '123'}
        cookies = [
            s.strip() for s in response.headers['Set-Cookie'].split(';')
        ]
        assert 'PHPSESSID=' + new_external_session in cookies
        assert response.headers['X-Eats-Session'] == new_external_session
        assert 'Max-Age=61' in cookies


@pytest.mark.eater(i100={})
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_session_with_deleted_user(
        request_proxy, mockserver, mock_core_eater, mock_eater_authorizer,
):
    response = await request_proxy(auth_method=None, url='test/123')
    assert response.status_code == 401


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_session_header(taxi_eats_authproxy, mockserver):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        assert request.json == {
            'outer_session_id': 'sss',
            'no_new_session': False,
        }
        assert (
            request.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        )
        assert request.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert request.headers['X-Device-Id'] == DEVICE_ID

        data = {
            'inner_session_id': 'internal',
            'outer_session_id': 'new',
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }

        return data

    @mockserver.json_handler('test401/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'internal'
        assert request.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
        return {'id': '123'}

    headers = {
        'X-Host': 'localhost',
        'User-Agent': USER_AGENT_NATIVE,
        'x-eats-session': 'sss',
        'X-Device-Id': DEVICE_ID,
    }
    response = await taxi_eats_authproxy.post(
        'test401/123', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert response.headers['X-Eats-Session'] == 'new'


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_newsession_nocache(taxi_eats_authproxy, mockserver):
    counter = {'x': 1}

    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        assert request.json == {
            'outer_session_id': '',
            'no_new_session': False,
        }
        assert (
            request.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        )
        assert request.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert request.headers['X-Device-Id'] == DEVICE_ID

        counter['x'] += 1
        data = {
            'inner_session_id': 'internal',
            'outer_session_id': str(counter['x']),
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }

        return data

    @mockserver.json_handler('test401/123')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'internal'
        assert request.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
        return {'id': '123'}

    headers = {
        'X-Host': 'localhost',
        'User-Agent': USER_AGENT_NATIVE,
        'X-Device-Id': DEVICE_ID,
    }
    response = await taxi_eats_authproxy.post(
        'test401/123', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert response.headers['X-Eats-Session'] == '2'

    response = await taxi_eats_authproxy.post(
        'test401/123', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert response.headers['X-Eats-Session'] == '3'


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_proxy401_nosession(taxi_eats_authproxy, mockserver):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        assert request.json == {
            'outer_session_id': '',
            'no_new_session': False,
        }

        data = {
            'inner_session_id': 'internal',
            'outer_session_id': 'outer',
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }

        return data

    @mockserver.json_handler('401/test')
    def _mock_backend(request):
        assert request.headers['X-YaTaxi-Proxy'] == 'eats-authproxy'
        assert 'Cookie' in request.headers
        assert 'X-YaTaxi-Session' in request.headers
        assert 'X-Eats-Session' in request.headers
        assert 'X-Eats-Session-Type' in request.headers
        return {'id': '123'}

    response = await taxi_eats_authproxy.post(
        '401/test', data=json.dumps({}), headers={'X-Host': 'localhost'},
    )

    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize(
    'url,proxy401',
    [
        pytest.param('401/test', True, id='proxy401 and no_new_session'),
        pytest.param('proxy401/test', True, id='Only proxy401'),
        pytest.param('nonewsession/test', False, id='Only no_new_session'),
    ],
)
async def test_nosession(taxi_eats_authproxy, mockserver, url, proxy401):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        assert req.json == {
            'outer_session_id': '',
            'no_new_session': not proxy401,
        }
        assert req.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        assert req.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert req.headers['X-Device-Id'] == ''

        if req.json['no_new_session']:
            return mockserver.make_response(
                json={'code': 'SESSION_NOT_FOUND', 'message': 'not found'},
                status=404,
            )

        return {
            'inner_session_id': 'internal',
            'outer_session_id': 'outer',
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }

    @mockserver.json_handler(url)
    def _mock_backend(request):
        assert request.headers['X-YaTaxi-Proxy'] == 'eats-authproxy'
        if not proxy401:
            assert 'Cookie' not in request.headers
            assert 'X-YaTaxi-Session' not in request.headers
            assert 'X-Eats-Session' not in request.headers
            assert 'X-Eats-Session-Type' not in request.headers
        else:
            assert request.cookies['PHPSESSID'] == 'internal'
            assert (
                request.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
            )
        return {'id': '123'}

    response = await taxi_eats_authproxy.post(
        url, data=json.dumps({}), headers={'X-Host': 'localhost'},
    )

    assert _mock_sessions.times_called == 1

    if not proxy401:
        assert response.status_code == 401
    else:
        assert response.status_code == 200
        assert response.json() == {'id': '123'}
        assert response.headers['X-Eats-Session'] == 'outer'


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_proxy401_oksession(taxi_eats_authproxy, mockserver):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        assert request.json == {
            'outer_session_id': 'sss',
            'no_new_session': False,
        }
        assert (
            request.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        )
        assert request.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert request.headers['X-Device-Id'] == DEVICE_ID

        data = {
            'inner_session_id': 'internal',
            'outer_session_id': 'outer',
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }

        return data

    @mockserver.json_handler('401/test')
    def _mock_backend(request):
        assert request.headers['X-YaTaxi-Proxy'] == 'eats-authproxy'
        assert request.cookies['PHPSESSID'] == 'internal'
        assert request.headers['X-Eats-Session'] == 'internal'
        assert request.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
        assert set(request.headers['X-YaTaxi-Pass-Flags'].split(',')) == {
            'no-login',
            'credentials=eats-session',
        }
        return {'id': '123'}

    headers = {
        'X-Host': 'localhost',
        'User-Agent': USER_AGENT_NATIVE,
        'x-eats-session': 'sss',
        'X-Device-Id': DEVICE_ID,
    }
    response = await taxi_eats_authproxy.post(
        '401/test', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert response.headers['X-Eats-Session'] == 'outer'


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_proxy401_badsession(taxi_eats_authproxy, mockserver):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        assert request.json == {
            'outer_session_id': 'sss',
            'no_new_session': True,
        }
        assert (
            request.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        )
        assert request.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert request.headers['X-Device-Id'] == DEVICE_ID

        return mockserver.make_response(
            json={'code': 'SESSION_NOT_FOUND', 'message': 'not found'},
            status=404,
        )

    @mockserver.json_handler('test/401')
    def _mock_backend(request):
        assert request.cookies['PHPSESSID'] == 'internal'
        return {'id': '123'}

    headers = {
        'X-Host': 'localhost',
        'User-Agent': USER_AGENT_NATIVE,
        'x-eats-session': 'sss',
        'X-Device-Id': DEVICE_ID,
    }
    response = await taxi_eats_authproxy.post(
        'test/401', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 401
    assert 'X-Eats-Session' not in response.headers
    assert 'X-Eats-Session-Type' not in response.headers


@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize(
    'url,proxy401',
    [
        pytest.param('401/test', True, id='proxy401 and no_new_session'),
        pytest.param('proxy401/test', True, id='Only proxy401'),
        pytest.param('nonewsession/test', False, id='Only no_new_session'),
    ],
)
async def test_badsession(taxi_eats_authproxy, mockserver, url, proxy401):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        assert req.json == {
            'outer_session_id': 'sss',
            'no_new_session': not proxy401,
        }
        assert req.headers['X-Request-Application'] == APPLICATION_NAME_NATIVE
        assert req.headers['X-Request-Application-Brand'] == BRAND_NATIVE
        assert req.headers['X-Device-Id'] == DEVICE_ID

        if req.json['no_new_session']:
            return mockserver.make_response(
                json={'code': 'SESSION_NOT_FOUND', 'message': 'not found'},
                status=404,
            )

        return {
            'inner_session_id': 'internal',
            'outer_session_id': 'outer',
            'ttl': 61,
            'session_type': SESSION_TYPE_NATIVE,
        }

    @mockserver.json_handler(url)
    def _mock_backend(request):
        assert request.headers['X-YaTaxi-Proxy'] == 'eats-authproxy'
        if not proxy401:
            assert 'Cookie' not in request.headers
            assert 'X-YaTaxi-Session' not in request.headers
            assert 'X-Eats-Session' not in request.headers
            assert 'X-Eats-Session-Type' not in request.headers
        else:
            assert request.cookies['PHPSESSID'] == 'internal'
            assert (
                request.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
            )
        return {'id': '123'}

    headers = {
        'X-Host': 'localhost',
        'User-Agent': USER_AGENT_NATIVE,
        'x-eats-session': 'sss',
        'X-Device-Id': DEVICE_ID,
    }
    response = await taxi_eats_authproxy.post(
        url, data=json.dumps({}), headers=headers,
    )

    if not proxy401:
        assert response.status_code == 401
        assert 'X-Eats-Session' not in response.headers
        assert 'X-Eats-Session-Type' not in response.headers
    else:
        assert response.status_code == 200
        assert response.json() == {'id': '123'}
        assert response.headers['X-Eats-Session'] == 'outer'


@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_no_cache(taxi_eats_authproxy, mockserver):
    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        return {
            'inner_session_id': 'internal',
            'outer_session_id': 'outer',
            'ttl': 61,
            'cache_enabled': False,
            'session_type': SESSION_TYPE_NATIVE,
        }

    @mockserver.json_handler('401/test')
    def _mock_backend(request):
        assert request.headers['X-Eats-Session-Type'] == SESSION_TYPE_NATIVE
        return {'id': '123'}

    for _i in [1, 2]:
        response = await taxi_eats_authproxy.post(
            '401/test',
            data=json.dumps({}),
            headers={'x-eats-session': 'sss', 'X-Host': 'localhost'},
        )
        assert response.status_code == 200

    assert _mock_sessions.next_call()
    assert _mock_sessions.next_call()


@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.config(EATS_AUTHPROXY_SESSION_ID_RULES=SESSION_ID_RULES)
async def test_invalid_session(taxi_eats_authproxy, mockserver):
    session = 'undefined'
    eats_user_id = '123'

    @mockserver.json_handler('eater-authorizer/v2/eater/sessions')
    def _mock_sessions(request):
        return {
            'inner_session_id': session,
            'outer_session_id': session,
            'ttl': 61,
            'cache_enabled': False,
            'session_type': SESSION_TYPE_NATIVE,
            'eater_id': eats_user_id,
        }

    @mockserver.json_handler('test/123')
    def _mock_noproxy_backend(request):
        return {'id': '123'}

    @mockserver.json_handler('401/test')
    def _mock_proxy_backend(request):
        return {'id': '123'}

    headers = {
        'X-Host': 'localhost',
        'User-Agent': USER_AGENT_NATIVE,
        'X-Device-Id': DEVICE_ID,
        'Cookie': 'PHPSESSID=' + session,
    }
    response = await taxi_eats_authproxy.post(
        'test/123', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 403
    assert 'X-Eats-Session' not in response.headers
    assert 'X-Eats-Session-Type' not in response.headers

    response = await taxi_eats_authproxy.post(
        '401/test', data=json.dumps({}), headers=headers,
    )
    assert response.status_code == 403
    assert 'X-Eats-Session' not in response.headers
    assert 'X-Eats-Session-Type' not in response.headers

    assert not _mock_sessions.has_calls
    assert not _mock_noproxy_backend.has_calls
    assert not _mock_proxy_backend.has_calls
