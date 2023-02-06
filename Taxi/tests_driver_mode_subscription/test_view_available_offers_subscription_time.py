import copy
import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_NOW = '2019-05-01T09:00:00+00:00'  # Wed
_LONG_AGO = datetime.datetime.fromisoformat('2010-05-01T09:00:00+00:00')

_DRIVER_MODE_RULES = mode_rules.patched(
    [mode_rules.Patch('driver_fix', stops_at=_LONG_AGO)],
)

_BUTTON_ENABLED = {'title': 'Выбрать', 'enabled': True}


def _build_disabled_button(start_time: Optional[str]):
    if start_time:
        return {'title': f'Доступно с {start_time}', 'enabled': False}

    return {'title': f'Сейчас недоступно', 'enabled': False}


def _get_query_component(url):
    pattern = '?id='
    i = url.rfind(pattern)
    return url[i + len(pattern) :]


def _tuples_to_schedule_entries(entries: List[Tuple[str, str]]):
    return [{'start': entry[0], 'stop': entry[1]} for entry in entries]


def _build_restrictions_config(
        allowed_ranges: List[Tuple[Tuple[str, str], Tuple[str, str]]],
        time_zone: str,
):
    subscription_schedule = [
        {
            'start': {'time': time_range[0][0], 'weekday': time_range[0][1]},
            'stop': {'time': time_range[1][0], 'weekday': time_range[1][1]},
        }
        for time_range in allowed_ranges
    ]

    return pytest.mark.config(
        DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
            'orders': {
                'time_zone': time_zone,
                'tariff_zones_settings': {
                    '__default__': {
                        'subscription_schedule': subscription_schedule,
                    },
                },
            },
        },
    )


_DEFAULT_OFFER_CARD = {
    'type': 'multi_section',
    'id': 'orders',
    'payload': {
        'type': 'deeplink',
        'url': 'taximeter://screen/driver_mode?id=orders',
    },
    'horizontal_divider_type': 'none',
    'orientation': 'vertical',
    'cross_axis_alignment': 'start',
    'item_divider_type': 'none',
    'items': [
        {
            'type': 'tip_detail',
            'left_tip': {
                'icon': {'icon_type': 'passenger', 'tint_color': '#21201F'},
                'size': 'mu_6',
                'background_color': '#E7E5E1',
                'form': 'round',
            },
            'right_icon': 'navigate',
            'title': 'За заказы',
            'subtitle': 'Всегда доступен',
            'primary_text_size': 'title_small',
            'secondary_text_size': 'hint',
            'accent_title': True,
            'padding_type': 'none',
        },
        {
            'type': 'text',
            'text': 'Заработок зависит от числа выполненных заказов',
            'padding': 'small_bottom',
            'max_lines': 3,
        },
    ],
}

_DEFAULT_OFFER_SCREEN_ITEMS = [
    {
        'type': 'header',
        'subtitle': 'Заказы',
        'gravity': 'left',
        'horizontal_divider_type': 'none',
    },
    {
        'type': 'text',
        'text': (
            'Режим дохода, в котором заработок зависит от числа '
            'выполненных заказов. А еще:'
        ),
        'padding': 'small_bottom',
        'horizontal_divider_type': 'none',
    },
    {
        'padding': 'small_bottom',
        'text': '— Вы сами выбираете удобные тарифы и способы оплаты.',
        'type': 'text',
        'horizontal_divider_type': 'none',
    },
    {
        'padding': 'small_bottom',
        'text': '— Доступен в любом регионе.',
        'type': 'text',
        'horizontal_divider_type': 'none',
    },
]


@dataclasses.dataclass
class DetailItem:
    title: str
    text: str


def _build_expected_offer_card(schedule: Optional[List[DetailItem]]):
    result: Dict[str, Any] = copy.deepcopy(_DEFAULT_OFFER_CARD)

    if schedule:
        items = [
            {'type': 'detail', 'title': item.title, 'detail': item.text}
            for item in schedule
        ]
        multi_section = {
            'type': 'multi_section',
            'orientation': 'vertical',
            'cross_axis_alignment': 'start',
            'items': items,
        }
        result['items'].append(multi_section)

    return result


