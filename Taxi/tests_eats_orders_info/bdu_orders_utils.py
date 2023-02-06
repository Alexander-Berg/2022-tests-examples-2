import pytest

PLACE_ID = '222325'
PLACE_NAME = 'Магнит'
DEFAULT_ORDER_NR = '000000-000001'
YA_UID = '3456723'
SAMPLE_TIME_CONVERTED = '2021-08-06T12:42:12+00:00'
SAMPLE_TIME_CONVERTED_FOR_BDU_ORDERS = '06 Августа 15:42, 2021'
CATALOG_STORAGE_URL = (
    '/eats-catalog-storage/internal/eats-catalog-storage'
    + '/v1/places/retrieve-by-ids'
)
METAINFO_URL = '/eats-core-orders/internal-api/v1/orders/metainfo'
TRACKING_URL = (
    '/eats-orders-tracking/internal/eats-orders-tracking/'
    'v1/tracking-for-ordershistory'
)
FEEDBACK_URL = (
    '/eats-feedback/internal/eats-feedback/'
    'v1/get-feedbacks-for-orders-history'
)
RESTAPP_URL = (
    '/eats-core-restapp/v1/eats-restapp-menu/ordershistory-place-menu'
)
RETAIL_UPDATE_URL = (
    '/eats-retail-order-history/internal/'
    'retail-order-history/v1/orders-for-history'
)
REVISIONS_URL = (
    '/eats-order-revision/v1/revision/latest/customer-services/details'
)
ORIGIN_ID = 'origin_1'
ORIGIN_ID_WITH_CHANGES = 'origin_123'


def feedback_widget_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_feedback_widget',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-orders-info/bdu-order'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {
                'deeplink': 'eda.yandex://feedback/order_nr',
                'title_key': 'feedback.question',
                'title_color': [
                    {'theme': 'light', 'value': '#000001'},
                    {'theme': 'dark', 'value': '#fffffe'},
                ],
                'icons': {
                    'icons_selected': [
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-on'
                            ),
                            'theme': 'light',
                        },
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-on'
                            ),
                            'theme': 'dark',
                        },
                    ],
                    'icons_unselected': [
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-off'
                            ),
                            'theme': 'light',
                        },
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-off'
                            ),
                            'theme': 'dark',
                        },
                    ],
                },
            },
        ),
    )


def gen_general_config_clause(status):
    return {
        'color': [
            {'theme': 'light', 'value': '#000001'},
            {'theme': 'dark', 'value': '#fffffe'},
        ],
        'deeplink': 'eda.yandex://order_history?orderNr={}',
        'text_key': status,
    }


def general_widget_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_general_widget',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-orders-info/bdu-order'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'confirmed',
                'value': gen_general_config_clause('confirmed_key'),
                'predicate': {
                    'init': {
                        'arg_name': 'order_status',
                        'arg_type': 'string',
                        'value': 'confirmed',
                    },
                    'type': 'eq',
                },
            },
            {
                'title': 'finished',
                'value': gen_general_config_clause('finished_key'),
                'predicate': {
                    'init': {
                        'arg_name': 'order_status',
                        'arg_type': 'string',
                        'value': 'finished',
                    },
                    'type': 'eq',
                },
            },
            {
                'title': 'cancelled',
                'value': gen_general_config_clause('cancelled_key'),
                'predicate': {
                    'init': {
                        'arg_name': 'order_status',
                        'arg_type': 'string',
                        'value': 'cancelled',
                    },
                    'type': 'eq',
                },
            },
            {
                'title': 'taken',
                'value': gen_general_config_clause('taken_key'),
                'predicate': {
                    'init': {
                        'arg_name': 'order_status',
                        'arg_type': 'string',
                        'value': 'taken',
                    },
                    'type': 'eq',
                },
            },
        ],
        default_value=dict(gen_general_config_clause('unknown_key')),
    )


def update_pagination_config3():
    return pytest.mark.experiments3(
        name='eats_orders_info_bdu_update_and_pagination',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-orders-info/bdu-update-and-pagination'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {
                'default_limit': 10,
                'update_period': 50,
                'default_goods_items_limit': 6,
                'days_limit': 111,
            },
        ),
    )


