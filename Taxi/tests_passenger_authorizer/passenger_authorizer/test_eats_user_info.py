import copy

import pytest

import utils


AM_ROUTING_RULE = utils.make_rule(
    {
        'input': {'prefix': '/4.0/proxy'},
        'output': {'upstream': {'$mockserver': '/upstream'}},
        'proxy': {
            'auth_type': 'oauth-or-session',
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'staff_login': False,
            },
        },
        'rule_type': 'passenger-authorizer',
    },
)


def _make_eats_v1_user_response(eats_user_id):
    return {
        'isSuccess': True,
        'payload': {
            'user': {'id': eats_user_id, 'payment_methods': []},
            'session_key': 'a152ntOVXQWezyNdABklSjKcdowbWEoLQoY9bkeq65jJ4=',
            'offer': {
                'deliveryTime': None,
                'fromTime': '2020-01-16T15:26:02+03:00',
                'tillTime': '2020-01-16T15:36:02+03:00',
                'counter': 0,
                'location': {'latitude': 59.959408, 'longitude': 30.406607},
            },
            'is_user_has_order': False,
        },
    }


def _make_eaters_info_by_uid_response(
        mockserver,
        eats_user_id,
        personal_phone_id=None,
        personal_email_id=None,
):
    if eats_user_id == 'error':
        return mockserver.make_response(status=402)
    if eats_user_id:
        return {
            'eater': {
                'id': eats_user_id,
                'uuid': 'uuid' + str(eats_user_id),
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
                'personal_phone_id': personal_phone_id,
                'personal_email_id': personal_email_id,
            },
        }

    return mockserver.make_response(
        headers={'X-YaTaxi-Error-Code': 'code'},
        json={'code': 'eater_not_found', 'message': 'not found'},
        status=404,
    )


@pytest.fixture(name='upstream')
def _upstream(mockserver, eats_user_id):
    @mockserver.json_handler('/upstream/4.0/proxy')
    def mock_upstream(request):
        flags = request.headers.get('X-YaTaxi-User', '')
        if eats_user_id is not None:
            assert f'eats_user_id={eats_user_id}' in flags
        else:
            assert 'eats_user_id' not in flags

        return {'id': '123'}

    return mock_upstream


