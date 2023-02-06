import pytest

BASE_ORDER_CLOSED = {
    'type': 'order_closed',
    'meta_schema_version': 1,
    'occured_at': '2019-10-03T21:00:00+0300',
    'meta': {'amount': '120', 'reason': 'closed'},
}
TANKER_ORDER_CLOSED = {
    'type': 'order_closed',
    'meta_schema_version': 1,
    'occured_at': '2019-10-03T21:00:00+0300',
    'meta': {
        'prices': {
            'consumer_price': '2400.0000',
            'performer_price': '2400.0000',
        },
        'reason': 'order closed',
    },
}


@pytest.mark.parametrize(
    'order_closed',
    [
        pytest.param(None, id='without_payments'),
        pytest.param(BASE_ORDER_CLOSED, id='with_payments'),
    ],
)
@pytest.mark.config(CORP_BILLING_SERVICES_IDS={'eats': [668], 'drive': [123]})
@pytest.mark.parametrize(
    ['topic', 'expected'],
    [
        pytest.param(
            'topic_eats_order_with_refund.json',
            'billing_order_eats_with_refund.json',
            id='eats',
        ),
        pytest.param(
            'topic_drive_order_with_refund.json',
            'billing_order_drive_with_refund.json',
            id='drive',
        ),
        pytest.param(
            'topic_discount_order_with_refund.json',
            'billing_order_discount_with_refund.json',
            id='discount',
        ),
    ],
)
async def test_happy_path(
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
        sync_with_corp_cabinet,
        topic,
        expected,
        order_closed,
):
    @mockserver.json_handler('/taxi-corp-integration/v1/departments/by_user')
    def _departments_by_user(request):
        return {
            'departments': [
                {'_id': '555555555555555555555555'},
                {'_id': '666666666666666666666666'},
            ],
        }

    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')
    orders = await _get_orders(_topic(topic, order_closed))
    response = list(map(normalize_order, orders))

    # remove order if it is empty (it is possible for discounts)
    expected = list(filter(lambda x: x, [_order(expected, order_closed)]))
    if order_closed is None and expected:
        expected[0]['event_at'] = '2019-10-03T17:00:00+0000'
    assert response == expected


@pytest.mark.config(CORP_BILLING_SERVICES_IDS={'eats': [668], 'drive': [123]})
@pytest.mark.parametrize(
    ['topic', 'expected'],
    [
        pytest.param(
            'topic_eats_order_refund_after_closed.json',
            'billing_order_eats_refund_after_closed.json',
            id='eats_refund_after_closed',
        ),
        pytest.param(
            'topic_discount_order_refund_after_closed.json',
            'billing_order_discount_refund_after_closed.json',
            id='discount_refund_after_closed',
        ),
    ],
)
async def test_happy_path_refund_after_closed(
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
        sync_with_corp_cabinet,
        load_json,
        topic,
        expected,
):
    @mockserver.json_handler('/taxi-corp-integration/v1/departments/by_user')
    def _departments_by_user(request):
        return {
            'departments': [
                {'_id': '555555555555555555555555'},
                {'_id': '666666666666666666666666'},
            ],
        }

    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')
    orders = await _get_orders(_topic(topic, None))
    response = list(map(normalize_order, orders))
    expected = [_order(expected, True)]
    assert response == expected


