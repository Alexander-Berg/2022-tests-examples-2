import dataclasses
import json
import typing

import pytest


@dataclasses.dataclass
class EventTokenRule:
    token: str
    app_brand: str
    app_name: str
    first_order: bool


@dataclasses.dataclass
class AdjustIdRule:
    app_brand: str
    id_field: str


@dataclasses.dataclass
class AppTokenRule:
    app_name: str
    app_token: str


EVENT_TOKEN_RULES = [
    EventTokenRule('wxe2h0', 'lavka', 'lavka_android', True),
    EventTokenRule('tj0uw3', 'lavka', 'lavka_android', False),
    EventTokenRule('bre0xv', 'lavka', 'lavka_iphone', True),
    EventTokenRule('ta9zos', 'lavka', 'lavka_iphone', False),
    EventTokenRule('xzyfm8', 'yataxi', 'mobileweb_android', True),
    EventTokenRule('6g9950', 'yataxi', 'mobileweb_android', False),
    EventTokenRule('nte072', 'yataxi', 'mobileweb_iphone', True),
    EventTokenRule('cgg54x', 'yataxi', 'mobileweb_iphone', False),
    EventTokenRule('6h9tin', 'yango', 'mobileweb_yango_android', True),
    EventTokenRule('5dhzqb', 'yango', 'mobileweb_yango_android', False),
    EventTokenRule('22rh0b', 'yango', 'mobileweb_yango_iphone', True),
    EventTokenRule('4eup5p', 'yango', 'mobileweb_yango_iphone', False),
    EventTokenRule('yusk4f', 'eats', 'eda_webview_android', True),
    EventTokenRule('7dkoo4', 'eats', 'eda_webview_android', False),
    EventTokenRule('daji45', 'eats', 'eda_webview_iphone', True),
    EventTokenRule('rrjt0r', 'eats', 'eda_webview_iphone', False),
    EventTokenRule('rcpqh4', 'yangodeli', 'yangodeli_android', True),
    EventTokenRule('s7jo97', 'yangodeli', 'yangodeli_android', False),
    EventTokenRule('1fq21z', 'yangodeli', 'yangodeli_iphone', True),
    EventTokenRule('bozbit', 'yangodeli', 'yangodeli_iphone', False),
]

ADJUST_ID_RULES = [
    AdjustIdRule('eats', 'appmetrica_device_id'),
    AdjustIdRule('lavka', 'taxi_user_id'),
    AdjustIdRule('yataxi', 'taxi_user_id'),
    AdjustIdRule('yango', 'taxi_user_id'),
    AdjustIdRule('yangodeli', 'taxi_user_id'),
]

ADJUST_ID_RULES_DICT = {
    rule.app_brand: rule.id_field for rule in ADJUST_ID_RULES
}

APP_TOKEN_RULES = [
    AppTokenRule('lavka_iphone', '767lbmo1h88w'),
    AppTokenRule('lavka_android', 'emdentw8t6gw'),
    AppTokenRule('mobileweb_iphone', 'cs75zaz26h8x'),
    AppTokenRule('mobileweb_android', '55ug2ntb3uzf'),
    AppTokenRule('eda_webview_iphone', '6umurlxdwgw0'),
    AppTokenRule('eda_webview_android', 't3i3lsfkfdhc'),
    AppTokenRule('mobileweb_yango_iphone', 'ct2oecwpzaps'),
    AppTokenRule('mobileweb_yango_android', 'hdsim8mkjrpc'),
    AppTokenRule('yangodeli_iphone', 'ag7o2ebd2io0'),
    AppTokenRule('yangodeli_android', 'es6g46bx6ygw'),
]

APP_TOKEN_RULES_DICT = {
    rule.app_name: rule.app_token for rule in APP_TOKEN_RULES
}


