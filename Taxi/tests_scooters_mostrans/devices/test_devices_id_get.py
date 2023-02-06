import copy

import pytest


OFFERS_RESPONSE = {
    'vehicles': [
        {
            'number': '103',
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
            'offer_id': 'offer_with_insurance',
            'type': 'minutes_offer',
            'vehicle_number': '103',
            'prices': {'unlock': 5000, 'riding': 640, 'parking': 320},
            'short_name': 'scooters_minutes_short_name',
            'subname': '',
            'name': 'Забронировать [krr]',
        },
        {
            'offer_id': '61964538-1044-859e-de5c-d47d81dde314',
            'type': 'fix_offer',
            'vehicle_number': '103',
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
async def test_device_get_wo_auth(
        taxi_scooters_mostrans, mockserver, load_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    response = await taxi_scooters_mostrans.get('/devices/103')
    assert response.status_code == 200
    assert response.json() == {
        'charge': 18,
        'code': '103',
        'location': {'lat': 55.897709, 'lon': 37.478066},
        'lock': {'lock_type': 'Electronic'},
        'price': {
            'activation': {'exact': {'value': 50, 'currency_code': 'RUB'}},
            'insurance': {'base': {'value_base': 1, 'currency_code': 'RUB'}},
            'minute': {
                'range': {
                    'value_min': 4,
                    'value_max': 6,
                    'currency_code': 'RUB',
                },
            },
        },
        'remain_km': 13.68,
        'type': 'scooter',
    }
    assert mock_car_details.times_called == 1


@pytest.mark.config(
    SCOOTERS_MOSTRANS_FILTER={
        'imei_mod_factor': 0,
        'telematic_sensors': {
            'fuel_level_exists': True,
            'fuel_distance_exists': True,
        },
    },
)
async def test_device_get(taxi_scooters_mostrans, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        assert request.query['car_number'] == '103'
        return load_json('scooter_backend_car_details_response.json')

    @mockserver.json_handler(
        '/scooters-offers/scooters-offers/v2/offers-create',
    )
    def mock_offer(request):
        assert request.json['vehicle_numbers'] == ['103']
        response = copy.deepcopy(OFFERS_RESPONSE)
        if request.json['insurance_type'] == 'standart':
            response['offers'][0]['id'] = 'offer_wo_insurance'
            response['offers'][0]['prices']['riding'] = 500
            response['offers'][0]['insurance_type'] = 'standart'
        return response

    response = await taxi_scooters_mostrans.get(
        '/devices/103',
        headers={
            'Locale': 'ru',
            'X-YaTaxi-UserId': 'user_id',
            'X-Yandex-UID': 'uid',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'charge': 18,
        'code': '103',
        'location': {'lat': 55.897709, 'lon': 37.478066},
        'lock': {'lock_type': 'Electronic'},
        'price': {
            'activation': {'exact': {'value': 5000, 'currency_code': 'RUB'}},
            'insurance': {'base': {'value_base': 140, 'currency_code': 'RUB'}},
            'minute': {'exact': {'value': 500, 'currency_code': 'RUB'}},
            'price_offer_id': 'offer_with_insurance',
        },
        'remain_km': 13.68,
        'type': 'scooter',
    }
    assert mock_car_details.times_called == 1
    assert mock_offer.times_called == 2
