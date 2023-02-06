import copy

import pytest

from tests_order_parts_proxy import consts


EMPTY_EATS_RESPONSE: dict = {
    'payload': {'trackedOrders': []},
    'meta': {'count': 0, 'checkAfter': 15},
}
EMPTY_GROCERY_RESPONSE: dict = {'grocery_orders': [], 'eats_orders': []}

GROCERY_REQUEST: dict = {'known_orders': [], 'should_poll_eats': False}


def replace_orders_statuses(base_eats_orders, status):
    eats_orders = copy.deepcopy(base_eats_orders)
    for order in eats_orders:
        order['status'] = status
    return eats_orders


def build_grocery_response(grocery_orders, eats_orders):
    return {'grocery_orders': grocery_orders, 'eats_orders': eats_orders}


def build_eats_response(eats_orders):
    return {
        'payload': {'trackedOrders': eats_orders},
        'meta': {'count': len(eats_orders), 'checkAfter': 15},
    }


def build_post_payload(known_orders):
    return {'known_orders': known_orders}


@pytest.mark.now('2018-10-01T17:00:00Z')
@pytest.mark.translations(
    client_messages={
        'foodtech.order_status.order_collecting_title': {
            'ru': 'order_collecting_title',
        },
        'foodtech.order_status.order_collecting_description': {
            'ru': 'order_collecting_description',
        },
        'foodtech.order_status.order_rover_arrived_title': {
            'ru': 'order_rover_arrived_title',
        },
        'foodtech.order_status.order_rover_arrived_description': {
            'ru': 'order_rover_arrived_description',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_courier_placemark_settings.json')
@pytest.mark.parametrize(
    (
        'grocery_orders_tracking_state_switching',
        'grocery_orders_state_handler',
    ),
    [
        (True, '/grocery-orders-tracking/lavka/v1/orders-tracking/v1/state'),
        (False, '/grocery-orders/lavka/v1/orders/v1/state'),
    ],
)
@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize(
    'grocery_response,eats_response,expected_orders,expected_check_after',
    [
        pytest.param(
            EMPTY_GROCERY_RESPONSE,
            EMPTY_EATS_RESPONSE,
            [],
            300,
            id='empty responses',
        ),
        pytest.param(
            build_grocery_response(consts.GROCERY_ORDERS, []),
            EMPTY_EATS_RESPONSE,
            consts.GROCERY_ORDER_RESPONSE,
            15,
            id='grocery orders only',
        ),
        pytest.param(
            build_grocery_response(consts.GROCERY_ORDERS, consts.EATS_ORDERS),
            build_eats_response(consts.EATS_ORDERS),
            consts.MERGED_ORDERS,
            15,
            id='remove duplicates',
        ),
    ],
)
async def test_basic_responses(
        taxi_order_parts_proxy,
        mockserver,
        grocery_response,
        eats_response,
        expected_orders,
        expected_check_after,
        method,
        experiments3,
        grocery_orders_tracking_state_switching,
        grocery_orders_state_handler,
):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return eats_response

    experiments3.add_config(
        name='grocery_orders_tracking_state_switching',
        consumers=['grocery_orders_tracking/state'],
        default_value={'enabled': grocery_orders_tracking_state_switching},
    )

    @mockserver.json_handler(grocery_orders_state_handler)
    def mock_grocery_tracking(request):
        return grocery_response

    response = await taxi_order_parts_proxy.request(
        method,
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
        json=build_post_payload([]),
    )

    assert response.status == 200
    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1

    data = response.json()
    assert data == {
        'meta': {
            'checkAfter': expected_check_after,
            'count': len(expected_orders),
        },
        'payload': {'trackedOrders': expected_orders},
    }


@pytest.mark.config(
    ORDER_PARTS_PROXY_TIME_TO_OBSOLETE_ORDER={
        'grocery': [{'statuses': ['order.cancel'], 'duration': 600}],
    },
)
@pytest.mark.translations(
    client_messages={
        'foodtech.order_status.order_collecting_title': {
            'ru': 'order_collecting_title',
        },
        'foodtech.order_status.order_collecting_description': {
            'ru': 'order_collecting_description',
        },
        'foodtech.order_status.order_rover_arrived_title': {
            'ru': 'order_rover_arrived_title',
        },
        'foodtech.order_status.order_rover_arrived_description': {
            'ru': 'order_rover_arrived_description',
        },
    },
)
@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize(
    'grocery_response,eats_response',
    [
        pytest.param(
            EMPTY_GROCERY_RESPONSE,
            build_eats_response(
                consts.EATS_ORDERS_THAT_WERE_CANCELED_LONG_AGO,
            ),
            id='eats response only',
        ),
    ],
)
async def test_orders_that_were_created_long_ago_and_cancele_not_displayed(
        taxi_order_parts_proxy,
        mockserver,
        grocery_response,
        eats_response,
        method,
):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return eats_response

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        return grocery_response

    response = await taxi_order_parts_proxy.request(
        method,
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
        json=build_post_payload([]),
    )

    assert response.status == 200
    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1

    data = response.json()
    assert data == {
        'meta': {'checkAfter': 300, 'count': 0},
        'payload': {'trackedOrders': []},
    }


@pytest.mark.parametrize(
    'eats_status_code,grocery_status_code,expected_status_code',
    [(200, 401, 500), (200, 500, 500), (500, 200, 500)],
)
async def test_error_handling(
        taxi_order_parts_proxy,
        mockserver,
        eats_status_code,
        grocery_status_code,
        expected_status_code,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return mockserver.make_response(
            status=eats_status_code, json=EMPTY_EATS_RESPONSE,
        )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        assert request.json == GROCERY_REQUEST
        return mockserver.make_response(
            status=grocery_status_code, json=EMPTY_GROCERY_RESPONSE,
        )

    response = await taxi_order_parts_proxy.get(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
    )

    assert response.status == expected_status_code


@pytest.mark.translations(
    client_messages={
        'foodtech.order_status.order_delivering_title': {'ru': 'Title'},
        'foodtech.order_status.order_delivering_description': {
            'ru': 'Description %(courier_name)s test',
        },
        'foodtech.order_status.order_rover_arrived_title': {
            'ru': 'order_rover_arrived_title',
        },
        'foodtech.order_status.order_rover_arrived_description': {
            'ru': 'order_rover_arrived_description',
        },
    },
)
async def test_courier_name_status(taxi_order_parts_proxy, mockserver):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return EMPTY_EATS_RESPONSE

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        assert request.json == GROCERY_REQUEST
        orders = consts.GROCERY_ORDERS
        for order in orders:
            order['status'] = 'delivering'
            order['courier_info'] = {'name': 'Courier Name'}
        return build_grocery_response(orders, [])

    response = await taxi_order_parts_proxy.get(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
    )

    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1

    assert response.status == 200
    data = response.json()
    assert len(data['payload']['trackedOrders']) == 2
    order = data['payload']['trackedOrders'][0]
    assert order['title'] == 'Title'
    assert order['description'] == 'Description Courier Name test'


@pytest.mark.parametrize(
    'path,value,expected',
    [
        ('status', 'order.created', (200, 'order.created')),
        ('status', 'order.cooking', (200, 'order.cooking')),
        ('status', 'order.delivering', (200, 'order.delivering')),
        ('status', 'order.delivered', (200, 'order.delivered')),
        ('status', 'order.cancel', (200, 'order.cancel')),
        ('status', 'order.awaiting_payment', (200, 'order.created')),
        ('status', 'unknown', (500,)),
        #
        ('order.deliveryType', 'native', (200, 'native')),
        ('order.deliveryType', 'marketplace', (200, 'marketplace')),
        ('order.deliveryType', 'unknown', (500,)),
        #
        ('order.shippingType', 'delivery', (200, 'delivery')),
        ('order.shippingType', 'pickup', (200, 'pickup')),
        ('order.shippingType', 'unknown', (500,)),
        #
        ('payment.status', 'payment.processing', (200, 'payment.processing')),
        ('payment.status', 'payment.success', (200, 'payment.success')),
        ('payment.status', 'payment.failed', (200, 'payment.failed')),
        ('payment.status', 'unknown', (500,)),
        #
        ('service', 'eats', (200, 'eats')),
        ('service', 'grocery', (200, 'grocery')),
        ('service', 'pharmacy', (200, 'pharmacy')),
        ('service', 'shop', (200, 'shop')),
        ('service', 'unknown', (500,)),
    ],
)
async def test_default_mappings(
        taxi_order_parts_proxy, mockserver, path, value, expected,
):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        eats_orders = copy.deepcopy(consts.EATS_ORDERS)
        for order in eats_orders:
            obj, prop = _path_to_object_and_prop(order, path)
            obj[prop] = value
        return build_eats_response(eats_orders)

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        return EMPTY_GROCERY_RESPONSE

    response = await taxi_order_parts_proxy.get(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
    )

    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1

    assert response.status == expected[0]
    assert mock_eda_tracking.times_called == 1
    if response.status == 500:
        return

    data = response.json()
    assert len(data['payload']['trackedOrders']) == 1
    order = data['payload']['trackedOrders'][0]
    obj, prop = _path_to_object_and_prop(order, path)
    assert obj[prop] == expected[1]


@pytest.mark.config(
    ORDER_PARTS_PROXY_MAPPINGS={
        'status': {'order.created': 'order.created', 'some': 'SOM'},
        'deliveryType': {'native': 'native', 'x': 'X'},
        'shippingType': {'delivery': 'delivery', 'y': 'Y'},
        'paymentStatus': {
            'payment.processing': 'payment.processing',
            'z': 'Z',
        },
        'service': {'something-new': 'NEW', '__default__': 'DEF'},
    },
)
@pytest.mark.parametrize(
    'path,value,expected',
    [
        ('status', 'some', (200, 'SOM')),
        ('status', 'unknown', (500,)),
        #
        ('order.deliveryType', 'x', (200, 'X')),
        ('order.deliveryType', 'unknown', (500,)),
        #
        ('order.shippingType', 'y', (200, 'Y')),
        ('order.shippingType', 'unknown', (500,)),
        #
        ('payment.status', 'z', (200, 'Z')),
        ('payment.status', 'unknown', (500,)),
        #
        ('service', 'something-new', (200, 'NEW')),
        ('service', 'unknown', (200, 'DEF')),
    ],
)
async def test_custom_mappings(
        taxi_order_parts_proxy, mockserver, path, value, expected,
):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        eats_orders = copy.deepcopy(consts.EATS_ORDERS)
        for order in eats_orders:
            obj, prop = _path_to_object_and_prop(order, path)
            obj[prop] = value
        return build_eats_response(eats_orders)

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        return EMPTY_GROCERY_RESPONSE

    response = await taxi_order_parts_proxy.get(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
    )

    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1

    assert response.status == expected[0]
    assert mock_eda_tracking.times_called == 1
    if response.status == 500:
        return

    data = response.json()
    assert len(data['payload']['trackedOrders']) == 1
    order = data['payload']['trackedOrders'][0]
    obj, prop = _path_to_object_and_prop(order, path)
    assert obj[prop] == expected[1]


@pytest.mark.parametrize(
    'header_has_eats_user_id, check_eats_user_id',
    [(True, True), (True, False), (False, True), (False, False)],
)
async def test_check_eats_user_id(
        taxi_order_parts_proxy,
        mockserver,
        taxi_config,
        header_has_eats_user_id,
        check_eats_user_id,
):
    taxi_config.set_values(
        dict(ORDER_PARTS_PROXY_CHECK_EATS_USER_ID=check_eats_user_id),
    )

    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return EMPTY_EATS_RESPONSE

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        return EMPTY_GROCERY_RESPONSE

    headers = copy.deepcopy(consts.DEFAULT_HEADER)
    if header_has_eats_user_id:
        headers['X-YaTaxi-User'] = 'eats_user_id=12345'

    response = await taxi_order_parts_proxy.get(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy', headers=headers,
    )

    assert (
        mock_eda_tracking.times_called == 0
        if check_eats_user_id and not header_has_eats_user_id
        else 1
    )
    assert mock_grocery_tracking.times_called == 1

    data = response.json()
    assert data['meta'] == {'checkAfter': 300, 'count': 0}


@pytest.mark.parametrize('expected_override_request', [True, False])
async def test_clients(
        taxi_order_parts_proxy,
        mockserver,
        experiments3,
        expected_override_request,
):
    experiments3.add_experiment(
        match={
            'predicate': {'type': 'true'},
            'enabled': expected_override_request,
        },
        name='use_overridden_client',
        consumers=['order-parts-proxy/proxy-handler'],
        clauses=[],
        default_value={'enabled': True},
    )

    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return EMPTY_EATS_RESPONSE

    @mockserver.json_handler(
        '/eats-orders-tracking/eats/v1/eats-orders-tracking/v1/tracking',
    )
    def mock_eats_orders_tracking(request):
        return EMPTY_EATS_RESPONSE

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        return EMPTY_GROCERY_RESPONSE

    response = await taxi_order_parts_proxy.get(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
    )

    assert response.status == 200
    assert mock_grocery_tracking.times_called == 1

    if expected_override_request:
        assert mock_eda_tracking.times_called == 0
        assert mock_eats_orders_tracking.times_called == 1
    else:
        assert mock_eda_tracking.times_called == 1
        assert mock_eats_orders_tracking.times_called == 0


@pytest.mark.parametrize(
    'known_orders,expected_orders',
    [
        ([], []),
        ([{'service': 'grocery', 'orderid': '1'}], [{'id': '1'}]),
        (
            [
                {'service': 'grocery', 'orderid': '1'},
                {'service': 'grocery', 'orderid': '2'},
            ],
            [{'id': '1'}, {'id': '2'}],
        ),
        (
            [
                {'service': 'grocery', 'orderid': '1'},
                {'service': 'eats', 'orderid': '2'},
            ],
            [{'id': '1'}],
        ),
        (
            [
                {'service': 'taxi', 'orderid': '1'},
                {'service': 'eats', 'orderid': '2'},
                {'service': 'market', 'orderid': '3'},
            ],
            [],
        ),
    ],
)
async def test_known_orders(
        taxi_order_parts_proxy, mockserver, known_orders, expected_orders,
):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return EMPTY_EATS_RESPONSE

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        assert request.json['known_orders'] == expected_orders
        return EMPTY_GROCERY_RESPONSE

    response = await taxi_order_parts_proxy.post(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
        json=build_post_payload(known_orders),
    )

    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1

    assert response.status == 200


@pytest.mark.config(
    ORDER_PARTS_PROXY_ORDER_CARD_SETTINGS={
        'market': {
            'header_settings': {
                'default_background': {'color': '#CFCFCF'},
                'settings': {
                    'courier:car': {
                        'icon_tag': 'car_icon',
                        'text': {
                            'text': 'courier_car_key',
                            'is_tanker_key': True,
                        },
                        'background': {'color': '#BFBFBF'},
                    },
                },
            },
            'state_timeline_settings': {
                'background_color': '#DFDFDF',
                'items': {
                    'created': {
                        'icon_tag': 'created_icon',
                        'active_color': '#AFAFA1',
                    },
                    'payed': {
                        'icon_tag': 'payed_icon',
                        'active_color': '#AFAFA2',
                    },
                    'delivery': {
                        'icon_tag': 'delivery_icon',
                        'active_color': '#AFAFA3',
                    },
                    'completed': {
                        'icon_tag': 'completed_icon',
                        'active_color': '#AFAFA4',
                    },
                },
            },
        },
    },
    EXTENDED_TEMPLATE_STYLES_MAP={
        'style': {'font_size': 14, 'color': '#000000'},
    },
)
@pytest.mark.translations(
    client_messages={
        'courier_car_key': {'ru': '<style>Доставка на машине</style>'},
    },
)
@pytest.mark.parametrize('enabled', [True, False])
async def test_market_orders_tracking(
        taxi_order_parts_proxy, mockserver, experiments3, enabled,
):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return EMPTY_EATS_RESPONSE

    @mockserver.json_handler('/grocery-orders/lavka/v1/orders/v1/state')
    def mock_grocery_tracking(request):
        return EMPTY_GROCERY_RESPONSE

    @mockserver.json_handler('/market-orders-tracking/api/v1')
    def mock_market_tracking(request):
        print(request)
        return consts.MARKET_RESPONSE

    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='market_orders_tracking_settings',
        consumers=['order-parts-proxy/market-tracking'],
        clauses=[
            {
                'title': '',
                'value': {'enabled': enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )

    response = await taxi_order_parts_proxy.post(
        '/4.0/mlutp/v1/foodtech/v1/orders/tracking/proxy',
        headers=consts.DEFAULT_HEADER,
        json=build_post_payload(
            [
                {'orderid': '1', 'service': 'grocery'},
                {'orderid': '2', 'service': 'market'},
            ],
        ),
    )

    assert mock_eda_tracking.times_called == 1
    assert mock_grocery_tracking.times_called == 1
    assert mock_market_tracking.times_called == (1 if enabled else 0)

    assert response.status == 200
    response_body = response.json()

    if enabled:
        assert response_body == consts.TRACKING_RESPONSE_WITH_MARKET_ORDERS
    else:
        assert response_body == {
            'meta': {'checkAfter': 300, 'count': 0},
            'payload': {'trackedOrders': []},
        }


def _path_to_object_and_prop(obj, path):
    *parts, last = path.split('.')

    for part in parts:
        obj = obj[part]

    return obj, last
