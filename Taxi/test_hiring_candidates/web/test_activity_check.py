import pytest

from test_hiring_candidates import conftest


LAST_RIDE_DATE_DEFAULT = '2020-06-04 08:43:30'
LAST_RIDE_DATE_CARS = '2020-06-02 14:17:55'

REQUEST_DEFAULT_FILE = 'request_default.json'
REQUEST_CARS_FILE = 'request_cars.json'
REQUEST_SELFEMPLOYMENT_FILE = 'request_selfemployment.json'


async def get_response_body(client, data, request_body, status=200):
    route = data['route']
    body = data['body'][request_body]
    _response = await client.post(route, json=body)
    assert _response.status == status
    return await _response.json()


@pytest.mark.parametrize('request_body', ['has_rides', 'no_rides', 'no_cars'])
@conftest.main_configuration
async def test_activity_cars(
        taxi_hiring_candidates_web, load_json, request_body,
):

    data = load_json(REQUEST_CARS_FILE)['car_plate']
    body = await get_response_body(
        taxi_hiring_candidates_web, data, request_body,
    )

    if request_body == 'has_rides':
        assert body['is_active']
        assert body['rides_count'] > 0
        assert body['last_ride_date'] == LAST_RIDE_DATE_CARS
    elif request_body in ('no_rides', 'no_cars'):
        assert not body['is_active']
        assert body['rides_count'] == 0


@pytest.mark.parametrize('request_type', ['phone', 'license'])
@pytest.mark.parametrize(
    'request_body, status',
    [('has_rides', 200), ('no_rides', 200), ('invalid', 400)],
)
@conftest.main_configuration
async def test_activity_default(
        taxi_hiring_candidates_web,
        load_json,
        request_type,
        request_body,
        status,
):
    data = load_json(REQUEST_DEFAULT_FILE)[request_type]
    body = await get_response_body(
        taxi_hiring_candidates_web, data, request_body, status,
    )

    if request_body == 'has_rides':
        assert body['is_active']
        assert body['rides_count'] > 0
        assert body['last_ride_date'] == LAST_RIDE_DATE_DEFAULT
    elif request_body == 'no_rides':
        assert not body['is_active']
        assert body['rides_count'] == 0


@pytest.mark.parametrize('request_type', ['phone', 'license'])
@pytest.mark.parametrize(
    'request_body, status',
    [
        ('has_rides', 200),
        ('no_rides', 200),
        ('no_selfemployment_rides', 200),
        ('invalid', 400),
    ],
)
@conftest.main_configuration
async def test_activity_selfemployment(
        taxi_hiring_candidates_web,
        load_json,
        request_type,
        request_body,
        status,
):
    data = load_json(REQUEST_SELFEMPLOYMENT_FILE)[request_type]
    body = await get_response_body(
        taxi_hiring_candidates_web, data, request_body, status,
    )

    if request_body == 'has_rides':
        assert body['is_selfemployed']
        assert body['last_ride_date'] == LAST_RIDE_DATE_DEFAULT
    elif request_body in ('no_rides', 'no_selfemployment_rides'):
        assert not body['is_selfemployed']


@pytest.mark.parametrize('enable_provider', [True, False])
@pytest.mark.parametrize(
    'request_type, request_file',
    [
        ('phone', REQUEST_DEFAULT_FILE),
        ('license', REQUEST_DEFAULT_FILE),
        ('phone', REQUEST_SELFEMPLOYMENT_FILE),
        ('license', REQUEST_SELFEMPLOYMENT_FILE),
        ('car_plate', REQUEST_CARS_FILE),
    ],
)
@conftest.main_configuration
async def test_enable_provider_filter(
        taxi_hiring_candidates_web,
        taxi_config,
        driver_orders_mock,
        load_json,
        enable_provider,
        request_type,
        request_file,
):
    taxi_config.set_values(
        {'HIRING_CANDIDATES_ENABLE_PICKUP_RIDES_FILTER': enable_provider},
    )
    await taxi_hiring_candidates_web.invalidate_caches()

    request_body = 'has_rides'
    data = load_json(request_file)[request_type]
    await get_response_body(taxi_hiring_candidates_web, data, request_body)

    assert driver_orders_mock.has_calls
    response = driver_orders_mock.next_call()['request']
    data = response.json
    order = data['query']['park']['order']

    if enable_provider:
        assert order.get('providers') == ['platform']
    else:
        assert not order.get('providers')
