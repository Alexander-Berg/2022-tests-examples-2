import pytest

from testsuite.utils import ordered_object

from . import experiments


@experiments.zone_priority_config_default
async def test_zones_404(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.post(
        '/lavka/v1/catalog/v1/zones',
        json={'position': {'location': [100, 100]}},
        headers={},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'REGION_NOT_FOUND',
        'message': 'Failed to get region_id with position (100; 100).',
    }


def setup_gdepots(mockserver, depots, zones):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return depots

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return zones


@pytest.mark.config(
    OVERLORD_CATALOG_SHOWN_COMMING_ZONE_TYPES=['pedestrian', 'yandex_taxi'],
)
@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
@pytest.mark.now('2021-11-04T21:01:56+03:00')
async def test_gd_zones_in_testing(
        taxi_overlord_catalog, mockserver, load_json,
):
    setup_gdepots(
        mockserver,
        load_json('gdepots-depots-testing.json'),
        load_json('gdepots-zones-testing.json'),
    )
    response = await taxi_overlord_catalog.post(
        '/lavka/v1/catalog/v1/zones',
        json={'position': {'location': [37.642474, 55.73552]}},
        headers={},
    )
    assert response.status_code == 200
    expected_response = load_json(
        'gdepots_in_testing_expected_for_moscow.json',
    )
    response_json = response.json()
    deep_sort(expected_response)
    deep_sort(response_json)
    ordered_object.assert_eq(
        response_json, expected_response, ['detailed_zones'],
    )


async def test_zones_grocery_depots_404(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.post(
        '/lavka/v1/catalog/v1/zones',
        json={'position': {'location': [100, 100]}},
        headers={},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'REGION_NOT_FOUND',
        'message': 'Failed to get region_id with position (100; 100).',
    }


# Проверяем выдачу по координатам
@pytest.mark.pgsql('overlord_catalog', files=['default.sql'])
@pytest.mark.parametrize(
    'location,region',
    [[[34.806794, 32.081278], 'telaviv'], [[37.619952, 55.752963], 'moscow']],
)
@pytest.mark.now('2021-10-01T15:00:00+00:00')
async def test_zones_by_coordinates(
        taxi_overlord_catalog, location, region, load_json, mockserver,
):
    setup_gdepots_as_defaultsql(mockserver, load_json)
    response = await taxi_overlord_catalog.post(
        '/lavka/v1/catalog/v1/zones',
        json={'position': {'location': location}},
        headers={},
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    response_json = response.json()
    deep_sort(response_json)
    deep_sort(expected_response[region])
    ordered_object.assert_eq(
        response_json, expected_response[region], ['detailed_zones'],
    )


@pytest.mark.pgsql('overlord_catalog', files=['default.sql'])
@pytest.mark.config(
    OVERLORD_CATALOG_SHOWN_COMMING_ZONE_TYPES=['pedestrian', 'yandex_taxi'],
)
@experiments.zone_priority_config_default
@pytest.mark.now('2021-10-01T15:00:00+00:00')
async def test_zones_config(taxi_overlord_catalog, mockserver, load_json):
    setup_gdepots_as_defaultsql(mockserver, load_json)
    response = await taxi_overlord_catalog.post(
        '/lavka/v1/catalog/v1/zones',
        json={'position': {'location': [37.619952, 55.752963]}},
        headers={},
    )
    expected_response = load_json('expected_response_with_config.json')
    assert response.status_code == 200
    resp_json = response.json()
    deep_sort(resp_json)
    deep_sort(expected_response)
    assert resp_json == expected_response


def setup_gdepots_as_defaultsql(mockserver, load_json):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return load_json('g-depots-depots-default.json')

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return load_json('g-depots-zones-default.json')


def deep_sort(data):
    for zone in data['detailed_zones']:
        for points in zone['geozone']['coordinates'][0]:
            points.sort(key=lambda coord: coord['lat'])
    data['detailed_zones'].sort(
        key=lambda x: x['geozone']['coordinates'][0][0][0]['lat'],
        reverse=True,
    )


# Проверяем что приходят спящие зоны
@pytest.mark.pgsql('overlord_catalog', files=['default.sql'])
@pytest.mark.now('2021-04-01T22:00:00+00:00')
@pytest.mark.config(OVERLORD_CATALOG_ZONES_RETRIEVE_TIME={'time': '12:00'})
async def test_zones_by_time(taxi_overlord_catalog, load_json, mockserver):
    setup_gdepots_as_defaultsql(mockserver, load_json)
    response = await taxi_overlord_catalog.post(
        '/lavka/v1/catalog/v1/zones',
        json={'position': {'location': [37.619952, 55.752963]}},
        headers={},
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    resp = response.json()
    moscow = expected_response['moscow']
    deep_sort(resp)
    deep_sort(moscow)
    assert resp == moscow
