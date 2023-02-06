import pytest

import utils


@pytest.mark.routing_rules([utils.make_rule({'proxy': {'proxy_401': True}})])
@pytest.mark.parametrize(
    'header',
    ['cookie', 'Cookie', 'COOKIE', 'Authorization', 'X-yataxi-authorization'],
)
async def test_priority_order(taxi_passenger_authorizer, mockserver, header):
    @mockserver.json_handler('/4.0/proxy')
    def mock(request):
        return {}

    async with taxi_passenger_authorizer.capture_logs() as capture:
        response = await taxi_passenger_authorizer.get(
            '/4.0/proxy', headers={header: '12345=ssecret'},
        )
        assert response.status_code == 200

        assert mock.times_called == 1

    logs = capture.select()
    for log in logs:
        assert 'ssecret' not in log.get('text', '')
