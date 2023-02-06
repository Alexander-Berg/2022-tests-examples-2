import json
import typing

import pytest

from plotva_ml_eats.api import grocery_suggest_v1
from plotva_ml_eats.common.grocery_suggest import constants

PING_PATH = '/plotva-ml-eats/v1/grocery-suggest/ping'
V1_PATH = '/plotva-ml-eats/v1/grocery-suggest'

EXP_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'

PA_HEADERS = {'X-Yandex-UID': '4003514353'}

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(
        attrs={
            'type': 'grocery_suggest_models',
            'version_build': '1629945215',
        },
    ),
    pytest.mark.download_ml_resource(
        attrs={
            'type': 'grocery_suggest_statistics',
            'version_build': '1629945486',
        },
    ),
]


def exp3_decorator(name, value):
    return pytest.mark.client_experiments3(
        consumer=constants.EXP3_CONSUMER,
        args=[
            {'name': 'user_id', 'type': 'string', 'value': EXP_USER_ID},
            {'name': 'device_id', 'type': 'string', 'value': EXP_DEVICE_ID},
            {'name': 'yandex_uid', 'type': 'string', 'value': '4003514353'},
            {'name': 'phone_id', 'type': 'string', 'value': ''},
            {'name': 'place_id', 'type': 'string', 'value': '123'},
            {'name': 'appmetrica_device_id', 'type': 'string', 'value': ''},
        ],
        experiment_name=name,
        value=value,
    )


DEFAULT_EXP = exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': False,
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_candidates_num': 100,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)


async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


@DEFAULT_EXP
async def test_v1_unsupported_type(web_app_client, load):
    response = await web_app_client.post(
        V1_PATH,
        data=load('dummy_request.json'),
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'type': 'impossibletesttype',
        },
        headers=PA_HEADERS,
    )
    assert response.status == 400


@DEFAULT_EXP
async def test_v1_dummy_item_page(web_app_client, load):
    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['items']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@DEFAULT_EXP
async def test_v1_dummy_cart_page(web_app_client, load):
    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@DEFAULT_EXP
@exp3_decorator(
    name='exp_with_promo_1',
    value={
        'tag': 'promo/promo_1',
        'target': {
            'type': 'product_ids',
            'product_ids': ['55ed76e6da8941c0bab1218787e45877000200010001'],
        },
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_1'],
        },
        'max_suggest_size': 1,
        'weight': 1,
    },
)
@exp3_decorator(
    name='exp_with_promo_2',
    value={
        'tag': 'promo/promo_2',
        'target': {'type': 'all'},
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_3'],
        },
        'max_suggest_size': 1,
        'weight': 0,
    },
)
@exp3_decorator(
    name='exp_with_promo_3',
    value={
        'tag': 'promo/promo_3',
        'target': {'type': 'product_ids', 'product_ids': ['unknown_itmes']},
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_4'],
        },
        'max_suggest_size': 1,
        'weight': 0,
    },
)
async def test_v1_promo(web_app_client, load):
    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})
    assert data['items'][0]['product_id'] == 'my_custom_item_1'
    assert data['items'][1]['product_id'] != 'my_custom_item_2'
    assert data['items'][1]['product_id'] != 'my_custom_item_3'
    assert data['items'][1]['product_id'] != 'my_custom_item_4'


@DEFAULT_EXP
async def test_v1_dummy_substitutes(web_app_client, load):
    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_SUBSTITUTE_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert bool(data['items'])


@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': True,
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
async def test_v1_ml_item_page(web_app_client, mockserver, load, load_json):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['items']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': True,
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
async def test_v1_ml_cart_page(web_app_client, mockserver, load, load_json):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': True,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
async def test_v1_ml_upsale_on_empty_input(
        web_app_client, mockserver, load, load_json,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_empty_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': grocery_suggest_v1.constants.REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert bool(data['items'])
    assert len(data['items']) == 4
    assert [x['product_id'] for x in data['items']] == [
        '8de236c045394ee6b7cb6de75cacb99a000200010001',
        '9641f1f7a2c44ab88313ab2696424e46000200010001',
        'c6d535a8d64041f6879dc3c82b4642a8000100010001',
        'fictionalproductid00000000000000000000000001',
    ]
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': True,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
async def test_v1_ml_upsale_on_search(
        web_app_client, mockserver, load, load_json,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_search_request.json')
    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': (
                grocery_suggest_v1.constants.REQUEST_SOURCE_SEARCH
            ),
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())
    assert bool(data['items'])
    assert len(data['items']) >= 4
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': True,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_from_user_history_only': True,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
async def test_v1_ml_upsale_with_candidate_from_past_orders_only(
        web_app_client, mockserver, load, load_json,
):
    """
    There are 4 items in user's history.
    These items (and only these) must be ranked and returned back.
    """

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_request.json')

    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': (
                grocery_suggest_v1.constants.REQUEST_SOURCE_CART
            ),
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert bool(data['items'])
    assert len(data['items']) == 4
    assert len(data['items']) == len({x['product_id'] for x in data['items']})

    user_history = load_json('ordershistory_get_orders_response.json')

    historical_item_ids: typing.Set[str] = set()
    for order in user_history['orders']:
        for item in order['calculation']['items']:
            historical_item_ids.add(item['product_id'])
    assert len(historical_item_ids) == 4

    assert {
        item['product_id'] for item in data['items']
    } == historical_item_ids


