import copy
import datetime as dt
import operator
from typing import Any
from typing import Dict
from typing import List

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
'2019-05-01T05:00:00+00:00'
_NOW = dt.datetime(2020, 5, 5, 15, 15, 5, 0, tzinfo=pytz.utc)

_UBERDRIVER_MODE_ITEM: Dict[str, Any] = {
    'availability': {'is_available': False, 'reasons': ['Не отображается']},
    'description': '',
    'display': {
        'is_displayed': False,
        'reasons': ['Не указана группа режимов'],
    },
    'mode_id': 'uberdriver',
    'offers_group': 'no_group',
    'subtitle': '',
    'title': 'Uber',
    'subscription': {},
}

_ORDERS_MODE_ITEM: Dict[str, Any] = {
    'availability': {'is_available': True, 'reasons': []},
    'description': '',
    'display': {'is_displayed': True, 'reasons': []},
    'mode_id': 'orders',
    'subtitle': '',
    'title': 'За заказы',
    'offers_group': 'taxi',
    'subscription': {},
}
_DRIVER_FIX_ITEM: Dict[str, Any] = {
    'availability': {'is_available': True, 'reasons': []},
    'description': '',
    'display': {'is_displayed': True, 'reasons': []},
    'mode_id': 'driver_fix',
    'subscription': {
        'settings': {
            'type': 'driver_fix',
            'values': {'rule_id': 'id_rule1', 'shift_close_time': '00:01'},
        },
    },
    'subtitle': '',
    'title': 'За время',
    'offers_group': 'taxi',
}
_EXTRA_ITEM: Dict[str, Any] = {
    'availability': {'is_available': True, 'reasons': []},
    'description': '',
    'display': {'is_displayed': True, 'reasons': []},
    'mode_id': 'custom_orders',
    'subtitle': '',
    'title': 'Карточка.Заголовок(default)',
    'offers_group': 'taxi',
    'subscription': {},
}


def _exclude_rule_id(data: List[Dict[str, Any]]):
    for item in data:
        assert 'rule_id' in item
        assert item['rule_id'] != ''
        del item['rule_id']
    return data


def _compare_result(
        actual: List[Dict[str, Any]], expected: List[Dict[str, Any]],
):
    actual.sort(key=operator.itemgetter('title'))
    expected.sort(key=operator.itemgetter('title'))
    assert actual == expected


def _mock_services(mockserver, mocked_time):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(request, 'orders', mocked_time)

    scenario.Scene.mock_driver_trackstory(mockserver)

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        data = request.json
        assert data['park_id'] == 'dbid'
        assert data['driver_profile_id'] == 'uuid'
        return {
            'offers': [
                {
                    'offer_card': {
                        'title': 'За время',
                        'subtitle': 'Доступен до 2 декабря',
                        'description': 'Заработок зависит от времени работы',
                        'is_new': True,
                        'enabled': True,
                    },
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
            ],
        }

    @mockserver.json_handler('/driver-fix/v1/view/geobooking_offer')
    async def _mock_view_geobooking_offer(request):
        data = request.json
        assert data['park_id'] == 'dbid'
        assert data['driver_profile_id'] == 'uuid'
        return {
            'offers': [
                {
                    'offer_card': {
                        'title': 'За geobooking',
                        'description': 'Заработок за бонусы по времени',
                        'is_new': True,
                        'enabled': True,
                    },
                    'key_params': {
                        'tariff_zone': 'test_tariff_zone',
                        'subvention_geoarea': 'test_subvention_geoarea',
                        'tag': 'no_free_slots_tag',
                    },
                    'settings': {'rule_id': 'id_rule1'},
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_profiles(request):
        return {'profiles': [{'park_driver_profile_id': 'dbid_uuid'}]}

    return [
        _driver_mode_index_mode_history,
        _mock_view_offer,
        _driver_profiles,
    ]


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders',
            'driver_fix': 'driver_fix',
            'custom_orders': 'custom_orders',
            'uberdriver': 'uberdriver',
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders': {
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
                    ],
                    'memo_items': [],
                    'screen_items': [
                        {
                            'data': {'text': 'orders_offer_screen.header'},
                            'type': 'header',
                        },
                    ],
                },
            },
            'driver_fix': {
                'model': {'title': 'offer_card.orders_title'},
                'schema': {
                    'card_items': [],
                    'memo_items': [
                        {
                            'data': {'text': 'orders_memo_screen.header'},
                            'type': 'header',
                        },
                    ],
                    'screen_items': [
                        {
                            'data': {'text': 'orders_offer_screen.header'},
                            'type': 'header',
                        },
                    ],
                },
            },
            'custom_orders': {
                'model': {'title': 'custom_orders.offer_card.title'},
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
                    ],
                    'memo_items': [
                        {
                            'data': {'text': 'orders_memo_screen.header'},
                            'type': 'header',
                        },
                    ],
                    'screen_items': [],
                },
            },
            'uberdriver': (offer_templates.DEFAULT_UBERDRIVER_TEMPLATE),
        },
    },
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
async def test_template_validation(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
):
    _mock_services(mockserver, mocked_time)

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )

    unavailable_status = {
        'is_available': False,
        'reasons': ['Не отображается'],
    }

    orders_item = copy.deepcopy(_ORDERS_MODE_ITEM)
    orders_item['availability'] = unavailable_status
    orders_item['display'] = {
        'is_displayed': False,
        'reasons': [
            'Неверный шаблон \'orders\': Offer memo screen template must '
            'not be empty',
        ],
    }

    driver_fix_item = copy.deepcopy(_DRIVER_FIX_ITEM)
    driver_fix_item['availability'] = unavailable_status
    driver_fix_item['display'] = {
        'is_displayed': False,
        'reasons': [
            'Неверный шаблон \'driver_fix\': Offer card template must '
            'not be empty',
        ],
    }

    extra_item = copy.deepcopy(_EXTRA_ITEM)
    extra_item['availability'] = unavailable_status
    extra_item['display'] = {
        'is_displayed': False,
        'reasons': [
            'Неверный шаблон \'custom_orders\': Offer screen template must '
            'not be empty',
        ],
    }

    expected_modes = [
        _UBERDRIVER_MODE_ITEM,
        orders_item,
        driver_fix_item,
        extra_item,
    ]

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)
