import datetime

import pytest


AUTH_PARAMS = {
    'db': 'park1',
    'll': '37.590533,55.733863',
    'session': 'session1',
}

AUTH_HEADERS = {'Accept-Language': 'ru', 'User-Agent': 'Taximeter 8.80 (562)'}


def validate_payment_types_response(
        response, expected_active, expected_reason=None,
):
    assert len(response) == 3
    payment_types = {item['payment_type'] for item in response}
    assert payment_types == {'cash', 'online', 'none'}
    for item in response:
        active = item['active']
        assert active == bool(expected_active == item['payment_type'])
        if expected_reason and not active:
            assert item['reason']['title'] == expected_reason
            assert item['available'] is False
        else:
            assert item['available'] is True
            assert 'reason' not in item


def fetch_reasons(payment_types):
    res = {}
    for i in payment_types:
        res[i['payment_type']] = i.get('reason', {}).get('title')
    return res


def validate_payment_type_db(mongodb, license_pd_id, payment_type):
    doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': license_pd_id},
    )
    assert doc['payment_type'] == payment_type


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


def generate_parks_activation(clid, payment_types, is_deactivated=False):
    park = {
        'revision': 1,
        'last_modified': '1970-01-15T03:56:07.000',
        'park_id': clid,
        'city_id': 'spb',
        'data': {
            'deactivated': is_deactivated,
            'can_cash': 'cash' in payment_types,
            'can_card': 'card' in payment_types,
            'can_coupon': 'coupon' in payment_types,
            'can_corp': 'corp' in payment_types,
        },
    }
    if is_deactivated:
        data = park['data']
        data['deactivated_reason'] = 'blocked'
    return [park]


@pytest.mark.parametrize(
    'driver_profile_id,park_id,payment_type',
    [
        ('driver1', 'park1', 'cash'),
        ('driver2', 'park3', 'online'),
        ('driver1', 'park3', 'none'),
    ],
)
async def test_driver_get(
        taxi_driver_payment_types,
        driver_authorizer,
        driver_profile_id,
        park_id,
        payment_type,
):
    driver_authorizer.set_session(park_id, 'session1', driver_profile_id)

    custom_auth = {
        'park_id': park_id,
        'll': '37.590533,55.733863',
        'session': 'session1',
    }

    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=custom_auth,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response = response.json()
    assert len(response) == 2
    assert response['enable_on_ui'] is True
    validate_payment_types_response(response['payment_types'], payment_type)


async def test_driver_get_zone_settings(
        taxi_driver_payment_types, driver_authorizer, tariffs_local,
):
    tariffs_local.set_payment_options(['card'])
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response = response.json()
    assert len(response) == 2
    assert response['enable_on_ui'] is True
    validate_payment_types_response(
        response['payment_types'], 'online', 'zone_settings_title',
    )


async def test_driver_get_zone_settings_card_fallback(
        taxi_driver_payment_types, driver_authorizer, tariffs_local,
):
    tariffs_local.set_payment_options(['unknown_option'])
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response = response.json()
    assert len(response) == 2
    assert response['enable_on_ui'] is True
    validate_payment_types_response(
        response['payment_types'], 'online', 'zone_settings_title',
    )


async def test_driver_get_low_balance(
        taxi_driver_payment_types,
        driver_authorizer,
        billing_reports,
        mock_parks_lowbalance_drivers,
        mockserver,
):

    billing_reports.set_driver_balance('park1', 'driver1', 'RUB', -100)
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response = response.json()
    assert len(response) == 2
    assert response['enable_on_ui'] is True
    validate_payment_types_response(
        response['payment_types'], 'online', 'low_balance_title',
    )


@pytest.mark.config(DRIVER_PAYMENT_TYPE_MAX_ENABLED_COUNT=2)
async def test_driver_get_limit_exceed(
        taxi_driver_payment_types, driver_authorizer,
):
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response = response.json()
    assert len(response) == 2
    assert response['enable_on_ui'] is True
    assert (
        response['payment_types'][1]['reason']['title'] == 'limit_exceed_title'
    )
    assert (
        'reason' not in response['payment_types'][0]
        and 'reason' not in response['payment_types'][2]
    )


