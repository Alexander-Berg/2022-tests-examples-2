# pylint: disable=too-many-lines

import copy
import typing

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_eats_payment_methods_availability import helpers

URL = '/v1/payment-methods/availability/'

DEFAULT_SND_POINT = [37.590533, 55.733863]
DEFAULT_DST_POINT = [37.534397, 55.750028]
DEFAULT_LOC_POINT = [37.534301, 55.750001]
NONDEFAULT_LOC_POINT = [71.433333, 51.13333]
DEFAULT_COUNTRY_ID = 225
NONDEFAULT_COUNTRY_ID = 159
DEFAULT_SND_BOX = [
    [37.59, 55.73],
    [37.59, 55.74],
    [37.60, 55.74],
    [37.60, 55.73],
]
DEFAULT_DST_BOX = [
    [37.53, 55.75],
    [37.53, 55.76],
    [37.54, 55.76],
    [37.54, 55.75],
]
DEFAULT_YANDEX_UID = '4003514353'
DEFAULT_PERSONAL_PHONE_ID = '5714f45e98956f06baaae3d4'
DEFAULT_APP_NAME = 'yango_android'
PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-Pass-Flags': 'phonish',
    'X-Yandex-UID': DEFAULT_YANDEX_UID,
    'X-YaTaxi-PhoneId': DEFAULT_PERSONAL_PHONE_ID,
    'X-Request-Language': 'ru',
    'X-Request-Application': f'app_name={DEFAULT_APP_NAME}',
    'X-Ya-User-Ticket': 'user_ticket',
    'Date': 'Tue, 01 Aug 2017 15:00:00 GMT',
    'X-YaTaxi-User': 'personal_phone_id=5714f45e98956f06baaae3d4',
}

DEFAULT_BRAND_ID = '123456'
DEFAULT_ORDER_TOTAL_COST = '1000'
DEFAULT_CURRENCY = 'RUB'

NO_CASH_REASON = 'В данном месте заказа не принимают наличные'
NOT_FOOD_REASON = 'На бейдж можно покупать только еду'

CARD: dict = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
}

CARD_WITH_SETTINGS: dict = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
    'tracking_settings': {'enabled': True, 'error_delay': 5},
}

YANDEX_BANK_CARD: dict = {
    'availability': {'available': True, 'disabled_reason': ''},
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'Счет в Яндексе',
    'short_title': 'yandex-bank',
    'number': 'yandex-bank-number-overwrite',
    'system': 'YandexBank',
    'type': 'yandex_bank',
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
}

LPM_MOCK_CARDS = [
    {
        'id': 'card-x1b81b062ef77491d72d1134f',
        'bin': '400000',
        'name': 'VISA',
        'type': 'card',
        'number': '400000****8596',
        'system': 'VISA',
        'currency': 'RUB',
        'availability': {'available': True, 'disabled_reason': ''},
        'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
    },
    {
        'id': 'card-x434db6f255a39636ffdf5c5c',
        'bin': '555555',
        'name': 'MasterCard',
        'type': 'card',
        'number': '555555****4444',
        'system': 'MasterCard',
        'currency': 'RUB',
        'availability': {'available': True, 'disabled_reason': ''},
        'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
    },
]

API_PROXY_CARD = {**CARD, 'available': True, 'card_country': 'RU'}

CARD_DISABLED: dict = {
    'availability': {
        'available': False,
        'disabled_reason': 'Требуется верификация на данном устройстве',
    },
    'bin': '462729',
    'currency': 'RUB',
    'id': 'card-x3609',
    'name': 'VISA',
    'number': '462729****0957',
    'system': 'VISA',
    'type': 'card',
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
}
API_PROXY_CARD_DISABLED = {
    **CARD_DISABLED,
    'available': False,
    'card_country': 'RU',
}

MERCHANT_IDS = ['merchant.ru.yandex.ytaxi.trust']
ROSNEFT_MERCHANT_IDS = ['merchant.ru.yandex.mobile.zapravki.vbrr.eda']

API_PROXY_APPLE_PAY = {'type': 'applepay'}
APPLE_PAY: dict = {
    'type': 'applepay',
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'Apple Pay',
    'merchant_id_list': MERCHANT_IDS,
    'service_token': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
}

API_PROXY_GOOGLE_PAY = {'type': 'googlepay'}
MERCHANT_ID = 'google_pay_merchant_id'
SERVICE_TOKEN = 'google_pay_service_token'
GOOGLE_PAY: dict = {
    'type': 'googlepay',
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'Google Pay',
    'merchant_id': MERCHANT_ID,
    'service_token': SERVICE_TOKEN,
}

BADGE = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': '',
    'id': 'badge:yandex_badge:RUB',
    'name': 'Yandex Badge',
    'type': 'corp',
}

CORP = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'eats 3796 of 10000 RUB',
    'balance_left': '3796',
    'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
    'name': 'corp-test',
    'type': 'corp',
    'user_id': '9e63c266c0d84206bbc8765f2cf7a730',
    'client_id': 'beed2277ae71428db1029c07394e542c',
}

CORP_UNAVAILABLE = {
    'availability': {'available': False, 'disabled_reason': 'test_reason'},
    'currency': 'RUB',
    'description': '',
    'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
    'name': 'corp-test',
    'type': 'corp',
    'user_id': '9e63c266c0d84206bbc8765f2cf7a730',
    'client_id': 'beed2277ae71428db1029c07394e542c',
}

SBP = {
    'type': 'sbp',
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'СБП',
    'description': 'Система быстрых платежей',
}

