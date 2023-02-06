async def test_bookings_cancel(taxi_scooters_mostrans, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def _mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        return {
            'user': {'user_id': 'user_id'},
            'segment': {
                'car_number': '103',
                'session': {
                    'specials': {
                        'free_time': 270,
                        'current_offer': {
                            'constructor_id': 'some_tariff',
                            'type': 'main',
                            'prices': {'acceptance_cost': 0, 'riding': 0},
                        },
                        'current_offer_state': {},
                    },
                },
                'meta': {
                    'start': 1655467280,
                    'user_id': 'user_id',
                    'object_id': 'scooter_103_id',
                    'instance_id': 'instance',
                    'session_id': 'session_id',
                },
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/drop')
    def mock_sessions_drop(request):
        assert request.query['session_id'] == 'session_id'
        assert request.headers['UserIdDelegation'] == 'user_id'
        return {}

    response = await taxi_scooters_mostrans.post(
        '/bookings/session_id/cancel',
        {},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert mock_sessions_drop.times_called == 1


async def test_bookings_cancel_not_found(taxi_scooters_mostrans, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/drop')
    def mock_sessions_drop(request):
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        return {'user': {'user_id': 'user_id'}}

    response = await taxi_scooters_mostrans.post(
        '/bookings/session_id/cancel',
        {},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 404
    assert mock_sessions_drop.times_called == 1
    assert mock_sessions_current.times_called == 1


async def test_bookings_cancel_error(taxi_scooters_mostrans, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/drop')
    def mock_sessions_drop(request):
        return mockserver.make_response(status=400, json={})

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        return {
            'user': {'user_id': 'user_id'},
            'segment': {
                'session': {
                    'specials': {
                        'current_offer': {
                            'constructor_id': 'some_tariff',
                            'type': 'main',
                            'prices': {
                                'acceptance_cost': 0,
                                'riding': 0,
                                'insurance_price': 0,
                            },
                        },
                        'current_offer_state': {},
                    },
                },
                'meta': {
                    'user_id': 'user_id',
                    'object_id': 'scooter_1234',
                    'instance_id': 'instance',
                    'session_id': 'session_id',
                },
            },
        }

    response = await taxi_scooters_mostrans.post(
        '/bookings/session_id/cancel',
        {},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'Other',
        'message': '',
        'deeplink': 'yandextaxi://scooters',
    }
    assert mock_sessions_drop.times_called == 1
    assert mock_sessions_current.times_called == 1
