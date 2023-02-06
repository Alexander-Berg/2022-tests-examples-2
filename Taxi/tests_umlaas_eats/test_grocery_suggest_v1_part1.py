import json

import pytest

EXP_EATS_USER_ID = '1184610'
EXP_DEVICE_ID = 'BC5B7039-40C3-46F5-9D10-2B539DC0B730'

REQUEST_SUBSTITUTE_TYPE = 'substitute-items'
REQUEST_COMPLEMENT_TYPE = 'complement-items'
REQUEST_SOURCE_ITEM = 'item-page'
REQUEST_SOURCE_CART = 'cart-page'
REQUEST_SOURCE_MENU = 'menu-page'

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


def exp3_decorator(name, value, consumer='ml/grocery_suggest'):
    return pytest.mark.experiments3(
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


DEFAULT_CANDIDATES_CONFIG = {
    '__default__': [
        '55ed76e6da8941c0bab1218787e45877000200010001',
        '1a4bc1e3b969411fb9002d795bcc3089000200010000',
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
        '6ee0771d5989430dae1021cf193d373b000100010001',
        '5bbee656dbed4d4cb4f15da9248cc4d2000300010000',
        'ad002a7af3d643628a077eefb259a383000200010000',
        'dc1e1b7cd62441038f3f312ad240a1da000100010001',
        '149726c44f384514b83e18387f764fac000200010001',
        '4a46f152863c4f0ea4856565001e0919000300010000',
    ],
    'custom': [
        {
            'name': 'dummy',
            'place_ids': ['123'],
            'candidates': [
                '55ed76e6da8941c0bab1218787e45877000200010001',
                '1a4bc1e3b969411fb9002d795bcc3089000200010000',
                '6ee0771d5989430dae1021cf193d373b000100010001',
                '5bbee656dbed4d4cb4f15da9248cc4d2000300010000',
                'ad002a7af3d643628a077eefb259a383000200010000',
                'dc1e1b7cd62441038f3f312ad240a1da000100010001',
                '149726c44f384514b83e18387f764fac000200010001',
                '4a46f152863c4f0ea4856565001e0919000300010000',
                'ef2dcd5a413f44028dd2a318e538bace000200010000',
            ],
        },
    ],
}
# removed these items from candidates in custom group:
# '8209fdc1ab904e568529b8c24d8b19df000200010001',
# '2cae8c4c7a914d94ae0933404486d299000300010000',

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

EXP3_DEFAULT_CANDIDATES = exp3_decorator(
    'grocery_suggest_ml', {**BASE_EXP_PARAMS, 'max_candidates_num': 0},
)

EXP3_DEFAULT_CANDIDATES_CHECK_STOCKS = exp3_decorator(
    'grocery_suggest_ml', {**BASE_EXP_PARAMS, 'stocks_filter_enabled': True},
)

EXP3_HISTORY_ONLY = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'complement_candidates_from_user_history_only': True,
        'fallback_to_resources_empty_history': False,
        'complement_enabled': True,
        'substitute_enabled': True,
        'stocks_filter_enabled': False,
    },
)
EXP3_MODEL = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'complement_candidates_from_user_history_only': True,
        'complement_ml_enabled': True,
    },
)
EXP3_MODEL_MAINPAGE = exp3_decorator(
    'grocery_suggest_ml', {**BASE_EXP_PARAMS, 'complement_ml_enabled': True},
)
EXP3_MODEL_MAINPAGE_MODEL_SAMPLING = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'complement_ml_enabled': True,
        'sample_with_model_scores': True,
    },
)
EXP3_NPMI_ITEM_RANKING = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'complement_ml_enabled': False,
        'complement_candidates_ranker_field': 'npmi',
        'complement_candidates_extractor_field': 'npmi',
        'complement_candidates_from_user_history_only': False,
        'min_suggest_size': 5,
    },
)
EXP3_NPMI_HISTORY_OVERRIDEN_RANKING = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'overrides': {
            'item-page': {
                'complement_ml_enabled': False,
                'complement_candidates_ranker_field': 'npmi',
                'complement_candidates_extractor_field': 'npmi',
                'complement_candidates_from_user_history_only': False,
            },
        },
    },
)