def generate_ordershistory_orders(orders_data):
    orders = []
    for order in orders_data:
        result_order = {
            'order_id': order['order_nr'],
            'status': order['status'],
            'created_at': order['created_at'],
            'source': order['source'] if 'source' in order else 'eda',
            'delivery_location': {'lat': 1.0, 'lon': 1.0},
            'total_amount': str(order['total_cost']),
            'is_asap': True,
            'place_id': order['place_id'],
        }
        if 'order_type' in order:
            result_order['order_type'] = order['order_type']
        if 'shipping_type' in order:
            result_order['shipping_type'] = order['shipping_type']
        if 'shipping_type' in order:
            result_order['delivery_type'] = order['delivery_type']
        if 'items' in order:
            result_order['cart'] = []
            for item in order['items']:
                result_item = {
                    'place_menu_item_id': 1,
                    'name': item['name'],
                    'quantity': 1,
                }
                if 'origin_id' in item:
                    result_item['origin_id'] = item['origin_id']
                if 'parent_origin_id' in item:
                    result_item['parent_origin_id'] = item['parent_origin_id']
                result_order['cart'].append(result_item)
        orders.append(result_order)
    return orders


def generate_grocery_orders(orders_data):
    orders = []
    for order in orders_data:
        result_order = {
            'id': order['id'],
            'order_nr': order['order_nr'],
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
                'delivery_cost_thresholds': [],
                'enabled': False,
                'id': 1,
                'is_new': False,
                'is_promo_available': False,
                'market': False,
                'minimal_order_price': 0,
                'name': 'lavka',
                'picture': '',
                'price_category': {'id': 1, 'name': '₽', 'value': 0},
                'rating': 1.0,
                'resized_picture': '',
                'slug': '',
            },
            'comment': 'None',
            'created_at': order['created_at'],
            'address': {
                'city': '',
                'house': '',
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'street': '',
            },
            'awaiting_payment': False,
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
                'place': None,
                'place_slug': '',
                'promo_items': [],
                'promo_notification': {
                    'description': '',
                    'items': [],
                    'name': '',
                    'picture_uri': 'None',
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
                'total_rational': str(order['total_cost']),
                'updated_at': '2021-01-01 01:00:00',
            },
            'client_app': 'native',
            'currency': {'code': 'RUB', 'sign': '₽'},
            'feedback_status': 'wait',
            'has_feedback': False,
            'payment_status': {'id': 2, 'title': 'оплачен', 'type': 1},
            'persons_quantity': 1,
            'phone_number': '',
            'service': 'grocery',
            'shipping_type': 'pickup',
            'status': {
                'date': '2020-12-31 22:00:00',
                'id': order['status_id'],
                'title': order['status'],
            },
            'without_callback': True,
        }
        if 'items' in order:
            for item in order['items']:
                result_item = {
                    'id': 1,
                    'item_id': 2,
                    'name': item['name'],
                    'price': 100,
                    'item_options': [],
                    'quantity': 1,
                    'description': item['origin_id'],
                    'weight': '123Kg',
                    'price_rational': '100.05',
                    'quantity_rational': 1.0,
                }
                if 'image_url_template' in item:
                    result_item['image_url_template'] = item[
                        'image_url_template'
                    ]
                result_order['cart']['items'].append(result_item)

        orders.append(result_order)
    return orders


def generate_catalog_info(places_data, not_found_place_ids):
    places = []
    for place in places_data:
        places.append(
            {
                'id': int(place['id']),
                'revision_id': 1,
                'updated_at': SAMPLE_TIME_CONVERTED,
                'name': place['name'],
                'region': {
                    'id': 1,
                    'geobase_ids': [],
                    'time_zone': 'Europe/Moscow',
                },
            },
        )
    return {'places': places, 'not_found_place_ids': not_found_place_ids}


def generate_metainfo_orders(orders_data):
    orders = []
    for order in orders_data:
        result_order = {
            'order_nr': order['order_nr'],
            'location_latitude': 1.0,
            'location_longitude': 2.0,
            'city': 'city',
            'street': 'street',
            'is_asap': True,
            'place_id': PLACE_ID,  # not used
            'region_id': '1',
            'place_delivery_zone_id': '1',
            'app': 'web',
            'currency': 'RUB',
        }
        if 'shipping_type' in order:
            result_order['shipping_type'] = order['shipping_type']
        if 'bus_type' in order:
            result_order['business_type'] = order['bus_type']
        if 'status' in order:
            result_order['status'] = order['status']
        orders.append(result_order)
    return orders


