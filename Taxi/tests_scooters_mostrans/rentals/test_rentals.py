import copy

import pytest


AREAS = [
    {
        'id': 'parking_1',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
                [[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 0.0]],
            ],
        },
        'tags': ['allow_drop_car'],
        'revision': '1',
    },
]

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
        'session_id': 'session_1',
    },
    'device_diff': {
        'mileage': 0,
        'start': {'latitude': 12.34, 'longitude': 45.67},
    },
}

SESSION_1_AFTER_EVOLVE = {
    'car_number': '103',
    'session': {
        'specials': {
            'current_offer': {
                'constructor_id': 'some_tariff',
                'type': 'main',
                'prices': {'acceptance_cost': 5000, 'riding': 500},
                'offer_id': 'offer_1',
            },
            'current_offer_state': {'duration_price': 5000},
        },
    },
    'meta': {
        'start': 1655467280,
        'user_id': 'user_id',
        'object_id': 'scooter_103_id',
        'instance_id': 'instance',
        'session_id': 'session_1',
    },
    'device_diff': {
        'mileage': 0,
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
            'current_offer_state': {'duration_price': 15500},
        },
    },
    'meta': {
        'start': 1655467280,
        'user_id': 'user_id',
        'object_id': 'scooter_102_id',
        'instance_id': 'instance',
        'session_id': 'session_2',
    },
    'device_diff': {
        'mileage': 120,
        'start': {'latitude': 12.34, 'longitude': 45.67},
    },
}

SESSION_3 = {
    'car_number': '105',
    'session': {
        'specials': {
            'free_time': 300,
            'current_offer': {
                'constructor_id': 'some_tariff',
                'type': 'main',
                'prices': {'acceptance_cost': 5000, 'riding': 500},
                'offer_id': 'offer_3',
            },
            'current_offer_state': {},
        },
    },
    'meta': {
        'start': 1655467280,
        'user_id': 'user_id',
        'object_id': 'scooter_105_id',
        'instance_id': 'instance',
        'session_id': 'session_3',
    },
    'device_diff': {
        'mileage': 0,
        'start': {'latitude': 12.34, 'longitude': 45.67},
    },
}

SESSION_3_AFTER_EVOLVE = {
    'car_number': '105',
    'session': {
        'specials': {
            'current_offer': {
                'constructor_id': 'some_tariff',
                'type': 'main',
                'prices': {'acceptance_cost': 5000, 'riding': 500},
                'offer_id': 'offer_3',
            },
            'current_offer_state': {'duration_price': 5000},
        },
    },
    'meta': {
        'start': 1655467280,
        'user_id': 'user_id',
        'object_id': 'scooter_105_id',
        'instance_id': 'instance',
        'session_id': 'session_3',
    },
    'device_diff': {
        'mileage': 0,
        'start': {'latitude': 12.34, 'longitude': 45.67},
    },
}

