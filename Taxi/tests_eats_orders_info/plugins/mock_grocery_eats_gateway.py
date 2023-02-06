# pylint: disable=invalid-name

import pytest

YA_UID = '3456723'
RESPONSE_ORDERS = [
    {
        'address': {
            'city': None,
            'house': '',
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'street': '',
        },
        'awaiting_payment': False,
        'can_contact_us': True,
        'cancelable': False,
        'cart': {
            'available_time_picker': [],
            'country': None,
            'delivery_date_time': None,
            'delivery_fee': 0,
            'delivery_fee_rational': '0',
            'delivery_time': None,
            'discount': 0,
            'discount_promo': 0,
            'discount_promo_rational': '0',
            'discount_rational': '0',
            'items': [],
            'place': {
                'available_payment_methods': [],
                'address': {
                    'city': '',
                    'house': '',
                    'location': {'latitude': 0.0, 'longitude': 0.0},
                    'street': '',
                },
                'is_store': False,
                'id': '-1',
                'name': '',
                'slug': '',
                'market': False,
            },
            'place_slug': '',
            'promo_items': [],
            'promo_notification': {
                'description': '',
                'items': [],
                'name': '',
                'picture_uri': '',
            },
            'promocode': None,
            'promos': [],
            'requirements': {
                'next_delivery_threshold': None,
                'sum_to_free_delivery': None,
                'sum_to_min_order': None,
            },
            'subtotal': 123,
            'subtotal_rational': '123',
            'surge': {
                'delivery_fee': None,
                'description': None,
                'message': None,
                'title': None,
            },
            'total': 123,
            'total_rational': '123',
            'updated_at': '2021-01-01 01:00:00',
        },
        'client_app': 'native',
        'comment': '',
        'courier': None,
        'created_at': '2020-12-31 21:00:00',
        'currency': {'code': 'RUB', 'sign': '₽'},
        'feedback_status': '',
        'has_feedback': False,
        'id': '11111222223333344444555556666677-grocery',
        'order_nr': '11111222223333344444555556666677-grocery',
        'payment_status': {'id': 2, 'title': 'оплачен', 'type': 1},
        'persons_quantity': 0,
        'phone_number': '',
        'place': {
            'address': {
                'city': '',
                'house': '',
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'street': '',
            },
            'business_hours': [],
            'business_hours_sliced': [],
            'categories': [],
            'delivery_conditions': None,
            'delivery_cost_thresholds': [],
            'description': None,
            'enabled': False,
            'footer_description': None,
            'id': -1,
            'is_new': False,
            'is_promo_available': False,
            'market': False,
            'minimal_order_price': 0,
            'name': '',
            'picture': '',
            'price_category': {'id': 1, 'name': '₽', 'value': 0},
            'rating': 1.0,
            'resized_picture': '',
            'slug': '',
        },
        'service': 'grocery',
        'shipping_type': 'pickup',
        'status': {
            'date': '2020-12-31 22:00:00',
            'id': 4,
            'title': 'доставлен',
        },
        'without_callback': True,
    },
]
RESPONSE_ORDER = {
    'courier_phone_id': '',
    'created_at': '2021-01-01T00:05:00',
    'currency': {
        'code': 'RUB',
        'sign': '₽',
        'template': '$VALUE$$SIGN$$CURRENCY$',
    },
    'delivery_address': {
        'city': '',
        'house': '10',
        'location': {'latitude': 0.0, 'longitude': 0.0},
        'short': 'some street, 10',
        'street': 'some street',
    },
    'delivery_cost_for_customer': '0',
    'delivery_point': {'latitude': 0.0, 'longitude': 0.0},
    'diff': {
        'add': [],
        'no_changes': [
            {
                'cost_for_customer': '200',
                'count': 1,
                'id': '-1',
                'images': [{'resized_url_pattern': 'url/image_1/{w}x{h}.jpg'}],
                'name': 'kakao',
            },
            {
                'cost_for_customer': '210',
                'count': 1,
                'id': '-1',
                'images': [{'resized_url_pattern': 'url/image_2.jpg'}],
                'name': 'fish',
            },
            {
                'cost_for_customer': '10',
                'count': 1,
                'id': '-1',
                'images': [{'resized_url_pattern': 'url/image_3.jpg'}],
                'name': 'cheese',
            },
        ],
        'remove': [],
        'replace': [],
        'update': [],
    },
    'final_cost_for_customer': '0',
    'forwarded_courier_phone': '',
    'id': 'order_1',
    'order_nr': 'order_1',
    'order_refund_amount': '0',
    'original_cost_for_customer': '0',
    'original_items': [
        {
            'cost_for_customer': '200',
            'count': 1,
            'id': '-1',
            'images': [{'resized_url_pattern': 'url/image_1.jpg'}],
            'name': 'kakao',
        },
        {
            'cost_for_customer': '210',
            'count': 1,
            'id': '-1',
            'images': [{'resized_url_pattern': 'url/image_2.jpg'}],
            'name': 'fish',
        },
        {
            'cost_for_customer': '10',
            'count': 1,
            'id': '-1',
            'images': [{'resized_url_pattern': 'url/image_3.jpg'}],
            'name': 'cheese',
        },
    ],
    'original_total_cost_for_customer': '0',
    'place': {
        'address': {
            'city': '',
            'house': '',
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'street': '',
        },
        'id': '-1',
        'name': '',
        'slug': '',
    },
    'receipts': [
        {
            'receipt_url': 'receipt_url',
            'title': 'receipt_title',
            'receipt_type': 'refund_receipt',
            'creation_timestamp': '2021-11-22T15:33:00+03:00',
        },
    ],
    'show_feedback_button': False,
    'status_for_customer': 4,
    'tips': '0',
    'total_cost_for_customer': '0',
    'can_be_removed': True,
}


@pytest.fixture(name='grocery', autouse=False)
def mock_grocery(mockserver):
    @mockserver.json_handler(
        '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/orders',
    )
    def mock_orders(request):
        if request.headers['X-Yandex-UID'] != context.yandex_uid:
            return mockserver.make_response(json=[], status=200)
        return mockserver.make_response(json=context.orders, status=200)

    class Context:
        def __init__(self):
            self.orders = RESPONSE_ORDERS
            self.yandex_uid = YA_UID

        def times_called_info(self):
            return mock_orders.times_called

        def get_orders(self):
            return self.orders

        def set_yandex_uid(self, yandex_uid):
            self.yandex_uid = yandex_uid

    context = Context()
    return context


@pytest.fixture(name='grocery_order', autouse=False)
def mock_grocery_order(mockserver):
    @mockserver.json_handler(
        '/grocery-eats-gateway/internal/grocery-eats-gateway/v1/order',
    )
    def mock_orders(request):
        if request.headers['X-Yandex-UID'] != context.yandex_uid:
            return mockserver.make_response(json=[], status=200)
        return mockserver.make_response(json=context.order, status=200)

    class Context:
        def __init__(self):
            self.order = RESPONSE_ORDER
            self.yandex_uid = YA_UID

        def times_called_info(self):
            return mock_orders.times_called

        def get_order(self):
            return self.order

        def set_yandex_uid(self, yandex_uid):
            self.yandex_uid = yandex_uid

    context = Context()
    return context
