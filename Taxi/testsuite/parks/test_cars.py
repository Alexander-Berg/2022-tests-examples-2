# coding=utf-8
import datetime
import json
import uuid

import pytest

from . import error
from . import utils


ENDPOINT_URL = '/cars'

MIN_MANUFACTURED_YEAR = 1990
CAR_MANUFACTURED_YEAR = 2015
CURRENT_YEAR = 2018
QUERY_PARK_ID = '1234abc'
QUERY_CAR_ID = '00033693fa67429588f09de95f4aaa9c'
POST_QUERY_PARAMS = {'park_id': QUERY_PARK_ID}
PUT_QUERY_PARAMS = {'park_id': QUERY_PARK_ID, 'id': QUERY_CAR_ID}
CAR_AMENITIES_BASE = {
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
CAR_CATEGORIES_FILTER = [
    'econom',
    'comfort',
    'comfort_plus',
    'business',
    'minivan',
    'limousine',
    'vip',
    'trucking',
    'wagon',
    'minibus',
    'pool',
    'start',
    'standart',
    'ultimate',
    'maybach',
    'cargo',
]
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
CREATE_CAR_CATEGORIES_BASE = {
    'econom': False,
    'comfort': False,
    'comfort_plus': False,
    'business': False,
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
    'cargo': False,
}
MODIFY_CAR_CATEGORIES_BASE = utils.updated(
    CREATE_CAR_CATEGORIES_BASE, {'mkk': True},
)
REQUIRED_FIELDS = {
    'brand': 'Audi',
    'model': 'A1',
    'color': 'Белый',
    'year': CAR_MANUFACTURED_YEAR,
    'number': 'НВ 123124',
    'callsign': 'driver name',
    'status': 'unknown',
    'booster_count': 0,
    'mileage': 0,
    'transmission': 'unknown',
    'amenities': [],
    'categories': [],
    'categories_filter': CAR_CATEGORIES_FILTER,
}

AUTHOR_YA_HEADERS = {
    'X-Ya-User-Ticket': '_!fake!_ya-11',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Real-Ip': '1.2.3.4',
}
AUTHOR_DRIVER_HEADERS = {'X-YaTaxi-Driver-Id': 'driver-author'}
AUTHOR_FLEET_API_HEADERS = {
    'X-Fleet-API-Client-ID': 'antontodua',
    'X-Fleet-API-Key-ID': '17',
    'X-Real-Ip': '8.7.6.5',
}
CHANGE_LOG_AUTHOR_PARAMS = [
    (AUTHOR_YA_HEADERS, '1', 'Boss', '1.2.3.4'),
    (AUTHOR_DRIVER_HEADERS, 'driver-author', 'Driver', ''),
    (AUTHOR_FLEET_API_HEADERS, '17', 'API7 Key 17', '8.7.6.5'),
]

AUTHOR_YA_UNREAL_HEADERS = {
    'X-Ya-User-Ticket': 'unreal_user_ticket',
    'X-Ya-User-Ticket-Provider': 'unreal_user_ticket_provider',
    'X-Real-Ip': '12.34.56.78',
}


@pytest.fixture
def driver_categories_api(mockserver):
    @mockserver.json_handler('/driver-categories-api/v2/car/categories')
    def mock_callback(request):
        request.get_data()
        return {}

    return mock_callback


@pytest.fixture
def taximeter_xservice(mockserver):
    @mockserver.json_handler(
        '/taximeter-xservice.taxi.yandex.net/utils/car-updated-trigger',
    )
    def mock_callback(request):
        request.get_data()
        return {}

    return mock_callback


def prepare_data(data, test_fields):
    if test_fields is not None:
        new_data = data.copy()
        for key, value in test_fields.items():
            if value is None:
                del new_data[key]
            else:
                new_data[key] = value
        return new_data
    return data


def get_idempotency_header(token=None):
    if token is None:
        token = uuid.uuid1().hex
    return {'X-Idempotency-Token': token}


CREATE_OK_PARAMS = [
    (
        QUERY_PARK_ID,
        {
            'status': 'working',
            'transmission': 'automatic',
            'categories': ['econom', 'comfort', 'business', 'cargo'],
            'amenities': ['wifi', 'conditioner', 'cargo_clean'],
            'booster_count': 1,
            'cargo_loaders': 2,
            'vin': 'abcehkmptYX123456',
            'carrying_capacity': 123,
            'body_number': '0123456  7891234567',
            'cargo_hold_dimensions': {'length': 3, 'width': 4, 'height': 5},
            'registration_cert': '7717/186838',
            'carrier_permit_owner_id': '5b5984fdfefe3d7ba0ac1238',
            'euro_car_segment': 'B',
            'description': 'description0',
            'tariffs': ['Комфорт'],
            'chairs': [
                {
                    'isofix': True,
                    'brand': 'chair_brand',
                    'categories': ['Category1', 'Category2'],
                },
            ],
            'onlycard': True,
            'fuel_type': 'electricity',
        },
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': CAR_MANUFACTURED_YEAR,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'vin': 'ABCEHKMPTYX123456',
            'booster_count': 1,
            'mileage': 0,
            'registration_cert': '7717186838',
            'status': 'working',
            'transmission': 'automatic',
            'carrier_permit_owner_id': '5b5984fdfefe3d7ba0ac1238',
            'euro_car_segment': 'B',
            'description': 'description0',
            'onlycard': True,
            'tariffs': ['Комфорт'],
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': utils.updated(
                CREATE_CAR_CATEGORIES_BASE,
                {
                    'econom': True,
                    'comfort': True,
                    'business': True,
                    'cargo': True,
                },
            ),
            'service': utils.updated(
                CAR_AMENITIES_BASE,
                {'wifi': True, 'conditioner': True, 'cargo_clean': True},
            ),
            'carrying_capacity': 123,
            'body_number': '01234567891234567',
            'cargo_hold_dimensions': {'length': 3, 'width': 4, 'height': 5},
            'chairs': [
                {'isofix': True, 'brand': 'chair_brand', 'categories': [1, 2]},
            ],
            'cargo_loaders_amount': 2,
            'fuel_type': 'electricity',
        },
        {
            'normalized_number': 'HB123124',
            'categories': ['econom', 'comfort', 'business', 'cargo'],
            'amenities': ['wifi', 'conditioner', 'cargo_clean'],
            'carrying_capacity': 123,
            'body_number': '01234567891234567',
            'cargo_hold_dimensions': {'length': 3, 'width': 4, 'height': 5},
            'chairs': [
                {
                    'brand': 'chair_brand',
                    'categories': ['Category1', 'Category2'],
                    'isofix': True,
                },
            ],
            'cargo_loaders': 2,
            'fuel_type': 'electricity',
        },
        True,
    ),
    (
        QUERY_PARK_ID,
        {'number': 'НВАА123124'},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВАА123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
        },
        {
            'number_normalized': 'HBAA123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
        },
        {'normalized_number': 'HBAA123124', 'categories': [], 'amenities': []},
        False,
    ),
    (
        QUERY_PARK_ID,
        {'categories': [], 'amenities': []},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
        },
        {'normalized_number': 'HB123124', 'categories': [], 'amenities': []},
        True,
    ),
    (
        QUERY_PARK_ID,
        {
            'chairs': [
                {'isofix': True, 'categories': ['Category1', 'Category2']},
                {
                    'isofix': True,
                    'brand': 'chair_brand1',
                    'categories': ['Category3', 'Category0'],
                },
            ],
        },
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
            'chairs': [
                {'isofix': True, 'categories': ['Category1', 'Category2']},
                {
                    'isofix': True,
                    'brand': 'chair_brand1',
                    'categories': ['Category3', 'Category0'],
                },
            ],
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'chairs': [
                {'isofix': True, 'categories': [1, 2]},
                {
                    'isofix': True,
                    'brand': 'chair_brand1',
                    'categories': [0, 3],
                },
            ],
        },
        {
            'normalized_number': 'HB123124',
            'categories': [],
            'amenities': [],
            'chairs': [
                {'isofix': True, 'categories': ['Category1', 'Category2']},
                {
                    'isofix': True,
                    'brand': 'chair_brand1',
                    'categories': ['Category0', 'Category3'],
                },
            ],
        },
        False,
    ),
    (
        QUERY_PARK_ID,
        {'number': 'С441ТК'},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'С441ТК',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
        },
        {
            'number_normalized': 'C441TK',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
        },
        {'normalized_number': 'C441TK', 'categories': [], 'amenities': []},
        True,
    ),
    (
        QUERY_PARK_ID,
        {'color': 'Черный', 'number': 'НВ123124і'},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Черный',
            'year': 2015,
            'number': 'НВ123124І',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
        },
        {
            'number_normalized': 'HB123124І',
            'number': 'НВ123124І',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
        },
        {'normalized_number': 'HB123124І', 'categories': [], 'amenities': []},
        False,
    ),
    (
        '322',
        {
            'park_id': '322',
            'color': 'Черный',
            'service_check_expiration_date': '2019-12-27',
            'car_insurance_expiration_date': '2019-12-27',
            'car_authorization_expiration_date': '2019-12-27',
            'insurance_for_goods_and_passengers_expiration_date': '2019-12-27',
            'badge_for_alternative_transport_expiration_date': '2019-12-27',
        },
        {
            'park_id': '322',
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Черный',
            'number': 'НВ123124',
            'service_check_expiration_date': '2019-12-27T00:00:00+0000',
            'car_insurance_expiration_date': '2019-12-27T00:00:00+0000',
            'car_authorization_expiration_date': '2019-12-27T00:00:00+0000',
            'insurance_for_goods_and_passengers_expiration_date': (
                '2019-12-27T00:00:00+0000'
            ),
            'badge_for_alternative_transport_expiration_date': (
                '2019-12-27T00:00:00+0000'
            ),
            'year': 2015,
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
        },
        {
            'service_check_expiration_date': datetime.datetime(
                2019, 12, 27, 0, 0,
            ),
            'car_insurance_expiration_date': datetime.datetime(
                2019, 12, 27, 0, 0,
            ),
            'car_authorization_expiration_date': datetime.datetime(
                2019, 12, 27, 0, 0,
            ),
            'insurance_for_goods_and_passengers_expiration_date': (
                datetime.datetime(2019, 12, 27, 0, 0)
            ),
            'badge_for_alternative_transport_expiration_date': (
                datetime.datetime(2019, 12, 27, 0, 0)
            ),
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'number_normalized': 'HB123124',
            'service': CAR_AMENITIES_BASE,
        },
        {'categories': [], 'amenities': [], 'normalized_number': 'HB123124'},
        True,
    ),
    (
        QUERY_PARK_ID,
        {'amenities': ['digital_lightbox'], 'rental': False},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
            'rental': False,
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': {**CAR_AMENITIES_BASE, 'digital_lightbox': True},
        },
        {
            'normalized_number': 'HB123124',
            'amenities': ['digital_lightbox'],
            'categories': [],
        },
        True,
    ),
    (
        QUERY_PARK_ID,
        {'rental': True, 'rental_status': 'park'},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
            'rental': True,
            'rental_status': 'park',
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
        },
        {'normalized_number': 'HB123124', 'categories': [], 'amenities': []},
        True,
    ),
    (
        QUERY_PARK_ID,
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
            'rental': True,
            'rental_status': 'leasing',
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 10, 10, 8, 30),
            'modified_date': datetime.datetime(2018, 10, 10, 8, 30),
            'category': CREATE_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'leasing_company': 'sber',
            'leasing_start_date': datetime.datetime(2018, 1, 1),
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        {
            'normalized_number': 'HB123124',
            'categories': [],
            'amenities': [],
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01T00:00:00+0000',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        True,
    ),
]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'park_id,optional_fields,expected_response,db_addition,api_addition,'
    'should_send_to_dca',
    CREATE_OK_PARAMS,
)
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={
        'rus': {
            'formats': ['AA123124', 'AA123124A', 'A441AA', 'AAAA123124'],
            'allowed_letters': [
                'Н',
                'В',
                'І',
                'С',
                'Т',
                'К',
                'А',
                'A',
                'а',
                'a',
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
def test_car_create_ok(
        taxi_parks,
        db,
        config,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        optional_fields,
        expected_response,
        db_addition,
        api_addition,
        should_send_to_dca,
        park_id,
):
    config.set_values(
        dict(DRIVER_CATEGORIES_API_WRITE_ENABLED=should_send_to_dca),
    )

    idempotency_token = uuid.uuid1().hex
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(
            AUTHOR_YA_HEADERS, get_idempotency_header(idempotency_token),
        ),
        params={'park_id': park_id},
        json=prepare_data(REQUIRED_FIELDS, optional_fields),
    )

    assert response.status_code == 200, response.text
    response_json = response.json()

    if 'categories' in response_json:
        response_json['categories'].sort()

    car_id = response_json.pop('id', None)
    assert car_id is not None
    doc = db.dbcars.find_one({'car_id': car_id})

    assert doc['car_id'] == car_id
    assert doc['idempotency_token'] == idempotency_token

    doc.pop('_id')
    doc.pop('car_id')
    doc.pop('updated_ts')
    doc.pop('idempotency_token')

    db_doc = expected_response.copy()
    db_doc.update(db_addition)
    assert doc == db_doc

    response_doc = expected_response.copy()
    response_doc.update(api_addition)

    if 'categories' in response_doc:
        response_doc['categories'].sort()

    assert response_json == response_doc

    if should_send_to_dca:
        assert driver_categories_api.times_called == 1
        assert driver_categories_api.next_call()['request'].args.to_dict() == {
            'car_id': car_id,
            'park_id': park_id,
        }
    else:
        assert driver_categories_api.times_called == 0

    assert taximeter_xservice.times_called == 1
    callback_data = json.loads(
        taximeter_xservice.next_call()['request'].get_data(),
    )
    assert callback_data['new_car']['car_id'] == car_id
    assert callback_data['new_car']['park_id'] == park_id


CREATE_BAD_PARAMS = [
    ({}, {'park_id': None}, 'parameter park_id must be set', None),
    (
        {'year': 1000},
        None,
        'year must be between '
        + str(MIN_MANUFACTURED_YEAR)
        + ' and '
        + str(CURRENT_YEAR),
        'invalid_year',
    ),
    (
        {'vin': 'invalid_value'},
        None,
        'vehicle identification number must be correct',
        'invalid_vin',
    ),
    (
        {'carrier_permit_owner_id': 'invalid_value'},
        None,
        'carrier permit owner id must be correct',
        'invalid_carrier_permit_owner_id',
    ),
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ аа 123124',
            'callsign': 'driver name',
            'booster_count': 0,
            'registration_cert': '7717/186838',
            'status': 'invalid_status',
            'transmission': 'automatic',
            'category': ['econom', 'comfort', 'business'],
            'amenities': ['wifi', 'conditioner'],
        },
        None,
        'status must be one of:'
        ' `unknown`, `working`, `not_working`, `tech_inspection`,'
        ' `repairing`, `highjacked`, `in_garage`',
        None,
    ),
    (
        {'chairs': [{'isofix': True, 'categories': [0]}]},
        None,
        'chairs[0].categories[0] must be a non-empty utf-8 string without BOM',
        None,
    ),
    (
        {'chairs': [{'isofix': True, 'categories': ['CategoryUnknown']}]},
        None,
        'chairs[0].categories[0] must be one of:'
        ' `Category0`, `Category1`, `Category2`, `Category3`',
        None,
    ),
    (
        {
            'chairs': [
                {
                    'isofix': True,
                    'categories': ['Category1', 'Category2', 'Category1'],
                },
            ],
        },
        None,
        'chairs[0].categories must contain unique values',
        None,
    ),
    ({'categories': 'yyy'}, None, 'categories must be an array', None),
    (
        {'categories': ['vip', 'econom', '']},
        None,
        'categories[2] must be a non-empty utf-8 string without BOM',
        None,
    ),
    (
        {'categories': ['vip', 'econom', 'vip']},
        None,
        'categories must contain unique values',
        None,
    ),
    (
        {'categories_filter': ['maybach', 'ultimate'], 'categories': ['vip']},
        None,
        'categories each element must be one of: `maybach`, `ultimate`',
        None,
    ),
    (
        {'number': 'I123A'},
        {'park_id': '1488'},
        'unexcepted symbols in car number',
        'invalid_number',
    ),
    (
        {'color': 'Вишнёвый'},
        None,
        'color must be one of: `Желтый`, `Белый`, '
        '`Черный`, `Серый`, `Красный`, `Синий`, `Голубой`, `Коричневый`, '
        '`Зеленый`, `Розовый`, `Оранжевый`, `Фиолетовый`, `Бежевый`',
        None,
    ),
    (
        {'body_number': 'неверный номер кузова'},
        None,
        'body_number must be correct',
        'invalid_body_number',
    ),
    (
        {'brand': 'unknown brand'},
        None,
        'car brand must be correct',
        'invalid_car_brand',
    ),
    (
        {'brand': 'pAgAnI'},
        None,
        'car brand must be correct',
        'invalid_car_brand',
    ),
    (
        {'brand': 'Pagani', 'model': 'unknown model'},
        None,
        'car model must be correct',
        'invalid_car_model',
    ),
    (
        {'brand': 'Pagani ssssss', 'model': 'Huayra'},
        None,
        'car brand must be correct',
        'invalid_car_brand',
    ),
    (
        {'brand': 'Pagani', 'model': ''},
        None,
        'model must be a non-empty utf-8 string without BOM',
        None,
    ),
    # Romania fields tests
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НН123124',
            'service_check_expiration_date': '2019-12-27',
        },
        None,
        (
            'car_service_check_expiration_date must '
            'be empty in country of this park'
        ),
        'unexpected_service_check_expiration_date',
    ),
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НН123124',
            'car_insurance_expiration_date': '2019-12-27',
        },
        None,
        'car_insurance_expiration_date must be empty in country of this park',
        'unexpected_car_insurance_expiration_date',
    ),
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НН123124',
            'car_authorization_expiration_date': '2019-12-27',
        },
        None,
        (
            'car_authorization_expiration_date must be '
            'empty in country of this park'
        ),
        'unexpected_car_authorization_expiration_date',
    ),
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НН123124',
            'insurance_for_goods_and_passengers_expiration_date': '2019-12-27',
        },
        None,
        (
            'insurance_for_goods_and_passengers_expiration_date '
            'must be empty in country of this park'
        ),
        'unexpected_insurance_for_goods_and_passengers_expiration_date',
    ),
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НН123124',
            'badge_for_alternative_transport_expiration_date': '2019-12-27',
        },
        None,
        (
            'badge_for_alternative_transport_expiration_date'
            ' must be empty in country of this park'
        ),
        'unexpected_badge_for_alternative_transport_expiration_date',
    ),
    (
        {'amenities': ['lightbox', 'digital_lightbox']},
        None,
        'cannot declare lightbox and digital lightbox simultaniously',
        'incompatiable_amenties',
    ),
    (
        {'fuel_type': 'test'},
        None,
        'car fuel_type must be correct',
        'invalid_fuel_type',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'test',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 1000,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing company must be correct',
        'invalid_leasing_company',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2030-01-01',
            'leasing_term': 1000,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing start year must be between 2008 and 2028',
        'invalid_leasing_date',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 70,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing term must be greater than 0 and less than 60',
        'invalid_leasing_term',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': -1,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing monthly payment must be positive',
        'invalid_leasing_monthly_payment',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': 1000,
            'leasing_interest_rate': -1,
        },
        None,
        'leasing interest rate must be greater than 0 and less than 100',
        'invalid_leasing_interest_rate',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': 1000,
            'leasing_interest_rate': 101,
        },
        None,
        'leasing interest rate must be greater than 0 and less than 100',
        'invalid_leasing_interest_rate',
    ),
]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'optional_fields,query_params,error_text,error_code', CREATE_BAD_PARAMS,
)
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={
        'rus': {
            'formats': ['AA123124', 'A441AA', 'AAAA123124', 'I123A'],
            'allowed_letters': ['Н', 'В', 'С', 'Т', 'К'],
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
def test_car_create_bad_request(
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        optional_fields,
        query_params,
        error_text,
        error_code,
):
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, get_idempotency_header()),
        params=prepare_data(POST_QUERY_PARAMS, query_params),
        json=prepare_data(REQUIRED_FIELDS, optional_fields),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_text, error_code)


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
def test_car_idempotent_create(
        taxi_parks,
        db,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
):
    """
    Checks that db don't change after first call of create with same token.
    """
    idempotency_token = uuid.uuid1().hex
    idempotency_headers = get_idempotency_header(idempotency_token)
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, idempotency_headers),
        params=POST_QUERY_PARAMS,
        json=REQUIRED_FIELDS,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()
    car_id = response_json['id']
    assert car_id is not None
    doc = db.dbcars.find_one({'car_id': car_id})
    assert doc['idempotency_token'] == idempotency_token

    # Check same request
    other_response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, idempotency_headers),
        params=POST_QUERY_PARAMS,
        json=REQUIRED_FIELDS,
    )

    assert other_response.status_code == 200, other_response.text
    other_response_json = other_response.json()
    assert other_response_json['id'] == car_id
    other_doc = db.dbcars.find_one({'car_id': car_id})
    assert doc == other_doc

    # Check other request with same idempotency token
    # Requests with same token considered as same request even if them differs
    # No changes must be made in database
    change = {
        'cargo_loaders': 2,
        'vin': 'abcehkmptYX123456',
        'registration_cert': '7717/186838',
        'carrier_permit_owner_id': '5b5984fdfefe3d7ba0ac1238',
        'euro_car_segment': 'B',
        'description': 'description0',
    }
    other_response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, idempotency_headers),
        params=POST_QUERY_PARAMS,
        json=prepare_data(REQUIRED_FIELDS, change),
    )

    assert other_response.status_code == 200, other_response.text
    other_response_json = other_response.json()
    assert other_response_json['id'] == car_id
    other_doc = db.dbcars.find_one({'car_id': car_id})
    assert doc == other_doc