SESSIONS_HISTORY = [
    {
        'car': {'number': '103', 'model_id': 'ninebot'},
        'segment': {
            'session_id': 'session_1',
            'events': [{'action': 'set_performer'}],
        },
    },
    {
        'car': {'number': '102', 'model_id': 'ninebot'},
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
]


@pytest.mark.parametrize(
    ['car_number', 'expected_book', 'expected_evolve', 'expected_response'],
    [
        pytest.param(
            '103',
            False,
            True,
            {
                'created_at': 1655467280,
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
                'distance_traveled': 0,
                'id': 'session_1',
                'price': {
                    'activation': {'currency_code': 'RUB', 'value': 5000},
                    'base': {'currency_code': 'RUB', 'value': 5000},
                    'fine': {'currency_code': 'RUB', 'value': 0},
                    'insurance': {'currency_code': 'RUB', 'value': 0},
                    'is_final': False,
                },
                'start_location': {'lat': 12.34, 'lon': 45.67},
                'status': 'Rented',
                'write_offs': [],
            },
            id='Only start ride',
        ),
        pytest.param(
            '102',
            False,
            False,
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
                'id': 'session_2',
                'price': {
                    'activation': {'currency_code': 'RUB', 'value': 5000},
                    'base': {'currency_code': 'RUB', 'value': 15500},
                    'fine': {'currency_code': 'RUB', 'value': 0},
                    'insurance': {'currency_code': 'RUB', 'value': 0},
                    'is_final': False,
                },
                'start_location': {'lat': 12.34, 'lon': 45.67},
                'status': 'Rented',
                'write_offs': [],
            },
            id='Ride already started',
        ),
        pytest.param(
            '105',
            True,
            True,
            {
                'created_at': 1655467280,
                'debts': [],
                'device': {
                    'charge': 18,
                    'code': '105',
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
                        'price_offer_id': 'offer_3',
                    },
                    'remain_km': 13.68,
                    'type': 'scooter',
                },
                'distance_traveled': 0,
                'id': 'session_3',
                'price': {
                    'activation': {'currency_code': 'RUB', 'value': 5000},
                    'base': {'currency_code': 'RUB', 'value': 5000},
                    'fine': {'currency_code': 'RUB', 'value': 0},
                    'insurance': {'currency_code': 'RUB', 'value': 0},
                    'is_final': False,
                },
                'start_location': {'lat': 12.34, 'lon': 45.67},
                'status': 'Rented',
                'write_offs': [],
            },
            id='Book and start',
        ),
    ],
)
async def test_rentals_post(
        taxi_scooters_mostrans,
        mockserver,
        load_json,
        car_number,
        expected_book,
        expected_evolve,
        expected_response,
):
    evolved = set()
    booked = {'session_1', 'session_2'}

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/history')
    def _mock_sessions_history(request):
        assert request.query['user_id'] == 'user_id'
        sessions = copy.deepcopy(SESSIONS_HISTORY)
        if 'session_3' in booked:
            sessions.append(
                {
                    'car': {'number': '105', 'model_id': 'ninebot'},
                    'segment': {
                        'session_id': 'session_3',
                        'events': [{'action': 'set_performer'}],
                    },
                },
            )
        return {'sessions': sessions}

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def _mock_sessions_current(request):
        assert request.query['user_id'] == 'user_id'
        assert request.query['session_id'] in {
            'session_1',
            'session_2',
            'session_3',
        }
        session_responses = {
            'session_1': (
                SESSION_1_AFTER_EVOLVE if 'session_1' in evolved else SESSION_1
            ),
            'session_2': SESSION_2,
            'session_3': (
                SESSION_3_AFTER_EVOLVE if 'session_3' in evolved else SESSION_3
            ),
        }
        return {
            'user': {'user_id': 'user_id'},
            'segment': session_responses[request.query['session_id']],
        }

    @mockserver.json_handler(
        '/scooter-backend/scooters/api/yandex/offers/book',
    )
    def mock_book(request):
        assert request.query == {}
        assert request.headers['X-Yandex-UID'] == 'uid'
        assert request.headers['X-YaTaxi-UserId'] == 'user_id'
        assert request.json == {'offer_id': 'offer_3'}
        booked.add('session_3')
        return {}

    @mockserver.json_handler('/scooter-backend/scooters/api/yandex/tag/evolve')
    def mock_tag_evolve(request):
        assert request.query == {'evolution_mode': 'ignore_telematic'}
        assert request.headers['X-Yandex-UID'] == 'uid'
        assert request.headers['X-YaTaxi-UserId'] == 'user_id'
        assert request.json['tag_name'] == 'old_state_riding'
        evolved.add(request.json['session_id'])
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == car_number
        response = load_json('scooter_backend_car_details_response.json')
        response['cars'][0]['number'] = request.query['car_number']
        if booked or not expected_book:
            response['cars'][0]['status'] = 'old_state_reservation'
        if evolved or not expected_evolve:
            response['cars'][0]['status'] = 'old_state_riding'
        return response

    request = {
        'user': {'location': {'lon': 12.34, 'lat': 45.67}},
        'code': car_number,
        'payment_info': {
            'payment_method': 'Card',
            'payment_system': 'Visa',
            'pan': '1234',
            'card_id': 'card_id',
            'token': 'payment_token',
            'email': 'email@email.ru',
            'price_offer_id': 'offer_3',
        },
        'with_insurance': False,
    }
    response = await taxi_scooters_mostrans.post(
        '/rentals',
        request,
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == expected_response
    assert mock_book.times_called == (1 if expected_book else 0)
    assert mock_tag_evolve.times_called == (1 if expected_evolve else 0)


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
async def test_rentals_id(taxi_scooters_mostrans, mockserver, load_json):
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
                            'prices': {'acceptance_cost': 0, 'riding': 0},
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
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    response = await taxi_scooters_mostrans.get(
        '/rentals/session_id',
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'created_at': 1655467280,
        'debts': [],
        'device': {
            'charge': 18,
            'code': '103',
            'location': {'lat': 55.897709, 'lon': 37.478066},
            'lock': {'lock_type': 'Electronic'},
            'price': {
                'activation': {'exact': {'currency_code': 'RUB', 'value': 0}},
                'insurance': {
                    'base': {'currency_code': 'RUB', 'value_base': 0},
                },
                'minute': {'exact': {'currency_code': 'RUB', 'value': 0}},
                'price_offer_id': 'offer_1',
            },
            'remain_km': 13.68,
            'type': 'scooter',
        },
        'distance_traveled': 250,
        'id': 'session_id',
        'price': {
            'activation': {'currency_code': 'RUB', 'value': 0},
            'base': {'currency_code': 'RUB', 'value': 0},
            'fine': {'currency_code': 'RUB', 'value': 0},
            'insurance': {'currency_code': 'RUB', 'value': 0},
            'is_final': False,
        },
        'start_location': {'lat': 12.34, 'lon': 45.67},
        'status': 'Rented',
        'write_offs': [],
    }
    assert mock_sessions_current.times_called == 1


async def test_rentals_id_not_found(taxi_scooters_mostrans, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        return {'user': {'user_id': 'user_id'}}

    response = await taxi_scooters_mostrans.get(
        '/rentals/session_id',
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 404
    assert mock_sessions_current.times_called == 1


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
async def test_rentals_end(taxi_scooters_mostrans, mockserver, load_json):
    finished = False

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        response = {
            'user': {'user_id': 'user_id'},
            'segment': {
                'car_number': '103',
                'session': {
                    'specials': {
                        'current_offer': {
                            'constructor_id': 'some_tariff',
                            'type': 'main',
                            'prices': {'acceptance_cost': 0, 'riding': 0},
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
            },
        }
        response['segment']['meta']['finished'] = finished
        return response

    @mockserver.json_handler(
        '/scooter-backend/scooters/api/yandex/trace/photo/upload',
    )
    def mock_photo_upload(request):
        assert request.query['object_id'] == 'scooter_103_id'
        assert request.query['photo_id'] == 'session_id'
        assert request.get_data() == b'some binary photo'
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/drop')
    def mock_sessions_drop(request):
        assert request.query['session_id'] == 'session_id'
        assert request.headers['UserIdDelegation'] == 'user_id'
        nonlocal finished
        finished = True
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    response = await taxi_scooters_mostrans.post(
        '/rentals/session_id/end',
        {'photo': 'c29tZSBiaW5hcnkgcGhvdG8='},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'created_at': 1655467280,
        'debts': [],
        'device': {
            'charge': 18,
            'code': '103',
            'location': {'lat': 55.897709, 'lon': 37.478066},
            'lock': {'lock_type': 'Electronic'},
            'price': {
                'activation': {'exact': {'currency_code': 'RUB', 'value': 0}},
                'insurance': {
                    'base': {'currency_code': 'RUB', 'value_base': 0},
                },
                'minute': {'exact': {'currency_code': 'RUB', 'value': 0}},
                'price_offer_id': 'offer_1',
            },
            'remain_km': 13.68,
            'type': 'scooter',
        },
        'distance_traveled': 250,
        'id': 'session_id',
        'price': {
            'activation': {'currency_code': 'RUB', 'value': 0},
            'base': {'currency_code': 'RUB', 'value': 0},
            'fine': {'currency_code': 'RUB', 'value': 0},
            'insurance': {'currency_code': 'RUB', 'value': 0},
            'is_final': True,
        },
        'start_location': {'lat': 12.34, 'lon': 45.67},
        'status': 'Ended',
        'write_offs': [],
    }
    assert mock_sessions_current.times_called == 2
    assert mock_photo_upload.times_called == 1
    assert mock_sessions_drop.times_called == 1


async def test_rentals_end_not_found(taxi_scooters_mostrans, mockserver):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        return {'user': {'user_id': 'user_id'}}

    response = await taxi_scooters_mostrans.post(
        '/rentals/session_id/end',
        {'photo': 'c29tZSBiaW5hcnkgcGhvdG8='},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 404
    assert mock_sessions_current.times_called == 1


@pytest.mark.parametrize(
    ['request_path', 'tag'],
    [
        pytest.param(
            '/rentals/session_id/resume', 'old_state_riding', id='Resume',
        ),
        pytest.param(
            '/rentals/session_id/pause', 'old_state_parking', id='Pause',
        ),
    ],
)
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
async def test_rentals_resume_pause(
        taxi_scooters_mostrans, mockserver, load_json, request_path, tag,
):
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
                            'prices': {'acceptance_cost': 0, 'riding': 0},
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
            },
        }

    @mockserver.json_handler('/scooter-backend/scooters/api/yandex/tag/evolve')
    def mock_tag_evolve(request):
        assert request.json['session_id'] == 'session_id'
        assert request.json['tag_name'] == tag
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    response = await taxi_scooters_mostrans.post(
        request_path,
        {},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'created_at': 1655467280,
        'debts': [],
        'device': {
            'charge': 18,
            'code': '103',
            'location': {'lat': 55.897709, 'lon': 37.478066},
            'lock': {'lock_type': 'Electronic'},
            'price': {
                'activation': {'exact': {'currency_code': 'RUB', 'value': 0}},
                'insurance': {
                    'base': {'currency_code': 'RUB', 'value_base': 0},
                },
                'minute': {'exact': {'currency_code': 'RUB', 'value': 0}},
                'price_offer_id': 'offer_1',
            },
            'remain_km': 13.68,
            'type': 'scooter',
        },
        'distance_traveled': 250,
        'id': 'session_id',
        'price': {
            'activation': {'currency_code': 'RUB', 'value': 0},
            'base': {'currency_code': 'RUB', 'value': 0},
            'fine': {'currency_code': 'RUB', 'value': 0},
            'insurance': {'currency_code': 'RUB', 'value': 0},
            'is_final': False,
        },
        'start_location': {'lat': 12.34, 'lon': 45.67},
        'status': 'Rented',
        'write_offs': [],
    }
    assert mock_sessions_current.times_called == 2
    assert mock_tag_evolve.times_called == 1


@pytest.mark.parametrize(
    ['request_path'],
    [
        pytest.param('/rentals/session_id/resume', id='Resume'),
        pytest.param('/rentals/session_id/pause', id='Pause'),
    ],
)
async def test_rentals_resume_pause_not_found(
        taxi_scooters_mostrans, mockserver, request_path,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def mock_sessions_current(request):
        assert request.query['session_id'] == 'session_id'
        assert request.query['user_id'] == 'user_id'
        return {'user': {'user_id': 'user_id'}}

    response = await taxi_scooters_mostrans.post(
        request_path,
        {},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 404
    assert mock_sessions_current.times_called == 1


@pytest.mark.config(
    SCOOTERS_MOSTRANS_POLYGONS_SETTINGS={
        'parking_tag': 'allow_drop_car',
        'work_zone_tag': 'user_app_work_zones_prod',
    },
    SCOOTERS_MOSTRANS_FILTER={
        'imei_mod_factor': 0,
        'telematic_sensors': {
            'fuel_level_exists': True,
            'fuel_distance_exists': True,
        },
    },
)
@pytest.mark.parametrize(
    ['areas', 'allow_drop_car', 'expected_availability'],
    [
        pytest.param(AREAS, True, 'Available', id='Available'),
        pytest.param(
            AREAS, False, 'Unavailable', id='Unavailable by scooter location',
        ),
        pytest.param(
            [], True, 'Unavailable', id='Unavailable by user location',
        ),
        pytest.param([], False, 'Unavailable', id='Unavailable by both'),
    ],
)
async def test_rentals_end_availability(
        taxi_scooters_mostrans,
        mockserver,
        load_json,
        areas,
        allow_drop_car,
        expected_availability,
):
    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    def _mock_areas(request):
        return {'areas': areas}

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
                'device_diff': {
                    'mileage': 250,
                    'start': {'latitude': 12.34, 'longitude': 45.67},
                },
            },
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == '103'
        response = load_json('scooter_backend_car_details_response.json')
        location_tags = ['allow_drop_car'] if allow_drop_car else []
        response['cars'][0]['location'].update({'tags': location_tags})
        return response

    response = await taxi_scooters_mostrans.post(
        '/rentals/session_id/end/availability',
        {'user': {'location': {'lon': 12.34, 'lat': 56.78}}},
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'availability': expected_availability}