def _build_expected_offer_screen(schedule: Optional[List[DetailItem]]):
    result: List[Dict[str, Any]] = copy.deepcopy(_DEFAULT_OFFER_SCREEN_ITEMS)

    if schedule:
        items = [{'type': 'icon_title', 'title': 'Расписание'}]
        items += [
            {'type': 'detail', 'title': item.title, 'detail': item.text}
            for item in schedule
        ]
        multi_section = {
            'type': 'multi_section',
            'orientation': 'vertical',
            'cross_axis_alignment': 'start',
            'items': items,
        }

        result.append({'type': 'title'})  # gap
        result.append(multi_section)

    return result


# offer card has limit of 2 schedule items, offer screen has not
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.geoareas(filename='geoareas_samara.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'expected_button, expected_offer_card, expected_offer_screen_items',
    [
        pytest.param(
            _BUTTON_ENABLED,
            _DEFAULT_OFFER_CARD,
            _DEFAULT_OFFER_SCREEN_ITEMS,
            id='no_restrictions',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _build_expected_offer_card(
                [DetailItem('Сегодня, 1 мая', '12:59 - 13:01')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Сегодня, 1 мая', '12:59 - 13:01')],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:59', 'wed'), ('09:01', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='ok',
        ),
        pytest.param(
            _build_disabled_button('Ср, 12:00'),
            _build_expected_offer_card(
                [DetailItem('Среда, 8 мая', '12:00 - 13:00')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Среда, 8 мая', '12:00 - 13:00')],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:00', 'wed'), ('09:00', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='fail_lately',
        ),
        pytest.param(
            _build_disabled_button('13:01'),
            _build_expected_offer_card(
                [DetailItem('Сегодня, 1 мая', '13:01 - 14:00')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Сегодня, 1 мая', '13:01 - 14:00')],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('09:01', 'wed'), ('10:00', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='fail_early',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _build_expected_offer_card(
                [DetailItem('Сегодня, 1 мая', '13:00 - 13:01')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Сегодня, 1 мая', '13:00 - 13:01')],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('12:00', 'wed'), ('12:01', 'wed'))],
                    time_zone='moscow',
                ),
            ],
            id='moscow_restriction_timezone',
        ),
        pytest.param(
            _build_disabled_button('Ср, 00:00'),
            _build_expected_offer_card(
                [DetailItem('Среда, 8 мая', '00:00 - 00:01')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Среда, 8 мая', '00:00 - 00:01')],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('00:00', 'wed'), ('00:01', 'wed'))],
                    time_zone='local',
                ),
            ],
            id='local_restriction_timezone',
        ),
        pytest.param(
            _build_disabled_button('Чт, 12:59'),
            _build_expected_offer_card(
                [
                    DetailItem('Завтра, 2 мая', '12:59 - 13:01'),
                    DetailItem('Пятница, 3 мая', '12:59 - 13:01'),
                ],
            ),
            _build_expected_offer_screen(
                [
                    DetailItem('Завтра, 2 мая', '12:59 - 13:01'),
                    DetailItem('Пятница, 3 мая', '12:59 - 13:01'),
                ],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[
                        (('08:59', 'thu'), ('09:01', 'thu')),
                        (('08:59', 'fri'), ('09:01', 'fri')),
                    ],
                    time_zone='utc',
                ),
            ],
            id='fail_weekday',
        ),
        pytest.param(
            _build_disabled_button('Чт, 12:59'),
            _build_expected_offer_card(
                [
                    DetailItem('Завтра, 2 мая', '12:59 - 00:00'),
                    DetailItem('Пятница, 3 мая', '00:00 - 13:01'),
                ],
            ),
            _build_expected_offer_screen(
                [
                    DetailItem('Завтра, 2 мая', '12:59 - 00:00'),
                    DetailItem('Пятница, 3 мая', '00:00 - 13:01'),
                ],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:59', 'thu'), ('09:01', 'fri'))],
                    time_zone='utc',
                ),
            ],
            id='test_multi_day_schedule_1',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _build_expected_offer_card(
                [
                    DetailItem('Сегодня, 1 мая', '00:00 - 00:00'),
                    DetailItem('Завтра, 2 мая', '00:00 - 13:01'),
                ],
            ),
            _build_expected_offer_screen(
                [
                    DetailItem('Сегодня, 1 мая', '00:00 - 00:00'),
                    DetailItem('Завтра, 2 мая', '00:00 - 13:01'),
                    DetailItem('Вторник, 7 мая', '12:59 - 00:00'),
                ],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:59', 'tue'), ('09:01', 'thu'))],
                    time_zone='utc',
                ),
            ],
            id='test_multi_day_schedule_2',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _build_expected_offer_card(
                [
                    DetailItem('Сегодня, 1 мая', '00:00 - 13:01'),
                    DetailItem('Вторник, 7 мая', '12:59 - 00:00'),
                ],
            ),
            _build_expected_offer_screen(
                [
                    DetailItem('Сегодня, 1 мая', '00:00 - 13:01'),
                    DetailItem('Вторник, 7 мая', '12:59 - 00:00'),
                ],
            ),
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:59', 'tue'), ('09:01', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='test_multi_day_schedule_3',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _DEFAULT_OFFER_CARD,
            _DEFAULT_OFFER_SCREEN_ITEMS,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:00', 'tue'), ('08:00', 'tue'))],
                    time_zone='utc',
                ),
            ],
            id='whole_week_allowed',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _build_expected_offer_card(
                [DetailItem('Сегодня, 1 мая', '13:00 - 13:01')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Сегодня, 1 мая', '13:00 - 13:01')],
            ),
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
                        'orders': {
                            'time_zone': 'utc',
                            'tariff_zones_settings': {
                                '__default__': {'subscription_schedule': []},
                                'samara': {
                                    'subscription_schedule': [
                                        {
                                            'start': {
                                                'time': '09:00',
                                                'weekday': 'wed',
                                            },
                                            'stop': {
                                                'time': '09:01',
                                                'weekday': 'wed',
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='ok_custom_tariff_zone',
        ),
        pytest.param(
            _BUTTON_ENABLED,
            _build_expected_offer_card(
                [DetailItem('Сегодня, 1 мая', '13:00 - 13:01')],
            ),
            _build_expected_offer_screen(
                [DetailItem('Сегодня, 1 мая', '13:00 - 13:01')],
            ),
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
                        'orders': {
                            'time_zone': 'utc',
                            'tariff_zones_settings': {
                                '__default__': {
                                    'subscription_schedule': [
                                        {
                                            'start': {
                                                'time': '09:00',
                                                'weekday': 'wed',
                                            },
                                            'stop': {
                                                'time': '09:01',
                                                'weekday': 'wed',
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='ok_default_tariff_zone',
        ),
        pytest.param(
            _build_disabled_button(None),
            _DEFAULT_OFFER_CARD,
            _DEFAULT_OFFER_SCREEN_ITEMS,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
                        'orders': {
                            'time_zone': 'utc',
                            'tariff_zones_settings': {
                                '__default__': {
                                    'subscription_schedule': [
                                        {
                                            'start': {
                                                'time': '09:00',
                                                'weekday': 'wed',
                                            },
                                            'stop': {
                                                'time': '09:01',
                                                'weekday': 'wed',
                                            },
                                        },
                                    ],
                                },
                                'samara': {'subscription_schedule': []},
                            },
                        },
                    },
                ),
            ],
            id='fail_custom_tariff_zone',
        ),
    ],
)
@pytest.mark.now(_NOW)
async def test_offers_subscription_time_validation(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        expected_button: Dict[str, Any],
        expected_offer_card: Dict[str, Any],
        expected_offer_screen_items: List[Dict[str, Any]],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = [
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': 'idempotency',
                'event_at': _NOW,
                'data': {
                    'driver': {
                        'park_id': 'park_id_0',
                        'driver_profile_id': 'uuid',
                    },
                    'mode': 'custom_orders',
                    'settings': None,
                },
            },
        ]
        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver, scenario.SAMARA_POSITION)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    offers_ui = {}
    for card in doc['ui']['items']:
        assert card['payload']['type'] == 'deeplink'
        link = card['payload']['url']
        link_name = _get_query_component(link)

        if link_name == 'orders':
            assert card == expected_offer_card

        meta = doc['driver_modes'][link_name]
        offers_ui[link_name] = meta['ui']

    assert offers_ui['orders']['accept_button'] == expected_button
    assert offers_ui['orders']['items'] == expected_offer_screen_items


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.geoareas(filename='geoareas_samara.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
        'orders': {
            'tariff_zones_settings': {
                '__default__': {
                    'subscription_schedule': [
                        {
                            'start': {'time': '00:00', 'weekday': 'wed'},
                            'stop': {'time': '23:00', 'weekday': 'wed'},
                        },
                    ],
                },
            },
            'time_zone': 'utc',
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize('trackstory_error', [False, True])
@pytest.mark.now(_NOW)
async def test_offers_subscription_time_trackstory_error(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        trackstory_error: bool,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = [
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': 'idempotency',
                'event_at': _NOW,
                'data': {
                    'driver': {
                        'park_id': 'park_id_0',
                        'driver_profile_id': 'uuid',
                    },
                    'mode': 'custom_orders',
                    'settings': None,
                },
            },
        ]
        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    if trackstory_error:
        scenario.Scene.mock_driver_trackstory(
            mockserver, None, scenario.ServiceError.ServerError,
        )
    else:
        scenario.Scene.mock_driver_trackstory(
            mockserver, None, scenario.ServiceError.NoError,
        )

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    offers_ui = {}
    for card in doc['ui']['items']:
        assert card['payload']['type'] == 'deeplink'
        link = card['payload']['url']
        link_name = _get_query_component(link)

        meta = doc['driver_modes'][link_name]
        del meta['ui']['items']
        offers_ui[link_name] = meta['ui']

    assert 'orders' not in offers_ui


_VIEW_OFFERS: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'За время',
            'subtitle': 'Доступен до 2 декабря',
            'description': 'Заработок зависит от времени работы',
            'is_new': True,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule1', 'shift_close_time': '00:01'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 1.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 1'}]},
    },
]

_EXPECTED_DRIVER_FIX_OFFER_CARD = {
    'horizontal_divider_type': 'none',
    'id': 'driver_fix_id_rule1',
    'item_divider_type': 'none',
    'items': [
        {
            'accent_title': True,
            'left_tip': {
                'background_color': '#E7E5E1',
                'form': 'round',
                'icon': {'icon_type': 'time', 'tint_color': '#21201F'},
                'size': 'mu_6',
            },
            'padding_type': 'none',
            'primary_text_size': 'title_small',
            'right_icon': 'navigate',
            'secondary_text_size': 'hint',
            'subtitle': 'Доступен до 2 декабря',
            'title': 'За время',
            'type': 'tip_detail',
        },
        {
            'max_lines': 3,
            'padding': 'small_bottom',
            'text': 'Заработок зависит от времени работы',
            'type': 'text',
        },
        {'title': 'Есть свободные места', 'type': 'detail'},
        {
            'type': 'multi_section',
            'orientation': 'vertical',
            'cross_axis_alignment': 'start',
            'items': [
                {
                    'type': 'detail',
                    'title': 'Сегодня, 1 мая',
                    'detail': '04:00 - 00:00',
                },
                {
                    'type': 'detail',
                    'title': 'Завтра, 2 мая',
                    'detail': '00:00 - 03:00',
                },
            ],
        },
    ],
    'orientation': 'vertical',
    'cross_axis_alignment': 'start',
    'payload': {
        'type': 'deeplink',
        'url': 'taximeter://screen/driver_mode?id=driver_fix_id_rule1',
    },
    'type': 'multi_section',
}


@pytest.mark.geoareas(filename='geoareas_samara.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                'driver_fix',
                features={
                    'driver_fix': {},
                    'booking': {'slot_policy': 'mode_settings_rule_id'},
                },
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
        'driver_fix': {
            'tariff_zones_settings': {
                '__default__': {
                    'subscription_schedule': [
                        {
                            'start': {'time': '00:00', 'weekday': 'wed'},
                            'stop': {'time': '23:00', 'weekday': 'wed'},
                        },
                    ],
                },
            },
            'time_zone': 'utc',
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now(_NOW)
async def test_offers_subscription_time_display_with_slots_info(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = [
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': 'idempotency',
                'event_at': _NOW,
                'data': {
                    'driver': {
                        'park_id': 'park_id_0',
                        'driver_profile_id': 'uuid',
                    },
                    'mode': 'custom_orders',
                    'settings': None,
                },
            },
        ]
        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver, scenario.SAMARA_POSITION)

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': _VIEW_OFFERS}

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    offers_ui = {}
    for card in doc['ui']['items']:
        assert card['payload']['type'] == 'deeplink'
        link = card['payload']['url']
        link_name = _get_query_component(link)

        if link_name == 'driver_fix_id_rule1':
            assert card == _EXPECTED_DRIVER_FIX_OFFER_CARD

        meta = doc['driver_modes'][link_name]
        offers_ui[link_name] = meta['ui']
