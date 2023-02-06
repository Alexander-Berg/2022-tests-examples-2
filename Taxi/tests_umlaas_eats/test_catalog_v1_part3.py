import pytest
# pylint: disable=import-error
from yabs.proto import user_profile_pb2  # noqa: E0401, F401

from tests_umlaas_eats import experiments


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
        'user_history_brand_cnt': 100000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.personal_block_with_mcd_subst(substitute_mcd=True)
@experiments.orders_history()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_substitute_macd_with_bk_and_kfc(
        catalog_v1, load_json, mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response_with_McD.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')

    assert web_response.status == 200
    data = web_response.json()

    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        54689,
        484751,
        3265,
        3621,
        36575,
        24968,
        11271,
        10479,
        24938,
        76511,
    ]
    assert set(data['exp_list']) == {'catalog_test', 'linear'}
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
        'user_offline_visit_cnt': 10000,
        'is_maps_and_taxi_click_brand': 100000,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_maps_and_taxi(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert set(data['exp_list']) == {'eta_test', 'catalog_test', 'linear'}
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }
    assert [place['id'] for place in data['result']] == [
        24968,
        10479,
        76511,
        24938,
        3621,
        3265,
        484751,
        54689,
        36575,
        11271,
    ]


@experiments.helper(
    name='eats_catalog_linear_model_params',
    value={
        'tag': 'linear',
        'enabled': True,
        'eta_minutes_min': -1,
        'average_user_rating': 0,
        'cancel_rate': 0,
        'shown_rating': 0,
        'surge_price': 0,
        'dishes_with_picture': 0,
        'is_new': 0,
        'is_yandex_taxi_courier_type': 0,
        'is_marketplace': 0,
        'user_offline_visit_cnt': 0,
        'is_user_offline_visit': 0,
        'user_history_brand_cnt': 100,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history(feedback_threshold=2)
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_hide_low_rated_place(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('orderhistory_get_orders_with_low_rate.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')

    assert web_response.status == 200
    data = web_response.json()

    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == [
        76511,
        3621,
        54689,
        36575,
        11271,
        484751,
        24968,
        24938,
        3265,
        10479,
    ]
    assert set(data['exp_list']) == {'linear'}
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@experiments.orders_history(orders_num_limit=None)
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
@pytest.mark.parametrize('cache_size', [0, 3, 50])
async def test_eats_eta_integration(
        taxi_umlaas_eats,
        catalog_v1,
        load_json,
        mockserver,
        experiments3,
        cache_size,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        assert request.json['days'] == 60
        assert 'orders' not in request.json
        return load_json('ordershistory_get_orders_response.json')

    @mockserver.json_handler('/eats-eta/api/v1/customer/places/save-eta')
    def eats_eta_mock(request):
        assert len(request.json['estimations']) == min(
            cache_size, 10,
        )  # 10 - amount of places in the /v1/catalog response
        return mockserver.make_response('OK')

    experiments3.add_experiment(
        name='umlaas_eats_estimation_cache_settings',
        match={'enabled': True, 'predicate': {'init': {}, 'type': 'true'}},
        clauses=[
            {
                'value': {'count': cache_size},
                'predicate': {
                    'init': {
                        'arg_name': 'eats_user_id',
                        'arg_type': 'string',
                        'value': '1184610',
                    },
                    'type': 'eq',
                },
            },
        ],
        consumers=['umlaas-eats/v1/catalog'],
    )
    await taxi_umlaas_eats.invalidate_caches()

    request = load_json('request.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    assert eats_eta_mock.times_called == 1


@experiments.orders_history(orders_num_limit=None)
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
@pytest.mark.experiments3(
    name='umlaas_eats_estimation_cache_settings',
    match={'enabled': True, 'predicate': {'init': {}, 'type': 'true'}},
    clauses=[
        {'value': {'count': 5}, 'predicate': {'init': {}, 'type': 'true'}},
    ],
    consumers=['umlaas-eats/v1/catalog'],
)
async def test_eats_eta_integration_fails(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        assert request.json['days'] == 60
        assert 'orders' not in request.json
        return load_json('ordershistory_get_orders_response.json')

    @mockserver.json_handler('/eats-eta/api/v1/customer/places/save-eta')
    def eats_eta_mock(_):
        raise mockserver.TimeoutError()

    request = load_json('request.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    assert eats_eta_mock.times_called == 1
