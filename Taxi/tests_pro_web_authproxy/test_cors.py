import pytest


CORS = {
    'allowed-origins': ['localhost', 'example.com'],
    'allowed-headers': [],
    'cache-max-age-seconds': 66,
}


@pytest.mark.config(PRO_WEB_AUTHPROXY_CORS=CORS)
@pytest.mark.parametrize('origin,ok_', [('localhost', True), ('evil', False)])
@pytest.mark.passport_session(session1={'uid': '100'})
async def test_cors(
        taxi_pro_web_authproxy, blackbox_service, mockserver, origin, ok_,
):
    @mockserver.json_handler('/test')
    def _test(request):
        assert 'X-Ya-User-Ticket' in request.headers
        return {'id': '123'}

    await taxi_pro_web_authproxy.invalidate_caches()

    response = await taxi_pro_web_authproxy.post(
        'test',
        data='123',
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'Origin': origin,
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
        },
    )

    if ok_:
        assert _test.has_calls

        # CORS
        assert response.headers['Access-Control-Allow-Credentials'] == 'true'
        assert response.headers['Access-Control-Allow-Headers'] == ''
        assert response.headers['Access-Control-Allow-Origin'] == origin
        methods = set(
            response.headers['Access-Control-Allow-Methods'].split(', '),
        )
        assert methods == set(
            ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'PATCH'],
        )
        assert response.headers['Access-Control-Max-Age'] == '66'
        assert response.status_code == 200
    else:
        assert not _test.has_calls
        assert response.status_code == 401
