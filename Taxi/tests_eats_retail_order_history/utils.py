import datetime
import enum
from typing import Dict
from typing import Optional

import pytest

YANDEX_UID = '100000'
CUSTOMER_ID = '123'
TAXI_USER_ID = '321'
ORDER_ID = '12345'
CLAIM_ID = '54321'
CORP_CLIENT_ALIAS = 'corp_client_alias'
PLACE_ID = '222325'
PLACE_SLUG = 'aaa-bbb'
PLACE_NAME = 'Магнит'
CITY = 'Москва'
PLACE_ADDRESS = 'ул. Абвгд, д. 0'
BRAND_ID = '1'
BRAND_SLUG = 'abc'
BRAND_NAME = 'Магнит'
COURIER_ID = '10'
PICKER_ID = '11'
COURIER_PHONE_ID = 'courier_phone_id'
PICKER_PHONE_ID = 'picker_phone_id'
COURIER_PHONE = {'phone': '+7(800)5553535', 'ext': '1234', 'ttl_seconds': 3600}
APPLICATION = 'go'
PERSONAL_PHONE_ID = 'personal_phone_id'
REGION_ID_RU = 1
REGION_ID_KZ = 2
REGION_ID_BY = 3


NOTIFICATIONS_CONFIG_ALL_DISABLED = {
    'first_retail_order_changes': {
        'enabled': False,
        'project': 'eda',
        'notification_key': 'notification_key_0',
        'locale': 'ru',
        'events': {
            'add': {'enabled': False},
            'remove': {'enabled': False},
            'update_count': {'enabled': False},
            'update_weight': {'enabled': False},
        },
    },
    'order_in_delivery': {
        'enabled': False,
        'project': 'eda',
        'notification_key': 'notification_key_1',
        'locale': 'ru',
        'conditions_waiting_time': 300,
        'stq_reschedule_delay': 1,
    },
}

NOTIFICATIONS_CONFIG_ALL_ENABLED = {
    'first_retail_order_changes': {
        'enabled': True,
        'project': 'eda',
        'notification_key': 'notification_key_0',
        'locale': 'ru',
        'events': {
            'add': {'enabled': True},
            'remove': {'enabled': True},
            'update_count': {'enabled': True},
            'update_weight': {'enabled': True},
        },
    },
    'order_in_delivery': {
        'enabled': True,
        'project': 'eda',
        'notification_key': 'notification_key_1',
        'locale': 'ru',
        'conditions_waiting_time': 300,
        'stq_reschedule_delay': 1,
    },
}

TRANSLATIONS = {
    'eats-retail-order-history': {
        'extra_fees.service_fee': {'ru': 'Сервисный сбор'},
        'discounts.promo': {'ru': 'Промоакция'},
        'discounts.promocode': {'ru': 'Промокод'},
        'discounts.eats_discount': {'ru': 'Скидка'},
    },
}


class StatusForCustomer(enum.IntEnum):
    awaiting_payment = 1
    confirmed = 2
    cooking = 3
    in_delivery = 4
    arrived_to_customer = 5
    delivered = 6
    cancelled = 7
    auto_complete = 8


class PickingStatus(enum.IntEnum):
    new = 1
    waiting_dispatch = 2
    dispatching = 3
    dispatch_failed = 4
    assigned = 5
    picking = 6
    waiting_confirmation = 7
    confirmed = 8
    picked_up = 9
    receipt_processing = 10
    receipt_rejected = 11
    paid = 12
    packing = 13
    handing = 14
    cancelled = 15
    complete = 16


class OrderClientEvent(enum.Enum):
    created = 1
    payed = 2
    confirmed = 3
    taken = 4
    finished = 5
    cancelled = 6
    promise_changed = 7
    ready_to_send = 8
    sent = 9


class OrderType(enum.Enum):
    native = 1
    retail = 2
    shop = 3
    lavka = 4
    pharmacy = 5
    fast_food = 6
    fuel_food = 7


