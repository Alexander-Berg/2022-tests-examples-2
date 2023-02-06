import base64
import json


async def test_route_content_encoding(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test': 0}

    @mockserver.handler('/4.0/test')
    def _test(request):
        stats['call-test'] += 1

        assert request.headers['Accept-Encoding'] == 'deflate'

        return mockserver.make_response(
            base64.b64decode('eJwrSS0u0c0tTtetgAMATacIEg=='),
            status=200,
            headers={'Content-Encoding': 'deflate'},
        )

    blackbox_service.set_token_info('test_token', uid='100')

    response = await taxi_passenger_authorizer.post(
        '4.0/test',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='test_token',
        headers={
            'Content-Type': 'application/json',
            'X-Forwarded-For': 'old-host',
            'X-YaTaxi-UserId': '12345',
            'X-Real-IP': '1.2.3.4',
            'Accept-Encoding': 'deflate',
        },
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.headers['Content-Encoding'] == 'deflate'
    assert response.content == b'test-msg-xxxxxxxxxx'