SBP_WITH_SETTINGS = {
    'type': 'sbp',
    'availability': {'available': True, 'disabled_reason': ''},
    'name': 'СБП',
    'description': 'Система быстрых платежей',
    'tracking_settings': {'enabled': True, 'error_delay': 6},
    'sbp_settings': {
        'members': [
            {
                'schema': 'bank100000000111',
                'logo_url': 'https://logo.ru/logo.png',
                'bank_name': 'Сбербанк',
                'package_name': 'ru.sberbankmobile',
            },
        ],
        'continue_button_delay': 10,
    },
}

CORP_RESPONSE = {
    'availability': {'available': True, 'disabled_reason': ''},
    'currency': 'RUB',
    'description': 'eats 3796 of 10000 RUB',
    'balance_left': '3796',
    'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
    'name': 'corp-test',
    'type': 'corp',
}

PERSONAL_WALLET = {
    'availability': {'available': True, 'disabled_reason': ''},
    'description': 'eats 3796 of 10000 RUB',
    'id': 'yandex:plus',
    'name': 'yandex-plus',
    'type': 'personal_wallet',
    'currency_rules': {
        'code': 'RUB',
        'template': '$VALUE$ $CURRENCY$',
        'text': 'руб.',
    },
}

PERSONAL_WALLET_KZ = {
    'availability': {'available': True, 'disabled_reason': ''},
    'description': 'eats 3796 of 10000 RUB',
    'id': 'yandex:plus',
    'name': 'yandex-plus',
    'type': 'personal_wallet',
    'currency_rules': {
        'code': 'KZT',
        'template': '"$VALUE$ $CURRENCY$"',
        'text': 'тнг.',
    },
}

PERSONAL_WALLET_WITH_MONEY_LEFT = {**PERSONAL_WALLET, **{'money_left': '0.99'}}

ADD_NEW_CARD: dict = {
    'type': 'add_new_card',
    'name': 'Привязать новую карту',
    'availability': {'available': True, 'disabled_reason': ''},
    'binding_service_token': 'taxifee_8c7078d6b3334e03c1b4005b02da30f4',
}

RESPONSE_BASE: typing.Dict[str, typing.Any] = {
    'last_used_payment_method': {
        'id': 'badge:yandex_badge:RUB',
        'type': 'corp',
    },
    'payment_methods': [],
}


def _make_cash_response(available=True, disabled_reason=NO_CASH_REASON):
    disabled_reason = '' if available else disabled_reason
    return {
        'type': 'cash',
        'availability': {
            'available': available,
            'disabled_reason': disabled_reason,
        },
        'name': 'Наличные',
    }


def _make_badge_response(available=True):
    disabled_reason = '' if available else NOT_FOOD_REASON
    return {
        'availability': {
            'available': available,
            'disabled_reason': disabled_reason,
        },
        'currency': 'RUB',
        'description': '',
        'id': 'badge:yandex_badge:RUB',
        'name': 'Yandex Badge',
        'type': 'corp',
    }


def _make_api_proxy_card_response(card_id: str, updated_at: str = None):
    card: typing.Dict[str, typing.Any] = {**API_PROXY_CARD, 'id': card_id}
    if updated_at is not None:
        card['updated_at'] = updated_at
    return card


def _make_card_response(card_id: str):
    return {**CARD, 'id': card_id}


def _make_response(
        payment_methods: typing.List[dict],
        country_expected=False,
        region_id=DEFAULT_COUNTRY_ID,
) -> dict:
    response: typing.Dict[str, typing.Any] = {
        **RESPONSE_BASE,
        'payment_methods': payment_methods,
    }

    for method in response['payment_methods']:
        if method['type'] == 'card' and method['name'] != 'yandex-bank':
            method['name'] = method['system'] + ' •• ' + method['number'][-4:]
            method['short_title'] = '•• ' + method['number'][-4:]

    if country_expected:
        response['region_id'] = region_id

    return response


def _add_false_availability(
        payment_method: dict, disabled_reason: str = '',
) -> dict:
    return {
        **payment_method,
        'availability': {
            'available': False,
            'disabled_reason': disabled_reason,
        },
    }


BASE_REQUEST = {
    'sender_point': DEFAULT_SND_POINT,
    'destination_point': DEFAULT_DST_POINT,
    'brand_id': '123456',
    'phone_id': '88005353535',
    'region_id': 77,
    'order_info': {
        'currency': DEFAULT_CURRENCY,
        'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
    },
    'place_info': {'accepts_cash': True},
}

NOT_ACCEPT_CASH = {'place_info': {'accepts_cash': False}}

ORDER_INFO_OTHER_ITEMS_TYPE = {
    'order_info': {
        'currency': DEFAULT_CURRENCY,
        'item_sets': [
            {'amount': '36.23', 'items_type': 'food'},
            {'amount': '0.05', 'items_type': 'other'},
        ],
    },
    'location': DEFAULT_LOC_POINT,
}


def _make_request(accepts_cash=True, base_request=None, **extra) -> dict:
    if base_request is None:
        base_request = BASE_REQUEST
    return {
        **base_request,
        **{'place_info': {'accepts_cash': accepts_cash}},
        **extra,
    }


USER_AGENT = 'yandex-taxi/3.129.0.110856 Android/9 (samsung; SM-A705FN)'

