import pytest


SESSION_1 = {
    'car_number': '103',
    'session': {
        'specials': {
            'free_time': 270,
            'current_offer': {
                'constructor_id': 'some_tariff',
                'type': 'main',
                'prices': {'acceptance_cost': 0, 'riding': 500},
                'offer_id': 'offer_1',
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
    'device_diff': {
        'mileage': 250,
        'start': {'latitude': 12.34, 'longitude': 45.67},
    },
}

SESSION_2 = {
    'car_number': '102',
    'session': {
        'specials': {
            'current_offer': {
                'constructor_id': 'some_tariff',
                'type': 'main',
                'prices': {'acceptance_cost': 5000, 'riding': 500},
                'offer_id': 'offer_2',
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
    'device_diff': {
        'mileage': 120,
        'start': {'latitude': 12.34, 'longitude': 45.67},
    },
}


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
async def test_sessions(taxi_scooters_mostrans, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/history')
    def mock_sessions_history(request):
        assert request.query['user_id'] == 'user_id'
        return {
            'sessions': [
                {
                    'car': {'number': '103', 'model_id': 'ninebot'},
                    'segment': {
                        'session_id': 'session_1',
                        'events': [{'action': 'set_performer'}],
                    },
                },
                {
                    'car': {'number': '103', 'model_id': 'ninebot'},
                    'segment': {
                        'session_id': 'session_2',
                        'events': [{'action': 'set_performer'}],
                    },
                },
                {
                    'car': {'number': '108', 'model_id': 'ninebot'},
                    'segment': {
                        'session_id': 'ended_session',
                        'events': [
                            {'action': 'set_performer'},
                            {'action': 'drop_performer'},
                        ],
                    },
                },
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['user_id'] == 'user_id'
        session_responses = {'session_1': SESSION_1, 'session_2': SESSION_2}
        return {
            'user': {'user_id': 'user_id'},
            'segment': session_responses[request.query['session_id']],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == '102,103'
        return load_json('scooter_backend_car_details_response.json')

    response = await taxi_scooters_mostrans.get(
        '/sessions',
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'max_booking_duration': 300,
        'bookings': [
            {
                'booking_expires_at': 1655467826,
                'created_at': 1655467280,
                'debts': [],
                'device': {
                    'charge': 18,
                    'code': '103',
                    'location': {'lat': 55.897709, 'lon': 37.478066},
                    'lock': {'lock_type': 'Electronic'},
                    'price': {
                        'activation': {
                            'exact': {'currency_code': 'RUB', 'value': 0},
                        },
                        'insurance': {
                            'base': {'currency_code': 'RUB', 'value_base': 0},
                        },
                        'minute': {
                            'exact': {'currency_code': 'RUB', 'value': 500},
                        },
                        'price_offer_id': 'offer_1',
                    },
                    'remain_km': 13.68,
                    'type': 'scooter',
                },
                'id': 'session_id',
                'status': 'Booked',
                'write_offs': [],
            },
        ],
        'rentals': [
            {
                'created_at': 1655467280,
                'debts': [],
                'device': {
                    'charge': 18,
                    'code': '102',
                    'location': {'lat': 55.897709, 'lon': 37.478066},
                    'lock': {'lock_type': 'Electronic'},
                    'price': {
                        'activation': {
                            'exact': {'currency_code': 'RUB', 'value': 5000},
                        },
                        'insurance': {
                            'base': {'currency_code': 'RUB', 'value_base': 0},
                        },
                        'minute': {
                            'exact': {'currency_code': 'RUB', 'value': 500},
                        },
                        'price_offer_id': 'offer_2',
                    },
                    'remain_km': 13.68,
                    'type': 'scooter',
                },
                'distance_traveled': 120,
                'id': 'session_id',
                'price': {
                    'activation': {'currency_code': 'RUB', 'value': 5000},
                    'base': {'currency_code': 'RUB', 'value': 0},
                    'fine': {'currency_code': 'RUB', 'value': 0},
                    'insurance': {'currency_code': 'RUB', 'value': 0},
                    'is_final': False,
                },
                'start_location': {'lat': 12.34, 'lon': 45.67},
                'status': 'Rented',
                'write_offs': [],
            },
        ],
    }
    assert mock_sessions_history.times_called == 1
    assert mock_sessions_current.times_called == 2
