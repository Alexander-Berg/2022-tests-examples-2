import copy

import pytest

from tests_vehicles_manager import utils


ENDPOINT_URL = '/fleet-api/v1/vehicles/car'

LEASING_INFO = {
    'company': 'sber',
    'start_date': '2018-01-01',
    'term': 1000,
    'monthly_payment': 50000,
    'interest_rate': '4.6',
}

ERROR_MESSAGE = 'Cannot edit field \'{}\''


def make_request(field, value):
    request = copy.deepcopy(utils.DEFAULT_REQUEST)

    tmp = request
    keys = field.split('.')
    latest = keys.pop()
    for key in keys:
        tmp = tmp.setdefault(key, {})
    tmp[latest] = value

    if not request.get('park_profile', {}).get('is_park_property', False):
        request.get('park_profile', {}).pop('ownership_type', None)
        request.get('park_profile', {}).pop('leasing_conditions', None)
        return request

    if request.get('park_profile', {}).get('ownership_type', '') != 'leasing':
        request.get('park_profile', {}).pop('leasing_conditions', None)
    return request


@pytest.mark.config(
    OPTEUM_CAR_ORDER_CATEGORIES=utils.OPTEUM_CAR_ORDER_CATEGORIES,
    FLEET_API_CAR_CATEGORIES=utils.FLEET_API_CAR_CATEGORIES,
)
@pytest.mark.parametrize('method', ['post', 'put'])
@pytest.mark.parametrize(
    'vehicle_specifications, vehicle_licenses, park_profile, cargo,'
    'child_safety, country',
    [
        (None, None, None, None, None, None),
        (None, None, {'is_park_property': True}, None, None, None),
        (None, None, {'is_park_property': False}, None, None, None),
        (
            None,
            None,
            {'is_park_property': True, 'ownership_type': 'park'},
            None,
            None,
            None,
        ),
        (
            {
                'vin': '12345678909876543',
                'body_number': '12343',
                'mileage': 10000,
            },
            {
                'registration_certificate': '123123',
                'licence_number': '234234234',
            },
            {
                'description': 'cadillac',
                'license_owner_id': '12345',
                'is_park_property': True,
                'ownership_type': 'leasing',
                'leasing_conditions': LEASING_INFO,
                'amenities': ['bicycle', 'conditioner', 'wifi'],
                'categories': ['cargo'],
                'tariffs': ['test', 'test1', 'test2'],
                'comment': '1234',
                'fuel_type': 'gas',
            },
            {
                'cargo_loaders': 5,
                'carrying_capacity': 20000000,
                'cargo_hold_dimensions': {
                    'length': 1,
                    'width': 2,
                    'height': 3,
                },
            },
            {
                'booster_count': 3,
                'chairs': [
                    {'isofix': True, 'categories': ['Category0']},
                    {
                        'isofix': False,
                        'categories': [
                            'Category0',
                            'Category1',
                            'Category2',
                            'Category3',
                        ],
                    },
                ],
            },
            None,
        ),
        (
            {'vin': '12345678909876543'},
            {'registration_certificate': '123123'},
            None,
            None,
            None,
            'rus',
        ),
    ],
)
async def test_ok(
        taxi_vehicles_manager,
        method,
        mock_parks_cars,
        mock_fleet_parks,
        mock_fleet_vehicles,
        vehicle_specifications,
        vehicle_licenses,
        park_profile,
        cargo,
        child_safety,
        country,
):
    is_put_method = method == 'put'
    req_spec = utils.DEFAULT_VEHICLE_SPECIFICATIONS.copy()
    req_licenses = utils.DEFAULT_VEHICLE_LICENSES.copy()
    req_profile = utils.DEFAULT_PARK_PROFILE.copy()
    if vehicle_specifications:
        req_spec.update(vehicle_specifications)
    if vehicle_licenses:
        req_licenses.update(vehicle_licenses)
    if park_profile:
        req_profile.update(park_profile)

    mock_parks_cars.set_data(
        vehicle_specifications=req_spec,
        vehicle_licenses=req_licenses,
        park_profile=req_profile,
        cargo=cargo,
        child_safety=child_safety,
        categories_filter=utils.EXTERNAL_CATEGORIES,
        fleet_api_client_id=utils.FLEET_API_CLIENT_ID,
        fleet_api_key_id=utils.FLEET_API_KEY_ID,
        real_ip=utils.X_REAL_IP,
        idempotency_token=utils.IDEMPOTENCY_TOKEN,
        is_put_method=is_put_method,
    )
    mock_fleet_parks.set_data(country=country)

    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=req_spec,
        vehicle_licenses=req_licenses,
        park_profile=req_profile,
        cargo=cargo,
        child_safety=child_safety,
    )
    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert mock_parks_cars.has_mock_parks_calls, response.text
    assert response.status_code == 200, response.text