EXP_PAYMENT_TYPES_YANDEX_UID_PREDICATE = {
    'init': {
        'arg_name': 'yandex_uid',
        'arg_type': 'string',
        'value': DEFAULT_YANDEX_UID,
    },
    'type': 'eq',
}
EXP_PAYMENT_TYPES_PERSONAL_PHONE_ID_PREDICATE = {
    'init': {
        'arg_name': 'personal_phone_id',
        'arg_type': 'string',
        'value': DEFAULT_PERSONAL_PHONE_ID,
    },
    'type': 'eq',
}
EXP_PAYMENT_TYPES_APPLICATION_PREDICATE = {
    'init': {
        'arg_name': 'application',
        'arg_type': 'string',
        'value': DEFAULT_APP_NAME,
    },
    'type': 'eq',
}
EXP_PAYMENT_TYPES_SENDER_POINT_PREDICATE = {
    'init': {
        'arg_name': 'sender_point',
        'arg_type': 'linear_ring',
        'value': DEFAULT_SND_BOX,
    },
    'type': 'falls_inside',
}
EXP_PAYMENT_TYPES_DESTINATION_POINT_PREDICATE = {
    'init': {
        'arg_name': 'destination_point',
        'arg_type': 'linear_ring',
        'value': DEFAULT_DST_BOX,
    },
    'type': 'falls_inside',
}
EXP_PAYMENT_TYPES_BRAND_ID_PREDICATE = {
    'init': {
        'arg_name': 'brand_id',
        'arg_type': 'string',
        'value': DEFAULT_BRAND_ID,
    },
    'type': 'eq',
}
EXP_PAYMENT_TYPES_ORDER_TOTAL_COST_PREDICATE = {
    'init': {
        'arg_name': 'order_total_cost',
        'arg_type': 'double',
        'value': float(DEFAULT_ORDER_TOTAL_COST),
    },
    'type': 'lte',
}
EXP_PAYMENT_TYPES_CURRENCY_PREDICATE = {
    'init': {
        'arg_name': 'currency',
        'arg_type': 'string',
        'value': DEFAULT_CURRENCY,
    },
    'type': 'eq',
}
EXP_PAYMENT_TYPES_FULL_PREDICATE = {
    'init': {
        'predicates': [
            EXP_PAYMENT_TYPES_YANDEX_UID_PREDICATE,
            EXP_PAYMENT_TYPES_PERSONAL_PHONE_ID_PREDICATE,
            EXP_PAYMENT_TYPES_APPLICATION_PREDICATE,
            EXP_PAYMENT_TYPES_SENDER_POINT_PREDICATE,
            EXP_PAYMENT_TYPES_DESTINATION_POINT_PREDICATE,
            EXP_PAYMENT_TYPES_BRAND_ID_PREDICATE,
            EXP_PAYMENT_TYPES_ORDER_TOTAL_COST_PREDICATE,
            EXP_PAYMENT_TYPES_CURRENCY_PREDICATE,
        ],
    },
    'type': 'all_of',
}


def make_saturn_request_experiment() -> dict:  # pylint: disable=invalid-name
    return {
        'name': 'eats_payments_saturn',
        'consumers': ['eats-payments/saturn'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {
                    'is_postpayment_request_enabled': True,
                    'is_cash_request_enabled': True,
                },
            },
        ],
        'default_value': {
            'is_postpayment_request_enabled': True,
            'is_cash_request_enabled': True,
        },
    }


def make_lpm_mock_experiment() -> dict:  # pylint: disable=invalid-name
    cards = [
        {
            'id': 'card-x1b81b062ef77491d72d1134f',
            'bin': '400000',
            'name': 'VISA',
            'type': 'card',
            'number': '400000****8596',
            'system': 'VISA',
            'currency': 'RUB',
            'available': True,
            'updated_at': '2021-11-29T14:23:10.927+00:00',
            'availability': {'available': True, 'disabled_reason': ''},
        },
        {
            'id': 'card-x434db6f255a39636ffdf5c5c',
            'bin': '555555',
            'name': 'MasterCard',
            'type': 'card',
            'number': '555555****4444',
            'system': 'MasterCard',
            'currency': 'RUB',
            'available': True,
            'updated_at': '2021-11-29T14:23:10.922+00:00',
            'availability': {'available': True, 'disabled_reason': ''},
        },
    ]

    return {
        'name': 'eats_payments_lpm_mock_card',
        'consumers': ['eats-payments/lpm-mock'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'cards': cards},
            },
        ],
        'default_value': {'cards': cards},
    }


ALL_API_PROXY_PAYMENT_METHODS = [
    API_PROXY_CARD,
    API_PROXY_APPLE_PAY,
    API_PROXY_GOOGLE_PAY,
    BADGE,
    CORP,
]

ALL_PAYMENT_METHODS = [
    CARD,
    APPLE_PAY,
    GOOGLE_PAY,
    BADGE,
    CORP_RESPONSE,
    ADD_NEW_CARD,
]
ALL_PAYMENT_METHODS_WITHOUT_CORP = [
    CARD,
    APPLE_PAY,
    GOOGLE_PAY,
    BADGE,
    ADD_NEW_CARD,
]
SOME_PAYMENT_METHODS_WITH_WALLET = [
    APPLE_PAY,
    GOOGLE_PAY,
    BADGE,
    PERSONAL_WALLET,
]

PAYMENT_METHOD_ONE_WALLET = [PERSONAL_WALLET]
PAYMENT_METHOD_WITH_MANY_WALLETS = [
    PERSONAL_WALLET,
    PERSONAL_WALLET_KZ,
    PERSONAL_WALLET,
]

ALL_AVAILABLE_PAYMENT_TYPES = [
    'add_new_card',
    'card',
    'applepay',
    'googlepay',
    'badge',
    'corp',
]

ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH = ALL_AVAILABLE_PAYMENT_TYPES + ['cash']

ALL_AVAILABLE_PAYMENT_TYPES_WITH_PERSONAL_WALLET = (
    ALL_AVAILABLE_PAYMENT_TYPES + ['personal_wallet']
)

POST_PAYMENT = {
    'type': 'postpayment',
    'availability': {'available': True, 'disabled_reason': ''},
}

PAYMENT_METHOD_VIEW = {
    'can_show': True,
    'text': {
        'color': [
            {'theme': 'dark', 'value': 'ffaaaa'},
            {'theme': 'light', 'value': 'aaaaff'},
        ],
        'text': 'test text',
    },
    'button': {
        'color': [
            {'theme': 'dark', 'value': 'ffaaaa'},
            {'theme': 'light', 'value': 'aaaaff'},
        ],
        'title': {
            'color': [
                {'theme': 'dark', 'value': 'ffaaaa'},
                {'theme': 'light', 'value': 'aaaaff'},
            ],
            'text': 'test button text',
        },
        'id': '123',
    },
}