@pytest.mark.config(DRIVER_PAYMENT_TYPE_CLEANUP_PERIOD=123)
@pytest.mark.now('2020-03-01T10:00:00.000Z')
@pytest.mark.parametrize('payment_type', ['online', 'cash', 'none'])
async def test_driver_post_successful(
        taxi_driver_payment_types, driver_authorizer, mongodb, payment_type,
):
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
        json={'payment_type': payment_type},
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 3
    validate_payment_types_response(response['payment_types'], payment_type)
    assert response['success'] is True
    doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_1'},
    )
    assert doc['payment_type'] == payment_type
    if payment_type != 'cash':
        cleanup_datetime = datetime.datetime(
            2020, 3, 1, 10,
        ) + datetime.timedelta(minutes=123)
        assert doc['cleanup_datetime'] == cleanup_datetime


@pytest.mark.parametrize(
    'payment_type,success',
    [('online', True), ('cash', False), ('none', False)],
)
async def test_driver_post_low_balance(
        taxi_driver_payment_types,
        driver_authorizer,
        payment_type,
        success,
        mock_parks_lowbalance_drivers,
        mockserver,
):
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
        json={'payment_type': payment_type},
    )
    assert response.status_code == 200
    response = response.json()
    validate_payment_types_response(
        response['payment_types'], 'online', 'low_balance_title',
    )
    assert response['success'] is success


@pytest.mark.parametrize(
    'payment_type,should_increase',
    [('online', True), ('cash', False), ('none', False)],
)
async def test_driver_post_enabled_count(
        taxi_driver_payment_types,
        driver_authorizer,
        mongodb,
        payment_type,
        should_increase,
):
    doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_1'},
    )
    enabled_count = doc['enabled_count']
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
        json={'payment_type': payment_type},
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 3
    validate_payment_types_response(response['payment_types'], payment_type)
    doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_1'},
    )
    assert enabled_count + should_increase == doc['enabled_count']


@pytest.mark.parametrize(
    'payment_type,success',
    [('online', False), ('cash', True), ('none', True)],
)
async def test_driver_post_limit_exceed(
        taxi_driver_payment_types,
        driver_authorizer,
        mongodb,
        payment_type,
        success,
):
    mongodb.driver_payment_type.update(
        {'license_pd_id': 'driver_license_pd_id_1'},
        {'$set': {'enabled_count': 5}},
    )
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
        json={'payment_type': payment_type},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['success'] is success
    if not success:
        assert response['reason']['title'] == 'limit_exceed_title'
    doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_1'},
    )
    assert doc['enabled_count'] == 5
    reasons = fetch_reasons(response['payment_types'])
    assert reasons == {
        'none': None,
        'online': 'limit_exceed_title',
        'cash': None,
    }


@pytest.mark.parametrize(
    'driver_profile_id,park_id,parks_activation_payment_types,'
    'parks_activation_is_deactivated,reason,payment_types_result',
    [
        ('driver1', 'park1', {'cash', 'card'}, False, None, 'cash'),
        ('driver1', 'park1', {'coupon', 'card'}, False, None, 'cash'),
        (
            'driver1',
            'park1',
            {'cash'},
            False,
            'parks_activation_title',
            'cash',
        ),
        ('driver1', 'park1', {'online'}, False, None, None),
        ('driver1', 'park1', {'online'}, True, 'disabled_title', 'none'),
        ('driver1', 'park1', {}, False, None, None),
    ],
)
async def test_driver_get_parks_activation(
        taxi_driver_payment_types,
        driver_authorizer,
        driver_profile_id,
        park_id,
        parks_activation_payment_types,
        parks_activation_is_deactivated,
        reason,
        payment_types_result,
        parks_activation_mocks,
):
    driver_authorizer.set_session(park_id, 'session1', driver_profile_id)
    parks_activation_mocks.set_parks(
        generate_parks_activation(
            'clid0',
            parks_activation_payment_types,
            parks_activation_is_deactivated,
        ),
    )

    custom_auth = {
        'park_id': park_id,
        'll': '37.590533,55.733863',
        'session': 'session1',
    }

    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=custom_auth,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response) == 2
    assert (
        response['enable_on_ui'] is not parks_activation_is_deactivated
        or payment_types_result is None
    )
    if payment_types_result is not None:
        validate_payment_types_response(
            response['payment_types'], payment_types_result, reason,
        )


