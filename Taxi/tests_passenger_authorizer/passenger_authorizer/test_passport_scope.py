import json

import pytest


async def test_scope(taxi_passenger_authorizer, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/scope')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100', scope='scope')

    response = await taxi_passenger_authorizer.post(
        '4.0/scope',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200


UA_YANDEX_TAXI_ANDROID = (
    'yandex-taxi/3.113.0.85658 Android/9' ' (OnePlus; ONEPLUS A5010)'
)
UA_UBER_ANDROID = (
    'yandex-uber/3.113.0.85658 Android/9' ' (OnePlus; ONEPLUS A5010)'
)


@pytest.mark.parametrize(
    'user_agent, request_brand',
    [
        (UA_YANDEX_TAXI_ANDROID, 'yataxi'),
        (UA_UBER_ANDROID, 'yauber'),
        ('unknown', 'default'),
    ],
)
@pytest.mark.parametrize(
    'scope, scope_brand',
    [
        ('yataxi:write', 'yataxi'),
        ('yauber:write', 'yauber'),
        ('default:write', 'default'),
        ('unknown', 'unknown'),
    ],
)
async def test_scope_by_brand(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        user_agent,
        request_brand,
        scope,
        scope_brand,
):
    @mockserver.json_handler('/4.0/')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100', scope=scope)

    response = await taxi_passenger_authorizer.post(
        '4.0/',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345', 'User-Agent': user_agent},
    )
    if scope_brand == request_brand:
        expected_code = 200
    else:
        expected_code = 401
    assert response.status_code == expected_code


async def test_otherscope(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/scope')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info(
        'test_token', uid='100', scope='otherscope',
    )
    response = await taxi_passenger_authorizer.post(
        '4.0/scope',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 401


async def test_noscope(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/scope')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100', scope='')

    response = await taxi_passenger_authorizer.post(
        '4.0/scope',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 401


async def test_noscope_required(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/noscope')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100', scope='')

    response = await taxi_passenger_authorizer.post(
        '4.0/noscope',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200


async def test_scope_pass(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    called = {'called': 0}

    @mockserver.json_handler('/4.0/scope-pass')
    def _test(request):
        called['called'] += 1

        # Auth headers
        assert 'X-Yandex-Uid' not in request.headers
        assert 'X-Yandex-UID' not in request.headers

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100', scope='')

    response = await taxi_passenger_authorizer.post(
        '4.0/scope-pass',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert called['called'] == 1
