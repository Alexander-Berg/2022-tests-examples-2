import datetime

import pytest

from tests_umlaas_eats import experiments


EXP3_DEFAULT_RANKING_PARAMS = experiments.helper(
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
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)

EXP3_RETAIL_RANKING_PARAMS = experiments.helper(
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

EXP3_RANKING_PARAMS_PLACE_WEIGHT = experiments.helper(
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
        'ranking_weight': 100,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)

ORDERS_HISTORY = experiments.helper(
    name='eats_catalog_orders_history',
    value={'tag': 'orders_history', 'days_num_limit': 60},
    consumers=[experiments.CONSUMER_CATALOG_V1],
)


@experiments.orders_history(orders_num_limit=None)
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_default(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        assert request.json['days'] == 60
        assert 'orders' not in request.json
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert data['result'] == [
        {
            'id': 76511,
            'relevance': 1.0,
            'type': 'ranking',
            'predicted_times': {'min': 5, 'max': 15},
            'blocks': [
                {'block_id': 'promo', 'relevance': 0.8888888888888888},
                {'block_id': 'retail', 'relevance': 8.0},
            ],
        },
        {
            'id': 3621,
            'relevance': 0.8888888888888888,
            'type': 'ranking',
            'predicted_times': {'min': 30, 'max': 30},
            'blocks': [
                {'block_id': 'promo', 'relevance': 0.7777777777777778},
                {'block_id': 'offline_visits', 'relevance': 1.0},
            ],
        },
        {
            'id': 56622,
            'relevance': 0.7777777777777778,
            'type': 'ranking',
            'predicted_times': {'min': 35, 'max': 45},
            'blocks': [
                {'block_id': 'promo', 'relevance': 0.6666666666666666},
                {'block_id': 'history_order', 'relevance': 0.5},
            ],
        },
        {
            'id': 36575,
            'relevance': 0.6666666666666666,
            'type': 'ranking',
            'predicted_times': {'min': 35, 'max': 45},
            'blocks': [{'block_id': 'promo', 'relevance': 0.5555555555555556}],
        },
        {
            'id': 24968,
            'relevance': 0.5555555555555556,
            'type': 'ranking',
            'predicted_times': {'min': 35, 'max': 45},
            'blocks': [{'block_id': 'promo', 'relevance': 0.4444444444444444}],
        },
        {
            'id': 24938,
            'relevance': 0.4444444444444444,
            'type': 'ranking',
            'predicted_times': {'min': 35, 'max': 45},
            'blocks': [{'block_id': 'promo', 'relevance': 0.3333333333333333}],
        },
        {
            'id': 11271,
            'relevance': 0.3333333333333333,
            'type': 'ranking',
            'predicted_times': {'min': 35, 'max': 45},
            'blocks': [{'block_id': 'promo', 'relevance': 0.2222222222222222}],
        },
        {
            'id': 10465,
            'relevance': 0.2222222222222222,
            'type': 'ranking',
            'predicted_times': {'min': 40, 'max': 50},
            'blocks': [{'block_id': 'promo', 'relevance': 0.1111111111111111}],
        },
        {
            'id': 3265,
            'relevance': 0.1111111111111111,
            'type': 'ranking',
            'predicted_times': {'min': 45, 'max': 55},
            'blocks': [
                {'block_id': 'promo', 'relevance': 0.0},
                {'block_id': 'history_order', 'relevance': 1.0},
            ],
        },
    ]
    assert set(data['exp_list']) == {
        'eta_test',
        'eta_retail_ml',
        'catalog_test',
        'grocery_test',
    }
    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


BRAND_WEIGHT_MAPPING = {
    '3179': 0,  # place witn id 3621
    '20369': 100000,  # place witn id 76511
    '1693': 5000000,  # place witn id 24968
    '2777': 10000000,  # place witn id 3265
}


@experiments.orders_history()
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
@pytest.mark.parametrize(
    'sort',
    [
        pytest.param('default'),
        pytest.param('fast_delivery'),
        pytest.param('high_rating'),
        pytest.param('cheap_first'),
        pytest.param('expensive_first'),
        pytest.param('unsupported'),
    ],
)
async def test_sorts(catalog_v1, load_json, mockserver, sort):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    response = await catalog_v1(request, sort=sort)

    if sort == 'unsupported':
        assert response.status == 400
    else:
        assert response.status == 200
        data = response.json()
        assert len(data['result']) == 9


@experiments.orders_history()
@experiments.ENABLE_EATS_ETA
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_using_routing(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert request.json == {
            'destination': [37.492266, 55.672123],
            'sources': [[37.403189, 55.901299], [37.491988, 55.683265]],
            'type': 'taxi',
        }
        return {
            'etas': [
                {'time': 42 * 60, 'distance': 15200},
                {'time': 50.5 * 60, 'distance': 10500},
            ],
        }

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request)
    assert web_response.status == 200
    assert _mock_eats_eta.times_called == 1
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    eta = {place['id']: place['predicted_times'] for place in data['result']}
    assert eta[76511] == {'min': 5, 'max': 15}
    assert eta[24938] == {'min': 75, 'max': 85}
    assert data['available_blocks'] == ['promo', 'retail', 'offline_visits']


@experiments.orders_history()
@experiments.ENABLE_EATS_ETA
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
@pytest.mark.parametrize(
    'expected_size',
    [
        pytest.param(1, marks=(experiments.router_limit(limit=1)), id='limit'),
        pytest.param(
            3, marks=(experiments.router_limit(percent=75)), id='percent',
        ),
        pytest.param(
            2,
            marks=(experiments.router_limit(percent=50, limit=3)),
            id='percent_limit',
        ),
        pytest.param(
            1,
            marks=(experiments.router_limit(percent=50, limit=1)),
            id='limit_percent',
        ),
        pytest.param(4, marks=(experiments.router_limit()), id='none'),
    ],
)
async def test_using_routing_limit(
        catalog_v1, load_json, mockserver, expected_size,
):
    @mockserver.json_handler('/eats-eta/v1/eta')
    def eats_eta(request):
        assert len(request.json['sources']) == expected_size
        return {'etas': []}

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_for_router.json')
    web_response = await catalog_v1(request)
    assert web_response.status == 200
    assert eats_eta.times_called == 1


@experiments.orders_history()
@EXP3_DEFAULT_RANKING_PARAMS
@EXP3_RETAIL_RANKING_PARAMS
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_control(catalog_v1, load_json, mockserver):
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
        56622,
        3265,
        10465,
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
        'retail_ranking',
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
        'surge_price': 0,
        'dishes_with_picture': -100,
        'is_new': 0,
        'is_yandex_taxi_courier_type': -10000,
        'is_marketplace': 0,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.helper(
    name='eats_catalog_linear_model_params_promo',
    value={
        'tag': 'linear_promo',
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
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.orders_history()
@EXP3_RETAIL_RANKING_PARAMS
@experiments.personal_block()
@experiments.ENABLE_ETA_CALCULATION
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_promo_linear_ranker(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']

    promo_places = filter(
        lambda x: x['blocks'] and x['blocks'][0]['block_id'] == 'promo',
        data['result'],
    )
    assert [
        place['id']
        for place in sorted(
            promo_places, key=lambda x: -x['blocks'][0]['relevance'],
        )
    ] == [3621, 56622, 3265, 10465, 36575, 24968, 11271, 76511, 24938]

    assert set(data['available_blocks']) == {
        'promo',
        'history_order',
        'retail',
        'offline_visits',
    }


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            [3621, 56622, 3265, 10465, 36575, 24968, 11271, 24938, 76511],
            marks=[pytest.mark.config(UMLAAS_EATS_BRAND_WEIGHT_MAPPING={})],
        ),
        pytest.param(
            [3265, 24968, 76511, 56622, 10465, 36575, 11271, 3621, 24938],
            marks=[
                pytest.mark.config(
                    UMLAAS_EATS_BRAND_WEIGHT_MAPPING=BRAND_WEIGHT_MAPPING,
                ),
            ],
        ),
    ],
)
@experiments.orders_history()
@EXP3_RANKING_PARAMS_PLACE_WEIGHT
@EXP3_RETAIL_RANKING_PARAMS
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_linear_ranker_with_place_weight_override(
        catalog_v1, load_json, mockserver, expected,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200
    data = web_response.json()
    assert request['request_id'] == data['request_id']
    assert 'provider' in data
    assert [place['id'] for place in data['result']] == expected


@experiments.orders_history()
@EXP3_RANKING_PARAMS_PLACE_WEIGHT
@EXP3_RETAIL_RANKING_PARAMS
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.config(UMLAAS_EATS_BRAND_WEIGHT_MAPPING=BRAND_WEIGHT_MAPPING)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_place_weight_override(
        catalog_v1, testpoint, load_json, mockserver,
):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    overridden_brands = set()

    @testpoint('catalog_v1_place_filled_for_ml_request')
    def _point(place):
        brand_id = str(place['brand_id'])
        if brand_id in BRAND_WEIGHT_MAPPING:
            assert place['ranking_weight'] == BRAND_WEIGHT_MAPPING[brand_id]
            overridden_brands.add(brand_id)

    request = load_json('request.json')
    web_response = await catalog_v1(request, place_list_context='common')
    assert web_response.status == 200

    assert len(overridden_brands) == len(BRAND_WEIGHT_MAPPING)


def exploration():
    return experiments.helper(
        name='eats_exploration_catalog',
        value={'tag': 'exploration_tag', 'enabled': True, 'variance': 0.5},
        consumers=[experiments.CONSUMER_CATALOG_V1],
    )


@experiments.orders_history(orders_num_limit=None)
@experiments.ENABLE_ETA_CALCULATION
@experiments.personal_block()
@experiments.retail_eats_eta()
@experiments.grocery_eta()
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
@exploration()
async def test_exploration(catalog_v1, load_json, mockserver):
    request = load_json('request.json')

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    response = await catalog_v1(request, place_list_context='common')
    data = response.json()
    assert response.status == 200

    # I. проверяем что плейсы отсортированы по убыванию скора
    assert data['result'] == sorted(
        data['result'], key=lambda x: x['relevance'], reverse=True,
    )

    # II. проверяем что повторный запрос, возвращает тот же результат
    reference_result = [
        (place['id'], place['relevance']) for place in data['result']
    ]
    response = await catalog_v1(request, place_list_context='common')
    data = response.json()
    assert all(
        i == (j['id'], j['relevance'])
        for i, j in zip(reference_result, data['result'])
    )

    # III. проверяем что ранжирование поменялось через час
    hour_later = datetime.datetime.fromisoformat(
        request['ranking_at'],
    ) + datetime.timedelta(hours=1)
    request['ranking_at'] = hour_later.isoformat()
    response = await catalog_v1(request, place_list_context='common')
    data = response.json()
    assert any(
        j != (i['id'], i['relevance'])
        for i, j in zip(data['result'], reference_result)
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
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'region_offset': 20,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.helper(
    name='umlaas_eats_custom_eta_setting',
    value={
        'tag': 'custom_eta_setting',
        'custom_brands': [
            {
                'id': 93333,
                'shift': 5,
                'max_delta': 100,
                'min_delta': 100,
                'rounding_params': [{'threshold': 60, 'closest_value': 60}],
                'always_use_last_rule': True,
            },
        ],
        'custom_places': [],
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
async def test_catalog_retail_rounding(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 919191
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'][0]['predicted_times']['max'] == 120
    assert data['result'][0]['predicted_times']['min'] == 60


@experiments.helper(
    name='eats_retail_eta_ml',
    value={
        'tag': 'eta_retail_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'slots_params': {'shift': 7, 'const_shift': 3},
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@pytest.mark.config(
    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['93333']},
)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-retail-eta.json',
)
async def test_catalog_retail_slots(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 919191
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'][0]['predicted_times']['max'] == 60
    assert data['result'][0]['predicted_times']['min'] == 40


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
        'taxi_routing_enabled': True,
        'region_taxi_shifts': [
            {'region_id': 321, 'taxi_shift': 10},
            {'region_id': 123, 'taxi_shift': 20},
        ],
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
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'taxi_routing_enabled': False,  # should be ignored
        # should be ignored
        'region_taxi_shifts': [
            {'region_id': 321, 'taxi_shift': 0},
            {'region_id': 123, 'taxi_shift': 0},
        ],
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-retail-eta.json',
)
async def test_custom_region_shifts_catalog(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    @mockserver.json_handler('/eats-eta/v1/eta')
    def _mock_eats_eta(request):
        assert len(request.json['sources']) == 1
        return {'etas': [{'time': 17 * 60, 'distance': 6600}]}

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 919191
    request['places'][0]['courier_type'] = 'yandex_taxi'
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'][0]['predicted_times']['max'] == 50 + 20
    assert data['result'][0]['predicted_times']['min'] == 30 + 20


@experiments.helper(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'taxi_routing_enabled': False,
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
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'taxi_routing_enabled': False,
        'catalog_model': 'linear',
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@experiments.helper(
    name='umlaas_eats_catalog_linear_model',
    value={
        'enabled': True,
        'model_coefficients': [
            36.3359,  # const
            4.4970,  # delivery
            3.1916,  # delivery ** 2
            -1.1451,  # delivery ** 0.5
            2.6867,  # cooking this round hour of day
            2.9591,  # cooking this day of week
            -2.8298,  # fast food and rating
            -3.6305,  # non fast food and rating
        ],
        'scaler_means': [
            0.0,
            21.1785,
            522.8603,
            4.5004,
            23.9363,
            23.7005,
            2.3352,
            2.2766,
        ],
        'scaler_scales': [
            1.0,
            8.6216,
            431.1709,
            0.9619,
            6.4042,
            6.3776,
            2.2667,
            2.3633,
        ],
        'min_prediction_value': 10,
        'max_prediction_value': 180,
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@pytest.mark.eats_catalog_storage_cache(
    file='eats-catalog-storage-retail-eta.json',
)
async def test_linear_eta_model_catalog(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 321123
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'][0]['predicted_times']['max'] == 55
    assert data['result'][0]['predicted_times']['min'] == 35


@experiments.helper(
    name='eats_eta_ml',
    value={
        'tag': 'eta_ml',
        'slug': 'const',
        'enabled': True,
        'shift_total_time': 0,
        'shift_cooking_time': 0,
        'shift_const_cooking_time': 0,
        'proxy_umlaas_eats': False,
        'taxi_routing_enabled': False,
        'boundary_shifts': {
            'type_catalog': {'min': -5, 'max': 5},
            'type_slug': {'min': -3, 'max': 1},
            'type_default': {'min': -2, 'max': 2},
            'type_checkout': {'min': -1, 'max': 3},
        },
    },
    consumers=[experiments.CONSUMER_CATALOG_V1],
)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_boundaries_shifts(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request = load_json('request_eta.json')
    request['places'][0]['id'] = 24968
    web_response = await catalog_v1(request)

    assert web_response.status == 200
    data = web_response.json()
    assert data['result'][0]['predicted_times']['min'] == 40 - 5
    assert data['result'][0]['predicted_times']['max'] == 60 + 5