@pytest.mark.parametrize(
    [
        'api_proxy_payment_methods',
        'available_payment_types',
        'response_payment_methods',
        'corp_payment_methods',
        'request_extra',
        'pass_afs_params',
        'pass_3ds_params',
    ],
    [
        pytest.param(
            [],
            [],
            [],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,
            False,
            id='nothing received, nothing available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            [],
            [],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, nothing available',
        ),
        pytest.param(
            [],
            ALL_AVAILABLE_PAYMENT_TYPES,
            [ADD_NEW_CARD],
            [CORP],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='nothing received, everything available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ['card', 'add_new_card'],
            [CARD, ADD_NEW_CARD],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, only card available',
        ),
        pytest.param(
            [
                API_PROXY_CARD_DISABLED,
                API_PROXY_APPLE_PAY,
                API_PROXY_GOOGLE_PAY,
                BADGE,
                CORP,
            ],
            ['card'],
            [CARD_DISABLED],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, only card available but disabled',
        ),
        pytest.param(
            [
                API_PROXY_CARD_DISABLED,
                API_PROXY_APPLE_PAY,
                API_PROXY_GOOGLE_PAY,
                BADGE,
                CORP,
            ],
            ['card'],
            [CARD_DISABLED],
            [],
            {'location': DEFAULT_LOC_POINT},
            True,
            False,
            id='everything received, only card available but '
            'disabled afs params only passed',
        ),
        pytest.param(
            [
                API_PROXY_CARD_DISABLED,
                API_PROXY_APPLE_PAY,
                API_PROXY_GOOGLE_PAY,
                BADGE,
                CORP,
            ],
            ['card'],
            [CARD_DISABLED],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,
            True,
            id='everything received, only card available but '
            'disabled 3ds params only passed',
        ),
        pytest.param(
            [
                API_PROXY_CARD_DISABLED,
                API_PROXY_APPLE_PAY,
                API_PROXY_GOOGLE_PAY,
                BADGE,
                CORP,
            ],
            ['card'],
            [CARD],
            [],
            {'location': DEFAULT_LOC_POINT},
            True,
            True,
            id='everything received, only disabled card available '
            'because afs params passed and 3ds available passed',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ['applepay'],
            [APPLE_PAY],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, only applepay available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ['googlepay'],
            [GOOGLE_PAY],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, only googlepay available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ['badge'],
            [_make_badge_response()],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, only badge available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ['corp'],
            [CORP_RESPONSE],
            [CORP],
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
                'location': DEFAULT_LOC_POINT,
            },
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, only corp available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ALL_AVAILABLE_PAYMENT_TYPES,
            ALL_PAYMENT_METHODS,
            [CORP],
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
                'location': DEFAULT_LOC_POINT,
            },
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, everything available',
        ),
        pytest.param(
            # api_proxy_payment_methods
            ALL_API_PROXY_PAYMENT_METHODS,
            # available_payment_types
            ALL_AVAILABLE_PAYMENT_TYPES,
            # response_payment_methods
            ALL_PAYMENT_METHODS,
            # corp_payment_methods
            [CORP],
            # request_extra
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
                'location': DEFAULT_LOC_POINT,
            },
            False,  # pass_afs_params
            False,  # pass_3ds_params
            id='everything received, everything available, with country',
        ),
    ],
)
async def test_available_payment_methods(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        api_proxy_payment_methods,
        available_payment_types,
        response_payment_methods,
        corp_payment_methods,
        request_extra,
        pass_afs_params,
        pass_3ds_params,
):
    api_proxy_handler = mock_api_proxy_list_payment_methods(
        api_proxy_payment_methods,
    )
    mock_corp_int_api_payment_methods_eats(
        corp_payment_methods,
        DEFAULT_ORDER_TOTAL_COST,
        DEFAULT_SND_POINT,
        DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')
    exp_payment_methods(available_payment_types)

    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_pass_afs_params_experiment(pass_afs_params),
    )
    experiments3.add_experiment(
        **helpers.make_pass_3ds_params_experiment(pass_3ds_params),
    )
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        response_payment_methods, country_expected='location' in request_extra,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.config(
    EATS_PAYMENTS_PAYMENT_AVAILABILITY_VIEW={
        'payment_methods_map': {'card': PAYMENT_METHOD_VIEW},
    },
)
async def test_different_country_notification(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
):
    api_proxy_handler = mock_api_proxy_list_payment_methods(
        ALL_API_PROXY_PAYMENT_METHODS,
    )
    print(api_proxy_handler)
    exp_payment_methods(['card'])

    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    request = copy.deepcopy(BASE_REQUEST)
    view = copy.deepcopy(PAYMENT_METHOD_VIEW)

    request['destination_point'] = NONDEFAULT_LOC_POINT
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(base_request=request), headers=headers,
    )
    assert response.status_code == 200
    view['text']['text'] = 'Карта другой страны'
    card = copy.deepcopy(CARD)
    card['availability']['view'] = view
    card['info'] = 'Карта другой страны'
    assert response.json() == _make_response(
        [card], country_expected=True, region_id=NONDEFAULT_COUNTRY_ID,
    )

    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(), headers=headers,
    )
    assert response.status_code == 200
    card = copy.deepcopy(CARD)
    card['availability']['view'] = PAYMENT_METHOD_VIEW
    assert response.json() == _make_response([card], country_expected=True)

    assert api_proxy_handler.times_called == 2