@pytest.mark.parametrize(
    ['order_closed', 'payment_method', 'expected'],
    [
        pytest.param(
            None,
            'corp',
            'billing_order_tanker_with_refund.json',
            id='not_closed',
        ),
        pytest.param(
            TANKER_ORDER_CLOSED,
            'corp',
            'billing_order_tanker_closed.json',
            id='closed_with_new_price',
        ),
        pytest.param(
            TANKER_ORDER_CLOSED,
            'card',
            'billing_order_tanker_closed.json',
            id='paid_with_card',
        ),
    ],
)
@pytest.mark.config(
    CORP_BILLING_SERVICES_IDS={'eats': [668], 'drive': [123], 'tanker': [636]},
)
async def test_happy_path_tanker(
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
        sync_with_corp_cabinet,
        expected,
        order_closed,
        payment_method,
):
    @mockserver.json_handler('/taxi-corp-integration/v1/departments/by_user')
    def _departments_by_user(request):
        return {
            'departments': [
                {'_id': '555555555555555555555555'},
                {'_id': '666666666666666666666666'},
            ],
        }

    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')
    orders = await _get_orders(
        _topic(
            'topic_tanker_order_with_refund.json',
            order_closed,
            payment_method,
        ),
    )
    response = list(map(normalize_order, orders))
    expected = [_order(expected, order_closed, payment_method)]
    if order_closed is None:
        expected[0]['event_at'] = '2019-10-03T17:00:00+0000'
    assert response == expected


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'cargo': {
            'client': 'cargo_multi_client_b2b_trip_payment',
            'partner': 'cargo_multi_park_b2b_trip_payment',
        },
    },
)
async def test_happy_path_cargo(
        sync_with_corp_cabinet,
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
):
    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    async def _get_mvp(request):
        return {'oebs_mvp_id': 'MSK'}

    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def _client(request):
        return {
            'client_id': request.args['client_id'],
            'contract_id': '42131 /12',
            'name': 'ООО КАРГО',
            'billing_contract_id': '123',
            'billing_client_id': '100',
            'country': 'rus',
            'services': {'cargo': {'is_test': True}},
        }

    orders = await _get_orders(
        _topic('topic_cargo_order_with_refund.json', BASE_ORDER_CLOSED),
    )
    response = list(map(normalize_order, orders))
    expected = [
        _order('billing_order_cargo_with_refund.json', BASE_ORDER_CLOSED),
    ]
    assert response == expected


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'logistic_cargo': {
            'client': 'cargo_client_b2b_logistics_payment',
            'partner': 'cargo_park_b2b_logistics_payment',
        },
    },
)
async def test_happy_path_cargo_logistic(
        sync_with_corp_cabinet,
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
):
    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    async def _get_mvp(request):
        return {'oebs_mvp_id': 'MSK'}

    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def _client(request):
        return {
            'client_id': request.args['client_id'],
            'contract_id': '42131 /12',
            'name': 'ООО КАРГО',
            'billing_contract_id': '123',
            'billing_client_id': '100',
            'country': 'rus',
            'services': {'cargo': {'is_test': True}},
        }

    orders = await _get_orders(
        _topic(
            'logistic_topic_cargo_order_with_refund.json', BASE_ORDER_CLOSED,
        ),
    )
    response = list(map(normalize_order, orders))
    expected = [
        _order(
            'logistic_billing_order_cargo_with_refund.json', BASE_ORDER_CLOSED,
        ),
    ]
    assert response == expected


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'logistic_cargo': {
            'client': 'cargo_client_b2b_logistics_payment',
            'partner': 'cargo_park_b2b_logistics_payment',
        },
    },
)
async def test_happy_path_cargo_test_without_contract(
        sync_with_corp_cabinet,
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    async def _active_contracts(request):
        return []

    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    async def _get_mvp(request):
        return {'oebs_mvp_id': 'MSK'}

    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    async def _client(request):
        return {
            'client_id': request.args['client_id'],
            'contract_id': '42131 /12',
            'name': 'ООО КАРГО',
            'billing_contract_id': '123',
            'billing_client_id': '100',
            'country': 'rus',
            'services': {'cargo': {'is_test': True}},
        }

    orders = await _get_orders(
        _topic(
            'logistic_topic_cargo_order_with_refund.json', BASE_ORDER_CLOSED,
        ),
    )
    response = list(map(normalize_order, orders))
    expected = [
        _order(
            'logistic_billing_order_cargo_with_refund_without_contract.json',
            BASE_ORDER_CLOSED,
        ),
    ]
    assert response == expected


@pytest.fixture
def _get_orders(
        request_billing_orders,
        get_billing_id_handler,
        get_billing_active_contract,
):
    async def _wrapper(topic):
        response = await request_billing_orders(topic)
        assert response.status_code == 200
        return response.json()['orders']

    return _wrapper


@pytest.fixture
def _topic(load_json, sync_with_corp_cabinet):
    def _wrapper(topic_file, order_closed, payment_method=None):
        topic = load_json(topic_file)
        if order_closed:
            topic['events'].append(order_closed)
        if payment_method is not None:
            topic['events'][0]['meta']['payment_method'] = payment_method
        return topic

    return _wrapper


@pytest.fixture
def _order(load_json, normalize_order):
    def _wrapper(expected_file, order_closed, payment_method=None):
        order = load_json(expected_file)
        if payment_method == 'card':
            entries = order['data']['template_entries'][2:]
            order['data']['template_entries'] = entries
        if not order_closed and 'tanker' not in order['topic']:
            order['data']['payments'] = []
            if order.get('kind') == 'arbitrary_payout':
                return {}
        return normalize_order(order)

    return _wrapper


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'cargo': {
            'client': 'cargo_multi_client_b2b_trip_payment',
            'partner': 'cargo_multi_park_b2b_trip_payment',
        },
    },
    CORP_BILLING_CARGO_SKIP_TOPIC_SETTINGS={
        'by_corp_client_ids': ['111111111111111111111111'],
    },
)
async def test_cargo_banned_corp_client(
        sync_with_corp_cabinet,
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
):
    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    async def _get_mvp(request):
        return {'oebs_mvp_id': 'MSK'}

    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def _client(request):
        return {
            'client_id': request.args['client_id'],
            'contract_id': '42131 /12',
            'name': 'ООО КАРГО',
            'billing_contract_id': '123',
            'billing_client_id': '100',
            'country': 'rus',
            'services': {'cargo': {'is_test': True}},
        }

    orders = await _get_orders(
        _topic('topic_cargo_order_with_refund.json', BASE_ORDER_CLOSED),
    )
    response = list(map(normalize_order, orders))
    assert response == []


@pytest.mark.config(
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'cargo': {
            'client': 'cargo_multi_client_b2b_trip_payment',
            'partner': 'cargo_multi_park_b2b_trip_payment',
        },
    },
    CORP_BILLING_CARGO_SKIP_TOPIC_SETTINGS={'by_tariff_classes': ['cargo']},
)
async def test_cargo_banned_tariff_class(
        sync_with_corp_cabinet,
        mockserver,
        _get_orders,
        _topic,
        _order,
        normalize_order,
):
    await sync_with_corp_cabinet('clients_eats_order_with_refund.json')

    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    async def _get_mvp(request):
        return {'oebs_mvp_id': 'MSK'}

    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def _client(request):
        return {
            'client_id': request.args['client_id'],
            'contract_id': '42131 /12',
            'name': 'ООО КАРГО',
            'billing_contract_id': '123',
            'billing_client_id': '100',
            'country': 'rus',
            'services': {'cargo': {'is_test': True}},
        }

    orders = await _get_orders(
        _topic('topic_cargo_order_with_refund.json', BASE_ORDER_CLOSED),
    )
    response = list(map(normalize_order, orders))
    assert response == []
