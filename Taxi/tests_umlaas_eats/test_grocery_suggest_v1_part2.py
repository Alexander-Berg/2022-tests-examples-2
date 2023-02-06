import json

import pytest

EXP_EATS_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'

REQUEST_SUBSTITUTE_TYPE = 'substitute-items'
REQUEST_COMPLEMENT_TYPE = 'complement-items'
REQUEST_SOURCE_ITEM = 'item-page'
REQUEST_SOURCE_CART = 'cart-page'
REQUEST_SOURCE_MENU = 'menu-page'
REQUEST_SOURCE_TABLEWARE = 'tableware'

PROMO_CONSUMER_NAME = 'umlaas-eats-grocery-suggest-commercial'

USER = f'personal_phone_id=3182348121,eats_user_id={EXP_EATS_USER_ID}'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-User': USER,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}


def exp3_decorator(
        name, value, consumer='ml/grocery_suggest', is_config: bool = False,
):
    return pytest.mark.experiments3(
        is_config=is_config,
        name=name,
        consumers=[consumer],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


@pytest.fixture
def _mock_ordershistory(mockserver, load_json):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock(request):
        return load_json('internal_retrieve_orders_raw.json')


@pytest.fixture
def _mock_ordershistory_error(mockserver):
    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def _mock_500(request):
        return mockserver.make_response(
            '{"code": "internal_server_error", "message": ""}',
            500,
            content_type='application/json',
        )


@pytest.fixture
def _mock_availableforsale_error(mockserver):
    @mockserver.json_handler(
        '/overlord-catalog/v1/catalog/availableforsale/', prefix=True,
    )
    def _mock_500(request):
        return mockserver.make_response(
            '{"code": "internal_server_error", "message": ""}',
            500,
            content_type='application/json',
        )


BASE_EXP_PARAMS = {
    'complement_candidates_extractor_field': 'npmi',
    'complement_candidates_ranker_field': 'npmi',
    'complement_candidates_from_user_history_only': True,
    'complement_enabled': True,
    'complement_ml_enabled': False,
    'max_candidates_num': 10,
    'max_candidates_num_per_item': 20,
    'max_suggest_size': 5,
    'min_item_cnt': 0,
    'min_pair_cnt': 0,
    'min_pair_npmi': 0,
    'min_suggest_size': 4,
    'stocks_filter_enabled': False,
    'filter_by_cart_categories': False,
    'filter_repeated_categories': False,
    'substitute_candidates_extractor_field': 'total_cnt',
    'substitute_candidates_ranker_field': 'total_cnt',
    'substitute_enabled': False,
    'tag': 'ml/test',
}

BASE_EXP_CONFIG = exp3_decorator('grocery_suggest_ml', BASE_EXP_PARAMS)
EXP3_MAIN_PAGE = exp3_decorator('grocery_suggest_ml', BASE_EXP_PARAMS)

EXP3_SUBSTITUTES = exp3_decorator(
    'grocery_suggest_ml', {**BASE_EXP_PARAMS, 'substitute_enabled': True},
)
EXP3_SUBSTITUTES_STOCKS = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'stocks_filter_enabled': True,
        'substitute_enabled': True,
    },
)
STOCKS_ENABLED = pytest.mark.config(GROCERY_SUGGEST_STOCKS_ENABLED=True)

EXAMPLE_TABLEWARE_CONFIG = {
    'tag': 'tableware',
    'mappings': [
        {
            'categories': ['Ready meals', 'Hot Kentucky Fried Chicken'],
            'items': ['cool_fork_knife_and_spoon', 'basic_tableware'],
            'name': 'tableware',
        },
        {
            'categories': ['Sushi', 'Sushi&Rolls'],
            'items': ['chopsticks'],
            'name': 'chopsticks',
        },
    ],
}


def tableware_config():
    return exp3_decorator(
        is_config=True,
        name='grocery_suggest_tableware',
        value=EXAMPLE_TABLEWARE_CONFIG,
    )


EXP3_TABLEWARE_CONFIG = tableware_config()


@EXP3_SUBSTITUTES
async def test_v1_substitutes(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('substitute_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_SUBSTITUTE_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    request = json.loads(request_body)
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['items']),
    )
    response_ids = [x['product_id'] for x in data['items']]

    assert len(response_ids) == 2
    assert '6ee0771d5989430dae1021cf193d373b000100010001' in response_ids
    assert 'substitute_not_in_stock' in response_ids