BAD_IDEMPOTENCY_TOKENS = [None, '', 'abc', 'pretder', ''.join(['a'] * 129)]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
@pytest.mark.parametrize('idempotency_token', BAD_IDEMPOTENCY_TOKENS)
def test_car_create_bad_idempotency_token(
        taxi_parks, db, dispatcher_access_control, idempotency_token,
):
    """
    Checks that invalid X-Idempotency-Token is properly handled.
    """
    if idempotency_token is not None:
        idempotency_headers = {'X-Idempotency-Token': idempotency_token}
    else:
        idempotency_headers = dict()

    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, idempotency_headers),
        params=POST_QUERY_PARAMS,
        json=REQUIRED_FIELDS,
    )
    assert response.status_code == 400, response.text
    msg_exp = (
        'Header X-Idempotency-Token must contain'
        ' from 8 to 128 ASCII symbols.'
    )
    assert response.json()['error']['text'] == msg_exp


MODIFY_OK_PARAMS = [
    (
        PUT_QUERY_PARAMS,
        {
            'service_date': '2018-10-01T08:30:00+0000',
            'vin': 'abcehkmptYX123456',
            'booster_count': 1,
            'mileage': 123,
            'carrier_permit_owner_id': '5b5984fdfefe3d7ba0ac1238',
            'permit_series': 'permit_series0',
            'permit_num': 'permit_num0',
            'permit_doc': 'permit_doc0',
            'euro_car_segment': 'B',
            'description': 'description0',
            'osago_date': '2018-10-01',
            'osago_number': 'osago_number0',
            'kasko_date': '2018-10-01',
            'registration_cert': '7717/186838',
            'status': 'working',
            'transmission': 'automatic',
            'categories': ['econom', 'comfort', 'business', 'cargo'],
            'amenities': ['wifi', 'conditioner'],
            'tariffs': ['Комфорт'],
            'carrying_capacity': 10,
            'body_number': '09876543211234567',
            'cargo_hold_dimensions': {'length': 11, 'width': 12, 'height': 13},
            'chairs': [
                {
                    'isofix': True,
                    'brand': 'chair_brand',
                    'categories': ['Category1', 'Category2'],
                },
            ],
            'onlycard': True,
            'fuel_type': 'gas',
        },
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'vin': 'ABCEHKMPTYX123456',
            'booster_count': 1,
            'mileage': 123,
            'registration_cert': '7717186838',
            'status': 'working',
            'transmission': 'automatic',
            'carrier_permit_owner_id': '5b5984fdfefe3d7ba0ac1238',
            'permit_series': 'permit_series0',
            'permit_num': 'permit_num0',
            'permit_doc': 'permit_doc0',
            'euro_car_segment': 'B',
            'description': 'description0',
            'osago_number': '0SAG0NUMBER0',
            'onlycard': True,
            'tariffs': ['Комфорт'],
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'osago_date': datetime.datetime(2018, 10, 1, 0, 0),
            'kasko_date': datetime.datetime(2018, 10, 1, 0, 0),
            'category': utils.updated(
                MODIFY_CAR_CATEGORIES_BASE,
                {
                    'econom': True,
                    'comfort': True,
                    'business': True,
                    'cargo': True,
                },
            ),
            'service': utils.updated(
                CAR_AMENITIES_BASE, {'wifi': True, 'conditioner': True},
            ),
            'carrying_capacity': 10,
            'body_number': '09876543211234567',
            'cargo_hold_dimensions': {'length': 11, 'width': 12, 'height': 13},
            'chairs': [
                {'isofix': True, 'brand': 'chair_brand', 'categories': [1, 2]},
            ],
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
            'fuel_type': 'gas',
        },
        {
            'normalized_number': 'HB123124',
            'osago_date': '2018-10-01T00:00:00+0000',
            'kasko_date': '2018-10-01T00:00:00+0000',
            'categories': ['econom', 'comfort', 'business', 'cargo'],
            'amenities': ['wifi', 'conditioner'],
            'carrying_capacity': 10,
            'body_number': '09876543211234567',
            'cargo_hold_dimensions': {'length': 11, 'width': 12, 'height': 13},
            'chairs': [
                {
                    'brand': 'chair_brand',
                    'categories': ['Category1', 'Category2'],
                    'isofix': True,
                },
            ],
            'fuel_type': 'gas',
        },
    ),
    (
        PUT_QUERY_PARAMS,
        {},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'status': 'unknown',
            'transmission': 'unknown',
            'booster_count': 0,
            'mileage': 0,
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'category': MODIFY_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
        },
        {'normalized_number': 'HB123124', 'categories': [], 'amenities': []},
    ),
    (
        PUT_QUERY_PARAMS,
        {
            'color': 'Желтый',
            'carrier_permit_owner_id': '5b5984fdfefe3d7ef0ac1000',
        },
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Желтый',
            'carrier_permit_owner_id': '5b5984fdfefe3d7ef0ac1000',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'status': 'unknown',
            'transmission': 'unknown',
            'booster_count': 0,
            'mileage': 0,
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'category': MODIFY_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
        },
        {'normalized_number': 'HB123124', 'categories': [], 'amenities': []},
    ),
    # Romania fields test
    (
        {'park_id': '322', 'id': '00033693fa67429588f09de95f4aaa9d'},
        {
            'park_id': '322',
            'color': 'Желтый',
            'service_check_expiration_date': '2019-12-27',
            'car_insurance_expiration_date': '2019-12-27',
            'car_authorization_expiration_date': '2019-12-27',
            'insurance_for_goods_and_passengers_expiration_date': '2019-12-27',
            'badge_for_alternative_transport_expiration_date': '2019-12-27',
        },
        {
            'park_id': '322',
            'service_check_expiration_date': '2019-12-27T00:00:00+0000',
            'car_insurance_expiration_date': '2019-12-27T00:00:00+0000',
            'car_authorization_expiration_date': '2019-12-27T00:00:00+0000',
            'insurance_for_goods_and_passengers_expiration_date': (
                '2019-12-27T00:00:00+0000'
            ),
            'badge_for_alternative_transport_expiration_date': (
                '2019-12-27T00:00:00+0000'
            ),
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Желтый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'status': 'unknown',
            'transmission': 'unknown',
            'booster_count': 0,
            'mileage': 0,
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'category': MODIFY_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'service_check_expiration_date': datetime.datetime(
                2019, 12, 27, 0, 0,
            ),
            'car_insurance_expiration_date': datetime.datetime(
                2019, 12, 27, 0, 0,
            ),
            'car_authorization_expiration_date': datetime.datetime(
                2019, 12, 27, 0, 0,
            ),
            'insurance_for_goods_and_passengers_expiration_date': (
                datetime.datetime(2019, 12, 27, 0, 0)
            ),
            'badge_for_alternative_transport_expiration_date': (
                datetime.datetime(2019, 12, 27, 0, 0)
            ),
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
        },
        {'normalized_number': 'HB123124', 'categories': [], 'amenities': []},
    ),
    # digital lightbox
    (
        PUT_QUERY_PARAMS,
        {'amenities': ['digital_lightbox'], 'rental': False},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'status': 'unknown',
            'transmission': 'unknown',
            'booster_count': 0,
            'mileage': 0,
            'rental': False,
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'category': MODIFY_CAR_CATEGORIES_BASE,
            'service': {**CAR_AMENITIES_BASE, 'digital_lightbox': True},
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
        },
        {
            'normalized_number': 'HB123124',
            'categories': [],
            'amenities': ['digital_lightbox'],
        },
    ),
    (
        PUT_QUERY_PARAMS,
        {'rental': True, 'rental_status': 'park'},
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'status': 'unknown',
            'transmission': 'unknown',
            'booster_count': 0,
            'mileage': 0,
            'rental': True,
            'rental_status': 'park',
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'category': MODIFY_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
        },
        {'normalized_number': 'HB123124', 'categories': [], 'amenities': []},
    ),
    (
        PUT_QUERY_PARAMS,
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ123124',
            'callsign': 'drivername',
            'booster_count': 0,
            'mileage': 0,
            'status': 'unknown',
            'transmission': 'unknown',
            'rental': True,
            'rental_status': 'leasing',
        },
        {
            'number_normalized': 'HB123124',
            'created_date': datetime.datetime(2018, 7, 26, 8, 23, 24, 982000),
            'category': MODIFY_CAR_CATEGORIES_BASE,
            'service': CAR_AMENITIES_BASE,
            'charge_confirmed': False,
            'lightbox_confirmed': False,
            'rug_confirmed': False,
            'sticker_confirmed': False,
            'confirmed_boosters': 0,
            'tags': ['dirty', 'dirty', 'yandex_branding'],
            'confirmed_chairs': [
                {
                    'brand': 'Спасатель',
                    'categories': [1, 2],
                    'confirmed_categories': [2, 1],
                    'inventory_number': '123',
                    'is_enabled': True,
                },
            ],
            'leasing_company': 'sber',
            'leasing_start_date': datetime.datetime(2018, 1, 1),
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        {
            'normalized_number': 'HB123124',
            'categories': [],
            'amenities': [],
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01T00:00:00+0000',
            'leasing_term': 50,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
    ),
]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'query_params,optional_fields,expected_response,'
    'db_addition,api_addition',
    MODIFY_OK_PARAMS,
)
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={
        'rus': {
            'formats': ['AA123124', 'A441AA', 'AAAA123124'],
            'allowed_letters': ['Н', 'В', 'С', 'Т', 'К', 'А', 'A', 'а', 'a'],
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
def test_car_modify_ok(
        taxi_parks,
        db,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        query_params,
        optional_fields,
        expected_response,
        db_addition,
        api_addition,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        headers=AUTHOR_YA_HEADERS,
        params=query_params,
        json=prepare_data(REQUIRED_FIELDS, optional_fields),
    )

    assert response.status_code == 200, response.text
    response_json = response.json()

    if 'categories' in response_json:
        response_json['categories'].sort()

    car_id = response_json.pop('id')
    assert car_id == query_params['id']
    doc = db.dbcars.find_one({'car_id': car_id})
    doc.pop('_id')
    assert doc.pop('car_id') == query_params['id']
    doc.pop('owner_id')
    utils.check_updated_ts(doc.pop('updated_ts'))
    utils.check_updated(doc.pop('modified_date'))

    db_doc = expected_response.copy()
    db_doc.update(db_addition)
    assert doc == db_doc

    response_doc = expected_response.copy()
    response_doc.update(api_addition)

    if 'categories' in response_doc:
        response_doc['categories'].sort()

    assert response_json == response_doc


MODIFY_BAD_PARAMS = [
    ({}, {'id': None}, 'parameter id must be set', None),
    ({}, {'park_id': None}, 'parameter park_id must be set', None),
    (
        {'year': 3000},
        None,
        'year must be between '
        + str(MIN_MANUFACTURED_YEAR)
        + ' and '
        + str(CURRENT_YEAR),
        'invalid_year',
    ),
    (
        {'vin': 'invalid_value'},
        None,
        'vehicle identification number must be correct',
        'invalid_vin',
    ),
    (
        {'callsign': ''},
        None,
        'call sign must be non-empty',
        'invalid_call_sign',
    ),
    (
        {'callsign': '    '},
        None,
        'call sign must be non-empty',
        'invalid_call_sign',
    ),
    (
        {'registration_cert': ''},
        None,
        'registration certificate must be non-empty',
        'invalid_registration_certificate',
    ),
    (
        {'registration_cert': '    '},
        None,
        'registration certificate must be non-empty',
        'invalid_registration_certificate',
    ),
    (
        {'carrier_permit_owner_id': 'invalid_value'},
        None,
        'carrier permit owner id must be correct',
        'invalid_carrier_permit_owner_id',
    ),
    (
        {
            'park_id': QUERY_PARK_ID,
            'brand': 'Audi',
            'model': 'A1',
            'color': 'Белый',
            'year': 2015,
            'number': 'НВ аа 123124',
            'callsign': 'driver name',
            'booster_count': 0,
            'registration_cert': '7717/186838',
            'status': 'unknown',
            'transmission': 'invalid_transmission',
            'categories': ['econom', 'comfort', 'business'],
            'amenities': ['wifi', 'conditioner'],
        },
        None,
        'transmission must be one of:'
        ' `unknown`, `mechanical`, `automatic`, `robotic`, `variator`',
        None,
    ),
    ({'categories': 'yyy'}, None, 'categories must be an array', None),
    (
        {'categories': ['vip', 'econom', '']},
        None,
        'categories[2] must be a non-empty utf-8 string without BOM',
        None,
    ),
    (
        {'categories': ['vip', 'econom', 'vip']},
        None,
        'categories must contain unique values',
        None,
    ),
    (
        {'categories_filter': ['maybach', 'ultimate'], 'categories': ['vip']},
        None,
        'categories each element must be one of: `maybach`, `ultimate`',
        None,
    ),
    (
        {'color': 'Сиренево-бело-красный'},
        None,
        'color must be one of: `Желтый`, `Белый`, '
        '`Черный`, `Серый`, `Красный`, `Синий`, `Голубой`, `Коричневый`, '
        '`Зеленый`, `Розовый`, `Оранжевый`, `Фиолетовый`, `Бежевый`',
        None,
    ),
    (
        {'cargo_hold_dimensions': {'length': 228, 'width': 322}},
        None,
        'cargo_hold_dimensions.height must be present',
        None,
    ),
    (
        {'brand': 'Pagani', 'model': ''},
        None,
        'model must be a non-empty utf-8 string without BOM',
        None,
    ),
    (
        {'brand': 'Pagani', 'model': 'invalid'},
        None,
        'car model must be correct',
        'invalid_car_model',
    ),
    (
        {'brand': 'invalid', 'model': 'HUAYRA'},
        None,
        'car brand must be correct',
        'invalid_car_brand',
    ),
    (
        {'number': '1-2-3-4'},
        {'park_id': '1488'},
        'invalid car number format',
        'invalid_number',
    ),
    (
        {'number': 'ЭЭЭ123'},
        {'park_id': '1488'},
        'unexcepted symbols in car number',
        'invalid_number',
    ),
    (
        {'number': 'ЭЭЭ123'},
        {'park_id': '1488'},
        'unexcepted symbols in car number',
        'invalid_number',
    ),
    (
        {'amenities': ['lightbox', 'digital_lightbox']},
        {'park_id': 'digital_lightbox_park', 'id': 'car1'},
        'cannot declare lightbox and digital lightbox simultaniously',
        'incompatiable_amenties',
    ),
    (
        {'fuel_type': 'test'},
        None,
        'car fuel_type must be correct',
        'invalid_fuel_type',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'test',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 1000,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing company must be correct',
        'invalid_leasing_company',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2030-01-01',
            'leasing_term': 1000,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing start year must be between 2008 and 2028',
        'invalid_leasing_date',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 70,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing term must be greater than 0 and less than 60',
        'invalid_leasing_term',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': -1,
            'leasing_interest_rate': 4.6,
        },
        None,
        'leasing monthly payment must be positive',
        'invalid_leasing_monthly_payment',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': 1000,
            'leasing_interest_rate': -1,
        },
        None,
        'leasing interest rate must be greater than 0 and less than 100',
        'invalid_leasing_interest_rate',
    ),
    (
        {
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 10,
            'leasing_monthly_payment': 1000,
            'leasing_interest_rate': 101,
        },
        None,
        'leasing interest rate must be greater than 0 and less than 100',
        'invalid_leasing_interest_rate',
    ),
]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'optional_fields,query_params,error_text,error_code', MODIFY_BAD_PARAMS,
)
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={
        'rus': {
            'formats': ['AA123124', 'A441AA', 'AAAA123124'],
            'allowed_letters': ['Н', 'В', 'С', 'Т', 'К', 'А', 'A', 'а', 'a'],
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
def test_car_modify_bad_request(
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        optional_fields,
        query_params,
        error_text,
        error_code,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        headers=AUTHOR_YA_HEADERS,
        params=prepare_data(PUT_QUERY_PARAMS, query_params),
        json=prepare_data(REQUIRED_FIELDS, optional_fields),
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(error_text, error_code)


CAR_BRAND_MODEL_VALIDATION_PARAMS = [
    ({'brand': 'Pagani', 'model': 'Huayra'}, None, 200, None),
    ({'brand': 'Pagani', 'model': 'HUAYRA'}, None, 200, None),
    ({'brand': 'PAGANI', 'model': 'Huayra'}, None, 200, None),
    ({'brand': 'PAGANI', 'model': 'HUAYRA'}, None, 200, None),
    (
        {'brand': 'PAGANi', 'model': 'HUAYRA'},
        'car brand must be correct',
        400,
        'invalid_car_brand',
    ),
    (
        {'brand': 'Pagani', 'model': 'HUayra'},
        'car model must be correct',
        400,
        'invalid_car_model',
    ),
    (
        {'brand': 'unknown brand', 'model': 'Huayra'},
        'car brand must be correct',
        400,
        'invalid_car_brand',
    ),
    (
        {'brand': 'Pagani', 'model': 'unknown'},
        'car model must be correct',
        400,
        'invalid_car_model',
    ),
]


@pytest.mark.now('2018-10-10T11:30:00+0300')
@pytest.mark.parametrize(
    'optional_fields,error_text,response_code,error_code',
    CAR_BRAND_MODEL_VALIDATION_PARAMS,
)
@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
def test_car_brand_model_validation(
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        optional_fields,
        error_text,
        error_code,
        response_code,
):
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, get_idempotency_header()),
        params=prepare_data(POST_QUERY_PARAMS, None),
        json=prepare_data(REQUIRED_FIELDS, optional_fields),
    )

    assert response.status_code == response_code, response.text
    if response.status_code == 400:
        assert response.json() == error.make_error_response(
            error_text, error_code,
        )


@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
def test_car_modify_not_found(
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
):
    response = taxi_parks.put(
        ENDPOINT_URL,
        headers=AUTHOR_YA_HEADERS,
        params={'park_id': QUERY_PARK_ID, 'id': 'abra'},
        json=REQUIRED_FIELDS,
    )

    assert response.status_code == 404, response.text
    assert response.json() == error.make_error_response(
        'car with id `abra` was not found', 'car_id_not_found',
    )


@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
def test_modify_two_cars(
        taxi_parks,
        db,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
):
    # first car
    response = taxi_parks.put(
        ENDPOINT_URL,
        headers=AUTHOR_YA_HEADERS,
        params=PUT_QUERY_PARAMS,
        json=REQUIRED_FIELDS,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()

    car_id1 = response_json.pop('id')
    assert car_id1 == QUERY_CAR_ID
    doc1 = db.dbcars.find_one({'car_id': car_id1})
    utils.check_updated_ts(doc1['updated_ts'])

    # second car
    query_car_id2 = '005c49c5f2fb4075a3fbd015ebace10e'
    response2 = taxi_parks.put(
        ENDPOINT_URL,
        headers=AUTHOR_YA_HEADERS,
        params={'park_id': QUERY_PARK_ID, 'id': query_car_id2},
        json=REQUIRED_FIELDS,
    )

    assert response2.status_code == 200, response.text
    response_json2 = response2.json()

    car_id2 = response_json2.pop('id')
    assert car_id2 == query_car_id2
    doc2 = db.dbcars.find_one({'car_id': car_id2})
    utils.check_updated_ts(doc2['updated_ts'])


CHANGE_LOG_CREATE_CAR = {
    'brand': 'Audi',
    'model': 'A1',
    'color': 'Белый',
    'year': CAR_MANUFACTURED_YEAR,
    'number': 'НВ 123124',
    'callsign': 'driver name',
    'service_date': '2018-10-01',
    'vin': 'abcehkmptYX123456',
    'booster_count': 1,
    'mileage': 123,
    'body_number': '01234567891234567',
    'carrier_permit_owner_id': '5b5984fdfefe3d7ba0ac1238',
    'permit_series': 'permit_series0',
    'permit_num': 'permit_num0',
    'permit_doc': 'permit_doc0',
    'euro_car_segment': 'B',
    'description': 'description0',
    'osago_date': '2018-10-01',
    'osago_number': 'osago_number0',
    'kasko_date': '2018-10-01',
    'registration_cert': '7717/186838',
    'status': 'working',
    'transmission': 'automatic',
    'categories_filter': CAR_CATEGORIES_FILTER,
    'categories': ['econom', 'comfort', 'business', 'cargo'],
    'amenities': ['wifi', 'conditioner'],
    'tariffs': ['Комфорт'],
    'carrying_capacity': 10,
    'cargo_hold_dimensions': {'length': 123, 'width': 321, 'height': 333},
    'chairs': [
        {
            'isofix': True,
            'brand': 'chair_brand',
            'categories': ['Category1', 'Category2'],
        },
    ],
    'onlycard': False,
    'fuel_type': 'gas',
    'rental': True,
    'rental_status': 'leasing',
    'leasing_company': 'sber',
    'leasing_start_date': '2018-01-01',
    'leasing_term': 10,
    'leasing_monthly_payment': 1000,
    'leasing_interest_rate': 4,
}

EXPECTED_CHANGE_CREATE_CAR = {
    'BoosterCount': {'current': '1', 'old': ''},
    'Brand': {'current': 'Audi', 'old': ''},
    'Callsign': {'current': 'drivername', 'old': ''},
    'Category': {'current': 'Business, Cargo, Comfort, Econom', 'old': 'None'},
    'CarryingCapacity': {'current': '10', 'old': ''},
    'BodyNumber': {'current': '01234567891234567', 'old': ''},
    'CargoHoldDimensions': {
        'current': '{"height":333,"length":123,"width":321}',
        'old': '',
    },
    'Chairs': {
        'current': (
            '[{"brand":"chair_brand","categories":[1,2],"isofix":true}]'
        ),
        'old': '',
    },
    'Color': {'current': 'Белый', 'old': ''},
    'Description': {'current': 'description0', 'old': ''},
    'EuroCarSegment': {'current': 'B', 'old': ''},
    'KaskoDate': {'current': '2018-10-01T00:00:00+0000', 'old': ''},
    'Mileage': {'current': '123', 'old': ''},
    'Model': {'current': 'A1', 'old': ''},
    'Number': {'current': 'НВ123124', 'old': ''},
    'NumberNormalized': {'current': 'HB123124', 'old': ''},
    'Onlycard': {'current': 'False', 'old': ''},
    'OsagoDate': {'current': '2018-10-01T00:00:00+0000', 'old': ''},
    'OsagoNumber': {'current': '0SAG0NUMBER0', 'old': ''},
    'OwnerId': {'current': '5b5984fdfefe3d7ba0ac1238', 'old': ''},
    'ParkId': {'current': '1234abc', 'old': ''},
    'PermitDocument': {'current': 'permit_doc0', 'old': ''},
    'PermitNumber': {'current': 'permit_num0', 'old': ''},
    'PermitSeries': {'current': 'permit_series0', 'old': ''},
    'RegistrationCertificate': {'current': '7717186838', 'old': ''},
    'Rental': {'current': 'True', 'old': ''},
    'RentalStatus': {'current': 'leasing', 'old': ''},
    'LeasingCompany': {'current': 'sber', 'old': ''},
    'LeasingInterestRate': {'current': '4.000000', 'old': ''},
    'LeasingMonthlyPayment': {'current': '1000', 'old': ''},
    'LeasingStartDate': {'current': '2018-01-01T00:00:00+0000', 'old': ''},
    'LeasingTerm': {'current': '10', 'old': ''},
    'FuelType': {'current': 'gas', 'old': ''},
    'Service': {'current': 'Conditioner, Wifi', 'old': 'None'},
    'Status': {'current': 'Working', 'old': ''},
    'Tariffs': {'current': '["Комфорт"]', 'old': ''},
    'Transmission': {'current': 'Automatic', 'old': ''},
    'Vin': {'current': 'ABCEHKMPTYX123456', 'old': ''},
    'Year': {'current': '2015', 'old': ''},
}


@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
def test_create_no_author(
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
):
    response = taxi_parks.post(
        ENDPOINT_URL, params=POST_QUERY_PARAMS, json=CHANGE_LOG_CREATE_CAR,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'An author must be provided',
    )


@pytest.mark.config(
    PARKS_CAR_MINIMUM_MANUFACTURED_YEAR=MIN_MANUFACTURED_YEAR,
    CAR_NUMBERS_FORMAT={},
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
)
def test_create_unreal_author(
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
):
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_UNREAL_HEADERS, None),
        params=POST_QUERY_PARAMS,
        json=CHANGE_LOG_CREATE_CAR,
    )

    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        'can not get change author',
    )


