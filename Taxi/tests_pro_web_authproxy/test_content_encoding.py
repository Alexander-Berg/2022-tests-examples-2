import base64
import json

import pytest


@pytest.mark.passport_session(session1={'uid': '100'})
async def test_route_content_encoding(
        taxi_pro_web_authproxy, blackbox_service, mockserver,
):
    @mockserver.handler('/test')
    def _test(request):
        assert request.headers['Accept-Encoding'] == 'deflate'
        return mockserver.make_response(
            base64.b64decode('eJwrSS0u0c0tTtetgAMATacIEg=='),
            status=200,
            headers={'Content-Encoding': 'deflate'},
        )

    response = await taxi_pro_web_authproxy.post(
        'test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Cookie': 'Session_id=session1',
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-Real-IP': '1.2.3.4',
            'Accept-Encoding': 'deflate',
        },
    )
    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.headers['Content-Encoding'] == 'deflate'
    assert response.content == b'test-msg-xxxxxxxxxx'
