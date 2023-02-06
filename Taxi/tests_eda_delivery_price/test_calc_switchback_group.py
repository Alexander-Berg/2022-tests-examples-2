import json

import pytest

from . import experiments

DEFAULT_REQUEST = {
    'offer': '2018-08-01T12:59:23.231000+00:00',
    'place_info': {
        'place_id': 1,
        'region_id': 2,
        'brand_id': 3,
        'position': [38, 57],
        'type': 'native',
        'business_type': 'restaurant',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'zone_info': {'zone_type': 'pedestrian'},
}

EATS_CATALOG_STORAGE_CACHE_DATA = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2018-08-01T12:59:23.231000+00:00',
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
        'business': 'restaurant',
        'type': 'native',
    },
]

EATS_ORDERS_STATS_HANDLER = '/eats-orders-stats/server/api/v1/order/stats'


@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_DATA)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@pytest.mark.config(
    EDA_DELIVERY_PRICE_MAIN={
        'switchback_exp_interval_minutes': 60,
        'switchback_time_offset_minutes': 0,
    },
)
@pytest.mark.parametrize(
    'offer_time, expected_group',
    [
        pytest.param('2021-05-05T16:00:00.00Z', 0),
        pytest.param('2021-05-05T16:59:59.00Z', 0),
        pytest.param('2021-05-05T17:00:00.00Z', 1),
        pytest.param('2021-05-05T15:59:59.00Z', 1),
    ],
)
async def test_calc_switchback_group_default(
        taxi_eda_delivery_price,
        mockserver,
        load_json,
        experiments3,
        offer_time,
        expected_group,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler_eda(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    request = DEFAULT_REQUEST.copy()
    request['offer'] = offer_time

    exp3_recorder = experiments3.record_match_tries('calc_if_delivery_is_free')
    response = await taxi_eda_delivery_price.post(
        '/v1/calc-delivery-price-surge', data=json.dumps(request),
    )

    assert response.status_code == 200
    assert search_handler_eda.times_called == 1

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    current_switchback_group = match_tries[1].kwargs['switchback_group']
    assert current_switchback_group == expected_group


@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_DATA)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@pytest.mark.config(
    EDA_DELIVERY_PRICE_MAIN={
        'switchback_exp_interval_minutes': 30,
        'switchback_time_offset_minutes': 3,
    },
)
@pytest.mark.parametrize(
    'offer_time, expected_group',
    [
        pytest.param('2021-05-05T16:29:00.00Z', 0),
        pytest.param('2021-05-05T16:29:59.00Z', 0),
        pytest.param('2021-05-05T16:30:00.00Z', 0),
        pytest.param('2021-05-05T16:30:59.00Z', 0),
        pytest.param('2021-05-05T16:32:59.00Z', 0),
        pytest.param('2021-05-05T16:33:00.00Z', 1),
    ],
)
async def test_calc_switchback_group_positive(
        taxi_eda_delivery_price,
        mockserver,
        load_json,
        experiments3,
        offer_time,
        expected_group,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler_eda(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    request = DEFAULT_REQUEST.copy()
    request['offer'] = offer_time

    exp3_recorder = experiments3.record_match_tries('calc_if_delivery_is_free')
    response = await taxi_eda_delivery_price.post(
        '/v1/calc-delivery-price-surge', data=json.dumps(request),
    )

    assert response.status_code == 200
    assert search_handler_eda.times_called == 1

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    current_switchback_group = match_tries[1].kwargs['switchback_group']
    assert current_switchback_group == expected_group


@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_DATA)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@pytest.mark.config(
    EDA_DELIVERY_PRICE_MAIN={
        'switchback_exp_interval_minutes': 30,
        'switchback_time_offset_minutes': -3,
    },
)
@pytest.mark.parametrize(
    'offer_time, expected_group',
    [
        pytest.param('2021-05-05T16:26:59.00Z', 0),
        pytest.param('2021-05-05T16:27:00.00Z', 1),
        pytest.param('2021-05-05T16:27:01.00Z', 1),
        pytest.param('2021-05-05T16:29:59.00Z', 1),
        pytest.param('2021-05-05T16:30:00.00Z', 1),
        pytest.param('2021-05-05T16:30:01.00Z', 1),
    ],
)
async def test_calc_switchback_group_negative(
        taxi_eda_delivery_price,
        mockserver,
        load_json,
        experiments3,
        offer_time,
        expected_group,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler_eda(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    request = DEFAULT_REQUEST.copy()
    request['offer'] = offer_time

    exp3_recorder = experiments3.record_match_tries('calc_if_delivery_is_free')
    response = await taxi_eda_delivery_price.post(
        '/v1/calc-delivery-price-surge', data=json.dumps(request),
    )

    assert response.status_code == 200
    assert search_handler_eda.times_called == 1

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    current_switchback_group = match_tries[1].kwargs['switchback_group']
    assert current_switchback_group == expected_group
