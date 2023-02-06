from typing import Any
from typing import Dict


class ApiKey:
    RESTAURANT_01 = 'RESTAURANT_01'
    INVALID = 'INVALID'
    RESTAURANT_DISABLED = 'RESTAURANT_DISABLED'


CONFIG_RESTAURANT_INFO: Dict[str, Dict[str, Any]] = {
    'restaurant01': {
        'api_key_hash': ApiKey.RESTAURANT_01,
        'restaurant_group_id': 'restaurant_group_01',
        'eda_place_id': 1,
        'eda_client_id': 1,
        'geosearch_id': '1400568734',
        'geopoint': {'lon': 37.618423, 'lat': 55.751244},
        'phone_number': '+70000047448',
        'address_ru': 'address_ru',
        'address_en': 'address_en',
        'inn': '1234567890',
    },
    'restaurant_disabled': {
        'api_key_hash': ApiKey.RESTAURANT_DISABLED,
        'eda_place_id': 2,
        'eda_client_id': 1,
        'geosearch_id': '1234567890',
        'restaurant_group_id': 'restaurant_group_01',
        'geopoint': {'lon': 37.618423, 'lat': 55.751244},
        'phone_number': '+70000047448',
        'address_ru': 'address_ru',
        'address_en': 'address_en',
        'enabled': False,
        'inn': '0987654321',
    },
}


CONFIG_RESTAURANT_GROUP_INFO = {
    'restaurant_group_01': {
        'tag_tanker_key': 'placeholder_tag_key',
        'name_tanker_key': 'maximum.kek',
        'cashback': 30,
        'commission': '10',
        'upper_text_tanker_key': 'restaurant_01_upper',
        'deeplink_template': 'default_{order_id}_1',
        'lower_text_tanker_key': 'default_lower',
    },
}


RESTAURANT_INFO_CONFIGS = {
    'IIKO_INTEGRATION_RESTAURANT_GROUP_INFO': CONFIG_RESTAURANT_GROUP_INFO,
    'IIKO_INTEGRATION_RESTAURANT_INFO': CONFIG_RESTAURANT_INFO,
}


CONFIG_USER_NOTIFICATION_BY_STATUS = {
    'PENDING+HELD': {
        'tanker_key': 'go.qr.order_paid',
        'intent': 'go_qr_order_paid',
    },
    'WAITING_FOR_CONFIRMATION+HELD': {
        'tanker_key': 'go.qr.order_paid',
        'intent': 'go_qr_order_paid',
    },
    'PENDING+HOLD_FAILED': {
        'tanker_key': 'go.qr.payment_failed',
        'intent': 'go_qr_payment_failed',
    },
    'CLOSED+': {
        'tanker_key': 'go.qr.closed_by_restaurant',
        'intent': 'go_qr_closed_by_restaurant',
    },
    'CANCELED+': {
        'tanker_key': 'go.qr.canceled_by_restaurant',
        'intent': 'go_qr_canceled_by_restaurant',
    },
}


ORDERHISTORY_TRANSLATIONS = {
    'qr_payment': {
        'maximum.kek': {'ru': 'Ресторан 01', 'en': 'Restaurant 01'},
        'restaurant.orderhistory.phone.label': {
            'ru': 'Телефон',
            'en': 'Phone number',
        },
        'restaurant.orderhistory.address.label': {
            'ru': 'Адрес',
            'en': 'Address',
        },
        'restaurant.orderhistory.legal.entities.title': {
            'ru': 'О ресторане',
            'en': 'About',
        },
        'restaurant.orderhistory.pay.reciept.label': {
            'ru': 'Чек за оплату',
            'en': 'Payment receipt',
        },
        'restaurant.orderhistory.refund.reciept.label': {
            'ru': 'Чек за возврат',
            'en': 'Refund receipt',
        },
        'restaurant.orderhistory.service.name': {
            'ru': 'QR оплата',
            'en': 'QR pay',
        },
        'restaurant.payment_method.personal_wallet': {
            'ru': 'Яндекс.Плюс',
            'en': 'Yandex.Plus',
        },
    },
    'tariff': {
        'currency_with_sign.RUB': {
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
            'en': '$VALUE$ $SIGN$$CURRENCY$',
        },
    },
}


CURRENCY_FORMATTING_RULES = {
    'RUB': {
        '__default__': 4,
        'restaurants_price': 2,
        'restaurants_cashback': 0,
    },
}