@pytest.mark.config(
    PARKS_ALLOWED_FUEL_VALUES=FUEL_CONFIG,
    PARKS_LEASING_CONFIG=PARKS_LEASING_CONFIG,
)
@pytest.mark.parametrize(
    'author_headers, user_id, display_name, client_ip',
    CHANGE_LOG_AUTHOR_PARAMS,
)
def test_create_change_log(
        mockserver,
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        sql_databases,
        author_headers,
        user_id,
        display_name,
        client_ip,
):
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(author_headers, get_idempotency_header()),
        params=POST_QUERY_PARAMS,
        json=CHANGE_LOG_CREATE_CAR,
    )

    assert response.status_code == 200, response.text
    object_id = response.json()['id']
    assert object_id is not None

    cursor = sql_databases.taximeter.conn.cursor()
    query = 'SELECT * FROM changes_0 WHERE object_id=\'{}\''.format(object_id)
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    change = list(rows[0])
    assert change[0] == '1234abc'
    # skip id and date
    change[8] = json.loads(change[8])
    # sort categories
    tmp = change[8]['Category']['current'].split(', ')
    tmp.sort()
    change[8]['Category']['current'] = ', '.join(s for s in tmp)
    assert change[8].pop('CarId', None) is not None
    assert change[3:] == [
        object_id,
        'MongoDB.Docs.Car.CarDoc',
        user_id,
        display_name,
        len(EXPECTED_CHANGE_CREATE_CAR) + 1,  # because of
        # poped CarId
        EXPECTED_CHANGE_CREATE_CAR,
        client_ip,
    ]