@pytest.mark.parametrize(
    [
        'api_proxy_payment_methods',
        'available_payment_types',
        'response_payment_methods',
        'corp_payment_methods',
        'request_extra',
        'pass_afs_params',
        'pass_3ds_params',
    ],
    [
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            ['card', 'sbp'],
            [CARD, ADD_NEW_CARD, SBP],
            [],
            {'location': DEFAULT_LOC_POINT},
            False,  # pass_afs_params
            False,  # pass_3ds_params
        ),
    ],
)
async def test_tracking_setting_in_response(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        api_proxy_payment_methods,
        available_payment_types,
        response_payment_methods,
        corp_payment_methods,
        request_extra,
        pass_afs_params,
        pass_3ds_params,
):
    experiments3.add_config(**helpers.make_payment_tracking_experiment())
    api_proxy_handler = mock_api_proxy_list_payment_methods(
        ALL_API_PROXY_PAYMENT_METHODS,
    )
    mock_corp_int_api_payment_methods_eats(
        [], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')
    exp_payment_methods(['card', 'add_new_card', 'sbp'])

    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_pass_afs_params_experiment(pass_afs_params),
    )
    experiments3.add_experiment(
        **helpers.make_pass_3ds_params_experiment(pass_3ds_params),
    )
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**{}), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        [CARD_WITH_SETTINGS, ADD_NEW_CARD, SBP_WITH_SETTINGS],
        country_expected='location' in request_extra,
    )
    assert api_proxy_handler.times_called == 1


