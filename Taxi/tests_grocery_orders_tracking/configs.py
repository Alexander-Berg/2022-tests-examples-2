import pytest


FORMATTER_CONFIGS = pytest.mark.config(
    GROCERY_LOCALIZATION_GROCERY_LOCALIZATIONS_KEYSET='grocery_localizations',
    GROCERY_LOCALIZATION_CURRENCIES_KEYSET='currencies',
    GROCERY_LOCALIZATION_CURRENCY_FORMAT={
        '__default__': {'precision': 2, 'rounding': '0.01'},
        'RUB': {'precision': 2, 'rounding': '0.01'},
        'GBP': {'precision': 2, 'rounding': '0.01'},
        'ILS': {'precision': 2, 'rounding': '0.01'},
    },
)

TRANSLATIONS_MARK = pytest.mark.translations(
    grocery_localizations={
        'decimal_separator': {'ru': ',', 'en': '.', 'fr': ',', 'he': '.'},
        'price_with_sign.default': {
            'ru': '$VALUE$$SIGN$',
            'en': '$VALUE$$SIGN$',
            'fr': '$VALUE$$SIGN$',
            'he': '$VALUE$$SIGN$',
        },
        'price_with_sign.gbp': {
            'ru': '$SIGN$$VALUE$',
            'en': '$SIGN$$VALUE$',
            'fr': '$SIGN$$VALUE$',
            'he': '$SIGN$$VALUE$',
        },
    },
    currencies={
        'currency_sign.eur': {'ru': '€', 'en': '€', 'fr': '€', 'he': '€'},
        'currency_sign.gbp': {'ru': '£', 'en': '£', 'fr': '£', 'he': '£'},
        'currency_sign.ils': {'ru': '₪', 'en': '₪', 'fr': '₪', 'he': '₪'},
        'currency_sign.rub': {'ru': '₽', 'en': '₽', 'fr': '₽', 'he': '₽'},
        'currency_sign.zar': {'ru': 'R', 'en': 'R', 'fr': 'R', 'he': 'R'},
    },
)

USE_DYNAMIC_DELIVERY_ETA = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'use_dynamic_delivery_eta': True},
        },
    ],
    is_config=True,
)

ASSEMBLING_ETA = 5
DISPATCH_GENERAL_CONFIG = pytest.mark.experiments3(
    name='grocery_orders_dispatch_general',
    consumers=['grocery-orders/dispatch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'assembling_eta': ASSEMBLING_ETA,
                'cancel_minutes_threshold': 4,
            },
        },
    ],
    is_config=True,
)

DEFAULT_COLOR = '#RRGGBB'
DEFAULT_LINK = 'https://random.org'
DEFAULT_BUTTON = {
    'action': 'close',
    'deeplink': 'deeplink://somewhere',
    'text_key': 'default_button_text_key',
    'text_color': DEFAULT_COLOR,
    'background_color': DEFAULT_COLOR,
}
DEFAULT_MODAL = {
    'text_key': 'default_modal_text_key',
    'title_key': 'default_modal_title_key',
    'picture_link': DEFAULT_LINK,
    'text_color': DEFAULT_COLOR,
    'background_color': DEFAULT_COLOR,
    'buttons_options': [DEFAULT_BUTTON],
    'use_full_screen': False,
}
PROMOCODE_MODAL = {
    'text_key': 'promocode_modal_text_key',
    'title_key': 'promocode_modal_title_key',
    'picture_link': DEFAULT_LINK,
    'text_color': DEFAULT_COLOR,
    'background_color': DEFAULT_COLOR,
    'buttons_options': [DEFAULT_BUTTON],
}
FIXED_VOUCHER_MODAL = {
    'text_key': 'promocode_modal_fixed_text_key',
    'title_key': 'promocode_modal_fixed_title_key',
    'picture_link': DEFAULT_LINK,
    'text_color': DEFAULT_COLOR,
    'background_color': DEFAULT_COLOR,
    'buttons_options': [DEFAULT_BUTTON],
}
COMPENSATION_MODAL = {
    'text_key': 'compensation_modal_text_key',
    'title_key': 'compensation_modal_title_key',
    'picture_link': DEFAULT_LINK,
    'text_color': DEFAULT_COLOR,
    'background_color': DEFAULT_COLOR,
    'buttons_options': [DEFAULT_BUTTON],
}