def datetime_to_string(timepoint):
    if isinstance(timepoint, datetime.datetime):
        if timepoint.tzinfo is None:
            timepoint = timepoint.replace(tzinfo=datetime.timezone.utc)
        return timepoint.isoformat()
    return timepoint


def synchronizer_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_retail_order_history_synchronizer',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-retail-order-history/synchronizer'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {
                'tasks_count': 10,
                'period_seconds': 5,
                'sync_duration': 3600,
                'orders_chunk_size': 100,
                'auto_complete_batch_size': 1000,
            },
            **kwargs,
        ),
    )


def synchronizer_force_update_cfg3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_retail_order_history_synchronizer_force_update',
        is_config=True,
        match={
            'consumers': [
                {
                    'name': (
                        'eats-retail-order-history/synchronizer-force-update'
                    ),
                },
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {
                'place_id': None,
                'brand_id': None,
                'order_nrs': None,
                'history_updated_after': None,
                'history_updated_before': None,
            },
            **kwargs,
        ),
    )


def get_fee_description_config3():
    return pytest.mark.experiments3(
        name='eats_retail_order_history_get_fee_description',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-retail-order-history/get-fee-description'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict({'description': 'Сервисный сбор'}),
    )


def notifications_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_retail_order_history_notifications',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-retail-order-history/notifications'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'enabled_eater_id',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'application',
                                    'set_elem_type': 'string',
                                    'set': ['go', 'eda_native', 'go_alias'],
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'set_elem_type': 'string',
                                    'arg_name': 'place_id',
                                    'set': [PLACE_ID],
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'set_elem_type': 'string',
                                    'arg_name': 'brand_id',
                                    'set': [BRAND_ID],
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'set_elem_type': 'string',
                                    'arg_name': 'eater_id',
                                    'set': [CUSTOMER_ID],
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'set_elem_type': 'string',
                                    'arg_name': 'eater_passport_id',
                                    'set': [YANDEX_UID],
                                },
                                'type': 'in_set',
                            },
                            {
                                'init': {
                                    'set_elem_type': 'string',
                                    'arg_name': 'eater_personal_phone_id',
                                    'set': [PERSONAL_PHONE_ID],
                                },
                                'type': 'in_set',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': dict(NOTIFICATIONS_CONFIG_ALL_ENABLED, **kwargs),
            },
        ],
        default_value=dict(NOTIFICATIONS_CONFIG_ALL_DISABLED, **kwargs),
    )


def polling_config3():
    return pytest.mark.experiments3(
        name='eats_retail_order_history_polling',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-retail-order-history/polling'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={
            'get_order_history': {'delay': 30},
            'refresh_history': {'delay': 30},
        },
    )


def currencies_config3():
    return pytest.mark.experiments3(
        name='eats_retail_currencies',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-retail-order-history/currencies'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'RUB',
                'predicate': {
                    'init': {
                        'value': str(REGION_ID_RU),
                        'arg_name': 'region_id',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                'value': {
                    'currency': {
                        'okv_code': 643,
                        'okv_str': 'RUB',
                        'okv_name': 'Российский рубль',
                        'sign': '₽',
                    },
                },
            },
            {
                'title': 'KZT',
                'predicate': {
                    'init': {
                        'value': str(REGION_ID_KZ),
                        'arg_name': 'region_id',
                        'arg_type': 'string',
                    },
                    'type': 'eq',
                },
                'value': {
                    'currency': {
                        'okv_code': 398,
                        'okv_str': 'KZT',
                        'okv_name': 'Тенге',
                        'sign': '₸',
                    },
                },
            },
        ],
        default_value={},
    )


def format_response(response_body):
    if 'created_at' in response_body:
        del response_body['created_at']
    response_body['original_items'].sort(key=lambda item: item['id'])
    response_body['diff']['add'].sort(key=lambda item: item['id'])
    response_body['diff']['remove'].sort(key=lambda item: item['id'])
    response_body['diff']['no_changes'].sort(key=lambda item: item['id'])
    response_body['diff']['replace'].sort(
        key=lambda replacement: replacement['from_item']['id'],
    )
    response_body['diff']['update'].sort(
        key=lambda update: update['from_item']['id'],
    )
    if 'soft_delete' in response_body['diff']:
        response_body['diff']['soft_delete'].sort(key=lambda item: item['id'])
    if 'picked_items' in response_body['diff']:
        response_body['diff']['picked_items'].sort()
    return response_body