EXPECTED_CHANGE_MODIFY_CAR = {
    'Category': {
        'current': 'Cargo',
        'old': 'Business, Cargo, Comfort, Econom',
    },
    'Onlycard': {'current': '', 'old': 'False'},
}


@pytest.mark.config(
    PARKS_ALLOWED_FUEL_VALUES=FUEL_CONFIG,
    PARKS_LEASING_CONFIG=PARKS_LEASING_CONFIG,
)
@pytest.mark.parametrize(
    'author_headers, user_id, display_name, client_ip',
    CHANGE_LOG_AUTHOR_PARAMS,
)
def test_modify_change_log(
        mockserver,
        taxi_parks,
        dispatcher_access_control,
        driver_categories_api,
        taximeter_xservice,
        sql_databases,
        author_headers,
        user_id,
        display_name,
        client_ip,
):
    response = taxi_parks.post(
        ENDPOINT_URL,
        headers=prepare_data(AUTHOR_YA_HEADERS, get_idempotency_header()),
        params=POST_QUERY_PARAMS,
        json=CHANGE_LOG_CREATE_CAR,
    )

    assert response.status_code == 200, response.text
    id = response.json()['id']
    assert id is not None

    response = taxi_parks.put(
        ENDPOINT_URL,
        headers=author_headers,
        params={'park_id': QUERY_PARK_ID, 'id': id},
        json=utils.remove(
            utils.replace(CHANGE_LOG_CREATE_CAR, {'categories': ['cargo']}),
            'onlycard',
        ),
    )

    assert response.status_code == 200, response.text
    object_id = response.json()['id']
    assert id == object_id

    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        'SELECT * FROM changes_0 WHERE object_id=\'{}\' '
        'ORDER BY date DESC'.format(object_id)
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 2
    change = list(rows[0])
    assert change[0] == QUERY_PARK_ID
    # skip date
    change[8] = json.loads(change[8])
    # sort categories
    tmp = change[8]['Category']['old'].split(', ')
    tmp.sort()
    change[8]['Category']['old'] = ', '.join(s for s in tmp)
    assert change[3:] == [
        object_id,
        'MongoDB.Docs.Car.CarDoc',
        user_id,
        display_name,
        len(EXPECTED_CHANGE_MODIFY_CAR),
        EXPECTED_CHANGE_MODIFY_CAR,
        client_ip,
    ]
