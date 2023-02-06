import json

import pytest


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:write'})
async def test_token(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/cookie')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/cookie', data=json.dumps({}), bearer='token1',
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
        response, {'edctoken': ('token1', expected_cookie_attributes)},
    )


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:write'})
async def test_use_cookie(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/cookie')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/cookie',
        data=json.dumps({}),
        headers={'Cookie': 'edctoken=token1'},
    )
    assert response.status_code == 200

    expected_cookie_attributes = {
        'path': '/4.0/cookie',
        'max-age': '3600',
        'secure': True,
        'httponly': True,
    }
    _check_response_cookies(
        response, {'edctoken': ('token1', expected_cookie_attributes)},
    )


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:write'})
async def test_nouse_cookie(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/get')
    def _test(request):
        return {}

    response = await taxi_edc_authproxy.post(
        '4.0/get', data=json.dumps({}), headers={'Cookie': 'edctoken=token1'},
    )
    assert response.status_code == 401
    assert 'Set-Cookie' not in response.headers


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:write'})
async def test_token_nocookie(
        taxi_edc_authproxy, blackbox_service, mockserver,
):
    @mockserver.json_handler('/4.0/get')
    def _test(request):
        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/get', data=json.dumps({}), bearer='token1',
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