async def test_driver_get_no_nearest_zone(
        taxi_driver_payment_types, driver_authorizer,
):
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params={
            'db': 'park1',
            'll': '11.590533,22.733863',
            'session': 'session1',
        },
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response = response.json()
    assert len(response) == 2
    assert response['enable_on_ui'] is False
    validate_payment_types_response(
        response['payment_types'], 'none', 'disabled_title',
    )


async def test_driver_post_no_nearest_zone(
        taxi_driver_payment_types, driver_authorizer,
):
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params={'db': 'park1', 'll': '11.123,22.234', 'session': 'session1'},
        headers=AUTH_HEADERS,
        json={'payment_type': 'cash'},
    )
    assert response.status_code == 200
    response = response.json()
    validate_payment_types_response(
        response['payment_types'], 'none', 'disabled_title',
    )
    assert response['success'] is False


async def test_get_disabled_no_license_found(
        taxi_driver_payment_types, driver_authorizer,
):
    driver_authorizer.set_session('park1', 'session1', 'driver4')

    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    response = response.json()
    assert response['enable_on_ui'] is False
    validate_payment_types_response(
        response['payment_types'], 'none', 'disabled_title',
    )


async def test_post_disabled_no_license_found(
        taxi_driver_payment_types, driver_authorizer,
):
    driver_authorizer.set_session('park1', 'session1', 'driver4')

    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
        json={'payment_type': 'cash'},
    )

    assert response.status_code == 200

    response = response.json()
    assert response['enable_on_ui'] is False
    assert response['success'] is False
    validate_payment_types_response(
        response['payment_types'], 'none', 'disabled_title',
    )


async def test_post_disabled_no_park(
        taxi_driver_payment_types, driver_authorizer, parks_activation_mocks,
):
    driver_authorizer.set_session('park1', 'session1', 'driver1')
    parks_activation_mocks.set_parks([])

    response = await taxi_driver_payment_types.post(
        'driver/available-payment-types',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
        json={'payment_type': 'cash'},
    )

    assert response.status_code == 200

    response = response.json()
    assert response['enable_on_ui'] is False
    assert response['success'] is False
    validate_payment_types_response(
        response['payment_types'], 'none', 'disabled_title',
    )


@pytest.mark.config(
    HEATMAP_CACHE_NGROUPS_FETCH_SOURCE={'__default__': 'heatmap-storage'},
    DRIVER_PAYMENT_TYPE_MAX_ENABLED_COUNT=100,
)
@pytest.mark.parametrize(
    'park_id,driver_id,blocked_payment_types',
    [
        ('park1', 'driver1', ['online']),  # license_pd_id_1
        ('park3', 'driver2', ['cash']),  # license_pd_id_5
        ('park3', 'driver3', ['online', 'cash']),  # license_pd_id_6
    ],
)
async def test_driver_in_surge(
        taxi_driver_payment_types,
        driver_authorizer,
        heatmap_storage,
        park_id,
        driver_id,
        blocked_payment_types,
):
    driver_authorizer.set_session(park_id, 'session1', driver_id)
    heatmap_storage.build_and_set_surge_map(
        cell_size_meter=500.123,
        envelope={'tl': [37.59053, 55.73386], 'br': [38.15, 58.12]},
        values=[{'x': 0, 'y': 0, 'surge': 200.0, 'weight': 1.0}],
        grid_extra={'surge': 200},
    )
    custom_auth = {
        'park_id': park_id,
        'll': '37.590533,55.733863',
        'session': 'session1',
    }
    response = await taxi_driver_payment_types.get(
        'driver/available-payment-types',
        params=custom_auth,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    payment_types = {
        item['payment_type']: item for item in response.json()['payment_types']
    }
    online_available = 'online' not in blocked_payment_types
    cash_available = 'cash' not in blocked_payment_types
    assert payment_types['none']['available']
    assert payment_types['online']['available'] == online_available
    assert payment_types['cash']['available'] == cash_available
    if not online_available:
        assert payment_types['online']['reason']['title'] == 'surge_title'
    if not cash_available:
        assert payment_types['cash']['reason']['title'] == 'surge_title'
