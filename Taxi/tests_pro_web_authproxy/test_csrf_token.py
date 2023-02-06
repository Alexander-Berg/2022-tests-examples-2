import pytest


async def do_request(taxi_pro_web_authproxy, url, headers=None):
    final_headers = {
        'Cookie': 'Session_id=session1',
        'Content-Type': 'application/json',
        'X-Forwarded-For': 'old-host',
        'X-Real-IP': '1.2.3.4',
        'Origin': 'localhost',
    }
    if headers:
        final_headers.update(headers)
        for key, value in headers.items():
            if value is None:
                del final_headers[key]
    return await taxi_pro_web_authproxy.post(
        url, data='{}', headers=final_headers,
    )


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_no_csrf(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        return 'xxx'

    response = await do_request(taxi_pro_web_authproxy, url='test')
    assert response.status_code == 200
    assert response.text == '"xxx"'


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.config(
    PRO_WEB_AUTHPROXY_CSRF_TOKEN_SETTINGS={
        'validation-enabled': True,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
async def test_csrf(taxi_pro_web_authproxy, blackbox_service, mockserver):
    @mockserver.json_handler('/test')
    def _test(request):
        return 'xxx'

    headers = {}

    response = await do_request(
        taxi_pro_web_authproxy, url='test', headers=headers,
    )
    assert response.status_code == 401
    assert response.json()['code'] == 'INVALID_CSRF_TOKEN'

    response = await do_request(
        taxi_pro_web_authproxy, url='csrf_token', headers=headers,
    )
    assert response.status_code == 200
    assert 'sk' in response.json()
    token = response.json()['sk']

    headers['X-Csrf-Token'] = token

    response = await do_request(
        taxi_pro_web_authproxy, url='test', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == 'xxx'