async def test_changing_name_and_system_by_experiment(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_cashback_calculator_calculate,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
):
    api_proxy_handler = mock_api_proxy_list_payment_methods(
        ALL_API_PROXY_PAYMENT_METHODS,
    )
    mock_cashback_calculator_calculate()
    mock_corp_int_api_payment_methods_eats(
        [], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')
    exp_payment_methods(['card', 'yandex_bank'])

    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())
    experiments3.add_config(
        **helpers.make_card_attributes_overwrite_experiment(),
    )

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**{}), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        [YANDEX_BANK_CARD], country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.parametrize(
    [
        'api_proxy_payment_methods',
        'accepts_cash',
        'available_payment_types',
        'response_payment_methods',
        'request_extra',
        'saturn_response',
    ],
    [
        pytest.param(
            [],
            False,
            [],
            [],
            {'location': DEFAULT_LOC_POINT},
            'accepted',
            id='nothing received, does not accept cash, nothing allowed',
        ),
        pytest.param(
            [],
            True,
            [],
            [],
            {'location': DEFAULT_LOC_POINT},
            'accepted',
            id='nothing received, accepts cash, nothing allowed',
        ),
        pytest.param(
            [],
            False,
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH,
            [ADD_NEW_CARD] + [_make_cash_response(available=False)],
            {'location': DEFAULT_LOC_POINT},
            'accepted',
            id='nothing received, does not accept cash, everything allowed',
        ),
        pytest.param(
            [],
            True,
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH,
            [ADD_NEW_CARD] + [_make_cash_response(available=True)],
            {'location': DEFAULT_LOC_POINT},
            'accepted',
            id='nothing received, accepts cash, everything allowed',
        ),
        pytest.param(
            [API_PROXY_CARD],
            False,
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH,
            [CARD, ADD_NEW_CARD, _make_cash_response(available=False)],
            {'location': DEFAULT_LOC_POINT},
            'accepted',
            id='card received, does not accept cash, everything allowed',
        ),
        pytest.param(
            [API_PROXY_CARD],
            True,
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH,
            [CARD, ADD_NEW_CARD, _make_cash_response(available=True)],
            {'location': DEFAULT_LOC_POINT},
            'accepted',
            id='card received, accepts cash, everything allowed',
        ),
        pytest.param(
            [API_PROXY_CARD],
            True,
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH,
            [
                CARD,
                ADD_NEW_CARD,
                _make_cash_response(
                    available=False,
                    disabled_reason='Оплата наличными запрещена '
                    'сервисом скоринга Saturn',
                ),
            ],
            {'location': DEFAULT_LOC_POINT},
            'rejected',
            id='cash rejected by saturn',
        ),
    ],
)
async def test_cash(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        api_proxy_payment_methods,
        accepts_cash,
        available_payment_types,
        request_extra,
        response_payment_methods,
        saturn_response,
):
    exp_payment_methods(available_payment_types)
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    mock_corp_int_api_payment_methods_eats(
        [CORP], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    api_proxy_handler = mock_api_proxy_list_payment_methods(
        api_proxy_payment_methods,
    )
    mock_saturn(saturn_response)
    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(accepts_cash=accepts_cash), headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == _make_response(
        response_payment_methods, country_expected='location' in request_extra,
    )
    assert api_proxy_handler.times_called == 1


async def test_sbp(
        taxi_eats_payment_methods_availability,
        experiments3,
        mock_api_proxy_list_payment_methods,
        exp_payment_methods,
):
    exp_payment_methods(['sbp'])
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())
    api_proxy_handler = mock_api_proxy_list_payment_methods([])
    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL,
        json=_make_request(**ORDER_INFO_OTHER_ITEMS_TYPE),
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == _make_response(
        payment_methods=[SBP], country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.parametrize(
    ['request_extra', 'api_proxy_payment_methods', 'response_payment_methods'],
    [
        (
            ORDER_INFO_OTHER_ITEMS_TYPE,
            [CORP, BADGE],
            [
                _make_badge_response(available=False),
                ADD_NEW_CARD,
                _make_cash_response(),
            ],
        ),
    ],
)
async def test_badge_unavailable(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_saturn,
        request_extra,
        api_proxy_payment_methods,
        response_payment_methods,
):
    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH)
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    api_proxy_handler = mock_api_proxy_list_payment_methods(
        api_proxy_payment_methods,
    )
    mock_saturn('accepted')

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        response_payment_methods, country_expected='location' in request_extra,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.parametrize(
    ['request_extra'],
    [
        (
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'business': {
                        'type': 'fuelfood',
                        'specification': ['rosneft'],
                    },
                },
            },
        ),
    ],
)
async def test_google_pay_merchant_id_and_service_token(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_saturn,
        request_extra,
):
    exp_payment_methods(['card'])
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    api_proxy_handler = mock_api_proxy_list_payment_methods(
        ALL_API_PROXY_PAYMENT_METHODS,
    )
    mock_saturn('accepted')

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}

    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        payment_methods=[CARD], country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.parametrize(
    [
        'available_payment_types',
        'api_proxy_payment_methods',
        'response_payment_methods',
        'request_extra',
    ],
    [
        pytest.param(
            # available_payment_types
            ALL_AVAILABLE_PAYMENT_TYPES,
            # api_proxy_payment_methods
            [
                _make_api_proxy_card_response(
                    'card-3', '2021-01-18T19:01:00+03:00',
                ),
                _make_api_proxy_card_response('card-4', None),
                _make_api_proxy_card_response(
                    'card-2', '2021-01-18T19:02:00+03:00',
                ),
                _make_api_proxy_card_response('card-5', None),
                _make_api_proxy_card_response(
                    'card-1', '2021-01-18T19:03:00+03:00',
                ),
            ],
            # response_payment_methods
            [
                _make_card_response('card-1'),
                _make_card_response('card-2'),
                _make_card_response('card-3'),
                _make_card_response('card-4'),
                _make_card_response('card-5'),
                ADD_NEW_CARD,
            ],
            {},
            id='cards only',
        ),
        pytest.param(
            # available_payment_types
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_CASH,
            # api_proxy_payment_methods
            [
                _make_api_proxy_card_response(
                    'card-3', '2021-01-18T19:01:00+03:00',
                ),
                API_PROXY_APPLE_PAY,
                _make_api_proxy_card_response('card-4', None),
                API_PROXY_GOOGLE_PAY,
                _make_api_proxy_card_response(
                    'card-2', '2021-01-18T19:02:00+03:00',
                ),
                CORP,
                _make_api_proxy_card_response('card-5', None),
                BADGE,
                _make_api_proxy_card_response(
                    'card-1', '2021-01-18T19:03:00+03:00',
                ),
            ],
            # response_payment_methods
            [
                _make_card_response('card-1'),
                APPLE_PAY,
                _make_card_response('card-2'),
                GOOGLE_PAY,
                _make_card_response('card-3'),
                _make_card_response('card-4'),
                _make_badge_response(),
                _make_card_response('card-5'),
                CORP_RESPONSE,
                ADD_NEW_CARD,
                _make_cash_response(),
            ],
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
            },
            id='cards mixed with other payment methods',
        ),
    ],
)
async def test_cards_sorting(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        available_payment_types,
        api_proxy_payment_methods,
        response_payment_methods,
        request_extra,
):
    exp_payment_methods(available_payment_types)
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(
        **helpers.make_apple_pay_tokens_experiment(MERCHANT_IDS),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    api_proxy_handler = mock_api_proxy_list_payment_methods(
        api_proxy_payment_methods,
    )

    mock_corp_int_api_payment_methods_eats(
        [CORP], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )

    mock_saturn('accepted')

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        response_payment_methods, country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.parametrize(
    ['payment_type', 'value'],
    [
        ('googlepay', 1),
        ('corp', 1),
        ('badge', 1),
        ('applepay', 1),
        ('cash', 1),
        ('card', 1),
    ],
)
async def test_payment_methods_metrics_all_available(
        taxi_eats_payment_methods_availability,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        taxi_eats_payment_methods_availability_monitor,
        experiments3,
        exp_payment_methods,
        payment_type,
        value,
):
    mock_api_proxy_list_payment_methods(ALL_API_PROXY_PAYMENT_METHODS)
    mock_corp_int_api_payment_methods_eats(
        [CORP], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')

    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(
        **helpers.make_apple_pay_tokens_experiment(MERCHANT_IDS),
    )

    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES + ['cash'])
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    request_extra = {
        'order_info': {
            'currency': 'RUB',
            'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
            'total_cost': '1000',
        },
    }

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payment_methods_availability_monitor,
            sensor='eats_payments_payment_methods_metrics',
            labels={'payment_type': payment_type},
    ) as collector:
        response = await taxi_eats_payment_methods_availability.post(
            URL, json=_make_request(**request_extra), headers=headers,
        )

    assert response.status_code == 200

    metric = collector.get_single_collected_metric()
    assert metric.value == value
    assert metric.labels == {
        'sensor': 'eats_payments_payment_methods_metrics',
        'currency': 'RUB',
        'payment_type': payment_type,
    }


@pytest.mark.parametrize(
    ['payment_type', 'available'],
    [
        ('googlepay', True),
        ('corp', False),
        ('applepay', True),
        ('cash', False),
        ('card', False),
    ],
)
async def test_payment_methods_metrics_few_available(
        taxi_eats_payment_methods_availability,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        taxi_eats_payment_methods_availability_monitor,
        experiments3,
        exp_payment_methods,
        payment_type,
        available,
):
    mock_api_proxy_list_payment_methods(ALL_API_PROXY_PAYMENT_METHODS)
    mock_corp_int_api_payment_methods_eats(
        [CORP], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')

    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(
        **helpers.make_apple_pay_tokens_experiment(MERCHANT_IDS),
    )

    exp_payment_methods(['googlepay', 'applepay'])
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    request_extra = {
        'order_info': {
            'currency': 'RUB',
            'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
            'total_cost': '1000',
        },
    }

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payment_methods_availability_monitor,
            sensor='eats_payments_payment_methods_metrics',
            labels={'payment_type': payment_type},
    ) as collector:
        response = await taxi_eats_payment_methods_availability.post(
            URL, json=_make_request(**request_extra), headers=headers,
        )

    assert response.status_code == 200

    metric = collector.get_single_collected_metric()
    if available:
        assert metric.value == 1
    else:
        assert metric is None


