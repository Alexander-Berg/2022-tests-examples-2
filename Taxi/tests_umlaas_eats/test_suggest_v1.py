import json
from urllib import parse as urlparse

import pytest

from tests_umlaas_eats import experiments

URL = '/umlaas-eats/v1/eats-suggest'
CONSUMER_SUGGEST_V1 = 'umlaas-eats-suggest'

EXP_USER_ID = '777'
EXP_DEVICE_ID = '888'


def exp3_decorator(name, value):
    return pytest.mark.experiments3(
        name=name,
        consumers=[CONSUMER_SUGGEST_V1],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


@pytest.fixture
def _mock_ordershistory(mockserver, load_json):
    allowed_ids = {'eats_user_id', 'yandex_uid', 'taxi_user_id'}

    @mockserver.json_handler('/eats-ordershistory/v1/get-orders')
    def _mock(request):
        request_json: dict = request.json
        ids_present_in_request = request_json.keys() & allowed_ids
        assert len(ids_present_in_request) == 1  # only 1 id is allowed
        return load_json('ordershistory_mock.json')


EXP3_SUGGEST_PARAMS = exp3_decorator(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 3,
        'max_suggest_size': 10,
        'max_candidates_num_per_item': 10,
    },
)

EXP3_SUGGEST_PARAMS2 = exp3_decorator(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'enable_fallback': True,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 3,
        'max_suggest_size': 10,
        'max_candidates_num_per_item': 10,
    },
)

EXP3_SUGGEST_PARAMS3 = exp3_decorator(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'enable_rules': True,
        'enable_fallback': False,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 0,
        'max_suggest_size': 10,
        'max_candidates_num_per_item': 10,
    },
)

EXP3_SUGGEST_PARAMS4 = exp3_decorator(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'enable_rules': False,
        'enable_history': True,
        'enable_fallback': False,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 0,
        'max_suggest_size': 10,
        'max_candidates_num_per_item': 10,
    },
)

EXP3_SUGGEST_PARAMS5 = exp3_decorator(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'enable_rules': False,
        'enable_history': False,
        'enable_fallback': False,
        'ctr_fallback': True,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 0,
        'max_suggest_size': 10,
        'ctr_fallback_size': 7,
        'max_candidates_num_per_item': 10,
    },
)

EXP3_SUGGEST_PARAMS6 = exp3_decorator(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'enable_rules': False,
        'enable_history': False,
        'enable_fallback': False,
        'ctr_fallback': True,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 0,
        'max_suggest_size': 10,
        'ctr_fallback_sort_by': 'ctr_price_desc',
        'ctr_fallback_size': 7,
        'max_candidates_num_per_item': 10,
    },
)

EXP3_RULES_PARAMS = exp3_decorator(
    name='eats_suggest_rules',
    value={
        'category_suggest_rules': [
            {
                'name': 'для собак',
                'suggest': [
                    {'name': 'кола', 'weight': 10},
                    {'name': 'мясо', 'weight': 22},
                    {'name': 'аксессуары', 'weight': 65},
                ],
            },
            {
                'name': 'аксессуары',
                'suggest': [
                    {'name': 'несъедобное', 'weight': 77},
                    {'name': 'готовая еда', 'weight': 30},
                    {'name': 'для собак', 'weight': 2},
                ],
            },
        ],
        'category_block_rules': [
            {'name': 'для собак', 'block_list': ['десерты', 'аксессуары']},
        ],
    },
)


def get_query_params(
        x_yandex_uid='0',
        x_yataxi_userid='0',
        service_name='pytest',
        request_id='value_request_id',
        user_id=0,
        device_id='0',
        suggest_type='complement-items',
        request_source='cart',
):
    params = dict(
        x_yandex_uid=x_yandex_uid,
        x_yataxi_userid=x_yataxi_userid,
        service_name=service_name,
        request_id=request_id,
        user_id=user_id,
        device_id=device_id,
        suggest_type=suggest_type,
        request_source=request_source,
    )
    return params


@EXP3_SUGGEST_PARAMS
async def test_default(taxi_umlaas_eats, load):
    request_body = load('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '228', 'group_id': '228'},
        {'uuid': '229', 'group_id': '229'},
        {'uuid': '230', 'group_id': '230'},
        {'uuid': '231', 'group_id': '231'},
    ]