@pytest.mark.parametrize('method', ['post', 'put'])
@pytest.mark.parametrize(
    'specifications, licenses, park_profile, error',
    [
        (
            {},
            {},
            {'fuel_type': 'gas', 'is_park_property': False},
            'Required field \'vin\' is empty',
        ),
        (
            {'vin': '123'},
            {},
            {'fuel_type': 'gas', 'is_park_property': False},
            'Required field \'registration_certificate\' is empty',
        ),
        (
            {},
            {'registration_certificate': '123'},
            {'fuel_type': 'gas', 'is_park_property': False},
            'Required field \'vin\' is empty',
        ),
        (
            {'vin': '123'},
            {'registration_certificate': '123'},
            {},
            'Required field \'fuel_type\' is empty',
        ),
        (
            {'vin': '123'},
            {'registration_certificate': '123'},
            {'fuel_type': 'gas'},
            'Required field \'is_park_property\' is empty',
        ),
        (
            {},
            {},
            {'fuel_type': 'gas', 'is_park_property': True},
            'Required field \'ownership_type\' is empty',
        ),
        (
            {},
            {},
            {
                'fuel_type': 'gas',
                'is_park_property': True,
                'ownership_type': 'leasing',
            },
            'Field \'leasing_conditions\' is empty',
        ),
        (
            {},
            {},
            {
                'fuel_type': 'gas',
                'is_park_property': True,
                'ownership_type': 'park',
                'leasing_conditions': LEASING_INFO,
            },
            (
                'Cannot declare \'leasing_conditions\' '
                'when ownership_type isn\'t \'leasing\''
            ),
        ),
        (
            {},
            {},
            {
                'fuel_type': 'gas',
                'is_park_property': False,
                'ownership_type': 'park',
            },
            (
                'Cannot declare ownership type or '
                'leasing conditions with not rental car'
            ),
        ),
        (
            {},
            {},
            {
                'fuel_type': 'gas',
                'is_park_property': False,
                'ownership_type': 'leasing',
            },
            (
                'Cannot declare ownership type or '
                'leasing conditions with not rental car'
            ),
        ),
        (
            {},
            {},
            {
                'fuel_type': 'gas',
                'is_park_property': False,
                'ownership_type': 'leasing',
                'leasing_conditions': LEASING_INFO,
            },
            (
                'Cannot declare ownership type or '
                'leasing conditions with not rental car'
            ),
        ),
        (
            {},
            {},
            {
                'fuel_type': 'gas',
                'is_park_property': False,
                'leasing_conditions': LEASING_INFO,
            },
            (
                'Cannot declare ownership type or '
                'leasing conditions with not rental car'
            ),
        ),
    ],
)
@pytest.mark.config(
    VEHICLES_MANAGER_RENTAL_SETTINGS=utils.DEFAULT_RUS_CONFIG,
    VEHICLES_MANAGER_FUEL_SETTINGS=utils.DEFAULT_RUS_CONFIG,
)
async def test_bad_request(
        taxi_vehicles_manager,
        method,
        mock_fleet_parks,
        mock_fleet_vehicles,
        specifications,
        licenses,
        park_profile,
        error,
):
    is_put_method = method == 'put'
    specifications.update(utils.DEFAULT_VEHICLE_SPECIFICATIONS)
    licenses.update(utils.DEFAULT_VEHICLE_LICENSES)
    park_profile.update(utils.DEFAULT_PARK_PROFILE)

    mock_fleet_parks.set_data(country='rus')
    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=specifications,
        vehicle_licenses=licenses,
        park_profile=park_profile,
    )

    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': error}


