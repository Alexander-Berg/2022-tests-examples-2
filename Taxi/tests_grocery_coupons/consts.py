import pytest

VALID_PROMOCODE = {
    'currency_code': 'RUB',
    'descr': 'Скидка 30% на 3 поездки',
    'details': [
        'Осталось поездок: 2',
        'Действует до: 31.12.2020',
        'Методы оплаты: «Банковская карта»',
        'Скидка не более 100 руб.',
    ],
    'format_currency': False,
    'limit': 100,
    'percent': 30,
    'valid': True,
    'value': 100,
    'series_purpose': 'support',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

VALID_FIXED_PROMOCODE = {
    'currency_code': 'RUB',
    'descr': 'Скидка 30% на 3 поездки',
    'details': [
        'Осталось поездок: 2',
        'Действует до: 31.12.2020',
        'Методы оплаты: «Банковская карта»',
        'Скидка не более 100 руб.',
    ],
    'format_currency': False,
    'limit': 100,
    'valid': True,
    'value': 100,
    'series_purpose': 'support',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

PROMO_CAN_BE_VALID = {
    'currency_code': 'RUB',
    'descr': 'Скидка 20% на 999 поездок',
    'details': ['Ошибка!\\nПромокод недействителен в вашем городе'],
    'error_code': 'ERROR_UNKNOWN',
    'format_currency': True,
    'valid': False,
    'valid_any': True,
    'value': 0,
    'series_purpose': 'marketing',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

PROMO_ERROR_INVALID_CODE = {
    'currency_code': '',
    'descr': 'Неверный промокод',
    'details': ['Неверный промокод'],
    'error_code': 'ERROR_NOT_FOUND',
    'format_currency': False,
    'valid': False,
    'valid_any': False,
    'value': 0,
    'series_purpose': 'support',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

PROMO_ERROR_INVALID_CODE_2 = {
    'currency_code': '',
    'descr': 'Неверный промокод',
    'details': ['Неверный промокод'],
    'error_code': 'ERROR_USED',
    'format_currency': False,
    'valid': False,
    'value': 0,
    'series_purpose': 'support',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

PROMO_ERROR_INVALID_CODE_3 = {
    'currency_code': '',
    'descr': 'Неверный промокод',
    'details': ['Неверный промокод'],
    'error_code': 'ERROR_CREDITCARD_REQUIRED',
    'format_currency': False,
    'valid': False,
    'value': 100,
    'series_purpose': 'support',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

PROMO_ERROR_INVALID_CODE_4 = {
    'currency_code': '',
    'descr': 'Неверный промокод',
    'details': ['Неверный промокод'],
    'error_code': 'ERROR_INVALID_CITY',
    'format_currency': False,
    'valid': False,
    'value': 0,
    'series_purpose': 'support',
    'expire_at': '2020-03-01T00:00:00+00:00',
}

COUPONS_ERROR_CODES = pytest.mark.experiments3(
    name='lavka_coupons_error_codes',
    consumers=['grocery-coupons/check'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'is_signal': False,
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {
                'not_found': ['ERROR_NOT_FOUND'],
                'already_used': ['ERROR_USED'],
                'no_payment_method': ['ERROR_CREDITCARD_REQUIRED'],
                'login_required': [],
                'external_validation_failed': ['ERROR_EXTERNAL_VALIDATION'],
                'invalid_location': ['ERROR_INVALID_CITY'],
                'invalid_app': ['ERROR_BAD_APP_VERSION'],
                'bad_timing': ['ERROR_TOO_LATE'],
            },
        },
    ],
    is_config=True,
)

MOSCOW_ZONE_NAME = 'moscow'
SPB_ZONE_NAME = 'spb'

GROCERY_COUPONS_ZONE_NAME = pytest.mark.experiments3(
    name='grocery_coupons_zone_name',
    consumers=['grocery-coupons/referral'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'MSK',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 213,
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                },
            },
            'value': {'zone_name': MOSCOW_ZONE_NAME},
        },
        {
            'title': 'SPB',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 2,
                    'arg_name': 'region_id',
                    'arg_type': 'int',
                },
            },
            'value': {'zone_name': SPB_ZONE_NAME},
        },
    ],
    default_value={'zone_name': 'moscow'},
    is_config=True,
)

