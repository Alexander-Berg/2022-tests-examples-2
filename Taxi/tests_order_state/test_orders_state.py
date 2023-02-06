import pytest

DEFAULT_HEADER = {'X-Yandex-UID': '999', 'X-YaTaxi-UserId': 'test_user_id_xxx'}
DEFAULT_TRACKING_RESPONSE = {
    'payload': {
        'trackedOrders': [
            {
                'status': 'order.created',
                'title': 'string',
                'description': 'string',
                'eta': 0,
                'deliveryDate': '2020-06-01T13:15:43Z',
                'checkAfter': 15,
                'order': {
                    'orderNr': '777777-888888',
                    'status': {'id': 0, 'date': '2018-10-01T17:00:00+0300'},
                    'location': {
                        'latitude': 55.736473,
                        'longitude': 37.640632,
                    },
                    'isAsap': True,
                    'deliveryTime': '2018-10-01T13:10:00+0300',
                    'deliveryType': 'native',
                    'shippingType': 'delivery',
                },
                'place': {
                    'name': 'Mc Donalds',
                    'location': {
                        'latitude': 55.736473,
                        'longitude': 37.640632,
                    },
                    'address': 'улица Льва Толстого, 14Ас6',
                    'locationLink': 'http://example.com',
                    'comment': 'string',
                },
                'courier': {
                    'name': 'Albert',
                    'location': {
                        'latitude': 55.736473,
                        'longitude': 37.640632,
                    },
                    'isHardOfHearing': False,
                },
                'contact': {'type': 'courier', 'phone': '+79999999999'},
                'contacts': [
                    {
                        'type': 'place',
                        'phone': '+79999999999,1234',
                        'title': 'Позвонить в ресторан',
                    },
                ],
                'time': 2,
                'createdAt': '2018-10-01T13:10:00+0300',
                'payment': {
                    'status': 'payment.processing',
                    'errorMessage': 'string',
                },
                'service': 'grocery',
                'clientApp': 'native',
                'actions': [
                    {
                        'type': 'contact_us',
                        'title': 'string',
                        'payload': {'phone': 'string'},
                        'actions': [],
                    },
                ],
                'statuses': [
                    {
                        'status': 'pending',
                        'uri': 'string',
                        'payload': {
                            'eta': {'count': 'string', 'units': 'string'},
                            'has_animation': True,
                        },
                    },
                ],
            },
        ],
    },
    'meta': {'count': 0, 'checkAfter': 15},
}
TAXI_ACTIVE_ORDERS = {
    'orders': [
        {
            'orderid': '2d85ee604c2c1c0dbebbef62e5d536c0',
            'status': 'transporting',
            'due': '2020-07-08T07:10:00+0000',
            'service_level': 0,
            'pending_changes': [],
        },
        {
            'orderid': 'a81f1f5e57e76605ae1ff32e96b60522',
            'status': 'transporting',
            'due': '2020-07-08T07:36:00+0000',
            'service_level': 0,
            'pending_changes': [],
        },
    ],
    'orders_state': {
        'orders': [
            {
                'orderid': '2d85ee604c2c1c0dbebbef62e5d536c0',
                'status': 'transporting',
            },
            {
                'orderid': 'a81f1f5e57e76605ae1ff32e96b60522',
                'status': 'transporting',
            },
        ],
    },
}


def _validate_answer_tags(response):
    response_orders = response['orders']
    for order in response_orders:
        order_service = order['service']
        if order_service in ['grocery', 'eats']:
            tag_key = 'eats_tracking'
        else:
            tag_key = 'taxiontheway'
        value = order['tags'].pop(tag_key, None)
        assert value, (
            'invalid tag key "{}" '
            'for order with service "{}" for order {}'.format(
                tag_key, order_service, order['orderid'],
            )
        )
        tags = order.pop('tags')
        assert tags == {}, (
            'some unexpected tags forgotten in {} for order {}'.format(
                tags, order['orderid'],
            )
        )


