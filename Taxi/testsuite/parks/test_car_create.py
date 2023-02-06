# encoding=utf-8
import datetime
import json

import pytest

from . import error
from . import utils

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
CAR_DB_CATEGORY = {
    'econom': True,
    'comfort': True,
    'courier': False,
    'comfort_plus': False,
    'express': False,
    'business': True,
    'minivan': False,
    'limousine': False,
    'vip': False,
    'trucking': False,
    'wagon': False,
    'minibus': False,
    'pool': False,
    'start': False,
    'standart': False,
    'ultimate': False,
    'maybach': False,
}
FUEL_CONFIG = ['petrol', 'gas', 'electricity']
PARKS_LEASING_CONFIG = {
    'available_leasing_companies': ['sber', 'alpha'],
    'available_leasing_interest_rate': {
        'min_leasing_rate': 0,
        'max_leasing_rate': 100,
    },
    'available_leasing_interest_term': {
        'min_leasing_term': 0,
        'max_leasing_term': 60,
    },
    'available_leasing_start_date_interval': {
        'years_before': 10,
        'years_after': 10,
    },
}

PARAMS = [
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ 123124',
            'callsign': 'driver name',
            'registration_cert': '7717/186838',
            'status': 'working',
            'fuel_type': 'gas',
            'amenities': ['wifi', 'conditioner'],
        },
        'ru',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': '1488',
            'year': 2015,
            'number': 'НВ123124',
            'number_normalized': 'HB123124',
            'callsign': 'drivername',
            'registration_cert': '7717186838',
            'booster_count': 0,
            'mileage': 0,
            'status': 'working',
            'fuel_type': 'gas',
            'transmission': 'unknown',
            'category': CAR_DB_CATEGORY,
            'service': utils.updated(
                CAR_DB_SERVICE, {'wifi': True, 'conditioner': True},
            ),
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
            'number': 'нв AA 123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
        },
        'en',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': '1488',
            'year': 2015,
            'number': 'НВАА123124',
            'number_normalized': 'HBAA123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'working',
            'transmission': 'unknown',
            'category': CAR_DB_CATEGORY,
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
            'number': 'нв AA 123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
        },
        'en',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': '1488',
            'year': 2015,
            'number': 'НВАА123124',
            'number_normalized': 'HBAA123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'working',
            'transmission': 'unknown',
            'category': CAR_DB_CATEGORY,
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
            'number': 'АА123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
        },
        'en',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': '1488',
            'year': 2015,
            'number': 'АА123124',
            'number_normalized': 'AA123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'working',
            'transmission': 'unknown',
            'category': CAR_DB_CATEGORY,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'АА123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'rental': True,
            'rental_status': 'park',
        },
        'en',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': '1488',
            'year': 2015,
            'number': 'АА123124',
            'number_normalized': 'AA123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'working',
            'rental': True,
            'rental_status': 'park',
            'transmission': 'unknown',
            'category': CAR_DB_CATEGORY,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'АА123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        'en',
        200,
        {
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'park_id': '1488',
            'year': 2015,
            'number': 'АА123124',
            'number_normalized': 'AA123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'working',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': datetime.datetime(2018, 1, 1),
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
            'transmission': 'unknown',
            'category': CAR_DB_CATEGORY,
            'service': CAR_DB_SERVICE,
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
        },
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
            'amenities': ['wifi'],
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
            'amenities': ['wifi'],
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
            'year': 2020,
            'number': 'АА123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': ['wifi'],
        },
        'en',
        400,
        'Incorrect field Year',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ ЯЯ123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': ['wifi'],
        },
        'en',
        400,
        'Incorrect field Number',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
        },
        'en',
        400,
        'You already have car with number НВ9999',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'АА123124',
            'callsign': 'driver name',
            'registration_cert': '',
            'status': 'working',
            'amenities': [],
        },
        'en',
        400,
        'Incorrect field Sts',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'АА123124',
            'callsign': 'driver name',
            'registration_cert': '    ',
            'status': 'working',
            'amenities': [],
        },
        'en',
        400,
        'Incorrect field Sts',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'vin': '0123456789XYZABCQ',
        },
        'en',
        400,
        'Incorrect field VIN',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'test',
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
    (
        {
            'brand': 'AUdi',
            'model': 'A1',
            'year': 2015,
            'number': 'нв AA 123124',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
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
            'amenities': [],
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
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'gas',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'test',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'gas',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2030-01-01',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'gas',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 70,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'gas',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': -1,
            'leasing_interest_rate': 4.6,
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'gas',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': 1000,
            'leasing_interest_rate': -1,
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
    (
        {
            'brand': 'AUDI',
            'model': 'A1',
            'year': 2015,
            'number': 'НВ9999',
            'callsign': 'driver name',
            'status': 'working',
            'amenities': [],
            'fuel_type': 'gas',
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': 1000,
            'leasing_interest_rate': 101,
        },
        'en',
        400,
        'Incorrect field Error',
        False,
    ),
]


@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'request_json,locale,status_code,expected_response,should_send_to_dca',
    PARAMS,
)
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=1990,
    CAR_NUMBERS_FORMAT={
        'rus': {
            'formats': ['AA123124', 'AA9999', 'A441AA', 'AAAA123124'],
            'allowed_letters': [
                'в',
                'В',
                'Н',
                'н',
                'С',
                'Т',
                'К',
                'А',
                'A',
                'Х',
                'У',
            ],
        },
    },
    FLEET_COUNTRY_PROPERTIES={
        'deu': {
            'car_license_types': [
                {'id': 'taxi', 'tanker_key': 'CarLicenseType.Standard'},
                {
                    'id': 'phv',
                    'tanker_key': 'CarLicenseType.PrivateHireVehicle',
                },
            ],
        },
    },
    PARKS_ALLOWED_FUEL_VALUES=FUEL_CONFIG,
    PARKS_LEASING_CONFIG=PARKS_LEASING_CONFIG,
)
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

    request_json.update(
        {
            'park_id': '1488',
            'color': 'Белый',
            'booster_count': 0,
            'mileage': 0,
            'category': ['econom', 'comfort', 'business'],
        },
    )

    headers = {'Accept-Language': locale}

    response = taxi_parks.post(
        '/car-create', json=request_json, headers=headers,
    )

    assert response.status_code == status_code, response.text
    response_json = response.json()
    if response.status_code == 200:
        assert response_json['id'] is not None
        doc = db.dbcars.find_one({'car_id': response_json['id']})
        doc.pop('_id')
        doc.pop('car_id')
        doc.pop('updated_ts')
        doc.pop('idempotency_token', None)
        assert doc == expected_response

        if should_send_to_dca:
            assert car_categories_callback.times_called == 1
            assert (
                car_categories_callback.next_call()['request'].args.to_dict()
                == {'car_id': response_json['id'], 'park_id': '1488'}
            )
        else:
            assert car_categories_callback.times_called == 0

        assert car_updated_trigger_callback.times_called == 1
        callback_data = json.loads(
            car_updated_trigger_callback.next_call()['request'].get_data(),
        )
        assert callback_data['new_car']['car_id'] == response_json['id']
        assert callback_data['new_car']['park_id'] == '1488'
    else:
        assert response_json == error.make_error_response(expected_response)