def make_order_client_event(
        order_nr: str,
        order_event: OrderClientEvent,
        eater_id: str = CUSTOMER_ID,
        eater_passport_uid: str = YANDEX_UID,
        taxi_user_id: str = TAXI_USER_ID,
        place_id: str = PLACE_ID,
        eater_personal_phone_id: str = PERSONAL_PHONE_ID,
        application: str = APPLICATION,
        order_type: OrderType = OrderType.retail,
):
    event: Dict[str, Optional[str]] = {
        'order_nr': order_nr,
        'order_event': order_event.name,
        'order_type': order_type.name,
        'created_at': '2021-08-27T18:00:00+00:00',
        'delivery_type': 'delivery_type',
        'shipping_type': 'shipping_type',
        'eater_id': eater_id,
        'eater_personal_phone_id': eater_personal_phone_id,
        'promised_at': '2021-08-27T18:01:00+00:00',
        'application': application,
        'place_id': place_id,
        'payment_method': 'payment-method',
    }
    if eater_passport_uid:
        event['eater_passport_uid'] = eater_passport_uid
    if taxi_user_id:
        event['taxi_user_id'] = taxi_user_id
    if order_event == OrderClientEvent.taken:
        event['taken_at'] = '2021-08-27T18:10:00+00:00'
    return event


def zero_fee_enabled(enabled=True):
    return {
        'name': 'eats_retail_order_history_show_zero_fee',
        'consumers': ['eats-retail-order-history/show-zero-fee'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [],
        'default_value': {'enabled': enabled},
    }


def da_headers():
    return {
        'Accept-Language': 'en',
        'X-Remote-IP': '12.34.56.78',
        'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
        'X-YaTaxi-Park-Id': 'park_id1',
        'X-Request-Application': 'XYPro',
        'X-Request-Application-Version': '9.99 (9999)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'ios',
    }


def discounts_experiment3(enabled=False):
    return pytest.mark.experiments3(
        name='eats_retail_order_history_discounts',
        match={
            'consumers': [{'name': 'eats-retail-order-history/discounts'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={'enabled': enabled},
    )


def extra_fee_tanker_ids_config3():
    return pytest.mark.experiments3(
        name='eats_retail_order_history_extra_fee_tanker_ids',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-retail-order-history/extra-fee-tanker-ids'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'service_fee',
                'predicate': {
                    'init': {
                        'arg_name': 'fee_code',
                        'arg_type': 'string',
                        'value': 'service_fee',
                    },
                    'type': 'eq',
                },
                'value': {'tanker_id': 'extra_fees.service_fee'},
            },
        ],
        default_value={'tanker_id': 'extra_fees.unknown'},
    )


def discount_tanker_ids_config3():
    return pytest.mark.experiments3(
        name='eats_retail_order_history_discount_tanker_ids',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-retail-order-history/discount-tanker-ids'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'title': 'promo',
                'predicate': {
                    'init': {
                        'arg_name': 'discount_code',
                        'arg_type': 'string',
                        'value': 'promo',
                    },
                    'type': 'eq',
                },
                'value': {'tanker_id': 'discounts.promo'},
            },
            {
                'title': 'promocode',
                'predicate': {
                    'init': {
                        'arg_name': 'discount_code',
                        'arg_type': 'string',
                        'value': 'promocode',
                    },
                    'type': 'eq',
                },
                'value': {'tanker_id': 'discounts.promocode'},
            },
            {
                'title': 'eats_discount',
                'predicate': {
                    'init': {
                        'arg_name': 'discount_code',
                        'arg_type': 'string',
                        'value': 'eats_discount',
                    },
                    'type': 'eq',
                },
                'value': {'tanker_id': 'discounts.eats_discount'},
            },
        ],
        default_value={'tanker_id': 'discounts.unknown'},
    )
