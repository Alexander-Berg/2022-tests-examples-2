import pytest

AUTH_PARAMS = {'park_id': 'test_db'}

AUTH_HEADERS = {
    'Accept-Language': 'ru',
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-Driver-Session': 'test_session',
}


def update_settings(load_json, config, update):
    new_config = load_json('config.json')['DRIVER_CCTV_MAP_ZONES_SETTINGS']
    new_config.update(update)
    config.set_values(dict(DRIVER_CCTV_MAP_ZONES_SETTINGS=new_config))


async def test_driver_cctv_zones(
        taxi_driver_cctv_map, mockserver, load_json, driver_authorizer,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return load_json('pickuppoints_single_polygon.json')

    response = await taxi_driver_cctv_map.get(
        'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert 'ETag', 'Cache-Control' in response.headers
    response = response.json()
    zones = response['cctv_zones']
    assert len(zones) == 1
    assert set(zones[0]['geohash']) == {
        'ucfsym',
        'ucfsyj',
        'ucfsyt',
        'ucfsyk',
        'ucfsyh',
        'ucfsys',
        'ucfsyq',
        'ucfsyn',
        'ucfsyw',
    }
    assert len(zones[0]) == 5


@pytest.mark.parametrize(
    'driver_zone_types',
    (
        pytest.param(
            ['falcon_taximeter', 'dedicated_lanes'],
            marks=pytest.mark.experiments3(
                name='taximeter_zones',
                consumers=['driver-cctv-map'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={
                    'zones': [
                        {'type': 'falcon_taximeter'},
                        {'type': 'dedicated_lanes'},
                    ],
                },
            ),
        ),
        pytest.param(
            ['dedicated_lanes'],
            marks=pytest.mark.experiments3(
                name='taximeter_zones',
                consumers=['driver-cctv-map'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={'zones': [{'type': 'dedicated_lanes'}]},
            ),
        ),
        pytest.param(
            [],
            marks=pytest.mark.experiments3(
                name='taximeter_zones',
                consumers=['driver-cctv-map'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={'zones': []},
            ),
        ),
    ),
)
async def test_driver_cctv_different_zone_types(
        taxi_driver_cctv_map,
        mockserver,
        load_json,
        driver_authorizer,
        driver_zone_types,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        request_json = request.json
        allowed_zone_types = request_json['filter']['allowed_zone_types']
        assert set(allowed_zone_types) == set(driver_zone_types)
        return load_json('pickuppoints_different_types.json')

    response = await taxi_driver_cctv_map.get(
        'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert 'ETag', 'Cache-Control' in response.headers
    response = response.json()
    zones = response['cctv_zones']
    types = [zone['type'] for zone in zones]
    assert set(types) == set(driver_zone_types)


async def test_driver_cctv_separated_zones(
        taxi_driver_cctv_map, mockserver, driver_authorizer, load_json,
):
    polygon_num = 0

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        nonlocal polygon_num
        response = load_json('pickuppoints_single_polygon.json')
        response['zones'][0]['id'] += str(polygon_num)
        polygon_num += 1
        return response

    response = await taxi_driver_cctv_map.get(
        'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    assert len(response['cctv_zones']) == 9


async def test_special_zones_bad_respones(
        taxi_driver_cctv_map, mockserver, driver_authorizer,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return mockserver.make_response('{"message": "something bad"}', 500)

    response = await taxi_driver_cctv_map.get(
        'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['cctv_zones'] == []


async def test_cctv_map_cache(
        taxi_driver_cctv_map, load_json, mockserver, driver_authorizer,
):
    call_count = 0

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        nonlocal call_count
        call_count += 1
        return load_json('pickuppoints_single_polygon.json')

    response = await taxi_driver_cctv_map.get(
        'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert call_count == 9
    call_count = 0

    response = await taxi_driver_cctv_map.get(
        'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert call_count == 0


@pytest.mark.parametrize(
    'config_update,expected_code,special_zones_calls,'
    'expected_zone_type,expected_etag',
    [
        ({'enable': False}, 200, 0, 'falcon_taximeter', 'empty_response'),
        (
            {'pickuppoints_request_zone_type': 'some_type'},
            200,
            9,
            'some_type',
            None,
        ),
        ({'min_request_geohash_length': 10}, 400, 0, 'falcon_taximeter', None),
        ({'return_neighbour_areas': False}, 200, 1, 'falcon_taximeter', None),
    ],
)
async def test_cctv_map_config_settings(
        taxi_driver_cctv_map,
        taxi_config,
        mockserver,
        config_update,
        expected_code,
        load_json,
        special_zones_calls,
        expected_etag,
        expected_zone_type,
        driver_authorizer,
):
    # independent geohash in every call to avoid storing response in cache
    update_settings(load_json, taxi_config, config_update)
    call_count = 0

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        nonlocal call_count
        request_json = request.json
        call_count += 1
        allowed_zone_types = request_json['filter']['allowed_zone_types']
        assert allowed_zone_types == [expected_zone_type]
        if 'falcon_taximeter' in allowed_zone_types:
            return load_json('pickuppoints_single_polygon.json')
        return load_json('pickuppoints_empty_response.json')

    response = await taxi_driver_cctv_map.get(
        f'driver/cctv-map/v1/zones/ucfsym',
        params=AUTH_PARAMS,
        headers=AUTH_HEADERS,
    )
    assert response.status_code == expected_code
    assert call_count == special_zones_calls
    if expected_code == 200:
        if expected_etag:
            assert response.headers['ETag'] == expected_etag