def get_switch_item_for_event_token(event_token_rule: EventTokenRule):
    number_comp_operator = (
        'equal_to' if event_token_rule.first_order else 'greater'
    )
    return {
        'arguments': {
            'dst_key': 'event_token',
            'value': event_token_rule.token,
        },
        'filters': [
            {
                'arguments': {
                    'src': 'app_brand',
                    'match_with': event_token_rule.app_brand,
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {
                    'src': 'app_name',
                    'match_with': event_token_rule.app_name,
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
            {
                'arguments': {'key': 'is_successful', 'expected': 'true'},
                'operation_name': 'bool_equal',
                'type': 'filter',
            },
            {
                'arguments': {
                    'lhs_key': 'total_orders_count',
                    'rhs_value': 1,
                    'operator': number_comp_operator,
                },
                'operation_name': 'number_compare',
                'type': 'filter',
            },
        ],
    }


def get_switch_item_for_adjust_id(adjust_id_rule: AdjustIdRule):
    return {
        'arguments': {
            'recursive_keys': [adjust_id_rule.id_field],
            'flat_key': 'adjust_user_id',
        },
        'filters': [
            {
                'arguments': {
                    'src': 'app_brand',
                    'match_with': adjust_id_rule.app_brand,
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
        ],
    }


def get_switch_item_for_app_token(app_token_rule: AppTokenRule):
    return {
        'arguments': {
            'dst_key': 'app_token',
            'value': app_token_rule.app_token,
        },
        'filters': [
            {
                'arguments': {
                    'src': 'app_name',
                    'match_with': app_token_rule.app_name,
                },
                'operation_name': 'string_equal',
                'type': 'filter',
            },
        ],
    }


EVENT_TOKEN_SWITCH_OPTIONS = [
    get_switch_item_for_event_token(etr) for etr in EVENT_TOKEN_RULES
]

ADJUST_ID_SWITCH_OPTIONS = [
    get_switch_item_for_adjust_id(aid) for aid in ADJUST_ID_RULES
]

APP_TOKEN_SWITCH_OPTIONS = [
    get_switch_item_for_app_token(at) for at in APP_TOKEN_RULES
]

OEP_PIPELINES = [
    {
        'description': '',
        'st_ticket': '',
        'source': {'name': 'grocery-adjust-events'},
        'root': {
            'output': {'sink_name': 'grocery_adjust_sink'},
            'operations': [
                {
                    'name': 'check-app-vars',
                    'operation_variant': {
                        'operation_name': 'field_check',
                        'type': 'filter',
                        'arguments': {
                            'key': 'app_vars',
                            'policy': 'key_exists',
                        },
                    },
                },
                {
                    'name': 'app-vars-to-dict',
                    'operation_variant': {
                        'operation_name': 'string_to_dict',
                        'type': 'mapper',
                        'arguments': {
                            'src': 'app_vars',
                            'dst': 'app_vars_dict',
                        },
                    },
                },
                {
                    'name': 'set-app-name',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'recursive_keys': ['app_vars_dict', 'app_name'],
                            'flat_key': 'app_name',
                        },
                    },
                },
                {
                    'name': 'set-app-brand',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'recursive_keys': ['app_vars_dict', 'app_brand'],
                            'flat_key': 'app_brand',
                        },
                    },
                },
                {
                    'name': 'tags-array-to-map',
                    'operation_variant': {
                        'operation_name': 'atlas::list_to_map',
                        'type': 'mapper',
                        'arguments': {
                            'src': ['matched_tags'],
                            'dst': ['matched_tags_map'],
                            'map_by_key': 'tag',
                        },
                    },
                },
                {
                    'name': 'set-total-orders-count',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'recursive_keys': [
                                'matched_tags_map',
                                'total_orders_count',
                                'count',
                            ],
                            'flat_key': 'total_orders_count',
                        },
                    },
                },
                {
                    'name': 'set-event-token',
                    'operation_variant': {
                        'operation_name': 'set_string_value',
                        'options': EVENT_TOKEN_SWITCH_OPTIONS,
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'set-app-token',
                    'operation_variant': {
                        'operation_name': 'set_string_value',
                        'options': APP_TOKEN_SWITCH_OPTIONS,
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'set-adjust-id',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'options': ADJUST_ID_SWITCH_OPTIONS,
                        'type': 'mapper',
                    },
                },
                {
                    'name': 'check-order-id',
                    'operation_variant': {
                        'operation_name': 'field_check',
                        'type': 'filter',
                        'arguments': {
                            'key': 'order_id',
                            'policy': 'key_exists',
                        },
                    },
                },
                {
                    'name': 'check-adjust-user-id',
                    'operation_variant': {
                        'operation_name': 'field_check',
                        'type': 'filter',
                        'arguments': {
                            'key': 'adjust_user_id',
                            'policy': 'key_exists',
                        },
                    },
                },
                {
                    'name': 'check-app-name',
                    'operation_variant': {
                        'operation_name': 'field_check',
                        'type': 'filter',
                        'arguments': {
                            'key': 'app_name',
                            'policy': 'key_exists',
                        },
                    },
                },
                {
                    'name': 'check-app-token',
                    'operation_variant': {
                        'operation_name': 'field_check',
                        'type': 'filter',
                        'arguments': {
                            'key': 'app_token',
                            'policy': 'key_exists',
                        },
                    },
                },
                {
                    'name': 'check-event-token',
                    'operation_variant': {
                        'operation_name': 'field_check',
                        'type': 'filter',
                        'arguments': {
                            'key': 'event_token',
                            'policy': 'key_exists',
                        },
                    },
                },
            ],
        },
        'name': 'grocery-adjust-events',
    },
]