@EXP3_SUGGEST_PARAMS2
async def test_with_popular(taxi_umlaas_eats, load):
    request_body = load('request3.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '309779482', 'group_id': '309779482'},
        {'uuid': '309778732', 'group_id': '309778732'},
        {'uuid': '309784242', 'group_id': '309784242'},
        {'uuid': '309761142', 'group_id': '309761142'},
        {'uuid': '3097611423', 'group_id': '3097611423'},
    ]


@EXP3_SUGGEST_PARAMS
async def test_ids_universalization(taxi_umlaas_eats, load):
    request_body = load('request_universal_ids.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '10', 'group_id': '10'},
        {'uuid': '11', 'group_id': '11'},
        {'uuid': '12', 'group_id': '12'},
    ]


@EXP3_SUGGEST_PARAMS
async def test_equivalent_ids(taxi_umlaas_eats, load):
    request_body = load('request_equivalent_items.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '100', 'group_id': '100'},
        {'uuid': '101', 'group_id': '100'},
        {'uuid': '102', 'group_id': '100'},
        {'uuid': '200', 'group_id': '200'},
        {'uuid': '201', 'group_id': '200'},
        {'uuid': '202', 'group_id': '200'},
        {'uuid': '300', 'group_id': '300'},
        {'uuid': '301', 'group_id': '300'},
        {'uuid': '302', 'group_id': '300'},
    ]


@experiments.helper(
    name='eats_experiment_suggest',
    value={
        'tag': 'suggest_test',
        'enabled': True,
        'min_pair_npmi': 0,
        'min_pair_pmi': 0,
        'min_pair_cnt': 0,
        'min_item_cnt': 0,
        'min_suggest_size': 3,
        'max_suggest_size': 10,
        'max_candidates_num_per_item': 10,
        'sort_by': 'price_desc',
    },
    consumers=[CONSUMER_SUGGEST_V1],
)
async def test_sort_suggest_by_price(taxi_umlaas_eats, load):
    request_body = load('request.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '230', 'group_id': '230'},
        {'uuid': '228', 'group_id': '228'},
        {'uuid': '229', 'group_id': '229'},
        {'uuid': '231', 'group_id': '231'},
    ]


@EXP3_SUGGEST_PARAMS3
@EXP3_RULES_PARAMS
async def test_suggest_rules(taxi_umlaas_eats, load):
    request_body = load('request_for_rules.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '230', 'group_id': '230'},
        {'uuid': '229', 'group_id': '229'},
        {'uuid': '3', 'group_id': '3'},
        {'uuid': '777', 'group_id': '777'},
        {'uuid': '231', 'group_id': '231'},
        {'uuid': '228', 'group_id': '228'},
        {'uuid': '1', 'group_id': '1'},
        {'uuid': '15736585', 'group_id': '15736585'},
    ]


@EXP3_SUGGEST_PARAMS4
async def test_suggest_history(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('request_for_rules.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'][:2] == [
        {'uuid': '1', 'group_id': '1'},
        {'uuid': '3', 'group_id': '3'},
    ]


@EXP3_SUGGEST_PARAMS5
async def test_suggest_ctr(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('request_for_ctr.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '99', 'group_id': '99'},
        {'uuid': '3', 'group_id': '3'},
        {'uuid': '1', 'group_id': '1'},
        {'uuid': '15736585', 'group_id': '15736585'},
        {'uuid': '777', 'group_id': '777'},
        {'uuid': '36878128', 'group_id': '36878128'},
        {'uuid': '19737116', 'group_id': '19737116'},
    ]


@EXP3_SUGGEST_PARAMS5
async def test_suggest_ctr2(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('request_for_ctr2.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '1001', 'group_id': '1001'},
        {'uuid': '1002', 'group_id': '1002'},
        {'uuid': '1003', 'group_id': '1003'},
        {'uuid': '1000', 'group_id': '1000'},
    ]


@EXP3_SUGGEST_PARAMS6
async def test_suggest_ctr3(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('request_for_ctr2.json')
    params = get_query_params()
    web_response = await taxi_umlaas_eats.post(
        f'{URL}?{urlparse.urlencode(params)}', data=request_body,
    )
    assert web_response.status == 200
    res = json.loads(web_response.text)
    request_body = json.loads(request_body)
    assert params['request_id'] == res['request_id']
    assert res['items'] == [
        {'uuid': '1001', 'group_id': '1001'},
        {'uuid': '1003', 'group_id': '1003'},
        {'uuid': '1000', 'group_id': '1000'},
        {'uuid': '1002', 'group_id': '1002'},
    ]