@pytest.mark.parametrize('method', ['post', 'put'])
@pytest.mark.parametrize(
    'cargo, categories, error',
    (
        [None, ['cargo'], 'Field \'cargo\' is empty'],
        [
            utils.DEFAULT_CARGO,
            [],
            'Field \'cargo\' is only available for the \'cargo\' category',
        ],
    ),
)
async def test_bad_cargo_request(
        taxi_vehicles_manager,
        method,
        mock_fleet_parks,
        mock_fleet_vehicles,
        cargo,
        categories,
        error,
):
    is_put_method = method == 'put'
    req_spec = utils.DEFAULT_VEHICLE_SPECIFICATIONS.copy()
    req_licenses = utils.DEFAULT_VEHICLE_LICENSES.copy()
    park_profile = utils.DEFAULT_PARK_PROFILE.copy()
    park_profile.update({'categories': categories})

    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=req_spec,
        vehicle_licenses=req_licenses,
        park_profile=park_profile,
        cargo=cargo,
    )

    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': error}


@pytest.mark.parametrize('method', ['post', 'put'])
@pytest.mark.parametrize(
    'status_code, error_code, error_message',
    [
        (400, 'invalid_year', 'year must be between 1900 and 2022'),
        (
            400,
            'invalid_carrier_permit_owner_id',
            'carrier permit owner id must be correct',
        ),
    ],
)
@pytest.mark.config(FLEET_API_CAR_CATEGORIES=utils.FLEET_API_CAR_CATEGORIES)
async def test_bad_request_from_parks(
        taxi_vehicles_manager,
        method,
        mock_parks_cars,
        mock_fleet_parks,
        mock_fleet_vehicles,
        status_code,
        error_code,
        error_message,
):
    is_put_method = method == 'put'
    error_response = {'code': error_code, 'message': error_message}
    mock_parks_cars.set_data(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=utils.DEFAULT_PARK_PROFILE,
        categories_filter=utils.EXTERNAL_CATEGORIES,
        fleet_api_client_id=utils.FLEET_API_CLIENT_ID,
        fleet_api_key_id=utils.FLEET_API_KEY_ID,
        real_ip=utils.X_REAL_IP,
        idempotency_token=utils.IDEMPOTENCY_TOKEN,
        is_put_method=is_put_method,
        status_code=status_code,
        error_message=error_message,
        error_code=error_code,
    )

    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=utils.DEFAULT_PARK_PROFILE,
    )

    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert response.status_code == 400, response.text
    assert response.json() == error_response


@pytest.mark.parametrize('method', ['post', 'put'])
async def test_park_not_fount(
        taxi_vehicles_manager, method, mock_fleet_parks, mock_fleet_vehicles,
):
    is_put_method = method == 'put'
    mock_fleet_parks.set_data(is_park_found=False)
    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=utils.DEFAULT_PARK_PROFILE,
    )

    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert response.status_code == 404, response.text


@pytest.mark.parametrize('method', ['post', 'put'])
@pytest.mark.config(
    OPTEUM_CAR_ORDER_CATEGORIES={
        'categories': ['eda', 'scooters', 'selfdriving', 'lavka'],
    },
    OPTEUM_CAR_CATEGORIES_EDA_LAVKA=utils.DEFAULT_CONFIG,
    OPTEUM_CAR_CATEGORIES_SELFDRIVING=utils.DEFAULT_CONFIG,
)
@pytest.mark.parametrize(
    'categories, status_code',
    [
        (['eda', 'scooters', 'selfdriving', 'lavka'], 400),
        (['eda', 'scooters', 'selfdriving'], 400),
        (['eda', 'selfdriving', 'lavka'], 200),
        (['selfdriving', 'lavka'], 200),
        (['eda', 'selfdriving'], 200),
        (['eda', 'lavka'], 200),
        (['selfdriving'], 200),
        (['selfdriving'], 200),
    ],
)
async def test_ok_valid_categories(
        taxi_vehicles_manager,
        method,
        mock_parks_cars,
        mock_fleet_parks,
        mock_fleet_vehicles,
        categories,
        status_code,
):
    is_put_method = method == 'put'
    park_profile = {'categories': categories}
    park_profile.update(utils.DEFAULT_PARK_PROFILE)

    mock_parks_cars.set_data(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=park_profile,
        fleet_api_client_id=utils.FLEET_API_CLIENT_ID,
        fleet_api_key_id=utils.FLEET_API_KEY_ID,
        real_ip=utils.X_REAL_IP,
        idempotency_token=utils.IDEMPOTENCY_TOKEN,
        is_put_method=is_put_method,
    )

    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=park_profile,
    )

    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert response.status_code == status_code, response.text
    if status_code == 400:
        expected_response = {'code': '400', 'message': 'Wrong category'}
        assert response.json() == expected_response


