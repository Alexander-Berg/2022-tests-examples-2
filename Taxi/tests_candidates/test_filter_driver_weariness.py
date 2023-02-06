import pytest


@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={
        '__default__': False,
        'Москва': True,
    },
)
async def test_filter_ok_driver(
        taxi_candidates, driver_positions, mockserver, load_binary,
):
    @mockserver.json_handler('/driver-weariness/v1/tired-drivers')
    def _tired_drivers(request):
        return {'items': []}

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 1,
        'filters': ['efficiency/driver_weariness'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }

    response = await taxi_candidates.post('search', json=request_body)
    await taxi_candidates.invalidate_caches()

    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1


@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={
        '__default__': True,
        'Москва': False,
    },
)
async def test_filter_tired_driver_but_park_disabled(
        taxi_candidates, driver_positions, mockserver, load_binary,
):
    @mockserver.json_handler('/driver-weariness/v1/tired-drivers')
    def _tired_drivers(request):
        return {
            'items': [
                {
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'tired_status': 'hours_exceed',
                    'block_till': '1970-01-01T00:00:00.0+0000',
                    'block_time': '1970-01-01T00:00:00.0+0000',
                },
            ],
        }

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 1,
        'filters': ['efficiency/driver_weariness'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }

    response = await taxi_candidates.post('search', json=request_body)
    await taxi_candidates.invalidate_caches()

    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1


@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={
        '__default__': False,
        'Москва': True,
    },
)
async def test_filter_tired_driver_hours(
        taxi_candidates, driver_positions, mockserver, load_binary,
):
    @mockserver.json_handler('/driver-weariness/v1/tired-drivers')
    def _tired_drivers(request):
        return {
            'items': [
                {
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'tired_status': 'hours_exceed',
                    'block_till': '1970-01-01T00:00:00.0+0000',
                    'block_time': '1970-01-01T00:00:00.0+0000',
                },
            ],
        }

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 1,
        'filters': ['efficiency/driver_weariness'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }

    response = await taxi_candidates.post('search', json=request_body)
    await taxi_candidates.invalidate_caches()

    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert json['drivers'] == []


@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={'__default__': True},
)
async def test_filter_tired_driver_no_rest(
        taxi_candidates, driver_positions, mockserver, load_binary,
):
    @mockserver.json_handler('/driver-weariness/v1/tired-drivers')
    def _tired_drivers(request):
        return {
            'items': [
                {
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'tired_status': 'no_long_rest',
                    'block_till': '1970-01-01T00:00:00.0+0000',
                    'block_time': '1970-01-01T00:00:00.0+0000',
                },
            ],
        }

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 1,
        'filters': ['efficiency/driver_weariness'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }

    response = await taxi_candidates.post('search', json=request_body)
    await taxi_candidates.invalidate_caches()

    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert json['drivers'] == []