@pytest.mark.routing_rules([AM_ROUTING_RULE])
@pytest.mark.passport_token(token={'uid': '100'})
@pytest.mark.parametrize(
    'eats_user_id,fallback_request_to_eats_core',
    [(None, True), ('eats-11', False), ('error', False)],
)
async def test_proxy_pa(
        taxi_passenger_authorizer,
        blackbox_service,
        eats_user_id,
        fallback_request_to_eats_core,
        mockserver,
        upstream,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def mock_eats_eaters(request):
        assert 'X-Api-Token' not in request.headers
        assert request.json['passport_uid'] == '100'
        assert 'PHPSESSID' not in request.cookies
        return _make_eaters_info_by_uid_response(mockserver, eats_user_id)

    @mockserver.json_handler('eats-core-eater/find-by-passport-uid')
    def mock_eats_core(request):
        assert 'X-Api-Token' not in request.headers
        assert request.json['passport_uid'] == '100'
        assert 'PHPSESSID' not in request.cookies
        return _make_eaters_info_by_uid_response(mockserver, eats_user_id)

    response = await taxi_passenger_authorizer.get(
        '/4.0/proxy', bearer='token', headers={'X-YaTaxi-UserId': '12345'},
    )

    if eats_user_id != 'error':
        assert response.status_code == 200
        assert response.json() == {'id': '123'}
        assert 'set-cookie' not in response.headers
        assert upstream.times_called == 1
    else:
        assert response.status_code == 500
        assert upstream.times_called == 0

    assert mock_eats_eaters.times_called == 1
    fallback_times_called = 1 if fallback_request_to_eats_core else 0
    assert mock_eats_core.times_called == fallback_times_called


@pytest.mark.passport_token(token={'uid': '100'})
@pytest.mark.parametrize('email_id', [None, 'qwe123'])
@pytest.mark.parametrize('phone_id', [None, 'asd456'])
@pytest.mark.parametrize('need_eats_eater_id', [True, False])
@pytest.mark.parametrize('need_eats_eater_uuid', [True, False])
@pytest.mark.parametrize('need_eats_email_id', [True, False])
@pytest.mark.parametrize('need_eats_phone_id', [True, False])
async def test_eats_user_header(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        email_id,
        phone_id,
        need_eats_eater_id,
        need_eats_eater_uuid,
        need_eats_email_id,
        need_eats_phone_id,
        routing_rules,
):
    am_rule = copy.deepcopy(AM_ROUTING_RULE)
    am_rule['proxy']['personal'] = {
        'eater_id': need_eats_eater_id,
        'eater_uuid': need_eats_eater_uuid,
        'staff_login': False,
        'eats_email_id': need_eats_email_id,
        'eats_phone_id': need_eats_phone_id,
    }
    routing_rules.set_rules([am_rule])
    eats_user_id = 'user123'

    header_must_exist = need_eats_eater_id or need_eats_eater_uuid
    header_must_exist = header_must_exist or (
        need_eats_email_id and email_id is not None
    )
    header_must_exist = header_must_exist or (
        need_eats_phone_id and phone_id is not None
    )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def mock_eats_eaters(request):
        assert 'X-Api-Token' not in request.headers
        assert request.json['passport_uid'] == '100'
        assert 'PHPSESSID' not in request.cookies
        return _make_eaters_info_by_uid_response(
            mockserver, eats_user_id, phone_id, email_id,
        )

    @mockserver.json_handler('/upstream/4.0/proxy')
    def mock_upstream(request):
        if header_must_exist:
            assert 'X-Eats-User' in request.headers

            flags = {}
            for entry in request.headers['X-Eats-User'].split(','):
                key, value = entry.split('=')
                flags[key] = value

            if need_eats_eater_id:
                assert flags['user_id'] == eats_user_id

            if need_eats_eater_uuid:
                assert flags['eater_uuid'] == 'uuid' + str(eats_user_id)

            if need_eats_email_id and email_id is not None:
                assert flags.get('personal_email_id') == email_id
            else:
                assert 'personal_email_id' not in flags
            if need_eats_phone_id and phone_id is not None:
                assert flags.get('personal_phone_id') == phone_id
            else:
                assert 'personal_phone_id' not in flags
        else:
            assert 'X-Eats-User' not in request.headers

        return {'id': '123'}

    response = await taxi_passenger_authorizer.get(
        '/4.0/proxy', bearer='token', headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert mock_upstream.times_called == 1

    if (
            need_eats_eater_id
            or need_eats_eater_uuid
            or need_eats_email_id
            or need_eats_phone_id
    ):
        assert mock_eats_eaters.times_called == 1
    else:
        assert mock_eats_eaters.times_called == 0


@pytest.mark.parametrize('eats_user_id', [None])
@pytest.mark.routing_rules(
    [
        {
            **AM_ROUTING_RULE,
            **{
                'proxy': {
                    'auth_type': 'oauth-or-session',
                    'late_login_allowed': True,
                    'personal': {
                        'eater_id': True,
                        'eater_uuid': True,
                        'staff_login': False,
                        'eats_email_id': False,
                        'eats_phone_id': False,
                    },
                },
            },
        },
    ],
)
async def test_late_login(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        upstream,
        eats_user_id,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters(request):
        assert False

    response = await taxi_passenger_authorizer.get(
        '/4.0/proxy', headers={'X-YaTaxi-UserId': 'z12345'},
    )

    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert 'set-cookie' not in response.headers
    assert upstream.times_called == 1


@pytest.mark.parametrize(
    'eats_user_id, allow_unauthorized, expect_unauthorized, '
    'enable_session_router',
    [
        (None, False, True, True),
        (None, True, False, True),
        (None, True, False, False),
        ('eats-11', False, True, False),
        ('eats-11', False, False, True),
    ],
)
async def test_proxy_session(
        taxi_passenger_authorizer,
        eats_user_id,
        allow_unauthorized,
        expect_unauthorized,
        mockserver,
        upstream,
        enable_session_router,
        routing_rules,
):
    am_rule = copy.deepcopy(AM_ROUTING_RULE)
    am_rule['proxy']['proxy_401'] = allow_unauthorized

    if enable_session_router:
        am_rule['proxy']['auth_type'] = 'eats-php-session-id'

    routing_rules.set_rules([am_rule])

    @mockserver.json_handler('eats-core-http/v1/user')
    def mock_eats_core(request):
        assert request.headers['X-Api-Token'] == '777'
        assert request.cookies['PHPSESSID'] == '53535'
        assert 'X-YaTaxi-UserId' not in request.headers
        assert 'X-Yandex-UID ' not in request.headers
        return _make_eats_v1_user_response(eats_user_id)

    response = await taxi_passenger_authorizer.get(
        '/4.0/proxy',
        headers={
            'X-YaTaxi-UserId': '12345',
            'Cookie': 'PHPSESSID=53535; token=aa',
        },
    )
    if expect_unauthorized:
        assert response.status_code == 401
        assert upstream.times_called == 0
    else:
        assert response.status_code == 200
        assert upstream.times_called == 1
        if enable_session_router:
            set_cookie = response.headers['set-cookie']
            assert 'PHPSESSID=53535' in set_cookie
            assert 'Max-Age=2592000' in set_cookie
            assert 'Path=/' in set_cookie
            assert 'HttpOnly' in set_cookie
            assert 'Secure' in set_cookie
        else:
            assert 'set-cookie' not in response.headers

    if enable_session_router:
        assert mock_eats_core.times_called == 1
    else:
        assert mock_eats_core.times_called == 0


@pytest.mark.passport_token(token={'uid': '100'})
@pytest.mark.parametrize(
    'enable_session_router, expected_response_code',
    [(False, 200), (True, 401)],
)
async def test_passport_or_session(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        enable_session_router,
        expected_response_code,
        routing_rules,
):
    am_rule = copy.deepcopy(AM_ROUTING_RULE)

    if enable_session_router:
        am_rule['proxy']['auth_type'] = 'eats-php-session-id'

    routing_rules.set_rules([am_rule])

    @mockserver.json_handler('eats-core-http/v1/user')
    def _mock_eats_core(request):
        return _make_eats_v1_user_response(eats_user_id=None)

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eats_eaters_tvm(request):
        return _make_eaters_info_by_uid_response(mockserver, eats_user_id=None)

    @mockserver.json_handler('eats-core-eater/find-by-passport-uid')
    def _mock_eats_core_tvm(request):
        return _make_eaters_info_by_uid_response(mockserver, eats_user_id=None)

    @mockserver.json_handler('/upstream/4.0/proxy')
    def _mock_upstream(request):
        return {'id': '123'}

    response = await taxi_passenger_authorizer.get(
        '/4.0/proxy',
        bearer='token',
        headers={'X-YaTaxi-UserId': '12345', 'Cookie': 'PHPSESSID=53535'},
    )

    assert response.status_code == expected_response_code
