import aiohttp.web
import pytest

ENDPOINT = '/api/v1/cars/update'

FLEET_COUNTRY_PROPERTIES = {
    'deu': {
        'car_license_types': [
            {'id': 'taxi', 'tanker_key': 'car_license_types.taxi'},
            {'id': 'phv', 'tanker_key': 'car_license_types.phv'},
        ],
    },
}

FLEET_API_CAR_CATEGORIES = {
    'internal_categories': ['econom', 'comfort', 'business', 'eda'],
    'external_categories': [],
}

VECHICLES_MANAGER_CONFIG = {
    'cities': [],
    'countries': ['rus'],
    'dbs': [],
    'dbs_disable': [],
    'enable': True,
}


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    OPTEUM_CARD_CAR_COURIER_CATEGORIES={'enable': False},
    OPTEUM_CAR_CATEGORIES_EDA_LAVKA={'enable': True},
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
    VEHICLES_MANAGER_RENTAL_SETTINGS=VECHICLES_MANAGER_CONFIG,
    VEHICLES_MANAGER_FUEL_SETTINGS=VECHICLES_MANAGER_CONFIG,
)
async def test_success(
        web_app_client, mockserver, mock_parks, headers, load_json,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'

    stub = load_json('success.json')

    @mockserver.json_handler('/parks/cars')
    async def _car_update(request):
        assert request.json == stub['cars_request']
        assert request.query['id'] == car_id_
        return aiohttp.web.json_response(stub['cars_response'])

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['cars_retrieve_request']
        return aiohttp.web.json_response(stub['cars_retrieve_response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json={
            'brand': 'TestBrand1',
            'model': 'TestModel1',
            'color': 'Желтый',
            'year': 2019,
            'number': 'UTS1',
            'mileage': 1337,
            'callsign': 'CALL-UTS1',
            'vin': '12345678901234567',
            'booster_count': 1,
            'registration_cert': 'TestCert1',
            'status': 'working',
            'transmission': 'robotic',
            'categories': ['econom', 'comfort', 'business', 'eda'],
            'amenities': ['wifi', 'conditioner'],
            'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
            'description': 'Данные для юниттестов 1',
            'tariffs': ['Комфорт', 'Эконом'],
            'chairs': [
                {
                    'brand': 'TestChairBrand1',
                    'categories': ['Category0', 'Category1', 'Category2'],
                    'isofix': True,
                },
            ],
            'cargo_loaders': 0,
            'carrying_capacity': 1234,
            'body_number': '12345',
            'cargo_hold_dimensions': {'height': 10, 'length': 20, 'width': 30},
            'rental': True,
            'rental_status': 'leasing',
            'leasing_company': 'sber',
            'leasing_start_date': '2018-01-01',
            'leasing_term': 1000,
            'leasing_monthly_payment': 50000,
            'leasing_interest_rate': 4.6,
            'permit_doc': 'QWE',
            'permit_num': '123',
            'permit_series': 'ASD',
            'fuel_type': 'gas',
        },
    )

    assert response.status == 200, response.text

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    OPTEUM_CARD_CAR_COURIER_CATEGORIES={'enable': False},
    OPTEUM_CAR_CATEGORIES_EDA_LAVKA={'enable': True},
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
)
@pytest.mark.parametrize(
    'json_name, request_json',
    [
        (
            'success_deu.json',
            {
                'brand': 'TestBrand1',
                'model': 'TestModel1',
                'color': 'Желтый',
                'year': 2019,
                'number': 'UTS1',
                'mileage': 1337,
                'callsign': 'CALL-UTS1',
                'vin': '12345678901234567',
                'booster_count': 1,
                'registration_cert': 'TestCert1',
                'status': 'working',
                'transmission': 'robotic',
                'categories': ['econom', 'comfort', 'business', 'eda'],
                'amenities': ['wifi', 'conditioner'],
                'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
                'description': 'Данные для юниттестов 1',
                'tariffs': ['Комфорт', 'Эконом'],
                'chairs': [
                    {
                        'brand': 'TestChairBrand1',
                        'categories': ['Category0', 'Category1', 'Category2'],
                        'isofix': True,
                    },
                ],
                'cargo_loaders': 0,
                'carrying_capacity': 1234,
                'body_number': '12345',
                'cargo_hold_dimensions': {
                    'height': 10,
                    'length': 20,
                    'width': 30,
                },
                'rental': True,
                'permit_doc': 'QWE',
                'permit_num': '123',
                'permit_series': 'ASD',
                'license_type': 'taxi',
            },
        ),
        (
            'success_deu_phv.json',
            {
                'brand': 'TestBrand1',
                'model': 'TestModel1',
                'color': 'Желтый',
                'year': 2019,
                'number': 'UTS1',
                'mileage': 1337,
                'callsign': 'CALL-UTS1',
                'vin': '12345678901234567',
                'booster_count': 1,
                'registration_cert': 'TestCert1',
                'status': 'working',
                'transmission': 'robotic',
                'categories': ['econom', 'comfort', 'business', 'eda'],
                'amenities': ['wifi', 'conditioner'],
                'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
                'description': 'Данные для юниттестов 1',
                'tariffs': ['Комфорт', 'Эконом'],
                'chairs': [
                    {
                        'brand': 'TestChairBrand1',
                        'categories': ['Category0', 'Category1', 'Category2'],
                        'isofix': True,
                    },
                ],
                'cargo_loaders': 0,
                'carrying_capacity': 1234,
                'body_number': '12345',
                'cargo_hold_dimensions': {
                    'height': 10,
                    'length': 20,
                    'width': 30,
                },
                'rental': True,
                'permit_doc': 'QWE',
                'permit_num': '123',
                'permit_series': 'ASD',
                'license_type': 'phv',
            },
        ),
    ],
)
async def test_success_deu(
        web_app_client,
        mock_parks_deu,
        headers,
        mockserver,
        load_json,
        json_name,
        request_json,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'

    stub = load_json(json_name)

    @mockserver.json_handler('/parks/cars')
    async def _car_update(request):
        assert request.json == stub['cars_request']
        assert request.query['id'] == car_id_
        return aiohttp.web.json_response(stub['cars_response'])

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['cars_retrieve_request']
        return aiohttp.web.json_response(stub['cars_retrieve_response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json=request_json,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    OPTEUM_CARD_TC_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['tariffs'],
        'enable_backend': True,
    },
)
async def test_validation_required_fields(
        web_app_client, mock_parks, headers, load_json,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json={
            'brand': 'TestBrand1',
            'model': 'TestModel1',
            'color': 'Желтый',
            'year': 2019,
            'number': 'UTS1',
            'mileage': 1337,
            'callsign': 'CALL-UTS1',
            'vin': '12345678901234567',
            'booster_count': 1,
            'registration_cert': 'TestCert1',
            'status': 'working',
            'transmission': 'robotic',
            'categories': ['econom', 'comfort', 'business'],
            'amenities': ['wifi', 'conditioner'],
            'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
            'description': 'Данные для юниттестов 1',
            'chairs': [
                {
                    'brand': 'TestChairBrand1',
                    'categories': ['Category0', 'Category1', 'Category2'],
                    'isofix': True,
                },
            ],
            'cargo_loaders': 0,
            'carrying_capacity': 1234,
            'body_number': '12345',
            'cargo_hold_dimensions': {'height': 10, 'length': 20, 'width': 30},
            'rental': True,
            'permit_doc': 'QWE',
            'permit_num': '123',
            'permit_series': 'ASD',
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == {'code': 'REQUIRED_FIELDS', 'message': 'Bad request'}


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
    OPTEUM_CARD_TC_FIELDS_EDIT={
        'enable': True,
        'fields': ['amenities'],
        'duration': 2,
        'enable_backend': True,
    },
)
@pytest.mark.now('2019-01-05T01:00:00+03:00')
async def test_validation_fields_edit(
        web_app_client, mock_parks, mockserver, headers, load_json,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'

    stub = load_json('success.json')

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['cars_retrieve_request']
        return aiohttp.web.json_response(stub['cars_retrieve_response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json={
            'brand': 'TestBrand1',
            'model': 'TestModel1',
            'color': 'Желтый',
            'year': 2019,
            'number': 'UTS1',
            'mileage': 1337,
            'callsign': 'CALL-UTS1',
            'vin': '12345678901234567',
            'booster_count': 1,
            'registration_cert': 'TestCert1',
            'status': 'working',
            'transmission': 'robotic',
            'categories': ['econom', 'comfort', 'business'],
            'amenities': ['wifi'],
            'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
            'description': 'Данные для юниттестов 1',
            'tariffs': ['Комфорт', 'Эконом'],
            'chairs': [
                {
                    'brand': 'TestChairBrand1',
                    'categories': ['Category0', 'Category1', 'Category2'],
                    'isofix': True,
                },
            ],
            'cargo_loaders': 0,
            'carrying_capacity': 1234,
            'body_number': '12345',
            'cargo_hold_dimensions': {'height': 10, 'length': 20, 'width': 30},
            'rental': True,
            'permit_doc': 'QWE',
            'permit_num': '123',
            'permit_series': 'ASD',
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == {'code': 'FIELDS_EDIT', 'message': 'Bad request'}


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    FLEET_API_CAR_CATEGORIES=FLEET_API_CAR_CATEGORIES,
    OPTEUM_CAR_CATEGORIES_EDA_LAVKA={'enable': False},
)
@pytest.mark.now('2019-01-05T01:00:00+03:00')
async def test_validation_categories(
        web_app_client, mock_parks, mockserver, headers, load_json,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'

    stub = load_json('success.json')

    @mockserver.json_handler('/parks/cars/retrieve')
    async def _car_retrieve(request):
        assert request.json == stub['cars_retrieve_request']
        return aiohttp.web.json_response(stub['cars_retrieve_response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json={
            'brand': 'TestBrand1',
            'model': 'TestModel1',
            'color': 'Желтый',
            'year': 2019,
            'number': 'UTS1',
            'mileage': 1337,
            'callsign': 'CALL-UTS1',
            'vin': '12345678901234567',
            'booster_count': 1,
            'registration_cert': 'TestCert1',
            'status': 'working',
            'transmission': 'robotic',
            'categories': ['econom', 'eda'],
            'amenities': ['wifi'],
            'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
            'description': 'Данные для юниттестов 1',
            'tariffs': ['Комфорт', 'Эконом'],
            'chairs': [
                {
                    'brand': 'TestChairBrand1',
                    'categories': ['Category0', 'Category1', 'Category2'],
                    'isofix': True,
                },
            ],
            'cargo_loaders': 0,
            'carrying_capacity': 1234,
            'body_number': '12345',
            'cargo_hold_dimensions': {'height': 10, 'length': 20, 'width': 30},
            'rental': True,
            'permit_doc': 'QWE',
            'permit_num': '123',
            'permit_series': 'ASD',
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == {'code': 'WRONG_CATEGORIES', 'message': 'Bad request'}


@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES=FLEET_COUNTRY_PROPERTIES,
    OPTEUM_CARD_CAR_COURIER_CATEGORIES={'enable': False},
    OPTEUM_CAR_CATEGORIES_EDA_LAVKA={'enable': True},
)
@pytest.mark.parametrize(
    'request_json, expected_response',
    [
        (
            {
                'brand': 'TestBrand1',
                'model': 'TestModel1',
                'color': 'Желтый',
                'year': 2019,
                'number': 'UTS1',
                'mileage': 1337,
                'callsign': 'CALL-UTS1',
                'vin': '12345678901234567',
                'booster_count': 1,
                'registration_cert': 'TestCert1',
                'status': 'working',
                'transmission': 'robotic',
                'categories': ['econom', 'comfort', 'business', 'eda'],
                'amenities': ['wifi', 'conditioner'],
                'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
                'description': 'Данные для юниттестов 1',
                'tariffs': ['Комфорт', 'Эконом'],
                'chairs': [
                    {
                        'brand': 'TestChairBrand1',
                        'categories': ['Category0', 'Category1', 'Category2'],
                        'isofix': True,
                    },
                ],
                'cargo_loaders': 0,
                'carrying_capacity': 1234,
                'body_number': '12345',
                'cargo_hold_dimensions': {
                    'height': 10,
                    'length': 20,
                    'width': 30,
                },
                'rental': True,
                'permit_doc': 'QWE',
                'permit_num': '123',
                'permit_series': 'ASD',
            },
            {'code': 'WRONG_LICENSE_TYPE', 'message': 'Bad request'},
        ),
        (
            {
                'brand': 'TestBrand1',
                'model': 'TestModel1',
                'color': 'Желтый',
                'year': 2019,
                'number': 'UTS1',
                'mileage': 1337,
                'callsign': 'CALL-UTS1',
                'vin': '12345678901234567',
                'booster_count': 1,
                'registration_cert': 'TestCert1',
                'status': 'working',
                'transmission': 'robotic',
                'categories': ['econom', 'comfort', 'business', 'eda'],
                'amenities': ['wifi', 'conditioner'],
                'carrier_permit_owner_id': '5c264bf5de2a722c671e6d33',
                'description': 'Данные для юниттестов 1',
                'tariffs': ['Комфорт', 'Эконом'],
                'chairs': [
                    {
                        'brand': 'TestChairBrand1',
                        'categories': ['Category0', 'Category1', 'Category2'],
                        'isofix': True,
                    },
                ],
                'cargo_loaders': 0,
                'carrying_capacity': 1234,
                'body_number': '12345',
                'cargo_hold_dimensions': {
                    'height': 10,
                    'length': 20,
                    'width': 30,
                },
                'rental': True,
                'permit_doc': 'QWE',
                'permit_num': '123',
                'permit_series': 'ASD',
                'license_type': 'unknown',
            },
            None,
        ),
    ],
)
async def test_bad_request_deu(
        web_app_client,
        mock_parks_deu,
        headers,
        request_json,
        expected_response,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json=request_json,
    )

    assert response.status == 400
    if expected_response is not None:
        data = await response.json()
        assert data == expected_response


DEFAULT_REQUEST_BODY = {
    'brand': 'TestBrand1',
    'model': 'TestModel1',
    'color': 'Желтый',
    'year': 2019,
    'number': 'UTS1',
    'callsign': 'CALL-UTS1',
    'booster_count': 1,
    'status': 'working',
    'transmission': 'robotic',
}


@pytest.mark.config(
    VEHICLES_MANAGER_RENTAL_SETTINGS=VECHICLES_MANAGER_CONFIG,
    VEHICLES_MANAGER_FUEL_SETTINGS=VECHICLES_MANAGER_CONFIG,
)
@pytest.mark.parametrize(
    'request_json, expected_response',
    (
        [
            {'fuel_type': 'gas'},
            {
                'code': 'BAD_REQUEST',
                'message': 'Required field \'rental\' is empty',
            },
        ],
        [
            {'rental': False},
            {
                'code': 'BAD_REQUEST',
                'message': 'Required field \'fuel_type\' is empty',
            },
        ],
    ),
)
async def test_rental_and_fuel_type_fields(
        web_app_client, mock_parks, headers, request_json, expected_response,
):
    car_id_ = '0fe5add44e4c307a88c374526982a356'
    request_body = {**DEFAULT_REQUEST_BODY, **request_json}
    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        params={'carId': car_id_},
        json=request_body,
    )

    assert response.status == 400, response.text
    assert await response.json() == expected_response