def get_event(
        event_token_rule: EventTokenRule,
        is_successful: bool,
        total_orders_count: int,
):
    return {
        'order_id': 'order_id',
        'app_vars': (
            f'app_brand={event_token_rule.app_brand},'
            'app_ver3=0,'
            'device_make=apple,'
            f'app_name={event_token_rule.app_name},'
            'platform_ver2=4,'
            'app_build=release,'
            'app_ver2=17,'
            'app_ver1=600,'
            'platform_ver1=14'
        ),
        'phone_id': 'phone_id',
        'yandex_uid': 'yandex_uid',
        'eats_user_id': 'eats_user_id',
        'matched_tags': [
            {'tag': 'total_orders_count', 'count': total_orders_count},
        ],
        'taxi_user_id': 'taxi_user_id',
        'is_successful': is_successful,
        'personal_phone_id': 'personal_phone_id',
        'appmetrica_device_id': 'appmetrica_device_id',
    }


def get_stq_kwargs(event_token_rule: EventTokenRule, total_orders_count: int):
    res = {
        'app_name': event_token_rule.app_name,
        'event_token': event_token_rule.token,
        'app_token': APP_TOKEN_RULES_DICT[event_token_rule.app_name],
        'created_at': {'$date': '2019-10-16T19:16:00.000Z'},
        'callback_params': {
            'order_id': 'order_id',
            'total_orders_count': str(total_orders_count),
            'phone_id': 'phone_id',
            'yandex_uid': 'yandex_uid',
            'eats_user_id': 'eats_user_id',
            'personal_phone_id': 'personal_phone_id',
            'taxi_user_id': 'taxi_user_id',
            'appmetrica_device_id': 'appmetrica_device_id',
        },
        'partner_params': {},
    }

    adjust_id_field = ADJUST_ID_RULES_DICT[event_token_rule.app_brand]
    callback_params = res['callback_params']
    res['adjust_user_id'] = typing.cast(
        typing.Dict[str, str], callback_params,
    )[adjust_id_field]

    return res


@pytest.mark.now('2019-10-16T19:16:00+0000')
async def test_grocery_adjust_sink(
        taxi_order_events_producer,
        testpoint,
        taxi_config,
        stq,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, OEP_PIPELINES,
    )

    token_rules_and_order_counts = [
        (etr, 1 if etr.first_order else 2) for etr in EVENT_TOKEN_RULES
    ]
    good_events = [
        get_event(etr, True, count)
        for etr, count in token_rules_and_order_counts
    ]

    bad_events = [
        get_event(etr, False, count)
        for etr, count in token_rules_and_order_counts
    ]
    bad_events.extend(
        [get_event(etr, True, 0) for etr, _ in token_rules_and_order_counts],
    )
    bad_events.extend(
        [
            get_event(
                EventTokenRule(
                    etr.token, 'not_in_rules', etr.app_name, etr.first_order,
                ),
                True,
                count,
            )
            for etr, count in token_rules_and_order_counts
        ],
    )
    bad_events.extend(
        [
            get_event(
                EventTokenRule(
                    etr.token, etr.app_brand, 'not_in_rules', etr.first_order,
                ),
                True,
                count,
            )
            for etr, count in token_rules_and_order_counts
        ],
    )

    for i, event in enumerate(good_events + bad_events):
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'grocery-adjust-events',
                    'data': json.dumps(event),
                    'topic': 'smth',
                    'cookie': f'cookie_for_grocery_adjust_sink_{i}',
                },
            ),
        )
        assert response.status_code == 200

        assert (await commit.wait_call())[
            'data'
        ] == f'cookie_for_grocery_adjust_sink_{i}'

    assert stq.grocery_adjust_events.times_called == len(good_events)
    for etr, count in token_rules_and_order_counts:
        call_args = stq.grocery_adjust_events.next_call()
        if 'log_extra' in call_args['kwargs']:
            del call_args['kwargs']['log_extra']
        assert call_args['queue'] == 'grocery_adjust_events'
        assert call_args['id'] == 'order_id'
        assert call_args['kwargs'] == get_stq_kwargs(etr, count)