GROCERY_COUPONS_SERIES_WITH_TAGS = pytest.mark.experiments3(
    name='grocery_coupons_series_with_tags',
    consumers=['grocery-coupons/list'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'coupons': ['promotag1']},
        },
    ],
    is_config=True,
)

GROCERY_COUPONS_FATAL_ERRORS = pytest.mark.experiments3(
    name='grocery_coupons_fatal_errors',
    consumers=['grocery-coupons/list'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {
                'coupons_errors': ['ERROR_USED', 'ERROR_NOT_FOUND'],
                'grocery_coupons_errors': ['ERROR_ORDERS_FIRST_LIMIT_REACHED'],
            },
        },
    ],
    is_config=True,
)

COMMON_ERROR = 'Не удалось применить данный промокод'
NO_MIN_CART_COST_ERROR = 'Стоимость корзины меньше, чем {}'
TAG_FIRST_LIMIT_REACHED_ERROR = (
    'Лимит использований ({}) промокода был достигнут'
)
ORDERS_FIRST_LIMIT_REACHED_ERROR = (
    'Промокод действует только на первые {} заказа'
)
CUSTOM_NO_REQUIRED_ERROR = 'Для этого промокода не хватает товаров бренда Х'
NO_REQUIRED_ITEM_ERROR = 'Для этого промокода не хватает товаров "{}"'
NO_ANY_OF_REQUIRED_ITEMS_ERROR = (
    'Нужен хотя бы один товар из необходимых для применения промокода'
)
NO_ANY_OF_REQUIRED_CATEGORY_ERROR = (
    'Нужен хотя бы один товар из необходимой категории'
)
NO_REQUIRED_CATEGORY_ERROR = (
    'Для этого промокода не хватает товаров из категории "{}"'
)
REGION_ID_ERROR = 'Этот промокод не действует в регионах {}'
CART_WAS_NOT_MATCHED_ERROR = 'В корзине нет необходимых товаров'
COFFEE_MATCHING_ERROR = 'Промокод действует на заказы с кофе'
USER_TAG_WAS_NOT_MATCHED = 'К сожалению, вы не можете применить этот промокод'

CART_ID = '00000000-0000-0000-0000-d98013100500'
CART_VERSION = 1
NOW = '2020-01-05T15:02:00+0000'
NOW_TIME = '2020-05-25T17:43:45+00:00'

ERROR_CODE_COMMON_ERROR = 'ERROR_UNKNOWN_ERROR'
ERROR_CODE_NO_MIN_CART_COST = 'ERROR_LESS_THAN_MIN_CART_COST'
ERROR_CODE_TAG_FIRST_LIMIT_REACHED = 'ERROR_TAG_FIRST_LIMIT_REACHED'
ERROR_CODE_ORDERS_FIRST_LIMIT_REACHED = 'ERROR_ORDERS_FIRST_LIMIT_REACHED'
ERROR_CODE_NO_REQUIRED_ITEM = 'ERROR_NO_REQUIRED_ITEM'
ERROR_CODE_NO_REQUIRED_CATEGORY = 'ERROR_NO_REQUIRED_CATEGORY'
ERROR_CODE_NO_ANY_OF_REQUIRED_ITEM = 'ERROR_NO_ANY_OF_REQUIRED_ITEM'
ERROR_CODE_NO_ANY_OF_REQUIRED_CATEGORY = 'ERROR_NO_ANY_OF_REQUIRED_CATEGORY'
ERROR_CODE_REGION_ID = 'ERROR_OTHER_REGION_ID'
ERROR_CODE_CART_WAS_NOT_MATCHED = 'ERROR_CART_WAS_NOT_MATCHED'
ERROR_CODE_USER_TAG_WAS_NOT_MATCHED = 'ERROR_USER_TAG_WAS_NOT_MATCHED'
ERROR_CODE_NO_YANDEX_UID = 'ERROR_NO_YANDEX_UID'
ERROR_CODE_UNKNOWN_ORDERS_COUNT = 'ERROR_UNKNOWN_ORDERS_COUNT'
ERROR_CODE_UNKNOWN_USAGE_COUNT = 'ERROR_UNKNOWN_USAGE_COUNT'

