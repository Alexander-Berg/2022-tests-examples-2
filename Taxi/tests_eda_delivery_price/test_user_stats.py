# pylint: disable=redefined-outer-name,unused-variable

import json

import pytest

from . import conftest

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
    'zone_info': {'zone_type': 'taxi'},
}


@pytest.fixture()
def mock_admin_pipeline_2(admin_pipeline, request, load_json):
    admin_pipeline.mock_single_pipeline(
        request,
        load_json,
        admin_pipeline.Config(
            prefix='delivery_price_pipeline_2',
            consumers=['eda-delivery-price-surge'],
        ),
    )


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
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
@pytest.mark.config(
    EDA_DELIVERY_PRICE_PROMO={
        'bad_retail_brands': [228],
        'bad_native_brands': [228, 322],
        'use_stats_client': True,
        'use_eater_client': True,
    },
)
async def test_calc_pricing_with_surge_with_stats(
        taxi_eda_delivery_price, mockserver, load_json, mock_admin_pipeline_2,
):
    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def stats(_):
        return {
            'data': [
                {
                    'identity': {'type': 'eater_id', 'value': '176999844'},
                    'counters': [
                        {
                            'first_order_at': '2021-05-27T15:32:00+0000',
                            'last_order_at': '2021-05-31T15:32:00+0000',
                            'properties': [
                                {'name': 'brand_id', 'value': '3'},
                                {
                                    'name': 'business_type',
                                    'value': 'restaurant',
                                },
                                {'name': 'delivery_type', 'value': 'native'},
                                {'name': 'place_id', 'value': '1'},
                            ],
                            'value': 3,
                        },
                        {
                            'first_order_at': '2021-05-27T15:32:00+0000',
                            'last_order_at': '2021-05-31T15:32:00+0000',
                            'properties': [
                                {'name': 'brand_id', 'value': '8'},
                                {
                                    'name': 'business_type',
                                    'value': 'restaurant',
                                },
                                {
                                    'name': 'delivery_type',
                                    'value': 'marketplace',
                                },
                                {'name': 'place_id', 'value': '5'},
                            ],
                            'value': 2,
                        },
                        {
                            'first_order_at': '2021-05-27T15:32:00+0000',
                            'last_order_at': '2021-05-31T15:32:00+0000',
                            'properties': [
                                {'name': 'brand_id', 'value': '100'},
                                {'name': 'business_type', 'value': 'retail'},
                                {'name': 'delivery_type', 'value': 'native'},
                                {'name': 'place_id', 'value': '108'},
                            ],
                            'value': 10,
                        },
                    ],
                },
            ],
        }

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    response = response.json()
    expected_response = load_json('expected_response.json')
    assert response == expected_response


@pytest.mark.parametrize(
    'consumer_name, exp_name',
    [
        pytest.param(
            'eda-delivery-price/is-new-user', 'eats_new_user_promotion',
        ),
        pytest.param(
            'eda-delivery-price/calc-delivery-price',
            'calc_if_delivery_is_free',
        ),
    ],
)
@pytest.mark.parametrize(
    'cur_stats, expected_stats_error',
    [
        pytest.param('500', True),
        pytest.param('200', True),
        pytest.param('stats_empty.json', False),
        pytest.param('stats_simple.json', False),
        pytest.param('stats_huge.json', False),
    ],
)
@pytest.mark.yt(
    static_table_data=[
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='db_tariffs.json')
@pytest.mark.config(
    EDA_DELIVERY_PRICE_PROMO={
        'bad_retail_brands': [228],
        'bad_native_brands': [228, 322],
        'use_stats_client': True,
        'use_eater_client': True,
    },
)
@pytest.mark.experiments3(filename='calc_settings.json')
async def test_stats_error(
        taxi_eda_delivery_price,
        mockserver,
        yt_apply,
        load_json,
        mock_admin_pipeline_2,
        cur_stats,
        experiments3,
        expected_stats_error,
        consumer_name,
        exp_name,
):
    if cur_stats not in ('500', '200'):
        cur_stats = load_json(cur_stats)

    experiments3.add_experiment(
        name=exp_name,
        consumers=[consumer_name],
        default_value={
            'free_surge': True,
            'eda_free_delivery': True,
            'retail_free_delivery': True,
            'show_eda_free_delivery': True,
        },
        clauses=[
            {
                'title': 'Обработка ошибок',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {'arg_name': 'stats_error'},
                                'type': 'bool',
                            },
                            {
                                'init': {'arg_name': 'personal_phone_id'},
                                'type': 'is_null',
                            },
                        ],
                    },
                    'type': 'any_of',
                },
                'value': {
                    'free_surge': False,
                    'eda_free_delivery': False,
                    'retail_free_delivery': False,
                    'show_eda_free_delivery': False,
                },
            },
        ],
    )

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(request):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(request):
        return {'tags': ['yandex', 'manager']}

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def response_handler(request):
        if cur_stats in ('200', '500'):
            return mockserver.make_response(status=int(cur_stats))
        return cur_stats

    exp3_recorder = experiments3.record_match_tries(exp_name)
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    current_stats_error = match_tries[0].kwargs['stats_error']
    # для статистик возвращающих 500 или 200 без data, stats_error == True
    assert current_stats_error == expected_stats_error