@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': True,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_from_user_history_only': True,
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_ranker_field': 'npmi',
        'complement_candidates_adjust_scores': True,
        'complement_candidates_field_for_score_adjustment': 'margin',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
async def test_v1_ml_upsale_with_margin_based_score_adjustment(
        web_app_client, mockserver, load, load_json,
):
    """
    There are 4 items in user's history.
    These items (and only these) must be ranked and returned back.
    """

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_request.json')

    response = await web_app_client.post(
        V1_PATH,
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': (
                grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
            ),
            'user_id': EXP_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': (
                grocery_suggest_v1.constants.REQUEST_SOURCE_CART
            ),
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(await response.text())

    assert bool(data['items'])
    assert len(data['items']) == 4
    assert len(data['items']) == len({x['product_id'] for x in data['items']})


@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': False,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_from_user_history_only': True,
        'complement_candidates_extractor_field': 'pair_cnt',
        'complement_candidates_ranker_field': 'total_cnt',
        'complement_candidates_ranker_bug': False,
        'complement_candidates_adjust_scores': False,
        'complement_candidates_field_for_score_adjustment': 'margin',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
async def test_v1_heuristic_upsale(
        web_app_client, mockserver, load, load_json,
):
    """
    There are 4 items in user's history.
    These items (and only these) must be ranked and returned back.
    """
    expected_id = '8209fdc1ab904e568529b8c24d8b19df000200010001'

    await _check_response_for_expected_id(
        expected_id, load, mockserver, web_app_client, load_json,
    )


@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': False,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_from_user_history_only': True,
        'complement_candidates_extractor_field': 'pair_cnt',
        'complement_candidates_ranker_field': 'pair_cnt',
        'complement_candidates_ranker_bug': False,
        'complement_candidates_adjust_scores': False,
        'complement_candidates_field_for_score_adjustment': 'margin',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
    },
)
async def test_v1_heuristic_upsale_counts_ordered_history(
        web_app_client, mockserver, load, load_json,
):
    """
    Expect bananas
    """
    expected_id = '1a4bc1e3b969411fb9002d795bcc3089000200010000'

    await _check_response_for_expected_id(
        expected_id, load, mockserver, web_app_client, load_json,
    )


async def _check_response_for_expected_id(
        expected_id, load, mockserver, web_app_client, load_json,
):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_userplaces(request):
        return load_json('ordershistory_get_orders_response.json')

    request_body = load('dummy_request.json')
    for _ in range(100):
        response = await web_app_client.post(
            V1_PATH,
            data=request_body,
            params={
                'service_name': 'suggest_test',
                'request_id': '-',
                'suggest_type': (
                    grocery_suggest_v1.constants.REQUEST_COMPLEMENT_TYPE
                ),
                'user_id': EXP_USER_ID,
                'device_id': EXP_DEVICE_ID,
                'request_source': (
                    grocery_suggest_v1.constants.REQUEST_SOURCE_CART
                ),
            },
            headers=PA_HEADERS,
        )
        assert response.status == 200
        data = json.loads(await response.text())

        assert bool(data['items'])
        assert len(data['items']) == 4
        assert len(data['items']) == len(
            {x['product_id'] for x in data['items']},
        )
        assert data['items'][0]['product_id'] == expected_id


@pytest.mark.config(GROCERY_SUGGEST_ML={'order_history_enabled': True})
@exp3_decorator(
    name=constants.EXP3_NAME,
    value={
        'tag': 'ml/test',
        'complement_enabled': True,
        'complement_ml_enabled': False,
        'complement_candidates_default': [
            '8de236c045394ee6b7cb6de75cacb99a000200010001',
            '9641f1f7a2c44ab88313ab2696424e46000200010001',
            'c6d535a8d64041f6879dc3c82b4642a8000100010001',
            'fictionalproductid00000000000000000000000001',
        ],
        'substitute_enabled': True,
        'max_candidates_num_per_item': 20,
        'max_suggest_size': 10,
        'min_item_cnt': 0,
        'min_pair_cnt': 0,
        'min_pair_npmi': 0,
        'min_suggest_size': 4,
        'complement_candidates_from_user_history_only': True,
        'complement_candidates_extractor_field': 'pair_cnt',
        'complement_candidates_ranker_field': 'total_cnt',
        'complement_candidates_ranker_bug': True,
        'complement_candidates_adjust_scores': False,
        'complement_candidates_field_for_score_adjustment': 'margin',
        'substitute_candidates_extractor_field': 'total_cnt',
        'substitute_candidates_ranker_field': 'total_cnt',
        'stocks_filter_enabled': False,
        'overrides': {
            grocery_suggest_v1.constants.REQUEST_SOURCE_CART: {
                'complement_candidates_ranker_bug': False,
            },
        },
    },
)
async def test_v1_heuristic_upsale_override_option(
        web_app_client, mockserver, load, load_json,
):
    """
    There are 4 items in user's history.
    These items (and only these) must be ranked and returned back.
    """
    expected_id = '8209fdc1ab904e568529b8c24d8b19df000200010001'

    await _check_response_for_expected_id(
        expected_id, load, mockserver, web_app_client, load_json,
    )