@pytest.mark.parametrize(
    [
        'api_proxy_payment_methods',
        'available_payment_types',
        'response_payment_methods',
        'request_extra',
    ],
    [
        pytest.param(
            [],
            ['add_new_card'],
            [ADD_NEW_CARD],
            {'location': DEFAULT_LOC_POINT},
            id='nothing received, nothing available',
        ),
        pytest.param(
            ALL_API_PROXY_PAYMENT_METHODS,
            [],
            [],
            {'location': DEFAULT_LOC_POINT},
            id='everything received, nothing available',
        ),
        pytest.param(
            PAYMENT_METHOD_ONE_WALLET,
            ['personal_wallet'],
            [PERSONAL_WALLET],
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
                'location': DEFAULT_LOC_POINT,
            },
            id='only wallet receiived, only wallet available',
        ),
        pytest.param(
            PAYMENT_METHOD_WITH_MANY_WALLETS,
            ['personal_wallet'],
            [PERSONAL_WALLET],
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
                'location': DEFAULT_LOC_POINT,
            },
            id='several wallets received, only wallet available',
        ),
        pytest.param(
            SOME_PAYMENT_METHODS_WITH_WALLET,
            ALL_AVAILABLE_PAYMENT_TYPES_WITH_PERSONAL_WALLET,
            SOME_PAYMENT_METHODS_WITH_WALLET + [ADD_NEW_CARD],
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'total_cost': DEFAULT_ORDER_TOTAL_COST,
                },
                'location': DEFAULT_LOC_POINT,
            },
            id='many payment types received, wallet included',
        ),
    ],
)
async def test_personal_wallet(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        api_proxy_payment_methods,
        available_payment_types,
        response_payment_methods,
        request_extra,
):
    api_proxy_handler = mock_api_proxy_list_payment_methods(
        api_proxy_payment_methods,
    )
    mock_corp_int_api_payment_methods_eats(
        [], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')

    exp_payment_methods(available_payment_types)
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_google_pay_tokens_experiment(
            merchant_id=MERCHANT_ID, service_token=SERVICE_TOKEN,
        ),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == _make_response(
        response_payment_methods, country_expected='location' in request_extra,
    )
    assert api_proxy_handler.times_called == 1


async def test_payment_methods_googlepay_blocked_by_fallback(
        taxi_eats_payment_methods_availability,
        mock_api_proxy_list_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        mock_saturn,
        exp_payment_methods,
        experiments3,
        statistics,
):
    mock_api_proxy_list_payment_methods(ALL_API_PROXY_PAYMENT_METHODS)
    mock_corp_int_api_payment_methods_eats(
        [CORP], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )
    mock_saturn('accepted')

    statistics.fallbacks = ['disable-googlepay-fallback']

    exp_payment_methods(ALL_AVAILABLE_PAYMENT_TYPES)

    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(
        **helpers.make_apple_pay_tokens_experiment(MERCHANT_IDS),
    )
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    request_extra = {
        'order_info': {
            'currency': 'RUB',
            'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
            'total_cost': '1000',
        },
    }

    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    payment_methods_without_google = [
        CARD,
        APPLE_PAY,
        BADGE,
        CORP_RESPONSE,
        ADD_NEW_CARD,
    ]

    assert response.status_code == 200
    assert response.json() == _make_response(
        payment_methods_without_google, country_expected=True,
    )


@pytest.mark.parametrize(
    ['request_extra'],
    [
        (
            {
                'order_info': {
                    'currency': 'RUB',
                    'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
                    'business': {
                        'type': 'fuelfood',
                        'specification': ['rosneft'],
                    },
                },
            },
        ),
    ],
)
async def test_apple_pay_merchant_ids(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_saturn,
        request_extra,
):
    exp_payment_methods(['applepay'])

    experiments3.add_config(
        **helpers.make_apple_pay_tokens_experiment(ROSNEFT_MERCHANT_IDS),
    )
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    api_proxy_handler = mock_api_proxy_list_payment_methods(
        ALL_API_PROXY_PAYMENT_METHODS,
    )
    mock_saturn('accepted')

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}

    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )

    assert response.status_code == 200

    expected_response = _make_response([APPLE_PAY], country_expected=True)
    assert expected_response['payment_methods']
    expected_response['payment_methods'][0][
        'merchant_id_list'
    ] = ROSNEFT_MERCHANT_IDS
    assert response.json() == expected_response

    assert api_proxy_handler.times_called == 1


async def test_post_payment_bad_request(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_saturn,
):
    exp_payment_methods(['applepay'])
    experiments3.add_config(
        **helpers.make_apple_pay_tokens_experiment(ROSNEFT_MERCHANT_IDS),
    )
    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())

    api_proxy_handler = mock_api_proxy_list_payment_methods(
        ALL_API_PROXY_PAYMENT_METHODS,
    )
    mock_saturn('accepted')

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}

    response = await taxi_eats_payment_methods_availability.post(
        URL, json=[], headers=headers,
    )

    assert response.status_code == 400

    assert api_proxy_handler.times_called == 0


