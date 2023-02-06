# pylint: disable=redefined-outer-name,unused-variable,too-many-lines

import copy
import json

import pytest

from . import conftest
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


DEFAULT_REQUEST_NO_BUSINESS_TYPE = {
    'offer': '2018-08-01T12:59:23.231000+00:00',
    'place_info': {
        'place_id': 1,
        'region_id': 2,
        'brand_id': 3,
        'position': [38, 57],
        'type': 'native',
    },
    'user_info': {
        'position': [38.5, 57.5],
        'device_id': 'some_id',
        'user_id': 'user_id1',
        'personal_phone_id': '123',
    },
    'zone_info': {'zone_type': 'pedestrian'},
}

DEFAULT_REQUEST_REDIS = {
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

HEADERS = {'X-Platform': 'testplatform'}

REDIS_KEY = (
    '1533128363231000000#\nuser_id1;123;'
    '(38.500000,57.500000(;#\n1#\npedestrian#\ntestplatform#\n'
)

EATS_ORDERS_STATS_HANDLER = '/eats-orders-stats/server/api/v1/order/stats'


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
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
@experiments.cart_service_fee('10.15')
async def test_calc_pricing_with_surge(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = load_json('expected_response.json')

    expected_response['service_fee'] = '10.15'

    assert response == expected_response


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.parametrize('empty_surge', [[{'placeId': 1}], []])
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
async def test_calc_pricing_empty_native_surge(
        taxi_eda_delivery_price, mockserver, load_json, empty_surge,
):
    # Проверяем если optional поле NativeInfo не придет
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return empty_surge

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = load_json('expected_response.json')

    assert (
        response['calculation_result']['result']['fees']
        == expected_response['calculation_result']['result']['fees']
    )
    assert response['surge_result']['nativeInfo'] == {
        'deliveryFee': 0.0,
        'loadLevel': 0,
        'surgeLevel': 0,
    }
    assert response['surge_result']['placeId'] == 1


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
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
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_new_user_promotion',
    consumers=['eda-delivery-price/is-new-user'],
    clauses=[],
    default_value={'free_surge': True, 'retail_free_delivery': False},
)
@pytest.mark.config(
    EDA_DELIVERY_PRICE_PROMO={
        'bad_retail_brands': [228],
        'bad_native_brands': [228, 322],
        'use_stats_client': False,
        'use_eater_client': True,
        'retail_brands': [3],
        'retail_separate_promotions': True,
    },
)
async def test_calc_pricing_with_surge_retail_not_zero(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = load_json('expected_response.json')
    expected_response['meta']['is_new_user'] = False
    expected_response['meta']['free_surge'] = False

    assert response == expected_response


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
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
@pytest.mark.config(
    EDA_DELIVERY_PRICE_PROMO={
        'bad_retail_brands': [],
        'bad_native_brands': [],
        'use_stats_client': False,
        'use_eater_client': True,
        'retail_brands': [],
        'retail_separate_promotions': True,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_new_user_promotion',
    consumers=['eda-delivery-price/is-new-user'],
    clauses=[
        {
            'value': {'free_surge': True, 'retail_free_delivery': True},
            'enabled': True,
            'predicate': {
                'init': {
                    'value': 'taxi',
                    'arg_name': 'zone_type',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'extension_method': 'replace',
        },
    ],
    default_value={'free_surge': False, 'retail_free_delivery': False},
)
@pytest.mark.parametrize('zone_type', ['taxi', 'pedestrian', 'vehicle'])
async def test_calc_pricing_zone_type_kwarg_pass_with_surge_retail_zero(
        taxi_eda_delivery_price, mockserver, load_json, zone_type,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    request = DEFAULT_REQUEST
    request['zone_info']['zone_type'] = zone_type
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = load_json('expected_response.json')
    if zone_type == 'taxi':
        expected_response = load_json('expected_response_2.json')
        expected_response['calculation_result']['result']['fees'][0][
            'order_price'
        ] = 0.0
        expected_response['meta']['is_new_user'] = False
        expected_response['meta']['is_retail_zero'] = True
        expected_response['meta']['free_surge'] = True

    assert response == expected_response


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
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
@pytest.mark.now('2021-05-05T16:30:00.00Z')
@pytest.mark.parametrize(
    'due, surge_zero',
    [
        pytest.param(
            '2021-05-05T18:30:00.00Z',
            True,
            marks=experiments.surge_planned(90),
            id='preorder',
        ),
        pytest.param(
            '2021-05-05T17:00:00.00Z',
            False,
            marks=experiments.surge_planned(90),
            id='in_asap_interval',
        ),
        pytest.param(
            '2021-05-05T16:30:00.00Z',
            False,
            marks=experiments.surge_planned(0),
            id='zero_interval_offer_equal_due',
        ),
    ],
)
async def test_calc_pricing_with_surge_planned(
        taxi_eda_delivery_price, mockserver, load_json, due, surge_zero,
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
    request['offer'] = '2021-05-05T16:30:00.00Z'
    request['due'] = due
    response = await taxi_eda_delivery_price.post(
        '/v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 200

    response = response.json()

    if surge_zero:
        assert search_handler_eda.times_called == 0
        assert response['surge_result']['nativeInfo'] == {
            'deliveryFee': 0,
            'loadLevel': 0,
            'surgeLevel': 0,
        }
        assert response['surge_result']['placeId'] == 1
    else:
        assert search_handler_eda.times_called == 1
        assert response['surge_result']['nativeInfo'] == {
            'deliveryFee': 199,
            'loadLevel': 91,
            'surgeLevel': 2,
        }
        assert response['surge_result']['placeId'] == 1


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.parametrize(
    'add_surge, result_file',
    [(True, 'expected_response_add.json'), (False, 'expected_response.json')],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(
    prefix='delivery_price_pipeline_add_surge',
)
@pytest.mark.yt(static_table_data=['yt_settings_data.yaml'])
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
async def test_calc_pricing_with_adding_surge(
        taxi_eda_delivery_price, mockserver, load_json, add_surge, result_file,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    request = DEFAULT_REQUEST.copy()
    request['add_surge_inside_pricing'] = add_surge

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = load_json(result_file)

    assert response == expected_response


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
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
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_new_user_promotion',
    consumers=['eda-delivery-price/is-new-user'],
    clauses=[],
    default_value={'free_surge': True, 'retail_free_delivery': False},
)
async def test_calc_pricing_with_surge_experiment(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200

    response = response.json()

    expected_response = load_json('expected_response_2.json')

    assert response == expected_response


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
            'business': 'store',
            'type': 'marketplace',
        },
    ],
)
async def test_get_surge_marketplace_lavka(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(_):
        return {'tags': ['yandex', 'manager']}

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['place_info']['type'] = 'marketplace'

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 200

    response = response.json()

    expected = {
        'calculation_result': {
            'calculation_name': '',
            'result': {'fees': [], 'is_fallback': False, 'extra': {}},
        },
        'experiment_results': [],
        'experiment_errors': [],
        'surge_extra': {},
        'surge_result': {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 2,
                'loadLevel': 91,
                'deliveryFee': 199.0,
            },
            'marketplaceInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'additionalTimePercents': 0,
            },
            'lavkaInfo': {'surgeLevel': 0, 'loadLevel': 0, 'minimumOrder': 0},
            'interval': {
                'min': '2021-01-14T11:57:07+00:00',
                'max': '2021-01-14T12:00:17+00:00',
            },
            'calculatorName': 'calc_surge_eats_2100m',
        },
        'meta': {},
        'service_fee': '0',
    }

    assert response == expected

    request = copy.deepcopy(DEFAULT_REQUEST)
    request['place_info']['type'] = 'lavka'

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 200

    response = response.json()

    assert response == expected


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@experiments.calc_if_delivery_is_free()
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@experiments.thresholds_templates(
    message_tmpl='Цена ниже за каждые 50 {currency_sign} в заказе',
    low_threshold_tmpl='Заказ от 0 {currency_sign}',
    high_threshold_tmpl='Заказ от {last_order_price} {currency_sign}',
)
@pytest.mark.parametrize(
    'use_continuous_fees',
    (
        pytest.param(
            False,
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='non_continuous_pipeline',
            ),
            id='no thresholds',
        ),
        pytest.param(
            True,
            marks=pytest.mark.set_simple_pipeline_file(
                prefix='continuous_pipeline',
            ),
            id='thresholds',
        ),
    ),
)
async def test_thresholds_info(
        taxi_eda_delivery_price, mockserver, load_json, use_continuous_fees,
):
    """
    Проверяем, что если пользователь попал
    в эксп с непрерывной ценой, то будет сформировано сообщение
    с трешхолдами
    """

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    request_body = copy.deepcopy(DEFAULT_REQUEST)
    request_body['place_info'].update({'currency': {'sign': '$'}})

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', json=request_body,
    )
    assert response.status_code == 200

    data = response.json()
    fees = data['calculation_result']['result']['fees']
    if use_continuous_fees:
        assert data['meta']['continuous_fees']
        thresholds = data['thresholds_info']['thresholds']
        assert thresholds == [
            {'name': 'Цена ниже за каждые 50 $ в заказе', 'value': ' '},
            {'name': 'Заказ от 0 $', 'value': '500 $'},
            {'name': 'Заказ от 1100 $', 'value': '0 $'},
        ]
        thresholds_fees = data['thresholds_info']['thresholds_fees']
        assert thresholds_fees == [
            {'delivery_cost': '500', 'order_price': '100'},
            {'delivery_cost': '0', 'order_price': '1100'},
        ]
        assert fees == [
            {'delivery_cost': 500, 'order_price': 0},
            {'delivery_cost': 0, 'order_price': 1100},
        ]
    else:
        assert 'continuous_fees' not in data['meta']
        assert 'thresholds_info' not in data
        assert fees == [
            {'delivery_cost': 300, 'order_price': 0},
            {'delivery_cost': 100, 'order_price': 500},
            {'delivery_cost': 0, 'order_price': 1000},
        ]


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@experiments.calc_if_delivery_is_free()
@experiments.calc_delivery_price('delivery_price_pipeline_2')
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='continuous_surge')
async def test_continuous_surge_range(
        taxi_eda_delivery_price, mockserver, load_json, surge_resolver,
):
    """
    Проверяем, что при непрерывной цене доставки в
    ответе ручке есть диапазон минимальной и максимальной цены
    с учетом суржа
    """

    native_info = {'deliveryFee': 10, 'loadLevel': 10, 'surgeLevel': 10}
    surge_resolver.native_info = native_info

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    request_body = copy.deepcopy(DEFAULT_REQUEST)
    request_body['place_info'].update({'currency': {'sign': '$'}})

    response = await taxi_eda_delivery_price.post(
        '/v1/calc-delivery-price-surge', json=request_body,
    )
    assert response.status_code == 200

    data = response.json()
    fees = data['calculation_result']['result']['fees']

    assert 'thresholds_info' not in data
    assert fees == [
        {'delivery_cost': 600, 'order_price': 0},  # 500 fee + 100 surge
        {'delivery_cost': 20, 'order_price': 1100},
    ]

    assert 'final_cost' not in data['surge_extra']

    continuous_surge_range = data['surge_extra']['continuous_surge_range']
    assert continuous_surge_range['min'] == '20'
    assert continuous_surge_range['max'] == '600'


@pytest.mark.yt(
    static_table_data=[
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@pytest.mark.parametrize(
    'redis_enabled,taxi_pricing_times_called',
    (
        pytest.param(True, 0, id='redis_on'),
        pytest.param(False, 1, id='redis_off'),
    ),
)
async def test_calc_pricing_redis_check(
        taxi_eda_delivery_price,
        mockserver,
        load_json,
        experiments3,
        redis_enabled,
        taxi_pricing_times_called,
):
    places_count = len(conftest.EATS_CATALOG_STORAGE_CACHE_DATA)

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_redis',
        consumers=['eda-delivery-price/calc-delivery-price'],
        clauses=[],
        default_value={'enabled': redis_enabled},
    )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()
    expected_response = load_json('expected_response.json')
    assert response == expected_response
    assert _prepare_handler.times_called == places_count

    # берем значение из Redis
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()
    assert response == expected_response
    assert (
        _prepare_handler.times_called
        == places_count + taxi_pricing_times_called
    )


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DATA,
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(
    prefix='delivery_price_pipeline_weight_thresholds',
)
async def test_calc_pricing_weights_thresholds_check(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()
    assert response['calculation_result']['result']['weight_fees'] == [
        {'heavy_weight_cost': 0, 'weight_threshold': 8000},
        {'heavy_weight_cost': 40, 'weight_threshold': 16000},
    ]


@pytest.mark.yt(
    static_table_data=[
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@pytest.mark.parametrize(
    'redis_enabled,expected_delivery_cost,headers',
    (
        pytest.param(True, 113.1, HEADERS, id='redis_on'),
        pytest.param(False, 500.1, '', id='redis_off'),
    ),
)
async def test_calc_pricing_redis_with_platform(
        taxi_eda_delivery_price,
        mockserver,
        load_json,
        redis_store,
        headers,
        experiments3,
        redis_enabled,
        expected_delivery_cost,
):
    redis_store.set(
        REDIS_KEY, json.dumps(load_json('redis_response_by_platform.json')),
    )

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eda_delivery_price_redis',
        consumers=['eda-delivery-price/calc-delivery-price'],
        clauses=[],
        default_value={'enabled': redis_enabled},
    )

    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(request):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(request):
        return load_json('pricing_response.json')

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge',
        data=json.dumps(DEFAULT_REQUEST_REDIS),
        headers=headers,
    )

    assert response.status_code == 200
    response = response.json()

    assert (
        response['calculation_result']['result']['fees'][0]['delivery_cost']
        == expected_delivery_cost
    )


@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
@pytest.mark.yt(
    static_table_data=[
        'yt_regions.yaml',
        'yt_continuous_commission.yaml',
        'yt_settings_data.yaml',
    ],
)
@pytest.mark.geoareas(filename='db_geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='db_tariffs.json')
async def test_calc_pricing_with_wrong_business_type(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(request):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(request):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(request):
        return {'tags': ['yandex', 'manager']}

    request = copy.deepcopy(DEFAULT_REQUEST)
    # вводим некорректное имя для business_type
    request['place_info']['business_type'] = 'restaraunt'
    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(request),
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
async def test_calc_pricing_with_no_business_type(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(request):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(request):
        return load_json('pricing_response.json')

    @mockserver.json_handler('/eats-tags/v2/match_single')
    def _tags_handler(request):
        return {'tags': ['yandex', 'manager']}

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge',
        data=json.dumps(DEFAULT_REQUEST_NO_BUSINESS_TYPE),
    )
    assert response.status_code == 400


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
            'business': 'restaurant',
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
async def test_place_data_from_request(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()
    assert response == load_json('expected_response.json')


@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 404,
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
            'business': 'restaurant',
            'type': 'native',
        },
    ],
)
@pytest.mark.experiments3(filename='calc_settings.json')
@pytest.mark.set_simple_pipeline_file(prefix='delivery_price_pipeline_2')
async def test_fallback_place_data_from_request(
        taxi_eda_delivery_price, mockserver, load_json,
):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def search_handler(_):
        return load_json('surge_response.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _prepare_handler(_):
        return load_json('pricing_response.json')

    response = await taxi_eda_delivery_price.post(
        'v1/calc-delivery-price-surge', data=json.dumps(DEFAULT_REQUEST),
    )
    assert response.status_code == 200
    response = response.json()
    assert response == load_json('expected_response.json')
