import pytest

MARKET_UTILS_CLIENT_QOS = pytest.mark.config(
    MARKET_UTILS_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
)
ENABLE_SEND_PUSHES = pytest.mark.experiments3(
    name='grocery_market_gw_send_push',
    consumers=['grocery-market-gw/orders'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)

NOTIFICATION_SUBTYPE = 'PUSH_STORE_LAVKA'

GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG = pytest.mark.config(
    GROCERY_MARKET_GW_PUSH_TEMPLATES={
        'delivering': {
            'title': 'Заказ {order_id} передан в доставку',
            'message': (
                'Заказ {order_id} передан в '
                'доставку и совсем скоро будет у вас'
            ),
            'deeplink': 'yamarket://lavka/order/track/{order_id}',
            'notification_sub_type': NOTIFICATION_SUBTYPE,
        },
    },
)


def _get_expected_market_utils_request(yandex_uid, order_id):
    return {
        'data': {
            'push_data_store_push_deeplink_v1': (
                f'yamarket://lavka/order/track/{order_id}'
            ),
            'push_template_param_message': (
                f'Заказ {order_id} передан в доставку и '
                'совсем скоро будет у вас'
            ),
            'push_template_param_title': (
                f'Заказ {order_id} передан в доставку'
            ),
        },
        'notificationSubtype': 'PUSH_STORE_LAVKA',
        'uid': int(yandex_uid),
    }


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
@pytest.mark.parametrize('enable_experiment', [None, False, True])
async def test_order_event_send_push_under_experiment(
        taxi_grocery_market_gw,
        experiments3,
        grocery_order_log,
        mockserver,
        mock_market_utils,
        enable_experiment,
):
    order_id = 'some_order_id'
    order_state = 'delivering'
    yandex_uid = '4065912996'

    if enable_experiment is not None:
        experiments3.add_config(
            name='grocery_market_gw_send_push',
            consumers=['grocery-market-gw/orders'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[
                {
                    'title': 'Always enabled',
                    'predicate': {'type': 'true'},
                    'value': {'enabled': enable_experiment},
                },
            ],
        )

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        status=order_state,
        items=[],
        price='0',
    )

    mock_market_utils.check_api_add_request(
        check_request_body=_get_expected_market_utils_request(
            yandex_uid=yandex_uid, order_id=order_id,
        ),
        response_code=201,
    )

    response = await taxi_grocery_market_gw.post(
        '/processing/v1/order/v1/event',
        json={'order_id': order_id, 'order_state': order_state},
    )
    assert response.status == 200
    if enable_experiment is True:
        assert mock_market_utils.api_event_add_called == 1
    else:
        assert mock_market_utils.api_event_add_called == 0


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
@ENABLE_SEND_PUSHES
@pytest.mark.parametrize(
    'order_state,should_send',
    [('delivering', True), ('closed', False), ('created', False)],
)
async def test_order_event_order_states(
        taxi_grocery_market_gw,
        grocery_order_log,
        mock_market_utils,
        order_state,
        should_send,
):
    order_id = 'some_order_id'
    yandex_uid = '4065912996'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        status=order_state,
        items=[],
        price='0',
    )

    mock_market_utils.check_api_add_request(
        check_request_body=_get_expected_market_utils_request(
            yandex_uid=yandex_uid, order_id=order_id,
        ),
        response_code=201,
    )

    response = await taxi_grocery_market_gw.post(
        '/processing/v1/order/v1/event',
        json={'order_id': order_id, 'order_state': order_state},
    )
    assert response.status == 200
    if should_send is True:
        assert mock_market_utils.api_event_add_called == 1
    else:
        assert mock_market_utils.api_event_add_called == 0


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
async def test_order_event_throw_on_order_log_error(
        taxi_grocery_market_gw, mockserver,
):
    order_id = 'some_order_id'

    @mockserver.json_handler(
        '/grocery-order-log/internal/orders/v1/retrieve-raw',
    )
    def mock_retrieve_orders(request):
        return mockserver.make_response(status=500)

    response = await taxi_grocery_market_gw.post(
        '/processing/v1/order/v1/event',
        json={'order_id': order_id, 'order_state': 'delivering'},
    )
    assert response.status == 500
    assert mock_retrieve_orders.has_calls


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
@ENABLE_SEND_PUSHES
@MARKET_UTILS_CLIENT_QOS
async def test_order_event_throw_on_market_utils_error(
        taxi_grocery_market_gw, grocery_order_log, mock_market_utils,
):
    order_id = 'some_order_id'
    yandex_uid = '4065912996'
    order_state = 'delivering'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        status=order_state,
        items=[],
        price='0',
    )

    mock_market_utils.check_api_add_request(response_code=500)

    response = await taxi_grocery_market_gw.post(
        '/processing/v1/order/v1/event',
        json={'order_id': order_id, 'order_state': order_state},
    )
    assert response.status == 500
    assert mock_market_utils.api_event_add_called == 1


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
@ENABLE_SEND_PUSHES
async def test_order_event_ignore_non_market_orders(
        taxi_grocery_market_gw, grocery_order_log, mock_market_utils,
):
    order_id = 'some_order_id'
    yandex_uid = '123456'
    order_state = 'delivering'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        status=order_state,
        items=[],
        price='0',
        order_source='lavka',
    )

    mock_market_utils.check_api_add_request(response_code=500)

    response = await taxi_grocery_market_gw.post(
        '/processing/v1/order/v1/event',
        json={'order_id': order_id, 'order_state': order_state},
    )
    assert response.status == 200
    assert mock_market_utils.api_event_add_called == 0


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
@ENABLE_SEND_PUSHES
async def test_order_event_retries(
        taxi_grocery_market_gw, grocery_order_log, mock_market_utils,
):
    order_id = 'some_order_id'
    yandex_uid = '4065912996'
    order_state = 'delivering'
    retries = 5

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        status=order_state,
        items=[],
        price='0',
    )

    prev_source_id = None

    def check_source_id_equal(request):
        nonlocal prev_source_id
        if prev_source_id is None:
            prev_source_id = request.json['sourceId']

        assert request.json['sourceId'] == prev_source_id

    mock_market_utils.check_api_add_request(
        check_request_body=_get_expected_market_utils_request(
            yandex_uid=yandex_uid, order_id=order_id,
        ),
        response_code=201,
        check_callback=check_source_id_equal,
    )

    for i in range(retries):
        response = await taxi_grocery_market_gw.post(
            '/processing/v1/order/v1/event',
            json={'order_id': order_id, 'order_state': order_state},
        )
        assert response.status == 200
        assert mock_market_utils.api_event_add_called == (i + 1)


@GROCERY_MARKET_GW_PUSH_TEMPLATES_CONFIG
@ENABLE_SEND_PUSHES
async def test_market_utils_400_error(
        taxi_grocery_market_gw, grocery_order_log, mock_market_utils,
):
    order_id = 'some_order_id'
    yandex_uid = '4065912996'
    order_state = 'delivering'

    grocery_order_log.add_order(
        yandex_uid=yandex_uid,
        order_id=order_id,
        status=order_state,
        items=[],
        price='0',
    )

    mock_market_utils.check_api_add_request(
        check_request_body=_get_expected_market_utils_request(
            yandex_uid=yandex_uid, order_id=order_id,
        ),
        response_code=400,
    )

    response = await taxi_grocery_market_gw.post(
        '/processing/v1/order/v1/event',
        json={'order_id': order_id, 'order_state': order_state},
    )
    assert response.status == 200
    assert mock_market_utils.api_event_add_called == 1
