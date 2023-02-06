import pytest

TEMPLATE_VALUE_FIRST = '$VALUE$ $SIGN$'
TEMPLATE_SIGN_FIRST = '$SIGN$ $VALUE$'
BASIC_TRANSLATIONS = pytest.mark.translations(
    grocery_referral={},
    grocery_localizations={
        'decimal_separator': {'ru': ',', 'en': '.', 'fr': ',', 'he': '.'},
        'price_with_sign.default': {
            'ru': TEMPLATE_VALUE_FIRST,
            'en': TEMPLATE_VALUE_FIRST,
            'fr': TEMPLATE_VALUE_FIRST,
            'he': TEMPLATE_VALUE_FIRST,
        },
        'price_with_sign.gbp': {
            'ru': TEMPLATE_SIGN_FIRST,
            'en': TEMPLATE_SIGN_FIRST,
            'fr': TEMPLATE_SIGN_FIRST,
            'he': TEMPLATE_SIGN_FIRST,
        },
    },
    currencies={
        'currency_sign.eur': {'ru': '€', 'en': '€', 'fr': '€', 'he': '€'},
        'currency_sign.gbp': {'ru': '£', 'en': '£', 'fr': '£', 'he': '£'},
        'currency_sign.ils': {'ru': '₪', 'en': '₪', 'fr': '₪', 'he': '₪'},
        'currency_sign.rub': {'ru': '₽', 'en': '₽', 'fr': '₽', 'he': '₽'},
    },
)

GROCERY_COUPONS_ZONE_NAME = pytest.mark.experiments3(
    name='grocery_coupons_zone_name',
    consumers=['grocery-coupons/referral', 'grocery-crm/user'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Moscow',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'zone_name': 'moscow'},
        },
    ],
    is_config=True,
)

GROCERY_REFERRAL_PAYMENT_OPTIONS = pytest.mark.experiments3(
    name='grocery_referral_payment_options',
    consumers=['grocery-coupons/referral', 'grocery-crm/user'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'For All',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'payment_options': ['card']},
        },
    ],
    is_config=True,
)

GROCERY_HELP_IS_NEAR = pytest.mark.experiments3(
    name='grocery_help_is_near',
    consumers=['grocery-orders/submit', 'grocery-crm/user'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'For All',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {
                'start_enabled': True,
                'finish_enabled': True,
                'check_subscription_enabled': True,
            },
        },
    ],
    is_config=True,
)
