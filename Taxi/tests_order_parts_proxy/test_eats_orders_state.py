DEFAULT_HEADER = {'X-Yandex-UID': '999', 'X-YaTaxi-UserId': 'test_user_id_xxx'}
DEFAULT_REQUEST = {'orders': [{'orderid': '777777-888888', 'tag': 'full'}]}
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


async def test_order_tracking(taxi_order_parts_proxy, mockserver):
    @mockserver.json_handler('/eats-tracking/v2/orders/tracking')
    def mock_eda_tracking(request):
        return DEFAULT_TRACKING_RESPONSE

    response = await taxi_order_parts_proxy.post(
        '/4.0/mlutp/v1/eats/v1/orders/state',
        json=DEFAULT_REQUEST,
        headers=DEFAULT_HEADER,
    )
    assert response.status == 200
    assert mock_eda_tracking.times_called == 1
    assert response.json() == {
        'orders': [
            {
                'courier': {
                    'is_hard_of_hearing': False,
                    'location': [37.640632, 55.736473],
                    'name': 'Albert',
                },
                'created_at': '2018-10-01T13:10:00+0300',
                'delivery_at': '2020-06-01T13:15:43+00:00',
                'description': 'string',
                'eta': 0,
                'order': {
                    'delivery_type': 'native',
                    'id': '777777-888888',
                    'is_asap': True,
                    'location': [37.640632, 55.736473],
                    'shipping_type': 'delivery',
                    'status': {'date': '2018-10-01T17:00:00+0300', 'id': 0},
                },
                'place': {
                    'address': 'улица Льва Толстого, 14Ас6',
                    'comment': 'string',
                    'location': [37.640632, 55.736473],
                    'location_link': 'http://example.com',
                    'name': 'Mc Donalds',
                },
                'service': 'grocery',
                'status': 'order.created',
                'title': 'string',
            },
        ],
    }
