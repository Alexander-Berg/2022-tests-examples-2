import pytest

import utils


AM_ROUTE_RULES = [
    utils.make_rule(
        {
            'proxy': {
                'auth_type': 'session_id-without-user_id',
                'proxy_401': True,
            },
        },
    ),
]


@pytest.mark.passport_session(session1={'uid': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
@pytest.mark.parametrize('userid', [None, '', '12345'])
async def test_happy_path(
        taxi_passenger_authorizer, blackbox_service, mockserver, userid,
):
    @mockserver.json_handler('/4.0/test')
    def mock(request):
        assert request.headers['X-Yandex-Login'] == 'login'
        assert 'X-YaTaxi-UserId' not in request.headers
        assert 'X-YaTaxi-Alleged-UserId' not in request.headers
        return {'id': '123'}

    headers = {'Cookie': 'Session_id=session1', 'X-Real-IP': '1.2.3.4'}
    if userid is not None:
        headers['X-YaTaxi-UserId'] = userid
    response = await taxi_passenger_authorizer.post(
        '4.0/test', data='{}', headers=headers,
    )
    assert mock.has_calls
    assert response.status_code == 200