@EXP3_SUBSTITUTES_STOCKS
@STOCKS_ENABLED
async def test_v1_substitutes_stocks(
        taxi_umlaas_eats, load, _mock_ordershistory, grocery_depots,
):
    grocery_depots.add_depot(legacy_depot_id='123')
    request_body = load('substitute_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_SUBSTITUTE_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    request = json.loads(request_body)
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['items']),
    )
    response_ids = [x['product_id'] for x in data['items']]

    assert len(response_ids) == 1
    assert '6ee0771d5989430dae1021cf193d373b000100010001' in response_ids
    assert 'substitute_not_in_stock' not in response_ids


@BASE_EXP_CONFIG
@EXP3_TABLEWARE_CONFIG
async def test_v1_tableware(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('tableware_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_TABLEWARE,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    response_ids = [x['product_id'] for x in data['items']]

    assert len(response_ids) == 2
    assert 'cool_fork_knife_and_spoon' in response_ids
    assert 'chopsticks' in response_ids


@EXP3_SUBSTITUTES_STOCKS
@EXP3_TABLEWARE_CONFIG
@STOCKS_ENABLED
async def test_v1_tableware_stocks(
        taxi_umlaas_eats, load, _mock_ordershistory, grocery_depots,
):
    request_body = load('tableware_request.json')
    grocery_depots.add_depot(legacy_depot_id='123')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_TABLEWARE,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    response_ids = [x['product_id'] for x in data['items']]

    assert len(response_ids) == 2
    assert 'cool_fork_knife_and_spoon' not in response_ids  # not in stocks
    assert 'basic_tableware' in response_ids
    assert 'chopsticks' in response_ids


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
)
@EXP3_MAIN_PAGE
@exp3_decorator(
    name='grocery_suggest_ml_promo_settings',
    value={'tag': 'promo/on', 'enabled': True},
)
@exp3_decorator(
    name='exp_with_promo_1',
    value={
        'tag': 'promo/promo_1',
        'target': {
            'type': 'history_categories',
            'history_categories': ['missed_category'],
            'history_period': 10,
        },
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_1'],
        },
        'max_suggest_size': 1,
        'weight': 1,
    },
    consumer=PROMO_CONSUMER_NAME,
)
@exp3_decorator(
    name='exp_with_promo_2',
    value={
        'tag': 'promo/promo_2',
        'target': {
            'type': 'history_categories',
            'history_categories': ['Просто хлеб'],
            'history_period': 2,
        },
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_2', 'my_custom_item_in_context'],
        },
        'max_suggest_size': 1,
        'weight': 1,
    },
    consumer=PROMO_CONSUMER_NAME,
)
async def test_v1_promo_by_category(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    request_body = load('dummy_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_MENU,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    request = json.loads(request_body)
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['items']),
    )
    # promo suggest to the first place
    assert data['items'][0]['product_id'] == 'my_custom_item_2'

    request_body = load('dummy_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_CART,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    request = json.loads(request_body)
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['items']),
    )
    # promo suggest does not work for cart-page
    assert data['items'][0]['product_id'] != 'my_custom_item_1'
    assert data['items'][0]['product_id'] != 'my_custom_item_in_context'
    assert data['items'][0]['product_id'] != 'my_custom_item_2'


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
)
@EXP3_MAIN_PAGE
@exp3_decorator(
    name='grocery_suggest_ml_promo_settings',
    value={'tag': 'promo/on', 'enabled': True},
)
@exp3_decorator(
    name='exp_with_promo_3',
    value={
        'tag': 'promo/promo_3',
        'target': {
            'type': 'history_categories',
            'history_categories': ['Sushi'],
            'history_period': 30,
        },
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_3', 'my_custom_item_in_context'],
        },
        'max_suggest_size': 1,
        'weight': 1,
    },
    consumer=PROMO_CONSUMER_NAME,
)
async def test_v1_promo_by_category_skip_old(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    request_body = load('dummy_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_MENU,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    # promo suggest does not work due to history outdated
    assert data['items'][0]['product_id'] != 'my_custom_item_3'
