import json

import pytest


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:write'})
async def test_token(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/123')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/123', data=json.dumps({}), bearer='token1',
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:write'})
async def test_invalid_token(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/123')
    def _test(request):
        assert False

    response = await taxi_edc_authproxy.post(
        '4.0/123', data=json.dumps({}), bearer='invalid_token',
    )
    assert response.status_code == 401


async def test_no_token(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/123')
    def _test(request):
        assert False

    response = await taxi_edc_authproxy.post('4.0/123', data=json.dumps({}))
    assert response.status_code == 401


async def test_proxy401(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/route401/123')
    def _test(request):
        # Auth headers
        assert 'X-Yandex-Uid' not in request.headers

        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/route401/123', data=json.dumps({}),
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'edc:read'})
async def test_bad_scope(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/123')
    def _test(request):
        assert False

    response = await taxi_edc_authproxy.post(
        '4.0/123', data=json.dumps({}), bearer='token1',
    )
    assert response.status_code == 401


@pytest.mark.passport_token(token1={'uid': '100', 'scope': 'scope'})
async def test_custom_scope(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/scope/123')
    def _test(request):
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/scope/123', data=json.dumps({}), bearer='token1',
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
