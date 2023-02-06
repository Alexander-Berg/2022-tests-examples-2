import pytest


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.parametrize('host', (None, 'invalid'))
async def test_set_x_forwarded_host(
        taxi_pro_web_authproxy, blackbox_service, mockserver, host,
):
    @mockserver.json_handler('/test')
    def _test(request):
        assert request.headers['X-Forwarded-Host'] == 'localhost:1180'
        return {'id': '123'}

    headers = {
        'Cookie': 'Session_id=session1',
        'X-Real-IP': '1.2.3.4',
        'X-Remote-Ip': 'remote',
    }
    if host:
        headers['X-Forwarded-Host'] = 'invalid'

    response = await taxi_pro_web_authproxy.post('test', headers=headers)

    assert response.status == 200
    assert _test.times_called == 1
