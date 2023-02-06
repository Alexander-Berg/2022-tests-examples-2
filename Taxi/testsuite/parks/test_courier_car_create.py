# encoding=utf-8
import datetime
import json
import uuid

import pytest

from . import error

TRANSLATIONS = {
    'car.error.bad_request': {'en': 'Incorrect format of request'},
    'car.error.bad_param': {'en': 'Incorrect field %(field)s'},
    'car.error.already_exists': {
        'en': 'You already have car with number %(field)s',
    },
    'car.year': {'en': 'Year'},
    'car.number': {'en': 'Number'},
    'car.registration_cert': {'en': 'Sts'},
    'car.vin': {'en': 'VIN'},
    'car.call_sign': {'en': 'call sign'},
    'car.brand': {'en': 'brand'},
    'car.model': {'en': 'model'},
}

PARK_ID = '1234abc'

CAR_DB_SERVICE = {
    'animals': False,
    'bicycle': False,
    'booster': False,
    'cargo_clean': False,
    'cargo_packing': False,
    'charge': False,
    'child_seat': False,
    'conditioner': False,
    'delivery': False,
    'extra_seats': False,
    'franchise': False,
    'lightbox': False,
    'digital_lightbox': False,
    'pos': False,
    'print_bill': False,
    'rigging_equipment': False,
    'rug': False,
    'ski': False,
    'smoking': False,
    'sticker': False,
    'vip_event': False,
    'wagon': False,
    'wifi': False,
    'woman_driver': False,
    'yandex_money': False,
}

QUERY_CAR_ID = '52333693fa67429588f09de95f4aabjh'

PARAMS = [
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'COURIER_123',
            'callsign': 'driver name',
            'status': 'working',
            'category': ['courier'],
        },
        'ru',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': PARK_ID,
            'year': 2015,
            'number': 'COURIER_123',
            'number_normalized': 'C0URIER123',
            'callsign': 'drivername',
            'status': 'working',
            'transmission': 'unknown',
            'category': {'courier': True, 'eda': False, 'lavka': False},
            'booster_count': 0,
            'mileage': 0,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
        True,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'EATS_COURIER',
            'callsign': 'driver name',
            'status': 'working',
            'category': ['eda'],
        },
        'ru',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': PARK_ID,
            'year': 2015,
            'number': 'EATS_COURIER',
            'number_normalized': 'EATSC0URIER',
            'callsign': 'drivername',
            'status': 'working',
            'transmission': 'unknown',
            'category': {'courier': False, 'eda': True, 'lavka': False},
            'booster_count': 0,
            'mileage': 0,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
        True,
    ),
    (
        {
            'brand': 'Audi',
            'model': 'A1',
            'year': 2015,
            'number': 'EATS_COURIER',
            'callsign': 'driver name',
            'status': 'working',
            'category': ['eda'],
        },
        'ru',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': PARK_ID,
            'year': 2015,
            'number': 'EATS_COURIER',
            'number_normalized': 'EATSC0URIER',
            'callsign': 'drivername',
            'status': 'working',
            'transmission': 'unknown',
            'category': {'courier': False, 'eda': True, 'lavka': False},
            'booster_count': 0,
            'mileage': 0,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
        True,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'LAVKA_COURIER',
            'callsign': 'driver name',
            'status': 'working',
            'category': ['lavka'],
        },
        'ru',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': PARK_ID,
            'year': 2015,
            'number': 'LAVKA_COURIER',
            'number_normalized': 'LAVKAC0URIER',
            'callsign': 'drivername',
            'status': 'working',
            'transmission': 'unknown',
            'category': {'courier': False, 'eda': False, 'lavka': True},
            'booster_count': 0,
            'mileage': 0,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
        True,
    ),
    (
        {
            'brand': 'UnknownBrand',
            'model': 'UnknownModel',
            'year': 2015,
            'number': 'COURIER_123',
            'callsign': 'driver name',
            'status': 'working',
        },
        'en',
        400,
        'Incorrect format of request',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': '2015',
            'number': 'АА123124',
            'callsign': 'driver name',
            'status': 'working',
        },
        'en',
        400,
        'Incorrect format of request',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'АА123124',
            'callsign': 'driver name',
            'status': 'unknown_type',
        },
        'en',
        400,
        'Incorrect format of request',
        False,
    ),
    (
        {
            'brand': 'Audi',
            'model': 'A1',
            'year': 2015,
            'number': 'нв AA 123124',
            'callsign': 'driver name',
            'status': 'working',
        },
        'en',
        400,
        'Incorrect format of request',
        False,
    ),
    (
        {
            'brand': 'PAGANI',
            'model': 'HUAyra',
            'year': 2015,
            'number': 'нв AA 123124',
            'callsign': 'driver name',
            'status': 'working',
        },
        'en',
        400,
        'Incorrect format of request',
        False,
    ),
]


