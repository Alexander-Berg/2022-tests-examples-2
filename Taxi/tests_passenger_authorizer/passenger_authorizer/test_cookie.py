import json

import pytest


@pytest.mark.config(PASS_AUTH_COOKIE_PATHS={'eats': '/4.0/cookie'})
async def test_token(taxi_passenger_authorizer, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/cookie')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/cookie',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    expected_cookie_attributes = {
        'path': '/4.0/cookie',
        'max-age': '3600',
        'secure': True,
        'httponly': True,
    }
    _check_response_cookies(
        response,
        {
            'webviewtoken': ('test_token', expected_cookie_attributes),
            'webviewuserid': ('12345', expected_cookie_attributes),
        },
    )


@pytest.mark.config(PASS_AUTH_COOKIE_PATHS={'eats': '/4.0'})
@pytest.mark.parametrize(
    'input_suffix,output_suffix', [('', '_eats'), ('_eats', '_eats')],
)
async def test_use_cookie_suffix(
        taxi_passenger_authorizer,
        blackbox_service,
        mockserver,
        input_suffix,
        output_suffix,
):
    @mockserver.json_handler('/4.0/cookie-suffix')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/cookie-suffix',
        data=json.dumps({}),
        headers={
            'Cookie': (
                'webviewtoken'
                + input_suffix
                + '=test_token; webviewuserid'
                + input_suffix
                + '=12345'
            ),
        },
    )
    assert response.status_code == 200

    expected_cookie_attributes = {
        'path': '/4.0',
        'max-age': '3600',
        'secure': True,
        'httponly': True,
    }
    _check_response_cookies(
        response,
        {
            'webviewtoken': ('test_token', expected_cookie_attributes),
            'webviewuserid': ('12345', expected_cookie_attributes),
            'webviewtoken'
            + output_suffix: ('test_token', expected_cookie_attributes),
            'webviewuserid'
            + output_suffix: ('12345', expected_cookie_attributes),
        },
    )


@pytest.mark.config(
    PASS_AUTH_COOKIE_PATHS={'eats': '/4.0', 'grocery': '/grocery/4.0'},
)
async def test_use_cookie_suffixes(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/cookie-suffixes')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Login'] == 'login'
        assert request.headers['X-Login-Id'] == 'login_id'
        assert request.headers['X-Yandex-Uid'] == '100'
        assert (
            request.headers['X-YaTaxi-Pass-Flags']
            == 'phonish,credentials=token-bearer'
        )
        assert request.headers['X-YaTaxi-UserId'] == '12345'

        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/cookie-suffixes',
        data=json.dumps({}),
        headers={
            'Cookie': (
                'webviewtoken_eats'
                + '=test_token; webviewuserid_eats'
                + '=12345'
            ),
        },
    )
    assert response.status_code == 200

    expected_cookie_attributes_eats = {
        'path': '/4.0',
        'max-age': '3600',
        'secure': True,
        'httponly': True,
    }

    expected_cookie_attrs_grocery = {
        'path': '/grocery/4.0',
        'max-age': '3600',
        'secure': True,
        'httponly': True,
    }
    _check_response_cookies(
        response,
        {
            'webviewtoken': ('test_token', expected_cookie_attrs_grocery),
            'webviewuserid': ('12345', expected_cookie_attrs_grocery),
            'webviewtoken'
            + '_eats': ('test_token', expected_cookie_attributes_eats),
            'webviewtoken'
            + '_grocery': ('test_token', expected_cookie_attrs_grocery),
            'webviewuserid'
            + '_eats': ('12345', expected_cookie_attributes_eats),
            'webviewuserid'
            + '_grocery': ('12345', expected_cookie_attrs_grocery),
        },
    )


async def test_nouse_cookie(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/get')
    def _test(request):
        return {}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/get',
        data=json.dumps({}),
        headers={
            'Cookie': 'webviewtoken=test_token',
            'X-YaTaxi-UserId': '12345',
        },
    )
    assert response.status_code == 401
    assert 'Set-Cookie' not in response.headers


async def test_token_nocookie(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/get')
    def _test(request):
        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/get',
        data=json.dumps({}),
        bearer='test_token',
        headers={'X-YaTaxi-UserId': '12345'},
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert 'Set-Cookie' not in response.headers


def _check_response_cookies(response, expected_cookies):
    for key, expected_cookie in expected_cookies.items():
        assert key in response.cookies
        value, attributes = expected_cookie
        cookie = response.cookies[key]
        assert cookie.value == value
        for attr_key, attr_val in attributes.items():
            assert cookie[attr_key] == attr_val
