import json

import pytest


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_session(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/123')
    def _test(request):

        # Auth headers
        assert request.headers['X-Yandex-Uid'] == '100'

        return {'id': '123'}

    response = await taxi_edc_authproxy.post(
        '4.0/123',
        data=json.dumps({}),
        headers={'Cookie': 'Session_id=session1'},
    )
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_invalid_token(taxi_edc_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/4.0/123')
    def _test(request):
        assert False

    response = await taxi_edc_authproxy.post(
        '4.0/123',
        data=json.dumps({}),
        headers={'Cookie': 'Session_id=invalid_session'},
    )
    assert response.status_code == 401


async def test_no_session(taxi_edc_authproxy, blackbox_service, mockserver):
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