GROCERY_MARKETING_TAG_CHECK = pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_coupons_check_first_limit': {
            'tag': 'total_paid_orders_count',
        },
    },
)

GROCERY_COUPONS_BRAND_NAMES = pytest.mark.experiments3(
    name='grocery_coupons_brand_names',
    consumers=['grocery-coupons/list'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Deli App',
            'predicate': {
                'init': {
                    'value': 'yangodeli_android',
                    'arg_name': 'application.name',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
            'value': {'brand_names': ['yangodeli']},
        },
        {
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {'brand_names': ['lavka', 'yataxi']},
        },
    ],
    is_config=True,
)

ERROR_CODES = [
    'ERROR_UNKNOWN_ERROR',
    'ERROR_LESS_THAN_MIN_CART_COST',
    'ERROR_TAG_FIRST_LIMIT_REACHED',
    'ERROR_ORDERS_FIRST_LIMIT_REACHED',
    'ERROR_NO_REQUIRED_ITEM',
    'ERROR_NO_REQUIRED_CATEGORY',
    'ERROR_NO_ANY_OF_REQUIRED_ITEM',
    'ERROR_NO_ANY_OF_REQUIRED_CATEGORY',
    'ERROR_OTHER_REGION_ID',
    'ERROR_CART_WAS_NOT_MATCHED',
    'ERROR_USER_TAG_WAS_NOT_MATCHED',
    'ERROR_NO_YANDEX_UID',
    'ERROR_UNKNOWN_ORDERS_COUNT',
    'ERROR_UNKNOWN_USAGE_COUNT',
]

COUPON_TYPES = ['support', 'marketing', 'referral', 'referral_reward']


def antifraud_check_exp_(enabled, cache_enabled=False):
    return pytest.mark.experiments3(
        name='grocery_enable_discount_antifraud',
        consumers=['grocery-antifraud'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enable': enabled, 'cache_enable': cache_enabled},
            },
        ],
        default_value={'enable': False},
        is_config=True,
    )


ANTIFRAUD_CHECK_ENABLED = antifraud_check_exp_(True)
ANTIFRAUD_CHECK_WITH_CACHE_ENABLED = antifraud_check_exp_(True, True)
ANTIFRAUD_CHECK_DISABLED = antifraud_check_exp_(False)

YANDEX_UID = '555'
APP_NAME = 'android'
EATS_USER_ID = 'eats-user-id'
PHONE_ID = 'abcde'
PERSONAL_PHONE_ID = 'personal-phone-id'
USER_INFO = (
    f'eats_user_id={EATS_USER_ID}, personal_phone_id={PERSONAL_PHONE_ID}'
)
APPMETRICA_DEVICE_ID = 'some_appmetrica'

HEADERS = {
    'X-YaTaxi-Session': 'taxi:1234',
    'X-Idempotency-Token': 'update-token',
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name={APP_NAME}',
    'X-YaTaxi-User': USER_INFO,
    'X-Yandex-UID': YANDEX_UID,
    'X-YaTaxi-PhoneId': PHONE_ID,
    'X-AppMetrica-DeviceId': APPMETRICA_DEVICE_ID,
}


def grocery_coupons_save_coupons(coupon_types=None):
    return pytest.mark.experiments3(
        name='grocery_coupons_save_coupons',
        consumers=['grocery-coupons/check'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'is_signal': False,
                'title': 'Always enabled',
                'predicate': {'init': {}, 'type': 'true'},
                'value': {
                    'coupon_types': (
                        [] if coupon_types is None else coupon_types
                    ),
                },
            },
        ],
        is_config=True,
    )


def grocery_coupons_show_saved(enabled=True):
    return pytest.mark.experiments3(
        name='grocery_coupons_show_saved_coupons',
        consumers=['grocery-coupons/list'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'is_signal': False,
                'title': 'Always enabled',
                'predicate': {'init': {}, 'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=True,
    )
