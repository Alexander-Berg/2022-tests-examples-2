import json
from urllib import parse as urlparse

import pytest

# pylint: disable=import-error
from yabs.proto import user_profile_pb2  # noqa: E0401, F401
# pylint: disable=C0302
from google.protobuf import json_format
from tests_umlaas_eats import experiments


URL = '/umlaas-eats/v1/eats-search-ranking'
EXP_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'
CONSUMER = 'umlaas-eats-search-ranking'


def get_query_params(
        service_name='pytest',
        request_id='value_request_id',
        user_id=0,
        device_id='0',
        source='catalog',
):
    params = dict(
        service_name=service_name,
        request_id=request_id,
        user_id=user_id,
        device_id=device_id,
        source=source,
    )
    return params


def exp3_decorator(name, value):
    return pytest.mark.experiments3(
        name=name,
        consumers=[CONSUMER],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


@exp3_decorator(
    name='eats_search_ranking_params',
    value={
        'tag': 'default_sort',
        'linear_params': {
            'average_user_rating': 10,
            'distance_in_km': -0.2,
            'available': 100,
            'is_restaurant': 0.1,
            'is_shop': 0,
            'place_relevance': 10,
            'max_items_relevance': 30,
            'avg_items_relevance': 2,
            'avg_top3_items_relevance': 1,
            'cnt_items': 2,
        },
        'max_items_cnt': 100,
        'min_items_relevance': -100,
        'model_type': 'linear',
    },
)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_default_linear(taxi_umlaas_eats, load_json):
    request_body = load_json('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert web_response.status == 200
    response = json.loads(web_response.text)

    assert len(response['result']) == len(request_body['block'])

    # shop with items
    assert response['result'][0]['place_id'] == 76511

    # not available at last place
    assert response['result'][-1]['place_id'] == 999

    # check if items per place is the same as in request
    items_num = {
        place['place_id']: len(place.get('items', []))
        for place in request_body['block']
    }
    for place in response['result']:
        assert (
            'items' not in place
            or len(place['items']) == items_num[place['place_id']]
        )


@exp3_decorator(
    name='eats_search_ranking_params',
    value={
        'tag': 'default_sort',
        'linear_params': {
            'average_user_rating': 10,
            'distance_in_km': -10,
            'available': 100,
            'is_restaurant': 0.1,
            'is_shop': 0,
            'place_relevance': 10,
            'max_items_relevance': 3,
            'avg_items_relevance': 2,
            'avg_top3_items_relevance': 1,
            'cnt_items': 2,
        },
        'max_items_cnt': 100,
        'min_items_relevance': -100,
    },
)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_distance(taxi_umlaas_eats, load_json):
    request_body = load_json('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert web_response.status == 200
    response = json.loads(web_response.text)

    assert len(response['result']) == len(request_body['block'])

    # restaurant because of distance
    assert response['result'][0]['place_id'] == 3265

    # check if items per place is the same as in request
    items_num = {
        place['place_id']: len(place.get('items', []))
        for place in request_body['block']
    }
    for place in response['result']:
        assert (
            'items' not in place
            or len(place['items']) == items_num[place['place_id']]
        )


@exp3_decorator(
    name='eats_search_ranking_params',
    value={
        'tag': 'default_sort',
        'linear_params': {
            'average_user_rating': 10,
            'distance_in_km': -10,
            'available': 100,
            'is_restaurant': 0.1,
            'is_shop': 0,
            'place_relevance': 10,
            'max_items_relevance': 3,
            'avg_items_relevance': 2,
            'avg_top3_items_relevance': 1,
            'cnt_items': 2,
        },
        'max_items_cnt': 1,
        'min_items_relevance': -100,
    },
)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_max_item_cnt(taxi_umlaas_eats, load_json):
    request_body = load_json('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert web_response.status == 200
    response = json.loads(web_response.text)

    assert len(response['result']) == len(request_body['block'])

    # check if 0 or 1 items per place
    for place in response['result']:
        assert 'items' not in place or len(place['items']) <= 1


@exp3_decorator(
    name='eats_search_ranking_params',
    value={'tag': 'default_sort', 'model_type': 'catboost'},
)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_default_catboost(taxi_umlaas_eats, load_json):
    request_body = load_json('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=json.dumps(request_body),
    )
    assert web_response.status == 200
    response = json.loads(web_response.text)
    assert len(response['result']) == len(request_body['block'])


@exp3_decorator(
    name='eats_search_ranking_params',
    value={'tag': 'default_sort', 'model_type': 'catboost'},
)
@experiments.ENABLE_BIGB
@pytest.mark.experiments3(
    is_config=True,
    name='eats_search_ranking_orders_history',
    consumers=[experiments.CONSUMER_SEARCH_RANKING],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'tag': 'tag',
        'orders_num_limit': 100,
        'days_num_limit': 60,
        'feedback_threshold': 0,
    },
)
@pytest.mark.config(UMLAAS_EATS_ORDERSHISTORY_ENABLED=True)
async def test_ml_request(taxi_umlaas_eats, testpoint, load_json, mockserver):
    @mockserver.json_handler('/eats-ordershistory/v2/get-orders')
    def _mock_eats_orderhistory(request):
        return load_json('ordershistory_get_orders_v2_response.json')

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
                    {
                        'keyword_id': 1112,
                        'trio_values': [
                            # brand_id, views, clicks
                            {'first': '11', 'second': '1534', 'third': '6794'},
                            {'first': '20', 'second': '234', 'third': '15000'},
                            {
                                'first': '44',
                                'second': '5124',
                                'third': '67334',
                            },
                        ],
                    },
                ],
            },
            msg,
        )
        return mockserver.make_response(
            msg.SerializeToString(deterministic=True),
        )

    @testpoint('eats-search-ranking-ml-request')
    def _eats_search_ranking_ml_request(ml_request):
        pass

    request_body = load_json('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}',
        data=json.dumps(request_body),
        headers={'x-yandex-uid': '12341212'},
    )
    assert web_response.status == 200

    await taxi_umlaas_eats.enable_testpoints()
    ml_request = (await _eats_search_ranking_ml_request.wait_call())[
        'ml_request'
    ]
    assert ml_request, 'error retrieving ML request'

    user_info = ml_request['user_info']
    assert user_info['gender'] == 1
    assert user_info['age'] == 3
    assert user_info['income'] == 4

    order_history = user_info['orders']
    assert len(order_history) == 14
    assert order_history[0]['is_asap'] == True
    assert order_history[0]['total_amount'] == '630'

    some_items = order_history[0]['cart']
    assert len(some_items) == 2
    item_names = [item['name'] for item in some_items]
    assert 'Cola' in item_names

    assert len(order_history[1]['cart']) == 0
    assert 'cart' not in order_history[2]

    brands_stats = user_info['brands_statistics']
    assert len(brands_stats) == 3
    assert 11 in [x['brand_id'] for x in brands_stats]
    assert 44 in [x['brand_id'] for x in brands_stats]
    assert 20 in [x['brand_id'] for x in brands_stats]
    brand11 = [x for x in brands_stats if x['brand_id'] == 11][0]
    assert brand11['views'] == 1534
    assert brand11['opens'] == 6794
