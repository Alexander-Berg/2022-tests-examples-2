import json


async def test_probability_percent_30_70(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test-30': 0, 'call-test-70': 0}

    @mockserver.json_handler('/30/4.0/probability_percent/30_70')
    def _test_30(request):
        stats['call-test-30'] += 1
        return {'id': '123'}

    @mockserver.json_handler('/70/4.0/probability_percent/30_70')
    def _test_70(request):
        stats['call-test-70'] += 1
        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    for _ in range(200):
        response = await taxi_passenger_authorizer.post(
            '4.0/probability_percent/30_70',
            data=json.dumps({'x': {'y': 1, 'z': 456}}),
            bearer='test_token',
            headers={
                'Content-Type': 'application/json',
                'X-Forwarded-For': 'old-host',
                'X-YaTaxi-UserId': '12345',
                'X-Real-IP': '1.2.3.4',
            },
        )
        assert response.status_code == 200
        assert response.json() == {'id': '123'}

    assert stats['call-test-30'] > 0
    assert stats['call-test-70'] > 0
    assert stats['call-test-70'] + stats['call-test-30'] == 200
    assert stats['call-test-70'] > stats['call-test-30']


async def test_probability_percent_0_100(
        taxi_passenger_authorizer, blackbox_service, mockserver,
):
    stats = {'call-test-0': 0, 'call-test-100': 0}

    @mockserver.json_handler('/0/4.0/probability_percent/0_100')
    def _test_0(request):
        stats['call-test-0'] += 1
        return {'id': '123'}

    @mockserver.json_handler('/100/4.0/probability_percent/0_100')
    def _test_100(request):
        stats['call-test-100'] += 1
        return {'id': '123'}

    blackbox_service.set_token_info('test_token', uid='100')

    for _ in range(100):
        response = await taxi_passenger_authorizer.post(
            '4.0/probability_percent/0_100',
            data=json.dumps({'x': {'y': 1, 'z': 456}}),
            bearer='test_token',
            headers={
                'Content-Type': 'application/json',
                'X-Forwarded-For': 'old-host',
                'X-YaTaxi-UserId': '12345',
                'X-Real-IP': '1.2.3.4',
            },
        )
        assert response.status_code == 200
        assert response.json() == {'id': '123'}

    assert stats['call-test-0'] == 0
    assert stats['call-test-100'] == 100
