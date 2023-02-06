import copy

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

OFFERS_RESPONSE = {
    'vehicles': [
        {
            'number': '105',
            'id': 'scooter_1',
            'model': 'Ninebot',
            'location': [37.478066, 55.897709],
            'status': {
                'remaining_distance': 13.68,
                'remaining_time': 65,
                'charge_level': 18,
            },
        },
    ],
    'offers': [
        {
            'offer_id': 'offer_3',
            'type': 'minutes_offer',
            'vehicle_number': '105',
            'prices': {'unlock': 5000, 'riding': 640, 'parking': 320},
            'short_name': 'scooters_minutes_short_name',
            'subname': '',
            'name': 'Забронировать [krr]',
        },
        {
            'offer_id': '61964538-1044-859e-de5c-d47d81dde314',
            'type': 'fix_offer',
            'vehicle_number': '105',
            'prices': {'unlock': 0, 'riding': 710, 'parking': 360},
            'cashback_percent': 10,
            'is_fake': True,
            'short_name': 'scooters_fixpoint_short_name',
            'subname': 'scooters_fixpoint_subname',
            'name': 'Фикс для самокатов',
            'pack_price': 1022400,
            'detailed_description': '',
        },
    ],
    'insurance_type': 'full',
    'currency_rules': {'code': 'RUB', 'sign': '', 'template': '', 'text': ''},
}


@pytest.mark.now('2022-06-17T12:05:56+00:00')
@pytest.mark.parametrize(
    [
        'car_number',
        'expected_book',
        'expected_create_offer',
        'expected_response_code',
        'expected_response',
    ],
    [
        pytest.param(
            '103',
            False,
            False,
            200,
            {
                'created_at': 1655467280,
                'booking_expires_at': 1655467826,
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
                'id': 'session_1',
                'status': 'Booked',
                'write_offs': [],
            },
            id='Already booked',
        ),
        pytest.param(
            '102',
            False,
            False,
            400,
            {'code': 'DeviceAlreadyRented'},
            id='Ride already started',
        ),
        pytest.param(
            '105',
            True,
            False,
            200,
            {
                'created_at': 1655467280,
                'booking_expires_at': 1655467856,
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
                'id': 'session_3',
                'status': 'Booked',
                'write_offs': [],
            },
            id='Book',
        ),
        pytest.param(
            '105',
            True,
            True,
            200,
            {
                'created_at': 1655467280,
                'booking_expires_at': 1655467856,
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
                'id': 'session_3',
                'status': 'Booked',
                'write_offs': [],
            },
            id='Create offer and book',
        ),
    ],
)
async def test_bookings_post(
        taxi_scooters_mostrans,
        mockserver,
        load_json,
        car_number,
        expected_book,
        expected_create_offer,
        expected_response_code,
        expected_response,
):
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
            'session_1': SESSION_1,
            'session_2': SESSION_2,
            'session_3': SESSION_3,
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

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        assert request.query['car_number'] == car_number
        response = load_json('scooter_backend_car_details_response.json')
        response['cars'][0]['number'] = car_number
        statuses = {
            '102': 'old_state_riding',
            '103': 'old_state_reservation',
            '105': (
                'old_state_reservation'
                if 'session_3' in booked
                else 'available'
            ),
        }
        response['cars'][0]['status'] = statuses[car_number]
        return response

    @mockserver.json_handler(
        '/scooters-offers/scooters-offers/v2/offers-create',
    )
    def mock_offer(request):
        assert request.json['vehicle_numbers'] == ['105']
        response = copy.deepcopy(OFFERS_RESPONSE)
        if request.json['insurance_type'] == 'standart':
            response['offers'][0]['id'] = 'offer_wo_insurance'
            response['offers'][0]['prices']['riding'] = 500
            response['offers'][0]['insurance_type'] = 'standart'
        return response

    request = {
        'user': {'location': {'lon': 12.34, 'lat': 45.67}},
        'code': car_number,
    }
    if not expected_create_offer:
        request['payment_info'] = {
            'payment_method': 'Card',
            'payment_system': 'Visa',
            'pan': '1234',
            'card_id': 'card_id',
            'token': 'payment_token',
            'email': 'email@email.ru',
            'price_offer_id': 'offer_3',
        }
    response = await taxi_scooters_mostrans.post(
        '/bookings',
        request,
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == expected_response_code
    assert response.json() == expected_response
    assert mock_book.times_called == (1 if expected_book else 0)
    assert mock_offer.times_called == (1 if expected_create_offer else 0)


async def test_bookings_post_non_authorized(
        taxi_scooters_mostrans, mockserver, load_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    request = {
        'user': {'location': {'lon': 12.34, 'lat': 45.67}},
        'code': '103',
        'payment_info': {
            'payment_method': 'Card',
            'payment_system': 'Visa',
            'pan': '1234',
            'card_id': 'card_id',
            'token': 'payment_token',
            'email': 'email@email.ru',
            'price_offer_id': 'offer_1',
        },
    }
    response = await taxi_scooters_mostrans.post(
        '/bookings', request, headers={'Locale': 'ru'},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'Other',
        'message': '',
        'deeplink': 'yandextaxi://scooters?number=103',
    }
    assert mock_car_details.times_called == 1
