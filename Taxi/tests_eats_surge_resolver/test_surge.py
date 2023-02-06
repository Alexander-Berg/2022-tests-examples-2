import copy

import pytest


PLACES = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 3,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 101,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {
            'id': 2,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'marketplace',
        'enabled': True,
    },
]

EXPECTED_RESPONSE = {
    'id': 1,
    'jsonrpc': '2.0',
    'result': [
        {
            'calculatorName': 'calc_surge_eats_2100m',
            'nativeInfo': {
                'deliveryFee': 399.0,
                'loadLevel': 85,
                'surgeLevel': 3,
                'busy': 0,
                'free': 0,
            },
            'marketplaceInfo': {
                'loadLevel': 85,
                'additionalTimePercents': 30,
                'surgeLevel': 3,
            },
            'taxiInfo': {
                'surgeLevel': 2,
                'show_radius': 500,
                'deliveryFee': 59.9,
            },
            'placeId': 1,
            'revisionId': 1,
        },
        {
            'calculatorName': 'calc_surge_eats_2100m',
            'nativeInfo': {
                'deliveryFee': 199.0,
                'loadLevel': 85,
                'surgeLevel': 3,
                'show_radius': 100.0,
                'busy': 0,
                'free': 0,
            },
            'marketplaceInfo': {
                'loadLevel': 85,
                'additionalTimePercents': 30,
                'surgeLevel': 3,
            },
            'placeId': 2,
            'revisionId': 1,
        },
        {
            'calculatorName': 'calc_surge_eats_2100m',
            'nativeInfo': {
                'deliveryFee': 299.0,
                'loadLevel': 85,
                'surgeLevel': 3,
                'busy': 0,
                'free': 0,
            },
            'marketplaceInfo': {
                'loadLevel': 85,
                'additionalTimePercents': 30,
                'surgeLevel': 3,
            },
            'placeId': 3,
            'revisionId': 1,
        },
        {
            'calculatorName': 'calc_surge_eats_2100m',
            'marketplaceInfo': {
                'additionalTimePercents': 0,
                'loadLevel': 0,
                'surgeLevel': 0,
            },
            'placeId': 101,
            'revisionId': 1,
        },
        {
            'placeId': 404,
            'nativeInfo': {
                'deliveryFee': 0.0,
                'loadLevel': 0,
                'surgeLevel': 0,
            },
        },
    ],
}


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.pgsql('surge', files=['db_surge.sql'])
async def test_surge_native(taxi_eats_surge_resolver, mockserver, pgsql):
    place_ids = [1, 2, 3, 101, 404]
    request = {
        'jsonrpc': '2.0',
        'method': 'surge.FindByPlaceIds',
        'id': 1,
        'params': {'placeIds': place_ids, 'ts': '2021-02-20T10:05:41+00:00'},
    }

    # check v1 api
    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200

    response = response.json()

    assert response == EXPECTED_RESPONSE

    # check v2 api
    response = await taxi_eats_surge_resolver.post(
        'api/v2/surge-level',
        json={
            'placeIds': place_ids,
            'ts': '2021-02-20T10:05:42+00:00',
            'calculator_name': 'calc_surge_eats_2100m',
            'user_info': {},
        },
    )
    assert response.status_code == 200

    response = response.json()

    assert response == EXPECTED_RESPONSE['result']


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.pgsql('surge', files=['db_surge_no_marketplace.sql'])
@pytest.mark.config(
    EATS_SURGE_RESOLVER_MARKETPLACE_CONF={
        'enabled': True,
        'surge': {
            'surge_level': 0,
            'load_level': 0,
            'additional_time_percents': 0,
        },
    },
)
async def test_surge_marketplace_conf(
        taxi_eats_surge_resolver, mockserver, pgsql,
):
    place_ids = [1, 2, 3, 101, 404]
    request = {
        'jsonrpc': '2.0',
        'method': 'surge.FindByPlaceIds',
        'id': 1,
        'params': {'placeIds': place_ids, 'ts': '2021-02-20T10:05:41+00:00'},
    }

    # check v1 api
    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = copy.deepcopy(EXPECTED_RESPONSE)
    del expected_response['result'][3]['revisionId']
    assert response == expected_response

    # check v2 api
    response = await taxi_eats_surge_resolver.post(
        'api/v2/surge-level',
        json={
            'placeIds': place_ids,
            'ts': '2021-02-20T10:05:42+00:00',
            'calculator_name': 'calc_surge_eats_2100m',
            'user_info': {},
        },
    )
    assert response.status_code == 200

    response = response.json()

    assert response == expected_response['result']


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.pgsql('surge', files=['db_surge.sql'])
async def test_eda_surge_cache(taxi_eats_surge_resolver, experiments3, pgsql):
    place_ids = [1, 2, 3, 101, 404]
    time = '2021-02-20T10:05:41+00:00'
    request = {
        'jsonrpc': '2.0',
        'method': 'surge.FindByPlaceIds',
        'id': 1,
        'params': {'placeIds': place_ids, 'ts': time},
    }

    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200
    response = response.json()
    assert response == EXPECTED_RESPONSE

    # clear surge values from DB
    cursor = pgsql['surge'].cursor()
    cursor.execute('TRUNCATE TABLE taxi_surger_parts_06')

    # response should be the same due to cache
    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200
    response = response.json()
    assert response == EXPECTED_RESPONSE

    # check v2

    expected_response_v2 = EXPECTED_RESPONSE['result']
    response = await taxi_eats_surge_resolver.post(
        'api/v2/surge-level',
        json={
            'placeIds': place_ids,
            'ts': time,
            'calculator_name': 'calc_surge_eats_2100m',
            'user_info': {},
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response == expected_response_v2

    # check v2 another pipeline, should not be in cache

    response = await taxi_eats_surge_resolver.post(
        'api/v2/surge-level',
        json={
            'placeIds': place_ids,
            'ts': time,
            'calculator_name': 'another_pipeline',
            'user_info': {},
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response != expected_response_v2


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.config(
    EATS_SURGE_RESOLVER_CACHE_SETTINGS={
        'lru_cache': {'enable_cache': False, 'max_size': 1000},
    },
)
@pytest.mark.pgsql('surge', files=['db_surge.sql'])
async def test_eda_surge_cache_off(taxi_eats_surge_resolver, pgsql):
    place_ids = [1, 2, 3, 101, 404]
    request = {
        'jsonrpc': '2.0',
        'method': 'surge.FindByPlaceIds',
        'id': 1,
        'params': {'placeIds': place_ids, 'ts': '2021-02-20T10:05:41+00:00'},
    }

    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200
    response = response.json()
    assert response == EXPECTED_RESPONSE

    cursor = pgsql['surge'].cursor()
    cursor.execute('TRUNCATE TABLE taxi_surger_parts_06')

    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200
    response = response.json()
    assert response != EXPECTED_RESPONSE


@pytest.mark.eats_catalog_storage_cache(PLACES)
@pytest.mark.config(EATS_SURGE_RESOLVER_SUBSTITUTE_VALUES_FLAG=True)
@pytest.mark.experiments3(
    filename='config3_eats_surge_resolver_places_info.json',
)
@pytest.mark.pgsql('surge', files=['db_surge.sql'])
async def test_eats_surge_substitute_values(
        taxi_eats_surge_resolver, grocery_surge,
):
    place_ids = [1, 2, 3, 101, 404]
    time = '2021-02-20T10:05:41+00:00'

    request = {
        'jsonrpc': '2.0',
        'method': 'surge.FindByPlaceIds',
        'id': 1,
        'params': {'placeIds': place_ids, 'ts': time},
    }

    expected_response_copy = copy.deepcopy(EXPECTED_RESPONSE)

    expected_response_copy['result'][0]['nativeInfo']['surgeLevel'] = 2
    expected_response_copy['result'][0]['nativeInfo']['loadLevel'] = 80
    expected_response_copy['result'][0]['nativeInfo']['deliveryFee'] = 100.0
    expected_response_copy['result'][0]['nativeInfo']['show_radius'] = 33.0
    expected_response_copy['result'][0]['lavkaInfo'] = {
        'surgeLevel': 5,
        'loadLevel': 5,
        'minimumOrder': 5,
    }
    expected_response_copy['result'][0]['marketplaceInfo']['surgeLevel'] = 3
    expected_response_copy['result'][0]['marketplaceInfo']['loadLevel'] = 90
    expected_response_copy['result'][0]['marketplaceInfo'][
        'additionalTimePercents'
    ] = 20

    expected_response_copy['result'][1]['marketplaceInfo'] = {
        'surgeLevel': 3,
        'loadLevel': 85,
        'additionalTimePercents': 30,
    }

    expected_response_copy['result'][2]['taxiInfo'] = {
        'surgeLevel': 4,
        'show_radius': 150.0,
        'deliveryFee': 39.9,
    }

    expected_response_copy['result'][3]['marketplaceInfo'] = {
        'surgeLevel': 0,
        'loadLevel': 0,
        'additionalTimePercents': 0,
    }

    expected_response_copy['result'][4]['marketplaceInfo'] = {
        'surgeLevel': 0,
        'loadLevel': 0,
        'additionalTimePercents': 0,
    }

    response = await taxi_eats_surge_resolver.post(
        'api/v1/surge-level', json=request,
    )
    assert response.status_code == 200
    response = response.json()
    print(response)
    assert response == expected_response_copy


@pytest.mark.experiments3(
    filename='config3_eats_surge_resolver_main_clauses.json',
)
@pytest.mark.pgsql('surge', files=['db_surge.sql'])
async def test_surge_personal_phone_id(taxi_eats_surge_resolver, pgsql):
    place_ids = [4]

    exp_phone_resp = [
        {
            'calculatorName': 'calc_surge_eats_2100m',
            'marketplaceInfo': {
                'additionalTimePercents': 15,
                'loadLevel': 85,
                'surgeLevel': 2,
            },
            'nativeInfo': {
                'deliveryFee': 113.0,
                'loadLevel': 85,
                'surgeLevel': 2,
                'busy': 3,
                'free': 2,
            },
            'placeId': 4,
            'revisionId': 1,
        },
    ]

    # check v2 api
    response = await taxi_eats_surge_resolver.post(
        'api/v2/surge-level',
        json={
            'placeIds': place_ids,
            'ts': '2021-02-20T10:05:42+00:00',
            'user_info': {'personal_phone_id': '123'},
        },
    )
    assert response.status_code == 200

    response = response.json()
    assert response == exp_phone_resp