MAPPED_TANKER_KEY = 'mapped_tanker_key'
RUS_CARD_MAPPED_TANKER_KEY = 'rus_card_mapped_tanker_key'
PAYMENTS_CLIENT_MAPPINGS_EXP = pytest.mark.experiments3(
    name='grocery_payments_client_mappings',
    consumers=['grocery-orders/payments_client_mappings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'RUS card',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'RUS',
                                'arg_name': 'country_iso3',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 'card',
                                'arg_name': 'payment_method_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 'not_enough_funds',
                                'arg_name': 'payment_error_code',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
            },
            'value': {'error_code': RUS_CARD_MAPPED_TANKER_KEY},
        },
    ],
    default_value={'error_code': MAPPED_TANKER_KEY},
    is_config=True,
)

TRACKING_PAYMENTS_ERROR = pytest.mark.experiments3(
    name='grocery_tracking_payment_errors_enabled',
    consumers=['grocery-orders/submit'],
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

CRM_INFORMERS_ENABLED = pytest.mark.experiments3(
    name='grocery_orders_tracking_enable_crm',
    consumers=['grocery-orders/submit'],
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

FEEDBACK_ENABLED = pytest.mark.experiments3(
    name='grocery_products_feedback_enabled',
    consumers=['grocery-orders/submit'],
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

FEEDBACK_DISABLED = pytest.mark.experiments3(
    name='grocery_products_feedback_enabled',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': False},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)

TRACKING_GAME_ENABLED = pytest.mark.experiments3(
    name='grocery_tracking_game_reward_enabled',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Disable for tristero',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'order_flow_version',
                    'arg_type': 'string',
                    'value': 'tristero_flow_v1',
                },
            },
            'value': {'enabled': False},
        },
        {
            'title': 'Other always enabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)


def tracking_informers_config(experiments3, late_order_modal=None):
    if late_order_modal is None:
        late_order_modal = PROMOCODE_MODAL
    return experiments3.add_config(
        name='grocery_orders_tracking_informers_options',
        consumers=['grocery-orders/submit'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'long_delivery_options': {
                        'priority': 2,
                        'text_key': 'informer_long_delivery',
                        'picture_link': DEFAULT_LINK,
                        'text_color': DEFAULT_COLOR,
                        'background_color': DEFAULT_COLOR,
                        'modal_options': DEFAULT_MODAL,
                        'extra_data': {'additional_text': 'More text'},
                    },
                    'long_delivery_promocode_options': {
                        'priority': 3,
                        'text_key': 'informer_long_delivery_promocode',
                        'picture_link': DEFAULT_LINK,
                        'text_color': DEFAULT_COLOR,
                        'background_color': DEFAULT_COLOR,
                        'modal_options': PROMOCODE_MODAL,
                    },
                    'long_courier_search_options': {
                        'priority': 1,
                        'text_key': 'informer_long_courier_search',
                        'picture_link': DEFAULT_LINK,
                        'text_color': DEFAULT_COLOR,
                        'background_color': DEFAULT_COLOR,
                        'modal_options': DEFAULT_MODAL,
                        'extra_data': {'additional_text': 'More text'},
                    },
                    'long_courier_search_promocode_options': {
                        'priority': 4,
                        'text_key': 'informer_long_courier_search_promocode',
                        'picture_link': DEFAULT_LINK,
                        'text_color': DEFAULT_COLOR,
                        'background_color': DEFAULT_COLOR,
                        'modal_options': PROMOCODE_MODAL,
                    },
                    'late_order_promocode_options': {
                        'priority': 5,
                        'text_key': 'informer_late_order_promocode',
                        'picture_link': DEFAULT_LINK,
                        'text_color': DEFAULT_COLOR,
                        'background_color': DEFAULT_COLOR,
                        'modal_options': late_order_modal,
                    },
                    'compensation_options': {
                        'priority': 5,
                        'text_key': 'informer_compensation_text',
                        'picture_link': DEFAULT_LINK,
                        'text_color': DEFAULT_COLOR,
                        'background_color': DEFAULT_COLOR,
                        'modal_options': COMPENSATION_MODAL,
                    },
                    'custom_options': {
                        'priority': 1,
                        'text_key': 'informer_test',
                    },
                },
            },
        ],
    )


EDIT_ADDRESS = pytest.mark.experiments3(
    name='grocery_orders_enable_edit_address',
    consumers=['grocery-orders/submit'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'enabled': True,
                'statuses': ['created', 'assembling', 'assembled'],
            },
        },
    ],
    default_value={},
    is_config=True,
)
