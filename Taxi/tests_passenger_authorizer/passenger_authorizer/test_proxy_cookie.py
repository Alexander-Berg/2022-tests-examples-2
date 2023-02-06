import json

import pytest

import utils


AM_ROUTE_RULES = [utils.make_rule({'input': {'prefix': '/4.0/proxy'}})]


@pytest.mark.passport_token(token={'uid': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_proxy_cookies(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    await taxi_passenger_authorizer.tests_control(invalidate_caches=True)
    stats = {'call-test': 0}

    @mockserver.json_handler('/4.0/proxy')
    def _test(request):
        stats['call-test'] += 1
        cookies = map(
            lambda x: x.strip(), request.headers['Cookie'].split(';'),
        )
        assert set(cookies) == set(['x=1', 'y=2'])

        return {'id': '123'}

    response = await taxi_passenger_authorizer.post(
        '4.0/proxy',
        data=json.dumps({'x': {'y': 1, 'z': 456}}),
        bearer='token',
        headers={'Cookie': 'x=1; y=2; z=3', 'X-YaTaxi-UserId': '12345'},
    )
    assert stats['call-test'] == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}
