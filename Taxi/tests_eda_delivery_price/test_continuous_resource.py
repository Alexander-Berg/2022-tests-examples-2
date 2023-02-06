import copy
import json

import pytest

USE_NP_CACHE = {
    'eda_delivery_price_use_continuous_commission_non_periodic_cache': {
        'description': (
            'Использовать непериодические кэш базы коэффициентов непрерывки'
        ),
        'enabled': True,
    },
}

DONT_USE_NP_CACHE = {
    'eda_delivery_price_use_continuous_commission_non_periodic_cache': {
        'description': (
            'Использовать непериодические кэш базы коэффициентов непрерывки'
        ),
        'enabled': False,
    },
}

DEFAULT_REQUEST = {
    'offer': '2018-08-01T12:59:23.231000+00:00',
    'place_info': {
        'place_id': 1,
        'region_id': 2,
        'brand_id': 3,
        'position': [38, 57],
        'type': 'native',
        'business_type': 'shop',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'zone_info': {'zone_type': 'taxi'},
}

EATS_ORDERS_STATS_HANDLER = '/eats-orders-stats/server/api/v1/order/stats'

EXPECTED_RESPONSE_GROUP_A = {
    'round_up': False,
    'points': [
        {'order_price': 100, 'delivery_cost': 79},
        {'order_price': 2999, 'delivery_cost': 0},
    ],
    'middle_point': 808,
    'min_price': 0,
}

EXPECTED_RESPONSE_GROUP_DEFAULT = {'middle_point': 813, 'key': 'value'}


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 2,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 3,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'shop',
            'type': 'native',
        },
        {
            'id': 2,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 2,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 300,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'shop',
            'type': 'native',
        },
        {
            'id': 3,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 300,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 300,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'shop',
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@pytest.mark.yt(
    static_table_data=[
        'yt_countries.yaml',
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='db_tariffs.json')
async def test_continuous_commission_resource(taxi_eda_delivery_price):
    # check value in place
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()
    assert response['calculation_result']['result']['extra'][
        'continuous_commission'
    ] == {'middle_point': 700, 'key': 'value'}

    # check default value in region
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['place_info']['place_id'] = 2
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 200
    response = response.json()
    assert response['calculation_result']['result']['extra'][
        'continuous_commission'
    ] == {'middle_point': 500, 'key': 'value for region'}

    # check default value in whole eda
    request = copy.deepcopy(DEFAULT_REQUEST)
    request['place_info']['place_id'] = 3
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 200
    response = response.json()
    assert response['calculation_result']['result']['extra'][
        'continuous_commission'
    ] == {'middle_point': 400, 'key': 'value for everywhere'}


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 3,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 4,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'shop',
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_3')
@pytest.mark.yt(
    static_table_data=[
        'yt_countries.yaml',
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='db_tariffs.json')
async def test_continuous_commission_resource_with_concrete_config(
        taxi_eda_delivery_price,
):
    # check value in place with concrete config 3.0
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()

    assert (
        response['calculation_result']['calculation_name']
        == 'delivery_price_pipeline_3'
    )

    assert response['calculation_result']['result']['extra'][
        'continuous_commission'
    ] == {'middle_point': 600, 'key': 'value for by'}


@pytest.mark.parametrize(
    ('expected_response', 'expected_value'),
    [
        pytest.param(
            EXPECTED_RESPONSE_GROUP_A,
            808,
            marks=(
                pytest.mark.experiments3(filename='calc_settings_groups.json')
            ),
        ),
        pytest.param(
            EXPECTED_RESPONSE_GROUP_DEFAULT,
            813,
            marks=(
                pytest.mark.experiments3(
                    filename='calc_settings_groups_none.json',
                )
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'expected_cache_data_source',
    [
        pytest.param(
            'non-periodic',
            marks=pytest.mark.config(EATS_SURGE_FEATURE_FLAGS=USE_NP_CACHE),
        ),
        pytest.param(
            'periodic',
            marks=pytest.mark.config(
                EATS_SURGE_FEATURE_FLAGS=DONT_USE_NP_CACHE,
            ),
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 1,
            'revision_id': 1,
            'updated_at': '2022-02-26T00:00:00.000000Z',
            'location': {'geo_point': [38.525496, 57.755680]},
            'region': {
                'id': 3,
                'geobase_ids': [1, 2, 3, 4, 5],
                'time_zone': 'UTC+3',
            },
            'brand': {
                'id': 14,
                'slug': 'universe-cafe',
                'name': 'Universe Cafe',
                'picture_scale_type': 'aspect_fit',
            },
            'business': 'shop',
            'type': 'native',
        },
    ],
)
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_4')
@pytest.mark.yt(
    static_table_data=[
        'yt_countries.yaml',
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='db_tariffs.json')
async def test_continuous_commission_resource_with_group(
        taxi_eda_delivery_price,
        expected_value,
        expected_response,
        testpoint,
        expected_cache_data_source,
):
    testpoint_values = dict()
    expected_tespoint_result = {
        'cache_data_source': expected_cache_data_source,
        'commission_data': expected_response,
    }
    await taxi_eda_delivery_price.run_distlock_task('commission-update')

    @testpoint('non-periodic-cache-data')
    def _testpoint_non_periodic_cache_from_resource(testpoint_data):
        testpoint_values.update(testpoint_data)

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    await _testpoint_non_periodic_cache_from_resource.wait_call()

    assert response.status_code == 200
    response = response.json()
    assert (
        response['calculation_result']['calculation_name']
        == 'delivery_price_pipeline_4'
    )
    assert (
        response['calculation_result']['result']['extra'][
            'continuous_commission'
        ]['middle_point']
        == expected_value
    )
    assert (
        response['calculation_result']['result']['extra'][
            'continuous_commission'
        ]
        == expected_response
    )
    assert testpoint_values == expected_tespoint_result
