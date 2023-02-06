import pytest

EXPECTED_ADD_SAMPLES_REQUEST = {
    'samples': [
        {
            'map_name': 'econom/default',
            'meta': {
                'calculation_type': 0,
                'free': 148,
                'free_chain': 3,
                'personal_phone_id': 'some_phone_id',
                'pins': 6,
                'pins_driver': 3,
                'pins_order': 2,
                'radius': 7,
                'total': 4,
                'user_id': 'some_user_id',
            },
            'point': {'lat': 51.0, 'lon': 38.1},
            'type': 'taxi_surge',
            'value': 1.0,
            'weight': 1.0,
        },
        {
            'map_name': 'econom/alternative',
            'meta': {
                'calculation_type': 0,
                'free': 148,
                'free_chain': 3,
                'personal_phone_id': 'some_phone_id',
                'pins': 6,
                'pins_driver': 3,
                'pins_order': 2,
                'radius': 7,
                'total': 4,
                'user_id': 'some_user_id',
            },
            'point': {'lat': 51.0, 'lon': 38.1},
            'type': 'taxi_surge',
            'value': 2.0,
            'weight': 1.0,
        },
    ],
}


@pytest.mark.now('2117-01-01T00:00:00.00000+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    SURGE_CALCULATOR_ADD_SAMPLES_TYPES=['default'],
    SURGE_CALCULATOR_ADD_SAMPLES_CATEGORIES=['econom'],
    SURGE_CACHE_SETTINGS={
        'ENABLED': True,
        'GEOHASH_SIZE': 7,
        'TTL_SEC': 120,
        'PROLONG_BY_USER_TTL_SEC': 310,
    },
)
@pytest.mark.parametrize('add_from_cache', (False, True))
async def test_add_samples(
        taxi_surge_calculator,
        mockserver,
        taxi_config,
        testpoint,
        add_from_cache,
        heatmap_storage_fixture,
):
    actual_requests = []

    @mockserver.json_handler('/heatmap-sample-storage/v1/add_samples')
    def add_samples(request):
        actual_requests.append(request.json)
        return {'timestamp': '2018-08-01T12:59:23.231000+00:00'}

    @testpoint('surge-cache-saved')
    def surge_cache_saved(_json):
        pass

    taxi_config.set(CREATE_SAMPLES_FROM_CACHED_VALUES=add_from_cache)
    request = {
        'point_a': [38.1, 51],
        'user_id': 'some_user_id',
        'phone_id': 'some_phone_id',
    }
    # Two requests to test cache influence
    await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    await surge_cache_saved.wait_call()
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200

    await add_samples.wait_call()
    expected_requests = [EXPECTED_ADD_SAMPLES_REQUEST]
    if add_from_cache:
        await add_samples.wait_call()
        expected_requests.append(EXPECTED_ADD_SAMPLES_REQUEST)
    assert actual_requests == expected_requests
