DEFAULT_HEADER = {
    'X-Yandex-UID': '999',
    'X-YaTaxi-UserId': 'test_user_id_xxx',
    'X-YaTaxi-PhoneId': 'phone_id',
    'X-AppMetrica-DeviceId': 'device_id',
    'X-Ya-User-Ticket': 'user_ticket',
}

EATS_ORDERS = [
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
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'isAsap': True,
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'shippingType': 'delivery',
        },
        'place': {
            'name': 'Mc Donalds',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'address': 'улица Льва Толстого, 14Ас6',
            'locationLink': 'http://example.com',
            'comment': 'string',
        },
        'courier': {
            'name': 'Albert',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'isHardOfHearing': True,
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
        'createdAt': '2018-10-01T17:00:00Z',
        'payment': {'status': 'payment.processing', 'errorMessage': 'string'},
        'service': 'grocery',
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
    {
        'status': 'order.created',
        'title': 'string',
        'description': 'string',
        'eta': 0,
        'deliveryDate': '2020-06-01T13:15:43Z',
        'checkAfter': 15,
        'order': {
            'orderNr': '8dcba798aad9448babfce6cfa3d0bce2-grocery',
            'status': {'id': 0, 'date': '2018-10-01T17:00:00+0300'},
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'isAsap': True,
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'shippingType': 'delivery',
        },
        'place': {
            'name': 'Mc Donalds',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'address': 'улица Льва Толстого, 14Ас6',
            'locationLink': 'http://example.com',
            'comment': 'string',
        },
        'courier': {
            'name': 'Albert',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'isHardOfHearing': True,
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
        'createdAt': '2018-10-01T17:00:00Z',
        'payment': {'status': 'payment.processing', 'errorMessage': 'string'},
        'service': 'grocery',
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
]


EATS_ORDERS_THAT_WERE_CANCELED_LONG_AGO = [
    {
        'status': 'order.cancel',
        'title': 'string',
        'description': 'string',
        'eta': 0,
        'deliveryDate': '2020-06-01T13:15:43Z',
        'checkAfter': 15,
        'order': {
            'orderNr': '777777-888888',
            'status': {'id': 0, 'date': '2018-10-01T17:00:00+0300'},
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'isAsap': True,
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'shippingType': 'delivery',
        },
        'place': {
            'name': 'Mc Donalds',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'address': 'улица Льва Толстого, 14Ас6',
            'locationLink': 'http://example.com',
            'comment': 'string',
        },
        'courier': {
            'name': 'Albert',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'isHardOfHearing': True,
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
        'createdAt': '2018-10-01T17:00:00Z',
        'payment': {'status': 'payment.processing', 'errorMessage': 'string'},
        'service': 'grocery',
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
]

GROCERY_ORDERS = [
    {
        'actions': [{'type': 'cancel'}],
        'courier_info': {},
        'id': '9dcba798aad9448babfce6cfa3d0bce3-grocery',
        'short_order_id': 'some_short_id',
        'payment_status': 'success',
        'status': 'assembling',
        'cart_id': '00000000-0000-0000-0000-000000000000',
        'location': [1.0, 2.0],
        'depot_location': [2.0, 1.0],
        'delivery_type': 'courier',
        'address': {'place_id': 'some_place_id'},
    },
    {
        'actions': [{'type': 'cancel'}],
        'courier_info': {'transport_type': 'rover'},
        'id': '9dcba798aad9448babfce6cfa3d0bce4-grocery',
        'short_order_id': 'some_short_id',
        'payment_status': 'success',
        'status': 'delivery_arrived',
        'status_updated': '2010-05-23T10:03:50+03:00',
        'cart_id': '00000000-0000-0000-0000-000000000000',
        'location': [1.0, 2.0],
        'depot_location': [2.0, 1.0],
        'delivery_type': 'rover',
        'address': {'place_id': 'some_place_id'},
    },
]

GROCERY_ORDER_RESPONSE = [
    {
        'courier': None,
        'createdAt': '2018-10-01T17:00:00Z',
        'description': 'order_collecting_description',
        'eta': None,
        'contact': {'phone': None, 'type': 'courier'},
        'order': {
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'isAsap': True,
            'location': {'latitude': 2.0, 'longitude': 1.0},
            'orderNr': '9dcba798aad9448babfce6cfa3d0bce3-grocery',
            'shippingType': 'delivery',
            'status': {'date': '2018-09-30T17:00:00Z', 'id': 0},
        },
        'place': {
            'address': '',
            'comment': None,
            'location': {'latitude': 1.0, 'longitude': 2.0},
            'locationLink': '',
            'name': '',
        },
        'service': 'grocery',
        'status': 'order.cooking',
        'title': 'order_collecting_title',
        'checkAfter': 15,
    },
    {
        'courier': None,
        'createdAt': '2018-10-01T17:00:00Z',
        'description': 'order_rover_arrived_description',
        'eta': None,
        'contact': {'phone': None, 'type': 'courier'},
        'order': {
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'isAsap': True,
            'location': {'latitude': 2.0, 'longitude': 1.0},
            'orderNr': '9dcba798aad9448babfce6cfa3d0bce4-grocery',
            'shippingType': 'delivery',
            'status': {'date': '2010-05-23T07:03:50Z', 'id': 0},
        },
        'place': {
            'address': '',
            'comment': None,
            'location': {'latitude': 1.0, 'longitude': 2.0},
            'locationLink': '',
            'name': '',
        },
        'service': 'grocery',
        'status': 'order.delivering',
        'title': 'order_rover_arrived_title',
        'checkAfter': 15,
    },
]

MERGED_ORDERS = [
    {
        'checkAfter': 15,
        'contact': {'phone': None, 'type': 'courier'},
        'courier': None,
        'createdAt': '2018-10-01T17:00:00Z',
        'description': 'order_collecting_description',
        'eta': None,
        'order': {
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'isAsap': True,
            'location': {'latitude': 2.0, 'longitude': 1.0},
            'orderNr': '9dcba798aad9448babfce6cfa3d0bce3-grocery',
            'shippingType': 'delivery',
            'status': {'date': '2018-09-30T17:00:00Z', 'id': 0},
        },
        'place': {
            'address': '',
            'comment': None,
            'location': {'latitude': 1.0, 'longitude': 2.0},
            'locationLink': '',
            'name': '',
        },
        'service': 'grocery',
        'status': 'order.cooking',
        'title': 'order_collecting_title',
    },
    {
        'courier': None,
        'createdAt': '2018-10-01T17:00:00Z',
        'description': 'order_rover_arrived_description',
        'eta': None,
        'contact': {'phone': None, 'type': 'courier'},
        'order': {
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'isAsap': True,
            'location': {'latitude': 2.0, 'longitude': 1.0},
            'orderNr': '9dcba798aad9448babfce6cfa3d0bce4-grocery',
            'shippingType': 'delivery',
            'status': {'date': '2010-05-23T07:03:50Z', 'id': 0},
        },
        'place': {
            'address': '',
            'comment': None,
            'location': {'latitude': 1.0, 'longitude': 2.0},
            'locationLink': '',
            'name': '',
        },
        'service': 'grocery',
        'status': 'order.delivering',
        'title': 'order_rover_arrived_title',
        'checkAfter': 15,
    },
    {
        'checkAfter': 15,
        'contact': {'phone': '+79999999999', 'type': 'courier'},
        'courier': {
            'isHardOfHearing': True,
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'name': 'Albert',
            'placemark': {
                'type': 'image_tag',
                'imageTag': 'grocery_courier',
                'anchor': [0.5, 0.5],
                'canRotate': True,
            },
        },
        'createdAt': '2018-10-01T17:00:00Z',
        'deliveryDate': '2020-06-01T13:15:43Z',
        'description': 'string',
        'eta': 0,
        'order': {
            'deliveryTime': '2018-10-01T17:00:00Z',
            'deliveryType': 'native',
            'isAsap': True,
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'orderNr': '777777-888888',
            'shippingType': 'delivery',
            'status': {'date': '2018-10-01T17:00:00+0300', 'id': 0},
        },
        'payment': {'errorMessage': 'string', 'status': 'payment.processing'},
        'place': {
            'address': 'улица Льва Толстого, 14Ас6',
            'comment': 'string',
            'location': {'latitude': 55.736473, 'longitude': 37.640632},
            'locationLink': 'http://example.com',
            'name': 'Mc Donalds',
        },
        'service': 'grocery',
        'status': 'order.created',
        'title': 'string',
    },
]

MARKET_ORDERS = [
    {
        'id': '123',
        'items': [
            {
                'id': 'food',
                'count': 1,
                'price': {'value': 32000, 'currency': 'RUB'},
                'title': 'Чипсы',
                'category': 'junkfood',
                'picture_url': 'http://lays.jpg',
            },
        ],
        'status': 'order.delivered',
        'substatus': 'substatus',
        'created_at': '2022-04-01T13:56:22.372+03:00',
        'status_icon': 'delivery',
        'status_text': 'Доставка',
        'status_icons': ['created', 'payed', 'delivery', 'completed'],
        'delivery_info': {'delivery_type': 'courier', 'transport_type': 'car'},
        'substatus_text': 'Сабстатус',
        'status_updated_at': '2022-04-01T14:56:22.372+03:00',
        'completion_datetime_to': '2022-04-01T18:56:22.372+03:00',
        'completion_datetime_from': '2022-04-01T17:56:22.372+03:00',
    },
]

MARKET_RESPONSE = {
    'results': [
        {
            'handler': 'resolveGoOrdersTrackingInfo',
            'result': {'orders': MARKET_ORDERS},
        },
    ],
}

TRACKING_RESPONSE_WITH_MARKET_ORDERS = {
    'payload': {
        'trackedOrders': [
            {
                'status': 'order.delivered',
                'rawStatus': 'order.delivered:substatus',
                'title': 'Доставка',
                'description': 'Сабстатус',
                'eta': None,
                'deliveryDate': '2022-04-01T15:56:22Z',
                'checkAfter': 15,
                'order': {
                    'orderNr': '123',
                    'status': {'id': 0, 'date': '2022-04-01T11:56:22Z'},
                    'location': {'latitude': 0.0, 'longitude': 0.0},
                    'isAsap': False,
                    'deliveryTime': '2022-04-01T15:56:22Z',
                    'deliveryType': 'native',
                    'shippingType': '',
                },
                'place': {
                    'name': '',
                    'location': {'latitude': 0.0, 'longitude': 0.0},
                    'address': '',
                    'locationLink': '',
                    'comment': None,
                },
                'courier': None,
                'contact': {'type': '', 'phone': None},
                'createdAt': '2022-04-01T10:56:22Z',
                'service': 'market',
                'orderCard': {
                    'header': {
                        'background': {'color': '#BFBFBF'},
                        'iconTag': 'car_icon',
                        'text': {
                            'items': [
                                {
                                    'type': 'text',
                                    'font_size': 14,
                                    'color': '#000000',
                                    'text': 'Доставка на машине',
                                },
                            ],
                        },
                    },
                    'stateTimeline': {
                        'progressCount': 3,
                        'accessibilityText': 'Доставка',
                        'backgroundColor': '#DFDFDF',
                        'items': [
                            {
                                'iconTag': 'created_icon',
                                'activeColor': '#AFAFA1',
                            },
                            {
                                'iconTag': 'payed_icon',
                                'activeColor': '#AFAFA2',
                            },
                            {
                                'iconTag': 'delivery_icon',
                                'activeColor': '#AFAFA3',
                            },
                            {
                                'iconTag': 'completed_icon',
                                'activeColor': '#AFAFA4',
                            },
                        ],
                    },
                },
            },
        ],
    },
    'meta': {'count': 1, 'checkAfter': 15},
}