def get_headers(locale=None):
    token = uuid.uuid1().hex
    return {'X-Idempotency-Token': token, 'Accept-Language': locale}


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'request_json,locale,status_code,expected_response,should_send_to_dca',
    PARAMS,
)
@pytest.mark.config(PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=1990)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_car_create(
        taxi_parks,
        db,
        config,
        request_json,
        locale,
        status_code,
        expected_response,
        should_send_to_dca,
        mockserver,
):
    config.set_values(
        dict(DRIVER_CATEGORIES_API_WRITE_ENABLED=should_send_to_dca),
    )

    @mockserver.json_handler('/driver-categories-api/v2/car/categories')
    def car_categories_callback(request):
        request.get_data()
        return {}

    @mockserver.json_handler(
        '/taximeter-xservice.taxi.yandex.net/' 'utils/car-updated-trigger',
    )
    def car_updated_trigger_callback(request):
        request.get_data()
        return {}

    headers = get_headers(locale)

    request_json.update(
        {
            'park_id': PARK_ID,
            'color': 'Белый',
            'booster_count': 0,
            'mileage': 0,
            'amenities': [],
        },
    )

    response = taxi_parks.post(
        '/courier/car-create', json=request_json, headers=headers,
    )

    assert response.status_code == status_code, response.text
    response_json = response.json()
    if response.status_code == 200:
        response_id = response_json['id']
        assert response_json['id'] is not None
        doc = db.dbcars.find_one({'car_id': response_json['id']})
        doc.pop('_id')
        doc.pop('car_id')
        doc.pop('updated_ts')
        doc.pop('idempotency_token', None)
        assert doc == expected_response

        retry_response = taxi_parks.post(
            '/courier/car-create', json=request_json, headers=headers,
        )
        assert retry_response.status_code == 200
        assert retry_response.json()['id'] == response_id

        if should_send_to_dca:
            assert car_categories_callback.times_called == 2
            assert (
                car_categories_callback.next_call()['request'].args.to_dict()
                == {'car_id': response_json['id'], 'park_id': PARK_ID}
            )
        else:
            assert car_categories_callback.times_called == 0

        assert car_updated_trigger_callback.times_called == 2
        callback_data = json.loads(
            car_updated_trigger_callback.next_call()['request'].get_data(),
        )
        assert callback_data['new_car']['car_id'] == response_json['id']
        assert callback_data['new_car']['park_id'] == PARK_ID
    else:
        assert response_json == error.make_error_response(expected_response)


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'request_json,locale,status_code,expected_response,should_send_to_dca',
    PARAMS,
)
@pytest.mark.config(PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=1990)
@pytest.mark.now('2018-10-10T11:30:00+0300')
def test_car_modify(
        taxi_parks,
        db,
        config,
        request_json,
        locale,
        status_code,
        expected_response,
        should_send_to_dca,
        mockserver,
):
    @mockserver.json_handler('/driver-categories-api/v2/car/categories')
    def car_categories_callback(request):
        request.get_data()
        return {}

    @mockserver.json_handler(
        '/taximeter-xservice.taxi.yandex.net/' 'utils/car-updated-trigger',
    )
    def car_updated_trigger_callback(request):
        request.get_data()
        return {}

    headers = get_headers(locale)

    request_json.update(
        {
            'park_id': PARK_ID,
            'color': 'Белый',
            'booster_count': 0,
            'mileage': 0,
            'amenities': [],
        },
    )

    response = taxi_parks.put(
        '/courier/car-create',
        json=request_json,
        headers=headers,
        params={'car_id': QUERY_CAR_ID},
    )

    assert response.status_code == status_code, response.text
    response_json = response.json()
    if response.status_code == 200:
        response_id = response_json['id']
        assert response_json['id'] is not None
        doc = db.dbcars.find_one({'car_id': QUERY_CAR_ID})
        doc.pop('_id')
        doc.pop('car_id')
        doc.pop('updated_ts')
        doc.pop('idempotency_token', None)
        doc.pop('modified_date')
        response = expected_response.copy()
        response.pop('modified_date')
        assert doc == response

        retry_response = taxi_parks.put(
            '/courier/car-create',
            json=request_json,
            headers=headers,
            params={'car_id': QUERY_CAR_ID},
        )
        assert retry_response.status_code == 200
        assert retry_response.json()['id'] == response_id

        assert car_updated_trigger_callback.times_called == 2
        callback_data = json.loads(
            car_updated_trigger_callback.next_call()['request'].get_data(),
        )
        assert callback_data['new_car']['car_id'] == QUERY_CAR_ID
        assert callback_data['new_car']['park_id'] == PARK_ID
    else:
        assert response_json == error.make_error_response(expected_response)
