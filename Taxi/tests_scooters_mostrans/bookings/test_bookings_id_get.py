import pytest


@pytest.mark.now('2022-06-17T12:05:56+00:00')
@pytest.mark.config(
    SCOOTERS_MOSTRANS_FILTER={
        'imei_mod_factor': 0,
        'telematic_sensors': {
            'fuel_level_exists': True,
            'fuel_distance_exists': True,
        },
    },
    SCOOTERS_MOSTRANS_PRICES={
        'activation': {'exact': {'value': 50}},
        'insurance': {'base': {'value': 1}},
        'minute': {'range': {'min': 4, 'max': 6}},
    },
)
async def test_bookings_id(taxi_scooters_mostrans, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
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
                            'offer_id': 'offer_1',
                            'prices': {
                                'acceptance_cost': 5000,
                                'riding': 500,
                                'insurance_price': 140,
                            },
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
    def mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    response = await taxi_scooters_mostrans.get(
        '/bookings/session_id',
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': 'session_id',
        'status': 'Booked',
        'created_at': 1655467280,
        'booking_expires_at': 1655467826,
        'write_offs': [],
        'debts': [],
        'device': {
            'charge': 18,
            'code': '103',
            'location': {'lat': 55.897709, 'lon': 37.478066},
            'lock': {'lock_type': 'Electronic'},
            'price': {
                'activation': {
                    'exact': {'currency_code': 'RUB', 'value': 5000},
                },
                'insurance': {
                    'base': {'currency_code': 'RUB', 'value_base': 140},
                },
                'minute': {'exact': {'currency_code': 'RUB', 'value': 500}},
                'price_offer_id': 'offer_1',
            },
            'remain_km': 13.68,
            'type': 'scooter',
        },
    }
    assert mock_sessions_current.times_called == 1
    assert mock_car_details.times_called == 1


@pytest.mark.now('2022-06-17T12:05:56+00:00')
@pytest.mark.config(
    SCOOTERS_MOSTRANS_FILTER={
        'imei_mod_factor': 0,
        'telematic_sensors': {
            'fuel_level_exists': True,
            'fuel_distance_exists': True,
        },
    },
    SCOOTERS_MOSTRANS_PRICES={
        'activation': {'exact': {'value': 50}},
        'insurance': {'base': {'value': 1}},
        'minute': {'range': {'min': 4, 'max': 6}},
    },
)
async def test_bookings_not_found(
        taxi_scooters_mostrans, mockserver, load_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        return {'user': {'user_id': 'user_id'}}

    response = await taxi_scooters_mostrans.get(
        '/bookings/session_id',
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 404
    assert mock_sessions_current.times_called == 1