@pytest.mark.config(
    EATS_PAYMENTS_PAYMENT_AVAILABILITY_VIEW={
        'payment_methods_map': {'sbp': PAYMENT_METHOD_VIEW},
    },
)
async def test_payment_method_view(
        taxi_eats_payment_methods_availability,
        experiments3,
        mock_api_proxy_list_payment_methods,
        exp_payment_methods,
):
    exp_payment_methods(['sbp'])
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())
    api_proxy_handler = mock_api_proxy_list_payment_methods([])
    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL,
        json=_make_request(**ORDER_INFO_OTHER_ITEMS_TYPE),
        headers=headers,
    )
    assert response.status_code == 200

    sbp_payment = {
        'type': 'sbp',
        'availability': {
            'available': True,
            'disabled_reason': '',
            'view': PAYMENT_METHOD_VIEW,
        },
        'name': 'СБП',
        'description': 'Система быстрых платежей',
    }

    assert response.json() == _make_response(
        payment_methods=[sbp_payment], country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.config(
    EATS_PAYMENTS_PAYMENT_AVAILABILITY_VIEW={
        'payment_methods_map': {'sbp': {'can_show': True}},
    },
)
async def test_payment_method_view_minimal_config(
        taxi_eats_payment_methods_availability,
        experiments3,
        mock_api_proxy_list_payment_methods,
        exp_payment_methods,
):
    exp_payment_methods(['sbp'])
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())
    api_proxy_handler = mock_api_proxy_list_payment_methods([])
    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL,
        json=_make_request(**ORDER_INFO_OTHER_ITEMS_TYPE),
        headers=headers,
    )
    assert response.status_code == 200

    sbp_payment = {
        'type': 'sbp',
        'availability': {
            'available': True,
            'disabled_reason': '',
            'view': {'can_show': True},
        },
        'name': 'СБП',
        'description': 'Система быстрых платежей',
    }

    assert response.json() == _make_response(
        payment_methods=[sbp_payment], country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.config(
    EATS_PAYMENTS_PAYMENT_AVAILABILITY_VIEW={
        'payment_methods_map': {
            'corp': {
                'can_show': True,
                'text': {
                    'color': [
                        {'theme': 'dark', 'value': 'ffaaaa'},
                        {'theme': 'light', 'value': 'aaaaff'},
                    ],
                    'text': 'test text',
                },
            },
        },
    },
)
@pytest.mark.parametrize(
    ['text', 'taxi_corp_response', 'description', 'color'],
    [
        pytest.param(
            'eats 3796 of 10000 RUB',
            CORP,
            'eats 3796 of 10000 RUB',
            '#9E9B98',
            id='corp_available',
        ),
        pytest.param(
            'test_reason',
            CORP_UNAVAILABLE,
            '',
            '#FA3E2C',
            id='corp_unavailable',
        ),
    ],
)
async def test_payment_method_view_with_corp_text(
        taxi_eats_payment_methods_availability,
        experiments3,
        mock_api_proxy_list_payment_methods,
        exp_payment_methods,
        mock_corp_int_api_payment_methods_eats,
        taxi_corp_response,
        text,
        description,
        color,
):
    exp_payment_methods(['corp'])
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())
    mock_corp_int_api_payment_methods_eats(
        [taxi_corp_response],
        DEFAULT_ORDER_TOTAL_COST,
        DEFAULT_SND_POINT,
        DEFAULT_DST_POINT,
    )
    api_proxy_handler = mock_api_proxy_list_payment_methods([])
    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    request_extra = {
        'order_info': {
            'currency': 'RUB',
            'item_sets': [{'amount': '36.23', 'items_type': 'food'}],
            'total_cost': '1000',
        },
    }
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**request_extra), headers=headers,
    )
    assert response.status_code == 200

    corp_payment = {
        'type': 'corp',
        'name': 'corp-test',
        'id': 'corp:9e63c266c0d84206bbc8765f2cf7a730:RUB',
        'currency': 'RUB',
        'description': description,
        'availability': {
            'available': taxi_corp_response['availability']['available'],
            'disabled_reason': taxi_corp_response['availability'][
                'disabled_reason'
            ],
            'view': {
                'can_show': True,
                'text': {
                    'color': [
                        {'theme': 'dark', 'value': color},
                        {'theme': 'light', 'value': color},
                    ],
                    'text': text,
                },
            },
        },
    }
    if 'balance_left' in taxi_corp_response:
        corp_payment['balance_left'] = taxi_corp_response['balance_left']

    assert response.json() == _make_response(
        payment_methods=[corp_payment], country_expected=True,
    )
    assert api_proxy_handler.times_called == 1


@pytest.mark.parametrize(
    ['yandex_bank_visibility', 'expected_payment_methods'],
    [
        pytest.param(
            True,
            [YANDEX_BANK_CARD, ADD_NEW_CARD],
            id='yandex_bank is visible',
        ),
        pytest.param(False, [ADD_NEW_CARD], id='yandex_bank is hidden'),
    ],
)
async def test_yandex_bank(
        taxi_eats_payment_methods_availability,
        experiments3,
        exp_payment_methods,
        mock_api_proxy_list_payment_methods,
        mock_cashback_calculator_calculate,
        mock_corp_int_api_payment_methods_eats,
        yandex_bank_visibility,
        expected_payment_methods,
):
    api_proxy_handler = mock_api_proxy_list_payment_methods([API_PROXY_CARD])
    mock_cashback_calculator_calculate()
    mock_corp_int_api_payment_methods_eats(
        [], DEFAULT_ORDER_TOTAL_COST, DEFAULT_SND_POINT, DEFAULT_DST_POINT,
    )

    exp_payment_methods(
        ['add_new_card', 'card', 'yandex_bank'],
        visibility={'yandex_bank': yandex_bank_visibility},
    )

    experiments3.add_experiment(**make_saturn_request_experiment())
    experiments3.add_config(**helpers.make_card_service_tokens_experiment())
    experiments3.add_config(
        **helpers.make_card_attributes_overwrite_experiment(),
    )

    headers = {**PA_HEADERS, 'User-Agent': USER_AGENT}
    response = await taxi_eats_payment_methods_availability.post(
        URL, json=_make_request(**{}), headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == _make_response(
        expected_payment_methods, country_expected=True,
    )
    assert api_proxy_handler.times_called == 1