def generate_tracking_orders(orders_data):
    orders = []
    for order in orders_data:
        order_widget = {
            'order_nr': order['order_nr'],
            'ordershistory_widget': {
                'deeplink': (
                    'eda.yandex://tracking/order_nr=' + order['order_nr']
                ),
                'title': 'short_title',
                'subtitle': 'short_title_for_ordershistory',
                'icons': [
                    {
                        'status': 'finished',
                        'uri': 'https://eda.yandex/s3/tracked-order/check.png',
                    },
                    {
                        'status': 'in_progress',
                        'uri': (
                            'https://eda.yandex/s3/tracked-order/cyclist.png'
                        ),
                    },
                ],
            },
        }
        orders.append(order_widget)
    return {'orders': orders}


def generate_feedbacks_orders(orders_data):
    feedbacks = []
    for order in orders_data:
        feedbacks.append(
            {
                'has_feedback': order['has_feedback'],
                'status': order['status'],
                'order_nr': order['order_nr'],
                'is_feedback_needed': order['is_feedback_needed'],
            },
        )
    return {'feedbacks': feedbacks}


def generate_bdu_orders(orders_data):
    orders = []
    for order in orders_data:
        widgets = {
            'order_nr': order['order_nr'],
            'widgets': {
                'general': {
                    'cost_value': str(order['total_cost']),
                    'currency': {
                        'code': 'RUB',
                        'sign': '₽',
                        'template': '$VALUE$ $SIGN$$CURRENCY$',
                        'text': 'руб.',
                    },
                    'date': order['created_at'],
                    'deeplink': (
                        'eda.yandex://order_history?orderNr='
                        + order['order_nr']
                    ),
                    'name': order['place_name'],
                    'status': {
                        'color': [
                            {'theme': 'light', 'value': '#000001'},
                            {'theme': 'dark', 'value': '#fffffe'},
                        ],
                        'text': order['status'],
                    },
                },
            },
            'swipe_left_actions': {
                'remove': {
                    'background': [
                        {'theme': 'light', 'value': '#FA3E2C'},
                        {'theme': 'dark', 'value': '#FA3E2C'},
                    ],
                    'swipe_text': 'Удалить',
                },
            },
        }
        if 'can_be_removed' not in order or not order['can_be_removed']:
            widgets['swipe_left_actions']['remove'][
                'cant_be_removed_reason'
            ] = 'Этот заказ нельзя удалить'

        if 'have_tracking' in order and order['have_tracking']:
            widgets['widgets']['tracking'] = {
                'deeplink': (
                    'eda.yandex://tracking/order_nr=' + order['order_nr']
                ),
                'title': 'short_title',
                'subtitle': 'short_title_for_ordershistory',
                'icons': [
                    {
                        'status': 'finished',
                        'uri': 'https://eda.yandex/s3/tracked-order/check.png',
                    },
                    {
                        'status': 'in_progress',
                        'uri': (
                            'https://eda.yandex/s3/tracked-order/cyclist.png'
                        ),
                    },
                ],
            }
        if 'show_feedback_button' in order and order['show_feedback_button']:
            widgets['widgets']['feedback'] = {
                'deeplink': 'eda.yandex://feedback/order_nr',
                'title': {
                    'color': [
                        {'theme': 'light', 'value': '#000001'},
                        {'theme': 'dark', 'value': '#fffffe'},
                    ],
                    'text': 'Как вам заказ?',
                },
                'icons': {
                    'icons_selected': [
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-on'
                            ),
                            'theme': 'light',
                        },
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-on'
                            ),
                            'theme': 'dark',
                        },
                    ],
                    'icons_unselected': [
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-off'
                            ),
                            'theme': 'light',
                        },
                        {
                            'icon': (
                                'https://eda.yandex/feedback-icon-light-off'
                            ),
                            'theme': 'dark',
                        },
                    ],
                },
            }
        if 'items' in order:
            widgets['widgets']['goods'] = {
                'items': [],
                'total_items_number': order['total_items_number'],
            }
            for item in order['items']:
                result_item = {
                    'title': item['name'],
                    'image_url_pattern': item['image_url'],
                }
                widgets['widgets']['goods']['items'].append(result_item)
        orders.append(widgets)
    return orders
