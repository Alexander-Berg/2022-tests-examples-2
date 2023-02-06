# pylint: disable=C0302
import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_NOW = datetime.datetime.fromisoformat('2019-05-01T12:00:00+03:00')
_LONG_AGO = datetime.datetime.fromisoformat('2010-05-01T12:00:00+03:00')

_BACKGROUND_COLOR_YELLOW = '#FCB000'
_BACKGROUND_COLOR_GRAY = '#E7E5E1'

_FOREGROUND_COLOR_DARK_GRAY = '#75736F'
_FOREGROUND_COLOR_LIGHT_GRAY = '#9E9B98'


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[mode_rules.Patch('driver_fix', stops_at=_LONG_AGO)],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'custom_orders': {
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
                        {
                            'data': {'text': 'orders_memo_screen.header'},
                            'type': 'header',
                        },
                        {
                            'data': {'text': 'orders_memo_screen.text'},
                            'type': 'multi_paragraph_text',
                        },
                    ],
                    'memo_bottom_items': [
                        {
                            'type': 'button',
                            'data': {
                                'button_text': 'memo_screen.button_title',
                                'deeplink': 'taximeter://screen/driver-modes',
                            },
                        },
                    ],
                    'screen_items': [
                        {
                            'data': {'text': 'orders_offer_screen.header'},
                            'type': 'header',
                        },
                        {
                            'data': {'text': 'orders_offer_screen.text'},
                            'type': 'multi_paragraph_text',
                        },
                        {'type': 'subscription_time_info'},
                        {
                            'type': 'bullet_list',
                            'data': {
                                'title': (
                                    'custom_orders.offer_screen.'
                                    'offer_options_group_title'
                                ),
                                'items': [
                                    {
                                        'icon_type': 'check',
                                        'title': (
                                            'custom_orders.offer_screen.'
                                            'offer_options_option1_title'
                                        ),
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': (
                                            'custom_orders.offer_screen.'
                                            'offer_options_option2_title'
                                        ),
                                        'subtitle': (
                                            'custom_orders.offer_screen.'
                                            'offer_options_option2_subtitle'
                                        ),
                                    },
                                    {
                                        'icon_type': 'warning',
                                        'title': (
                                            'custom_orders.offer_screen.'
                                            'offer_options_option1_title'
                                        ),
                                    },
                                ],
                            },
                        },
                        {
                            'type': 'details_button',
                            'data': {
                                'button_text': (
                                    'custom_orders.offer_screen.'
                                    'detail_button_title'
                                ),
                                'payload_url': 'http://yandex.ru',
                                'payload_title': (
                                    'custom_orders.offer_screen.'
                                    'detail_payload_title'
                                ),
                            },
                        },
                    ],
                },
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders',
            'driver_fix': 'driver_fix',
            'custom_orders': 'custom_orders',
        },
    },
)
@pytest.mark.now(_NOW.isoformat())
async def test_offer_screen_config(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    orders_ui = doc['driver_modes']['orders']['ui']['items']
    custom_orders_ui = doc['driver_modes']['custom_orders']['ui']['items']

    assert orders_ui == [
        {
            'type': 'header',
            'horizontal_divider_type': 'none',
            'subtitle': 'Заказы',
            'gravity': 'left',
        },
        {
            'type': 'text',
            'horizontal_divider_type': 'none',
            'text': (
                'Режим дохода, в котором заработок зависит от числа '
                'выполненных заказов. А еще:'
            ),
            'padding': 'small_bottom',
        },
        {
            'type': 'text',
            'horizontal_divider_type': 'none',
            'text': '— Вы сами выбираете удобные тарифы и способы оплаты.',
            'padding': 'small_bottom',
        },
        {
            'type': 'text',
            'horizontal_divider_type': 'none',
            'text': '— Доступен в любом регионе.',
            'padding': 'small_bottom',
        },
    ]

    assert custom_orders_ui == orders_ui + [
        # gap
        {'type': 'title'},
        # offer description
        {'type': 'icon_title', 'title': 'Что в режиме?'},
        {
            'type': 'tip_detail',
            'title': 'Бонусы выше',
            'left_tip': {
                'icon': {
                    'icon_type': 'check',
                    'tint_color': _FOREGROUND_COLOR_DARK_GRAY,
                },
                'background_color': _BACKGROUND_COLOR_YELLOW,
            },
            'horizontal_divider_type': 'bottom_gap',
        },
        {
            'type': 'tip_detail',
            'title': 'Нет точки Б',
            'subtitle': (
                'Точка Б недоступна даже для водителей золота и платины'
            ),
            'left_tip': {
                'icon': {
                    'icon_type': 'cross',
                    'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
                },
                'background_color': _BACKGROUND_COLOR_GRAY,
            },
            'horizontal_divider_type': 'bottom_gap',
        },
        {
            'type': 'tip_detail',
            'title': 'Бонусы выше',
            'left_tip': {
                'icon': {
                    'icon_type': 'warning4',
                    'tint_color': _FOREGROUND_COLOR_DARK_GRAY,
                },
                'background_color': _BACKGROUND_COLOR_YELLOW,
            },
            'horizontal_divider_type': 'none',
        },
        # gap
        {'type': 'title'},
        # details link button
        {
            'horizontal_divider_type': 'none',
            'id': 'full_description',
            'payload': {
                'title': 'Заголовок экрана полного описания',
                'type': 'navigate_url',
                'url': 'http://yandex.ru',
            },
            'right_icon': 'navigate',
            'title': 'Полное описание',
            'type': 'detail',
        },
    ]

    assert doc['driver_modes']['custom_orders']['memo_ui']['bottom_items'] == [
        {
            'type': 'button',
            'title': 'Понятно',
            'accent': True,
            'horizontal_divider_type': 'none',
            'payload': {
                'type': 'deeplink',
                'url': 'taximeter://screen/driver-modes',
            },
        },
    ]


_LIST_ITEM_ANY_OF_CONDITION = {
    'key': 'custom_orders.offer_screen.offer_options_option2_title',
    'title': 'Нет точки Б',
    'condition': {
        'available_modes': {
            'any_of': ['freemode_with_point_b', 'nonexisting_mode'],
        },
    },
}

_LIST_ITEM_NONE_OF_CONDITION = {
    'key': 'custom_orders.offer_screen.offer_options_option3_title',
    'title': 'Нет точки В',
    'condition': {
        'available_modes': {
            'none_of': ['freemode_with_point_b', 'nonexisting_mode'],
        },
    },
}

_LIST_ITEM_ALL_OF_CONDITION = {
    'key': 'custom_orders.offer_screen.offer_options_option4_title',
    'title': 'Нет точки Г',
    'condition': {
        'available_modes': {'all_of': ['freemode_with_point_b', 'orders']},
    },
}

_LIST_ITEM_AND_CONDITION = {
    'key': 'custom_orders.offer_screen.offer_options_option5_title',
    'title': 'Нет точки Д',
    'condition': {
        'and': [
            {'available_modes': {'none_of': ['nonexisting_mode']}},
            {
                'available_modes': {
                    'all_of': ['freemode_with_point_b', 'orders'],
                },
            },
        ],
    },
}

_LIST_ITEM_OR_CONDITION = {
    'key': 'custom_orders.offer_screen.offer_options_option6_title',
    'title': 'Нет точки Е',
    'condition': {
        'or': [
            {'available_modes': {'all_of': ['nonexisting_mode']}},
            {
                'available_modes': {
                    'all_of': ['freemode_with_point_b', 'orders'],
                },
            },
        ],
    },
}

_LIST_ITEM_MODE_CLASS_CONDITION = {
    'key': 'custom_orders.offer_screen.offer_options_option7_title',
    'title': 'Нет точки Ё',
    'condition': {'available_mode_classes': {'all_of': ['flexible']}},
}


_BULLET_LIST_1: List[Dict[str, Any]] = [
    {'type': 'icon_title', 'title': 'Что в режиме?'},
    {
        'type': 'tip_detail',
        'title': 'Бонусы выше',
        'left_tip': {
            'icon': {
                'icon_type': 'check',
                'tint_color': _FOREGROUND_COLOR_DARK_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_YELLOW,
        },
        'horizontal_divider_type': 'bottom_gap',
    },
    {
        'type': 'tip_detail',
        'title': _LIST_ITEM_NONE_OF_CONDITION['title'],
        'left_tip': {
            'icon': {
                'icon_type': 'cross',
                'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_GRAY,
        },
        'horizontal_divider_type': 'none',
    },
]

_BULLET_LIST_2: List[Dict[str, Any]] = [
    {'type': 'icon_title', 'title': 'Что в режиме?'},
    {
        'type': 'tip_detail',
        'title': 'Бонусы выше',
        'left_tip': {
            'icon': {
                'icon_type': 'check',
                'tint_color': _FOREGROUND_COLOR_DARK_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_YELLOW,
        },
        'horizontal_divider_type': 'bottom_gap',
    },
    {
        'type': 'tip_detail',
        'title': _LIST_ITEM_ANY_OF_CONDITION['title'],
        'left_tip': {
            'icon': {
                'icon_type': 'cross',
                'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_GRAY,
        },
        'horizontal_divider_type': 'bottom_gap',
    },
    {
        'type': 'tip_detail',
        'title': _LIST_ITEM_ALL_OF_CONDITION['title'],
        'left_tip': {
            'icon': {
                'icon_type': 'cross',
                'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_GRAY,
        },
        'horizontal_divider_type': 'bottom_gap',
    },
    {
        'type': 'tip_detail',
        'title': _LIST_ITEM_AND_CONDITION['title'],
        'left_tip': {
            'icon': {
                'icon_type': 'cross',
                'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_GRAY,
        },
        'horizontal_divider_type': 'bottom_gap',
    },
    {
        'type': 'tip_detail',
        'title': _LIST_ITEM_OR_CONDITION['title'],
        'left_tip': {
            'icon': {
                'icon_type': 'cross',
                'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_GRAY,
        },
        'horizontal_divider_type': 'bottom_gap',
    },
    {
        'type': 'tip_detail',
        'title': _LIST_ITEM_MODE_CLASS_CONDITION['title'],
        'left_tip': {
            'icon': {
                'icon_type': 'cross',
                'tint_color': _FOREGROUND_COLOR_LIGHT_GRAY,
            },
            'background_color': _BACKGROUND_COLOR_GRAY,
        },
        'horizontal_divider_type': 'none',
    },
]


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch('driver_fix', stops_at=_LONG_AGO),
                mode_rules.Patch('freemode_with_point_b'),
            ],
            mode_classes=[
                mode_rules.ModeClass('flexible', ['freemode_with_point_b']),
            ],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'custom_orders': {
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
                        {
                            'data': {'text': 'orders_memo_screen.header'},
                            'type': 'header',
                        },
                        {
                            'data': {'text': 'orders_memo_screen.text'},
                            'type': 'multi_paragraph_text',
                        },
                    ],
                    'screen_items': [
                        {
                            'data': {'text': 'orders_offer_screen.header'},
                            'type': 'header',
                        },
                        {
                            'data': {'text': 'orders_offer_screen.text'},
                            'type': 'multi_paragraph_text',
                        },
                        {'type': 'subscription_time_info'},
                        {
                            'type': 'conditional_text',
                            'data': {
                                'text': (
                                    'orders_offer_screen.'
                                    'no_point_b_bullet_text'
                                ),
                                'condition': {
                                    'available_modes': {
                                        'any_of': ['freemode_with_point_b'],
                                    },
                                },
                            },
                        },
                        {
                            'type': 'bullet_list',
                            'data': {
                                'title': (
                                    'custom_orders.offer_screen.'
                                    'offer_options_group_title'
                                ),
                                'items': [
                                    {
                                        'icon_type': 'check',
                                        'title': (
                                            'custom_orders.offer_screen.'
                                            'offer_options_option1_title'
                                        ),
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': _LIST_ITEM_ANY_OF_CONDITION[
                                            'key'
                                        ],
                                        'condition': (
                                            _LIST_ITEM_ANY_OF_CONDITION[
                                                'condition'
                                            ]
                                        ),
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': _LIST_ITEM_NONE_OF_CONDITION[
                                            'key'
                                        ],
                                        'condition': (
                                            _LIST_ITEM_NONE_OF_CONDITION[
                                                'condition'
                                            ]
                                        ),
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': _LIST_ITEM_ALL_OF_CONDITION[
                                            'key'
                                        ],
                                        'condition': (
                                            _LIST_ITEM_ALL_OF_CONDITION[
                                                'condition'
                                            ]
                                        ),
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': _LIST_ITEM_AND_CONDITION[
                                            'key'
                                        ],
                                        'condition': _LIST_ITEM_AND_CONDITION[
                                            'condition'
                                        ],
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': _LIST_ITEM_OR_CONDITION[
                                            'key'
                                        ],
                                        'condition': _LIST_ITEM_OR_CONDITION[
                                            'condition'
                                        ],
                                    },
                                    {
                                        'icon_type': 'cross',
                                        'title': (
                                            _LIST_ITEM_MODE_CLASS_CONDITION[
                                                'key'
                                            ]
                                        ),
                                        'condition': (
                                            _LIST_ITEM_MODE_CLASS_CONDITION[
                                                'condition'
                                            ]
                                        ),
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'custom_orders',
            'driver_fix': 'driver_fix',
            'custom_orders': 'orders',
            'freemode_with_point_b': 'orders',
        },
    },
)
@pytest.mark.parametrize(
    'is_point_b_warning_expected',
    [
        pytest.param(True),
        pytest.param(
            False,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_LONG_AGO),
                            mode_rules.Patch(
                                'freemode_with_point_b', stops_at=_LONG_AGO,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_offer_screen_conditional_items(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        is_point_b_warning_expected: bool,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    orders_ui = doc['driver_modes']['orders']['ui']['items']

    expected_orders_ui: List[Dict[str, Any]] = [
        {
            'type': 'header',
            'horizontal_divider_type': 'none',
            'subtitle': 'Заказы',
            'gravity': 'left',
        },
        {
            'type': 'text',
            'horizontal_divider_type': 'none',
            'text': (
                'Режим дохода, в котором заработок зависит от числа '
                'выполненных заказов. А еще:'
            ),
            'padding': 'small_bottom',
        },
        {
            'type': 'text',
            'horizontal_divider_type': 'none',
            'text': '— Вы сами выбираете удобные тарифы и способы оплаты.',
            'padding': 'small_bottom',
        },
        {
            'type': 'text',
            'horizontal_divider_type': 'none',
            'text': '— Доступен в любом регионе.',
            'padding': 'small_bottom',
        },
    ]

    if is_point_b_warning_expected:
        expected_orders_ui += [
            {
                'type': 'text',
                'horizontal_divider_type': 'none',
                'text': 'Недоступна точка Б.',
                'padding': 'small_bottom',
            },
        ]

    # gap
    expected_orders_ui.append({'type': 'title'})

    if is_point_b_warning_expected:
        expected_orders_ui += _BULLET_LIST_2
    else:
        expected_orders_ui += _BULLET_LIST_1

    assert orders_ui == expected_orders_ui


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[mode_rules.Patch('driver_fix', stops_at=_LONG_AGO)],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders_template': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix_template': (
                offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE
            ),
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'custom_orders_template': offer_templates.build_orders_template(
                card_title='offer_card.title',
                card_description='offer_card.title',
                card_subtitle='bad_title',
                screen_header='offer_card.title',
                screen_description='offer_card.title',
                memo_header='offer_card.title',
                memo_description='offer_card.title',
            ),
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'expected_http_code, expect_template_search_error',
    [
        pytest.param(200, False, id='check_disabled_config_enabled'),
        pytest.param(
            500,
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {},
                    },
                ),
            ],
            id='not_found',
        ),
    ],
)
async def test_offer_templates_checking(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        expected_http_code: int,
        expect_template_search_error: bool,
):
    profile = driver.Profile('dbid_uuid')
    scene = scenario.Scene({profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time)

    async with taxi_driver_mode_subscription.capture_logs() as capture:
        response = await common.get_available_offers(
            taxi_driver_mode_subscription, profile,
        )

        assert response.status_code == expected_http_code

    search_error = capture.select(
        link=response.headers['x-yarequestid'],
        text='template for work mode custom_orders not found',
    )

    if expect_template_search_error:
        assert search_error
    else:
        assert not search_error


_ORDERS_OFFER_CARD_HEADER = {
    'data': {
        'description': 'offer_card.orders_description',
        'icon_type': 'passenger',
        'subtitle': 'offer_card.orders_subtitle',
    },
    'type': 'card_header',
}

_ORDERS_OFFER_SCREEN_HEADER = {
    'data': {'text': 'orders_offer_screen.header'},
    'type': 'header',
}


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('driver_fix', stops_at=_LONG_AGO),
            mode_rules.Patch('custom_orders'),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders',
            'driver_fix': 'driver_fix',
            'custom_orders': 'custom_orders',
        },
    },
)
@pytest.mark.parametrize(
    'expect_custom_orders_offer',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
                            'driver_fix': (
                                offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE
                            ),
                            'custom_orders': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [_ORDERS_OFFER_CARD_HEADER],
                                    'memo_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                    'screen_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='ok',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
                            'driver_fix': (
                                offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE
                            ),
                            'custom_orders': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [
                                        {'type': 'booking_info'},
                                        _ORDERS_OFFER_CARD_HEADER,
                                    ],
                                    'memo_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                    'screen_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='wrong_order',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
                            'driver_fix': (
                                offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE
                            ),
                            'custom_orders': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [],
                                    'memo_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                    'screen_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='empty_card',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
                            'driver_fix': (
                                offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE
                            ),
                            'custom_orders': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [_ORDERS_OFFER_CARD_HEADER],
                                    'memo_items': [],
                                    'screen_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                },
                            },
                        },
                    },
                ),
            ],
            id='empty_memo',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
                        'templates': {
                            'orders': offer_templates.DEFAULT_ORDERS_TEMPLATE,
                            'driver_fix': (
                                offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE
                            ),
                            'custom_orders': {
                                'model': {'title': 'offer_card.orders_title'},
                                'schema': {
                                    'card_items': [_ORDERS_OFFER_CARD_HEADER],
                                    'memo_items': [
                                        _ORDERS_OFFER_SCREEN_HEADER,
                                    ],
                                    'screen_items': [],
                                },
                            },
                        },
                    },
                ),
            ],
            id='empty_screen',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_blank_template(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        expect_custom_orders_offer: bool,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    if not expect_custom_orders_offer:
        assert 'custom_orders' not in doc['driver_modes']
    else:
        assert 'custom_orders' in doc['driver_modes']
