import pytest


def validate_payment_types_response(
        response, expected_active, expected_reasons=None,
):
    assert len(response) == 3
    payment_types = {item['payment_type'] for item in response}
    assert payment_types == {'cash', 'online', 'none'}
    if expected_active:
        reasons = set()
        for item in response:
            active = item['active']
            assert active == bool(expected_active == item['payment_type'])
            if not active and expected_reasons:
                assert item['available'] is False
                reasons = reasons.union(item['reasons'])
        if expected_reasons:
            assert reasons == expected_reasons


async def test_bulk_retrieve(taxi_driver_payment_types):
    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'park1',
                    'driver_profile_id': 'driver1',
                    'position': [37.590533, 55.733863],
                },
                {
                    'park_id': 'park2',
                    'driver_profile_id': 'driver2',
                    'position': [37.590533, 55.733863],
                },
                {
                    'park_id': 'park2',
                    'driver_profile_id': 'driver3',
                    'position': [37.590533, 55.733863],
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'items' in response
    items = response['items']
    assert len(items) == 3
    for item in items:
        assert 'park_id', 'driver_profile_id' in item
        validate_payment_types_response(item['payment_types'], 'cash')


async def test_bulk_retrieve_parks_request(
        taxi_driver_payment_types, mockserver,
):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _driver_profiles_list(request):
        request = request.json
        park = request['query']['park']
        assert park['id'] == 'park1'
        driver_profiles_list = park.get('driver_profile', {}).get('id', [])
        driver_profiles_ids = [i for i in driver_profiles_list]
        assert driver_profiles_ids == ['driver1']
        driver_profiles = [
            {
                'accounts': [
                    {
                        'balance': '100',
                        'balance_limit': '100',
                        'id': 'driver1',
                    },
                ],
                'driver_profile': {'id': 'driver1'},
            },
        ]
        return {
            'parks': [{'country_id': 'rus'}],
            'driver_profiles': driver_profiles,
            'offset': 0,
            'total': 1,
        }

    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'park1',
                    'driver_profile_id': 'driver1',
                    'position': [37.590533, 55.733863],
                },
            ],
        },
    )
    assert response.status_code == 200


@pytest.mark.config(DRIVER_PAYMENT_TYPE_DISABLED_COUNTRIES=['rou'])
async def test_disabled_country(taxi_driver_payment_types, parks, mockserver):
    @mockserver.json_handler('territories/v1/countries/list')
    def _mock_territories(request):
        return {
            'countries': [
                {
                    '_id': 'rou',
                    'code2': 'RO',
                    'phone_code': '',
                    'phone_min_length': 1,
                    'phone_max_length': 1,
                    'national_access_code': '000',
                    'region_id': 0,
                },
            ],
        }

    parks.set_park_country('rou_park', 'rou')
    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'rou_park',
                    'driver_profile_id': 'driver1',
                    'position': [37.590533, 55.733863],
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    validate_payment_types_response(
        response['items'][0]['payment_types'], 'none', {'disabled'},
    )


async def test_no_nearest_zone(taxi_driver_payment_types):
    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'park1',
                    'driver_profile_id': 'driver1',
                    'position': [45.590533, 30.733863],
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'payment_types' not in response['items'][0]


@pytest.mark.parametrize(
    'zone_payment_types,expected_payment_type',
    [(['cash', 'card'], 'none'), (['cash'], 'cash'), (['card'], 'online')],
)
async def test_one_payment_type(
        taxi_driver_payment_types,
        tariffs_local,
        zone_payment_types,
        expected_payment_type,
):
    tariffs_local.set_payment_options(zone_payment_types)
    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'park3',
                    'driver_profile_id': 'driver1',
                    'position': [37.590533, 55.733863],
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    validate_payment_types_response(
        response['items'][0]['payment_types'], expected_payment_type,
    )


async def test_multiple_reasons(
        taxi_driver_payment_types,
        tariffs_local,
        mockserver,
        mock_parks_lowbalance_drivers,
):

    tariffs_local.set_payment_options(['cash'])

    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'park1',
                    'driver_profile_id': 'driver1',
                    'position': [37.590533, 55.733863],
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert 'items' in response
    items = response['items']
    for item in items:
        assert 'park_id', 'driver_profile_id' in item
        validate_payment_types_response(
            item['payment_types'], 'cash', {'zone_settings', 'low_balance'},
        )


@pytest.mark.parametrize(
    'work_mode,parks_balance,expected_payment_type',
    [
        ('parks', 100, 'cash'),
        ('parks', 50, 'online'),
        ('parks_with_verification', 50, 'online'),
    ],
)
async def test_billing_source_config(
        taxi_driver_payment_types,
        parks,
        expected_payment_type,
        work_mode,
        parks_balance,
        taxi_config,
):
    taxi_config.set_values(
        dict(DRIVER_PAYMENT_TYPE_BALANCE_SOURCE=dict(__default__=work_mode)),
    )

    parks.set_balance_info('park1', 'driver1', parks_balance, 100)

    response = await taxi_driver_payment_types.post(
        'service/v1/bulk-retrieve',
        json={
            'source': 'test',
            'items': [
                {
                    'park_id': 'park1',
                    'driver_profile_id': 'driver1',
                    'position': [37.590533, 55.733863],
                },
            ],
        },
    )
    assert response.status_code == 200
    response = response.json()
    validate_payment_types_response(
        response['items'][0]['payment_types'], expected_payment_type,
    )
