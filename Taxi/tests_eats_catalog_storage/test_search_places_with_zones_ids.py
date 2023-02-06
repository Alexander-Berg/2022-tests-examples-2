import pytest


OPTIMIZED_CONFIG = pytest.mark.config(
    EATS_CATALOG_STORAGE_PERFORMANCE={
        'zone_search_by_point': {
            'prefilter_zone_places': True,
            'prefilter_with_inner_geometry': True,
            'polygon_filter_chunk_size': 1,
        },
    },
)
PARAMETRIZE_WITH_OPTIMIZED = pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=[], id='unoptimized'),
        pytest.param(marks=[OPTIMIZED_CONFIG], id='optimized'),
    ],
)


def assert_response_ids(response, place_ids, zone_ids):
    r_zone_ids = set()
    r_place_ids = set()

    assert 'ids' in response
    for place in response['ids']:
        r_place_ids.add(place['place_id'])
        assert len(set(place['zone_ids'])) == len(place['zone_ids'])
        for zone_id in place['zone_ids']:
            r_zone_ids.add(zone_id)

    assert r_place_ids == place_ids, 'unexpected set of place_ids'
    assert r_zone_ids == zone_ids, 'unexpected set of zone_ids'


async def search_places_with_zones(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/search/places-zones-ids'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_empty_request(taxi_eats_catalog_storage):
    request_json = {}
    response = await search_places_with_zones(
        taxi_eats_catalog_storage, request_json,
    )
    assert response.status_code == 200

    response_data = response.json()
    assert 'ids' in response_data
    assert not response_data['ids']


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_geo_point(taxi_eats_catalog_storage):
    data = {'geo_point': [0.5, 0.5]}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_slug(taxi_eats_catalog_storage):
    data = {'place_slug': 'slug20'}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 103, 104, 105})


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_brand_ids(taxi_eats_catalog_storage):
    data = {'brand_ids': [1, 2]}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {10, 11}, {100, 105})


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_brand_ids_and_geo_point(taxi_eats_catalog_storage):
    data = {'brand_ids': [3, 4], 'geo_point': [0.5, 0.5]}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 105})


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_brand_ids_and_place_enabled_only(
        taxi_eats_catalog_storage,
):
    data = {'brand_ids': [1, 2], 'place_enabled_only': True}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {10}, set())


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_enabled_only_and_geo_point(
        taxi_eats_catalog_storage,
):
    data = {'geo_point': [0.5, 0.5], 'place_enabled_only': True}
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 105})


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_slug_brand_ids_geo_point(
        taxi_eats_catalog_storage,
):
    data = {
        'place_slug': 'slug20',
        'brand_ids': [3, 4],
        'geo_point': [0.5, 0.5],
    }
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, {20}, {101, 102, 105})


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_by_place_slug_brand_ids_geo_point_empty_resp(
        taxi_eats_catalog_storage,
):
    data = {
        'place_slug': 'slug10',
        'brand_ids': [3, 4],
        'geo_point': [0.5, 0.5],
    }
    response = await search_places_with_zones(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert 'ids' in response_data
    assert not response_data['ids']


@PARAMETRIZE_WITH_OPTIMIZED
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
@pytest.mark.parametrize(
    'body, expected_place_ids, expected_zone_ids',
    [
        pytest.param(
            {'place_ids': [20]},
            {20},
            {101, 102, 103, 104, 105},
            id='search by place ids',
        ),
        pytest.param(
            {'place_ids': [20], 'brand_ids': [4]},
            set(),
            set(),
            id='search by place ids and brand ids',
        ),
        pytest.param(
            {'place_ids': [20], 'brand_ids': [3]},
            {20},
            {101, 102, 103, 104, 105},
            id='search by place ids and brand ids',
        ),
        pytest.param(
            {'place_ids': [20], 'brand_ids': [3], 'geo_point': [0.5, 0.5]},
            {20},
            {101, 102, 105},
            id='search by place ids and brand ids and geo point',
        ),
        pytest.param(
            {'place_ids': [20], 'geo_point': [5, 5]},
            {20},
            {102},
            id='search by place ids and geo point in 3rd polygon',
        ),
        pytest.param(
            {
                'place_ids': [20],
                'brand_ids': [3],
                'geo_point': [0.5, 0.5],
                'place_slug': 'slug20',
            },
            {20},
            {101, 102, 105},
            id='search by place ids and brand ids and geo point and slug',
        ),
        pytest.param(
            {
                'place_ids': [10],
                'brand_ids': [4],
                'geo_point': [0.5, 0.5],
                'place_slug': 'slug20',
            },
            set(),
            set(),
            id='search by place ids and brand ids and geo point and slug',
        ),
        pytest.param(
            {'brand_slug': 'brand_slug2'},
            {11},
            {100, 105},
            id='search by brand slug',
        ),
        pytest.param(
            {'brand_slug': 'brand_slug2', 'place_enabled_only': True},
            set(),
            set(),
            id='search by brand slug enabled only',
        ),
        pytest.param(
            {'brand_slug': 'brand_slug2', 'brand_ids': [2, 3]},
            {11},
            {100, 105},
            id='search by brand slug and brand ids',
        ),
        pytest.param(
            {'brand_slug': 'brand_slug3', 'geo_point': [0.5, 0.5]},
            {20},
            {101, 102, 105},
            id='search by brand slug and geo point',
        ),
        pytest.param(
            {'brand_slug': 'unknown'},
            set(),
            set(),
            id='search by unknown brand slug',
        ),
    ],
)
async def test_search(
        taxi_eats_catalog_storage, body, expected_place_ids, expected_zone_ids,
):
    response = await search_places_with_zones(taxi_eats_catalog_storage, body)
    assert response.status_code == 200

    response_data = response.json()
    assert_response_ids(response_data, expected_place_ids, expected_zone_ids)