@pytest.mark.config(
    ORDER_STATE_SERVICE_SETTINGS={
        'taxi': {'enabled': True},
        'eats': {'enabled': True},
    },
)
@pytest.mark.experiments3(filename='exp3_polling_policy.json')
async def test_internal_orders_state(taxi_order_state, mockserver):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return DEFAULT_TRACKING_RESPONSE

    raw_response = await taxi_order_state.post(
        '/v1/orders/state',
        json={
            'taxi': {
                'active_orders': TAXI_ACTIVE_ORDERS,
                'can_make_more_orders': 'allowed',
            },
        },
        headers=DEFAULT_HEADER,
    )
    assert raw_response.status == 200, raw_response.text
    assert mock_eda_tracking.times_called == 1
    response = raw_response.json()

    assert response['allowed_changes'] == [
        {'can_make_more_orders': 'allowed', 'service': 'taxi'},
        {'can_make_more_orders': 'allowed', 'service': 'grocery'},
        {'can_make_more_orders': 'allowed', 'service': 'eats'},
        {'can_make_more_orders': 'allowed', 'service': 'shop'},
        {'can_make_more_orders': 'allowed', 'service': 'pharmacy'},
    ]

    _validate_answer_tags(response)
    assert response['orders'] == [
        {
            'need_request': ['taxiontheway'],
            'orderid': '2d85ee604c2c1c0dbebbef62e5d536c0',
            'service': 'taxi',
            'status': 'transporting',
            'update_status': 'actual',
        },
        {
            'need_request': ['taxiontheway'],
            'orderid': 'a81f1f5e57e76605ae1ff32e96b60522',
            'service': 'taxi',
            'status': 'transporting',
            'update_status': 'actual',
        },
        {
            'need_request': ['eats_tracking'],
            'orderid': '777777-888888',
            'service': 'grocery',
            'status': 'order.created',
            'update_status': 'actual',
        },
    ]
    assert response['polling_policy'] == [
        {
            'service': 'grocery',
            'part_name': 'tracking',
            'url': '/4.0/tracking',
            'fields': ['field1', 'field2'],
            'polling_type': 'polling_type_1',
            'part_type': 'eats_tracking',
            'priority': 1,
        },
        {
            'service': 'taxi',
            'part_name': 'taxiontheway',
            'url': '/4.0/taxiontheway',
            'fields': ['field1', 'field2'],
            'polling_type': 'polling_type_2',
            'part_type': 'taxiontheway',
            'priority': 1,
        },
    ]


@pytest.mark.config(
    ORDER_STATE_SERVICE_SETTINGS={
        'taxi': {'enabled': True},
        'eats': {'enabled': True},
    },
)
async def test_orders_state(taxi_order_state):
    raw_response = await taxi_order_state.post(
        '/4.0/mlutp/v1/orders/state',
        json={
            'supported_services': ['taxi', 'eats', 'grocery'],
            'known_orders': [
                {
                    'orderid': 'order1',
                    'tags': {
                        'fast_info': 'encoded_tag',
                        'part2': 'encoded_tag',
                    },
                    'service': 'taxi',
                    'status': 'searching',
                },
                {
                    'orderid': 'order2',
                    'tags': {'full_info': 'encoded_tag'},
                    'service': 'eats',
                    'status': 'cooking',
                    'some_field': 'some_value',
                },
            ],
        },
        headers=DEFAULT_HEADER,
    )
    assert raw_response.status == 200, raw_response.text
    response = raw_response.json()
    _validate_answer_tags(response)
    assert response == {
        'allowed_changes': [
            {'can_make_more_orders': 'not_modified', 'service': 'taxi'},
            {'can_make_more_orders': 'not_modified', 'service': 'eats'},
            {'can_make_more_orders': 'not_modified', 'service': 'grocery'},
        ],
        'orders': [
            {
                'need_request': ['taxiontheway'],
                'orderid': 'order1',
                'service': 'taxi',
                'status': 'searching',
                'update_status': 'actual',
            },
            {
                'need_request': ['eats_tracking'],
                'orderid': 'order2',
                'service': 'eats',
                'status': 'cooking',
                'update_status': 'actual',
            },
        ],
    }


# TODO: Rewrite it all
@pytest.mark.config(
    ORDER_STATE_SERVICE_SETTINGS={
        'taxi': {'enabled': True},
        'eats': {'enabled': True},
    },
    ORDER_STATE_SERVICE_TERMINAL_STATUSES={'taxi': ['complete']},
)
async def test_orders_state_complete(taxi_order_state):
    raw_response = await taxi_order_state.post(
        '/4.0/mlutp/v1/orders/state',
        json={
            'supported_services': ['taxi', 'eats', 'grocery'],
            'known_orders': [
                {
                    'orderid': 'order1',
                    'tags': {'taxiontheway': 'encoded_tag'},
                    'service': 'taxi',
                    'status': 'complete',
                },
                {
                    'orderid': 'order2',
                    'tags': {'full_info': 'encoded_tag'},
                    'service': 'eats',
                    'status': 'cooking',
                    'some_field': 'some_value',
                },
            ],
        },
        headers=DEFAULT_HEADER,
    )
    assert raw_response.status == 200, raw_response.text
    response = raw_response.json()
    _validate_answer_tags(response)
    assert response == {
        'allowed_changes': [
            {'can_make_more_orders': 'not_modified', 'service': 'taxi'},
            {'can_make_more_orders': 'not_modified', 'service': 'eats'},
            {'can_make_more_orders': 'not_modified', 'service': 'grocery'},
        ],
        'orders': [
            {
                'need_request': [],
                'orderid': 'order1',
                'service': 'taxi',
                'status': 'complete',
                'update_status': 'actual',
            },
            {
                'need_request': ['eats_tracking'],
                'orderid': 'order2',
                'service': 'eats',
                'status': 'cooking',
                'update_status': 'actual',
            },
        ],
    }