EXP3_NPMI_HISTORY_OVERRIDEN_RANKING_LOG_MARGIN = exp3_decorator(
    'grocery_suggest_ml',
    {
        **BASE_EXP_PARAMS,
        'overrides': {
            'item-page': {
                'complement_ml_enabled': False,
                'complement_candidates_ranker_field': 'npmi',
                'complement_candidates_extractor_field': 'npmi',
                'complement_candidates_from_user_history_only': False,
                'use_log_margin_for_ranking': True,
            },
        },
    },
)
EXP3_MAIN_PAGE = exp3_decorator('grocery_suggest_ml', BASE_EXP_PARAMS)
EXP3_MAIN_PAGE_CTRS = exp3_decorator(
    'grocery_suggest_ml',
    {**BASE_EXP_PARAMS, 'use_main_page_ctr_for_candidates_extraction': True},
)
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
COMPLEMENT_CANDIDATES_CONFIG = pytest.mark.config(
    GROCERY_SUGGEST_COMPLEMENT_CANDIDATES_DEFAULT=DEFAULT_CANDIDATES_CONFIG,
)


@EXP3_DEFAULT_CANDIDATES
@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={
        'order_history_enabled': True,
        'order_history_max_size': 10,
    },
)
@exp3_decorator(
    name='exp_with_promo',
    value={
        'tag': 'промо, который не должен сработать',
        'target': {'type': 'all'},
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_1', 'my_custom_item_2'],
        },
        'max_suggest_size': 1,
    },
    consumer=PROMO_CONSUMER_NAME,
)
@STOCKS_ENABLED
async def test_v1_default_item_page(
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
            'request_source': REQUEST_SOURCE_ITEM,
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
    assert len(data['items']) == len({x['product_id'] for x in data['items']})
    assert [x['product_id'] for x in data['items']] == [
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
        '6ee0771d5989430dae1021cf193d373b000100010001',
        '5bbee656dbed4d4cb4f15da9248cc4d2000300010000',
        'ad002a7af3d643628a077eefb259a383000200010000',
    ]


@EXP3_HISTORY_ONLY
@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={
        'order_history_enabled': False,
        'order_history_max_size': 10,
    },
)
@STOCKS_ENABLED
async def test_v1_default_item_page_empty_history(
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
            'request_source': REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    assert [x['product_id'] for x in data['items']] == [
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
        '6ee0771d5989430dae1021cf193d373b000100010001',
        '5bbee656dbed4d4cb4f15da9248cc4d2000300010000',
        'ad002a7af3d643628a077eefb259a383000200010000',
    ]


@EXP3_DEFAULT_CANDIDATES
@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={
        'order_history_enabled': True,
        'order_history_max_size': 10,
    },
)
@STOCKS_ENABLED
@COMPLEMENT_CANDIDATES_CONFIG
async def test_v1_default_item_page_default_complement_candidates(
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
            'request_source': REQUEST_SOURCE_ITEM,
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
    assert len(data['items']) == len({x['product_id'] for x in data['items']})
    complement = [x['product_id'] for x in data['items']]
    for item in complement:
        assert item not in [
            '8209fdc1ab904e568529b8c24d8b19df000200010001',
            '2cae8c4c7a914d94ae0933404486d299000300010000',
        ]


@EXP3_NPMI_ITEM_RANKING
async def test_v1_npmi_item_page(taxi_umlaas_eats, load, _mock_ordershistory):
    request_body = load('npmi_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_ITEM,
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
    assert len(data['items']) == len({x['product_id'] for x in data['items']})
    assert [x['product_id'] for x in data['items']] == [
        'top_candidate',
        'other',
        'double_candidate',
        'worst_candidate',
        '55ed76e6da8941c0bab1218787e45877000200010001',
    ]


@EXP3_NPMI_HISTORY_OVERRIDEN_RANKING
async def test_v1_npmi_overrides_item_page(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    request_body = load('npmi_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    assert [x['product_id'] for x in data['items']] == [
        'top_candidate',
        'other',
        'double_candidate',
        'worst_candidate',
    ]


@EXP3_NPMI_HISTORY_OVERRIDEN_RANKING_LOG_MARGIN
async def test_v1_npmi_overrides_item_page_log_margin_ranking(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    request_body = load('npmi_request.json')
    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    assert [x['product_id'] for x in data['items']] == [
        'double_candidate',
        'top_candidate',
        'worst_candidate',
        'other',
    ]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
    GROCERY_SUGGEST_MAIN_PAGE_SETTINGS={
        'blocklist_categories_main_page': ['Презервативы'],
        'candidates_per_history_item': 3,
    },
)
@EXP3_MAIN_PAGE
async def test_v1_menu_page_heuristic(
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
    # we cannot guarantee order in ctr sampling
    candidates = {'ba8ec180-022a-11ea-b7fe-ac1f6b974fa0', 'worst_candidate'}
    assert [x['product_id'] in candidates for x in data['items'][:2]]
    assert [x['product_id'] for x in data['items'][2:]] == [
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
        '6ee0771d5989430dae1021cf193d373b000100010001',
    ]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
    GROCERY_SUGGEST_MAIN_PAGE_SETTINGS={
        'blocklist_categories_main_page': ['Презервативы'],
        'candidates_per_history_item': 3,
    },
)
@EXP3_MAIN_PAGE_CTRS
async def test_v1_menu_page_heuristic_new_ctrs(
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
    assert data['items'][0]['product_id'] == 'double_candidate'


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
    GROCERY_SUGGEST_MAIN_PAGE_SETTINGS={
        'blocklist_categories_main_page': ['Презервативы'],
        'candidates_per_history_item': 3,
    },
)
@EXP3_MAIN_PAGE
@exp3_decorator(
    name='grocery_suggest_ml_promo_bonus',
    value={
        'tag': 'anytag',
        'products': [
            {
                'product_id': 'worst_candidate',
                'multiplier': 100000,
                'addition': 100000,
            },
        ],
    },
    consumer='ml/grocery_suggest',
)
async def test_v1_menu_page_promo(taxi_umlaas_eats, load, _mock_ordershistory):
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
    # we try to move the worst_candidate to the first place
    assert data['items'][0]['product_id'] == 'worst_candidate'


@EXP3_DEFAULT_CANDIDATES_CHECK_STOCKS
@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={
        'order_history_enabled': False,
        'order_history_max_size': 10,
    },
)
@STOCKS_ENABLED
async def test_v1_default_filtered_stocks(
        taxi_umlaas_eats, load, _mock_ordershistory, grocery_depots,
):
    request_body = load('dummy_request.json')
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
            'request_source': REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    assert [x['product_id'] for x in data['items']] == [
        '6ee0771d5989430dae1021cf193d373b000100010001',
    ]


@EXP3_DEFAULT_CANDIDATES_CHECK_STOCKS
@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={
        'order_history_enabled': True,
        'order_history_max_size': 10,
    },
)
@STOCKS_ENABLED
async def test_v1_default_filtered_stocks_sources_error(
        taxi_umlaas_eats,
        load,
        _mock_ordershistory_error,
        _mock_availableforsale_error,
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
            'request_source': REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    assert bool(data['items'])
    assert [x['product_id'] for x in data['items']] == [
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
        '6ee0771d5989430dae1021cf193d373b000100010001',
        '5bbee656dbed4d4cb4f15da9248cc4d2000300010000',
        'ad002a7af3d643628a077eefb259a383000200010000',
    ]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
)
@EXP3_HISTORY_ONLY
@STOCKS_ENABLED
async def test_v1_ml_upsale_with_candidate_from_past_orders_only(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    """
    There are 4 items in user's history.
    3 items which are not in context + 2 default candidates
    must be ranked and returned back.
    """

    request_body = load('request_only_bananas_context.json')

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
    assert [x['product_id'] for x in data['items']] == [
        '4a46f152863c4f0ea4856565001e0919000300010000',
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        'ef2dcd5a413f44028dd2a318e538bace000200010000',
        '55ed76e6da8941c0bab1218787e45877000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
    ]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
)
@EXP3_MODEL
async def test_v1_ml_model_from_history(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    """
    There are 4 items in user's history.
    3 items which are not in context + 2 default candidates
    must be ranked and returned back.
    """

    request_body = load('request_only_bananas_context.json')

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
    # we can't guarantee rank stability of candidates in mock mode
    model_candidates = {
        '4a46f152863c4f0ea4856565001e0919000300010000',
        '8209fdc1ab904e568529b8c24d8b19df000200010001',
        'ef2dcd5a413f44028dd2a318e538bace000200010000',
    }
    assert [x['product_id'] in model_candidates for x in data['items'][:3]]
    assert [x['product_id'] for x in data['items'][3:]] == [
        '55ed76e6da8941c0bab1218787e45877000200010001',
        '2cae8c4c7a914d94ae0933404486d299000300010000',
    ]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
    GROCERY_SUGGEST_MAIN_PAGE_SETTINGS={
        'blocklist_categories_main_page': ['Презервативы'],
        'candidates_per_history_item': 3,
    },
)
@EXP3_MODEL_MAINPAGE
async def test_v1_ml_model_main_page(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    request_body = load('request_only_bananas_context.json')
    # request body does not really matter here
    # since we do not look at context

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
    candidates = {'ba8ec180-022a-11ea-b7fe-ac1f6b974fa0', 'worst_candidate'}
    assert [x['product_id'] in candidates for x in data['items'][:2]]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
    GROCERY_SUGGEST_MAIN_PAGE_SETTINGS={
        'blocklist_categories_main_page': ['Презервативы'],
        'candidates_per_history_item': 3,
    },
)
@EXP3_MODEL_MAINPAGE_MODEL_SAMPLING
async def test_v1_ml_model_sampling_main_page(
        taxi_umlaas_eats, load, _mock_ordershistory,
):
    request_body = load('request_only_bananas_context.json')
    # request body does not really matter here
    # since we do not look at context

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
    candidates = {'ba8ec180-022a-11ea-b7fe-ac1f6b974fa0', 'worst_candidate'}
    assert [x['product_id'] in candidates for x in data['items'][:2]]


@pytest.mark.config(
    GROCERY_SUGGEST_ORDERSHISTORY_SETTINGS={'order_history_enabled': True},
)
@EXP3_HISTORY_ONLY
@exp3_decorator(
    name='grocery_suggest_ml_promo_settings',
    value={'tag': 'promo/on', 'enabled': True},
)
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
            'product_ids': ['my_custom_item_3', 'my_custom_item_in_context'],
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
        'target': {'type': 'all'},
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_1', 'my_custom_item_2'],
        },
        'max_suggest_size': 1,
        'weight': 0,
    },
    consumer=PROMO_CONSUMER_NAME,
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
    },
    consumer=PROMO_CONSUMER_NAME,
)
@exp3_decorator(
    name='exp_with_promo_4',
    value={
        'tag': 'promo/promo_4',
        'target': {
            'type': 'product_ids',
            'product_ids': ['1a4bc1e3b969411fb9002d795bcc3089000200010000'],
        },
        'suggest': {
            'type': 'product_ids',
            'product_ids': ['my_custom_item_item_page'],
        },
        'max_suggest_size': 1,
    },
    consumer=PROMO_CONSUMER_NAME,
)
@STOCKS_ENABLED
async def test_v1_promo(taxi_umlaas_eats, load, _mock_ordershistory):
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
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})
    assert data['items'][0]['product_id'] == 'my_custom_item_3'
    assert data['items'][1]['product_id'] != 'my_custom_item_1'
    assert data['items'][1]['product_id'] != 'my_custom_item_3'
    assert data['items'][1]['product_id'] != 'my_custom_item_2'
    assert data['items'][1]['product_id'] != 'my_custom_item_4'

    response = await taxi_umlaas_eats.post(
        '/umlaas-eats/v1/grocery-suggest',
        data=request_body,
        params={
            'service_name': 'suggest_test',
            'request_id': '-',
            'suggest_type': REQUEST_COMPLEMENT_TYPE,
            'user_id': EXP_EATS_USER_ID,
            'device_id': EXP_DEVICE_ID,
            'request_source': REQUEST_SOURCE_ITEM,
        },
        headers=PA_HEADERS,
    )
    assert response.status == 200
    data = json.loads(response.text)
    request = json.loads(request_body)
    assert bool(data['items'])
    assert not set(item['product_id'] for item in data['items']).intersection(
        set(item['product_id'] for item in request['context']['cart']),
    )
    assert len(data['items']) == len({x['product_id'] for x in data['items']})
    assert data['items'][0]['product_id'] == 'my_custom_item_item_page'


@STOCKS_ENABLED
async def test_v1_grocery_stocks(taxi_umlaas_eats, testpoint, grocery_depots):
    @testpoint('grocery-stocks-cache')
    def grocery_stocks_tp(data):
        pass

    grocery_depots.add_depot(legacy_depot_id='123')
    await taxi_umlaas_eats.enable_testpoints()
    response = await grocery_stocks_tp.wait_call()

    data = response['data']
    assert data['num_stores'] == 1
    assert data['num_products'] == 3
    assert data['product_count'] == 27