@pytest.mark.parametrize('method', ['post', 'put'])
@pytest.mark.config(
    OPTEUM_CAR_ORDER_CATEGORIES=utils.OPTEUM_CAR_ORDER_CATEGORIES,
    OPTEUM_CARD_CAR_REQUIRED_CATEGORIES=utils.get_required_caregories_config(),
    FLEET_API_CAR_CATEGORIES=utils.FLEET_API_CAR_CATEGORIES,
)
async def test_ok_get_required_caregories(
        taxi_vehicles_manager,
        method,
        mock_parks_cars,
        mock_fleet_parks,
        mock_fleet_vehicles,
):
    is_put_method = method == 'put'
    categories = ['test', 'cargo']
    expected_categories = ['wifi', 'top', 'express', 'courier'] + categories
    park_profile = {'categories': categories}
    park_profile.update(utils.DEFAULT_PARK_PROFILE)

    mock_parks_cars.set_data(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=park_profile,
        result_caregories=expected_categories,
        cargo=utils.DEFAULT_CARGO,
        categories_filter=utils.EXTERNAL_CATEGORIES,
        fleet_api_client_id=utils.FLEET_API_CLIENT_ID,
        fleet_api_key_id=utils.FLEET_API_KEY_ID,
        real_ip=utils.X_REAL_IP,
        idempotency_token=utils.IDEMPOTENCY_TOKEN,
        is_put_method=is_put_method,
    )

    request_body = utils.make_vehicle_request_body(
        vehicle_specifications=utils.DEFAULT_VEHICLE_SPECIFICATIONS,
        vehicle_licenses=utils.DEFAULT_VEHICLE_LICENSES,
        park_profile=park_profile,
        cargo=utils.DEFAULT_CARGO,
    )

    send_request = getattr(taxi_vehicles_manager, method)
    response = await send_request(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID) if is_put_method else None,
    )
    assert mock_parks_cars.has_mock_parks_calls, response.text
    assert response.status_code == 200, response.text


@pytest.mark.now('2022-07-01T00:00:00.000+00:00')
@pytest.mark.parametrize(
    'config_field, info', utils.VALIDATION_DISABLED_FIELDS.items(),
)
async def test_validation_disabled_fields(
        taxi_vehicles_manager,
        mock_fleet_parks,
        mock_fleet_vehicles,
        taxi_config,
        load_json,
        config_field,
        info,
):
    retrieve_response = load_json('vehicles.json')[utils.VEHILCE_ID]
    mock_fleet_vehicles.set_data(
        retrieve_response, utils.PARK_ID, utils.VEHILCE_ID,
    )
    taxi_config.set_values(
        {
            'OPTEUM_CARD_TC_FIELDS_EDIT': {
                'enable': True,
                'fields': [config_field],
                'enable_backend': True,
                'cities': [],
                'countries': [],
                'dbs': [],
                'dbs_disable': [],
                'enable_support': False,
                'enable_support_users': [],
            },
        },
    )

    request_body = make_request(info['field'], info['replace_value'])

    response = await taxi_vehicles_manager.put(
        ENDPOINT_URL,
        json=request_body,
        headers=utils.AUTHOR_FLEET_API_HEADERS,
        params=dict(vehicle_id=utils.VEHILCE_ID),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': '400',
        'message': ERROR_MESSAGE.format(info['field']),
    }
