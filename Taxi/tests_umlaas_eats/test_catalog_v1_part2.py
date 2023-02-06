# pylint: disable=C0302
from google.protobuf import json_format
import pytest
# pylint: disable=import-error
from yabs.proto import user_profile_pb2  # noqa: E0401, F401

from tests_umlaas_eats import experiments

EXP3_RETAIL_LINEAR_PARAMS_EXP = experiments.helper(
    name='eats_catalog_linear_model_params_retail',
    value={
        'tag': 'retail_ranking',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)


@experiments.helper(
    name='eats_eta_ml',
    value={'tag': 'eta_test', 'enabled': True, 'shift_delivery_time': 15},
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.grocery_eta()
@experiments.personal_block()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_eta_increase(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    times = {
        place['id']: place['predicted_times']['min']
        for place in data['result']
    }
    assert times == {
        76511: 5,
        56622: 50,
        3621: 30,
        36575: 50,
        11271: 50,
        24968: 50,
        24938: 50,
        10465: 55,
        3265: 60,
    }


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 10000,
        'is_user_offline_visit': 1,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.grocery_eta()
@experiments.personal_block()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_offline(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }
    assert [place['id'] for place in data['result']] == [
        76511,
        24938,
        3621,
        3265,
        56622,
        10465,
        36575,
        24968,
        11271,
    ]


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 1,
        'is_user_offline_visit': 1,
        'user_history_brand_cnt': -10000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.grocery_eta()
@experiments.personal_block()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_history_brand(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')

    assert web_response.status == 200
    data = web_response.json()

    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        3621,
        10465,
        36575,
        24968,
        11271,
        76511,
        56622,
        24938,
        3265,
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 1,
        'is_user_offline_visit': 1,
        'user_history_brand_cnt': -10000000,
        'place_has_plus': 100000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_yandex_plus_places(
        catalog_v1, load_json, mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_plus.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        10465,
        24938,
        3621,
        36575,
        24968,
        11271,
        76511,
        56622,
        3265,
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.helper(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'region_offset': -10,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.grocery_eta()
@experiments.personal_block()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage-eta.json')
async def test_catalog_eta_with_custom_offset(
        catalog_v1, load_json, mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert (
        data['result'][0]['predicted_times']['max']
        - data['result'][0]['predicted_times']['min']
        == 10
    )


@experiments.personal_block(should_limit=True)
@experiments.ENABLE_ETA_CALCULATION
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_default(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    web_response = await catalog_v1(load_json('request.json'))
    assert web_response.status == 200


@experiments.helper(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.helper(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'region_offset': 20,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.grocery_eta()
@experiments.personal_block()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-retail-eta.json',
)
async def test_catalog_retail_eta(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 919191
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert (
        data['result'][0]['predicted_times']['max']
        - data['result'][0]['predicted_times']['min']
        == 20
    )


@experiments.helper(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.helper(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'custom_brands': [],
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'region_offset': 20,
        'queue_params': {'threshold': 1, 'linear_coef': 10, 'shift': 20},
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.grocery_eta()
@experiments.personal_block()
@pytest.mark.config(
    UMLAAS_EATS_ORDERSHISTORY_ENABLED=True,
    UMLAAS_EATS_RETAILQUEUELENGTH_ENABLED=True,
)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-retail-eta.json',
)
async def test_queue_orders_params(
        catalog_v1,
        load_json,
        mockserver,
        retail_queue_length,
        retail_queue_length_filter,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 919191
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()

    assert (
        data['result'][0]['predicted_times']['max'] == 80
    )  # 50 base + (10 * 1 + 20) for orders queue
    assert (
        data['result'][0]['predicted_times']['min'] == 60
    )  # 30 base + (10 * 1 + 20) for orders queue


@experiments.orders_history()
@experiments.personal_block()
@EXP3_RETAIL_LINEAR_PARAMS_EXP
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-retail-eta.json',
)
async def test_catalog_retail_block(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 919191
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'] == [
        {
            'id': 919191,
            'relevance': 1.0,
            'type': 'ranking',
            'predicted_times': {'min': 50, 'max': 30},
            'blocks': [{'block_id': 'retail', 'relevance': 0.0}],
        },
    ]
    assert set(data['available_blocks']) == {
        'retail',
        'promo',
        'history_order',
    }


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
        'ranking_weight': 1000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_ranking_weight(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'][0]['id'] == 76511


@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-one-brand.json',
)
@pytest.mark.parametrize(
    'expected_order',
    [
        pytest.param([5, 3, 2], id='default'),
        pytest.param(
            [6, 3, 2],
            marks=experiments.deduplication('show_this'),
            id='with tag',
        ),
    ],
)
async def test_deduplication(
        catalog_v1, load_json, mockserver, expected_order,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    web_response = await catalog_v1(load_json('request_one_brand.json'))

    assert web_response.status == 200

    data = web_response.json()
    order = [x['id'] for x in data['result']]

    assert order == expected_order


@experiments.orders_history()
@experiments.ENABLE_EATS_ETA
@experiments.retail_eats_eta()
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-one-brand.json',
)
@pytest.mark.parametrize(
    'expected_order',
    [
        pytest.param(
            [4, 6, 2],
            marks=experiments.DEDUPLICATION_DELIVERY_TIME_PRIORITY,
            id='experiment enabled',
        ),
        # 4>3 because of eta
        # 6>5 because of delivery time
        # 2>1 because of id
        pytest.param([5, 4, 2], id='experiment disabled'),
        # 5>6 because of eta
        # 4>3 because of eta
        # 2>1 because of id
    ],
)
async def test_deduplication_delivery_time(
        catalog_v1, load_json, mockserver, expected_order,
):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def mock_eats_eta(request):
        assert request.json == {
            'sources': [
                [37.403189, 55.901299],
                [37.403189, 55.901299],
                [37.403189, 55.901299],
                [37.403189, 55.901299],
                [37.403189, 55.901299],
            ],
            'destination': [37.492266, 55.672123],
            'type': 'taxi',
        }
        return {
            'etas': [
                {'time': 200, 'distance': 0},
                {'time': 200, 'distance': 0},
                {'time': 200, 'distance': 0},
                {'time': 200, 'distance': 0},
                {'time': 2, 'distance': 0},
            ],
        }

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    web_response = await catalog_v1(load_json('request_one_brand_auto.json'))

    assert web_response.status == 200

    data = web_response.json()
    order = [x['id'] for x in data['result']]

    assert mock_eats_eta.times_called == 1
    assert order == expected_order


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': 0,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
        'user_opens_cnt': 100000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.ENABLE_BIGB
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_bigb_features(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    @mockserver.json_handler('/bigb/bigb')
    def _bigb(request):
        msg = user_profile_pb2.Profile()
        json_format.ParseDict(
            {
                'items': [
                    {
                        'keyword_id': 569,
                        'pair_values': [
                            {'first': 174, 'second': 1},  # gender
                            {'first': 543, 'second': 3},  # age
                            {'first': 614, 'second': 0},  # income_level
                        ],
                        'update_time': 1613372688,
                    },
                    {
                        'keyword_id': 1112,
                        'trio_values': [
                            {
                                'first': 3179,  # brand_id
                                'second': 15,  # views
                                'third': 2,  # clicks
                            },
                            {
                                'first': 11787,  # brand_id
                                'second': 10,  # views
                                'third': 8,  # clicks
                            },
                            {
                                'first': 8577,  # brand_id
                                'second': 5,  # views
                                'third': 5,  # clicks
                            },
                        ],
                        'update_time': 1613372688,
                    },
                ],
            },
            msg,
        )
        return mockserver.make_response(
            msg.SerializeToString(deterministic=True),
        )

    request = load_json('request.json')
    web_response = await catalog_v1(
        request,
        place_list_context='common',
        headers={'x-yandex-uid': '12341212'},
    )

    assert web_response.status == 200
    data = web_response.json()
    assert [place['id'] for place in data['result']] == [
        24938,
        10465,
        3621,
        56622,
        3265,
        36575,
        24968,
        11271,
        76511,
    ]


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -1000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 1,
        'is_user_offline_visit': 1,
        'user_history_brand_cnt': -1000,
        'retention': 1000000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_retention(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        3265,
        10465,
        24938,
        3621,
        36575,
        24968,
        11271,
        56622,
        76511,
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -1000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 1,
        'is_user_offline_visit': 1,
        'user_history_brand_cnt': -1000,
        'cm2_median': 1000000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_cm2(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        24938,
        10465,
        3621,
        3265,
        36575,
        24968,
        11271,
        56622,
        76511,
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -1000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 1,
        'is_user_offline_visit': 1,
        'total_ctr_is_good': 1000000,
        'retention_is_good': 1000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_thresholds(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        3621,
        3265,
        10465,
        56622,
        36575,
        24968,
        11271,
        24938,
        76511,
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -10,
        'average_user_rating': 100,
        'cancel_rate': 1,
        'shown_rating': 0,
        'surge_price': -100,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -1000,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 1,
        'is_user_offline_visit': 1,
        'income_segment_affinity': 10000000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.ENABLE_BIGB
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_bigb_income_segments(
        catalog_v1, load_json, mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    @mockserver.json_handler('/bigb/bigb')
    def _bigb(request):
        msg = user_profile_pb2.Profile()
        json_format.ParseDict(
            {
                'items': [
                    {
                        'keyword_id': 569,
                        'pair_values': [
                            {'first': 174, 'second': 1},  # gender
                            {'first': 543, 'second': 3},  # age
                            {'first': 614, 'second': 4},  # income_level
                        ],
                        'update_time': 1613372688,
                    },
                ],
            },
            msg,
        )
        return mockserver.make_response(
            msg.SerializeToString(deterministic=True),
        )

    request = load_json('request.json')
    web_response = await catalog_v1(
        request,
        place_list_context='common',
        headers={'x-yandex-uid': '12341212'},
    )
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        24938,
        10465,
        3621,
        3265,
        56622,
        36575,
        24968,
        11271,
        76511,
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'catalog_test',
        'linear',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.orders_history()
@experiments.personal_block()
@EXP3_RETAIL_LINEAR_PARAMS_EXP
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_catalog_offline_visits_block(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request)
    assert web_response.status == 200
    data = web_response.json()
    offline_visits_relevances = dict()
    for place in data['result']:
        for block in place['blocks']:
            if block['block_id'] == 'offline_visits':
                offline_visits_relevances[place['id']] = block['relevance']

    sorted_relevances = sorted(
        offline_visits_relevances.items(), key=lambda x: -x[1],
    )

    assert [place[0] for place in sorted_relevances] == [3621]

    assert set(data['available_blocks']) == {
        'retail',
        'history_order',
        'promo',
        'offline_visits',
    }
