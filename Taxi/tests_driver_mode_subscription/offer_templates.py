import copy
from typing import Any
from typing import Dict
from typing import Optional


DEFAULT_ORDERS_TEMPLATE: Dict[str, Any] = {
    'model': {'title': 'offer_card.orders_title'},
    'schema': {
        'card_items': [
            {
                'data': {
                    'description': 'offer_card.orders_description',
                    'icon_type': 'passenger',
                    'subtitle': 'offer_card.orders_subtitle',
                },
                'type': 'card_header',
            },
            {'type': 'booking_info'},
            {'type': 'subscription_time_info'},
        ],
        'memo_items': [
            {'data': {'text': 'orders_memo_screen.header'}, 'type': 'header'},
            {
                'data': {'text': 'orders_memo_screen.text'},
                'type': 'multi_paragraph_text',
            },
        ],
        'screen_items': [
            {'data': {'text': 'orders_offer_screen.header'}, 'type': 'header'},
            {
                'data': {'text': 'orders_offer_screen.text'},
                'type': 'multi_paragraph_text',
            },
            {'type': 'subscription_time_info'},
        ],
    },
}

DEFAULT_GEOBOOKING_TEMPLATE: Dict[str, Any] = {
    'model': {'title': 'offer_card.geobooking.title'},
    'schema': {
        'card_items': [
            {
                'data': {'icon_type': 'passenger'},
                'type': 'geobooking_card_header',
            },
            {'type': 'booking_info'},
            {'type': 'subscription_time_info'},
        ],
        'memo_items': [{'type': 'geobooking_memo_screen'}],
        'screen_items': [{'type': 'geobooking_offer_screen'}],
    },
}

DEFAULT_DRIVER_FIX_TEMPLATE: Dict[str, Any] = {
    'model': {'title': 'offer_card.title'},
    'schema': {
        'card_items': [
            {'data': {'icon_type': 'time'}, 'type': 'driver_fix_card_header'},
            {'type': 'booking_info'},
            {'type': 'subscription_time_info'},
        ],
        'memo_items': [{'type': 'driver_fix_memo_screen'}],
        'screen_items': [{'type': 'driver_fix_offer_screen'}],
    },
}


def build_orders_template(
        card_title: str,
        card_subtitle: Optional[str],
        card_description: str,
        screen_header: str,
        screen_description: str,
        memo_header: str,
        memo_description: str,
):
    template = copy.deepcopy(DEFAULT_ORDERS_TEMPLATE)
    template['model']['title'] = card_title
    if card_subtitle:
        template['schema']['card_items'][0]['data']['subtitle'] = card_subtitle
    else:
        del template['schema']['card_items'][0]['data']['subtitle']
    template['schema']['card_items'][0]['data'][
        'description'
    ] = card_description
    template['schema']['screen_items'][0]['data']['text'] = screen_header
    template['schema']['screen_items'][1]['data']['text'] = screen_description
    template['schema']['memo_items'][0]['data']['text'] = memo_header
    template['schema']['memo_items'][1]['data']['text'] = memo_description
    return template


def build_driver_fix_template(card_title: str):
    template = copy.deepcopy(DEFAULT_DRIVER_FIX_TEMPLATE)
    template['model']['title'] = card_title
    return template


def build_geobooking_template(card_title: str):
    template = copy.deepcopy(DEFAULT_GEOBOOKING_TEMPLATE)
    template['model']['title'] = card_title
    return template


DEFAULT_CUSTOM_ORDERS_TEMPLATE = build_orders_template(
    card_title='custom_orders.offer_card.title',
    card_subtitle='custom_orders.offer_card.subtitle',
    card_description='custom_orders.offer_card.description',
    screen_header='custom_orders.offer_screen.header',
    screen_description='custom_orders.offer_screen.text',
    memo_header='custom_orders.memo_screen.header',
    memo_description='custom_orders.memo_screen.text',
)

DEFAULT_UBERDRIVER_TEMPLATE = {
    'model': {'title': 'uberdriver.offer_card.title'},
    'schema': {'card_items': [], 'memo_items': [], 'screen_items': []},
}

DEFAULT_OFFER_TEMPLATES = {
    'templates': {
        'driver_fix_template': DEFAULT_DRIVER_FIX_TEMPLATE,
        'geobooking_template': DEFAULT_GEOBOOKING_TEMPLATE,
        'orders_template': DEFAULT_ORDERS_TEMPLATE,
        'custom_orders_template': DEFAULT_CUSTOM_ORDERS_TEMPLATE,
        'uberdriver_template': DEFAULT_UBERDRIVER_TEMPLATE,
    },
}

DEFAULT_MODE_TEMPLATE_RELATIONS = {
    'by_mode_class': {},
    'by_work_mode': {
        'orders': 'orders_template',
        'driver_fix': 'driver_fix_template',
        'custom_orders': 'custom_orders_template',
        'geobooking': 'geobooking_template',
        'uberdriver': 'uberdriver_template',
    },
}
