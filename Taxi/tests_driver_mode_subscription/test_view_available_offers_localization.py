from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()

_OFFER_CARD_TITLE = 'offer_card_title'
_OFFER_CARD_SUBTITLE = 'offer_card_subtitle'
_OFFER_CARD_DESCRIPTION = 'offer_card_description'
_OFFER_HEADER = 'offer_header'
_OFFER_TEXT = 'offer_text'
_MEMO_HEADER = 'memo_header'
_MEMO_TEXT = 'memo_text'

_DEFAULT_LOCALIZATION = {
    _OFFER_CARD_TITLE: 'Карточка.Заголовок(default)',
    _OFFER_CARD_SUBTITLE: 'Карточка.Подзаголовок(default)',
    _OFFER_CARD_DESCRIPTION: 'Карточка.Описание(default)',
    _OFFER_HEADER: 'Экран с предложением.Заголовок(default)',
    _OFFER_TEXT: 'Экран с предложением. Полный Текст(default)',
    _MEMO_HEADER: 'Экран с памяткой.Заголовок(default)',
    _MEMO_TEXT: 'Экран с памяткой. Основной текст(default)',
}

_CUSTOM_LOCALIZATION = {
    _OFFER_CARD_TITLE: 'Карточка.Заголовок(custom)',
    _OFFER_CARD_SUBTITLE: 'Карточка.Подзаголовок(custom)',
    _OFFER_CARD_DESCRIPTION: 'Карточка.Описание(custom)',
    _OFFER_HEADER: 'Экран с предложением.Заголовок(custom)',
    _OFFER_TEXT: 'Экран с предложением. Полный Текст(custom)',
    _MEMO_HEADER: 'Экран с памяткой.Заголовок(custom)',
    _MEMO_TEXT: 'Экран с памяткой. Основной текст(custom)',
}

_ORDERS_LOCALIZATION = {
    _OFFER_CARD_TITLE: 'За заказы',
    _OFFER_CARD_SUBTITLE: 'Всегда доступен',
    _OFFER_CARD_DESCRIPTION: 'Заработок зависит от числа выполненных заказов',
    _OFFER_HEADER: 'Заказы',
    _OFFER_TEXT: (
        'Режим дохода, в котором заработок зависит от числа'
        ' выполненных заказов. А еще:'
    ),
    _MEMO_HEADER: 'Включен режим дохода «Заказы»',
    _MEMO_TEXT: 'Как он работает:',
}

_ORDERS_LOCALIZATION_WITHOUT_SUBTITLE = {
    _OFFER_CARD_TITLE: 'За заказы',
    _OFFER_CARD_DESCRIPTION: 'Заработок зависит от числа выполненных заказов',
    _OFFER_HEADER: 'Заказы',
    _OFFER_TEXT: (
        'Режим дохода, в котором заработок зависит от числа'
        ' выполненных заказов. А еще:'
    ),
    _MEMO_HEADER: 'Включен режим дохода «Заказы»',
    _MEMO_TEXT: 'Как он работает:',
}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders_template': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix_template': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'custom_orders_template': (
                offer_templates.DEFAULT_CUSTOM_ORDERS_TEMPLATE
            ),
            'prefix_orders': offer_templates.build_orders_template(
                card_title='prefix_orders.offer_card.title',
                card_subtitle='prefix_orders.offer_card.subtitle',
                card_description='prefix_orders.offer_card.description',
                screen_header='prefix_orders.offer_screen.header',
                screen_description='prefix_orders.offer_screen.text',
                memo_header='prefix_orders.memo_screen.header',
                memo_description='prefix_orders.memo_screen.text',
            ),
            'orders_no_subtitle': (
                offer_templates.build_orders_template(
                    card_title='offer_card.orders_title',
                    card_subtitle=None,
                    card_description='offer_card.orders_description',
                    screen_header='orders_offer_screen.header',
                    screen_description='orders_offer_screen.text',
                    memo_header='orders_memo_screen.header',
                    memo_description='orders_memo_screen.text',
                )
            ),
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'current_mode, work_mode, expected_localization',
    [
        pytest.param(
            'orders',
            'custom_orders',
            _DEFAULT_LOCALIZATION,
            id='default_param_custom_orders',
        ),
        pytest.param(
            'custom_orders',
            'orders',
            _ORDERS_LOCALIZATION,
            id='default param orders',
        ),
        pytest.param(
            'orders',
            'custom_orders',
            _DEFAULT_LOCALIZATION,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {
                            'orders': 'prefix_orders',
                            'driver_fix': 'driver_fix_template',
                            'custom_orders': 'custom_orders_template',
                            'geobooking': 'geobooking_template',
                        },
                    },
                ),
            ],
            id='default empty fallback',
        ),
        pytest.param(
            'orders',
            'custom_orders',
            _CUSTOM_LOCALIZATION,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {
                            'orders': 'prefix_orders',
                            'driver_fix': 'driver_fix_template',
                            'custom_orders': 'prefix_orders',
                            'geobooking': 'geobooking_template',
                        },
                    },
                ),
            ],
            id='different prefix',
        ),
        pytest.param(
            'orders',
            'custom_orders',
            _CUSTOM_LOCALIZATION,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {
                            'orders': 'prefix_orders',
                            'driver_fix': 'driver_fix_template',
                            'custom_orders': 'prefix_orders',
                            'geobooking': 'geobooking_template',
                        },
                    },
                ),
            ],
            id='bad prefix',
        ),
        pytest.param(
            'orders',
            'custom_orders',
            _ORDERS_LOCALIZATION,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {
                            'orders': 'orders_template',
                            'driver_fix': 'driver_fix_template',
                            'custom_orders': 'orders_template',
                            'geobooking': 'geobooking_template',
                        },
                    },
                ),
            ],
            id='override',
        ),
        pytest.param(
            'orders',
            'custom_orders',
            _ORDERS_LOCALIZATION_WITHOUT_SUBTITLE,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {
                            'orders': 'orders_template',
                            'driver_fix': 'driver_fix_template',
                            'custom_orders': 'orders_no_subtitle',
                            'geobooking': 'geobooking_template',
                        },
                    },
                ),
            ],
            id='disable_subtitle',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_localization_config_fallbacks(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        current_mode: str,
        work_mode: str,
        expected_localization,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, current_mode, mocked_time,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    offer_item_ui = doc['ui']['items'][1]

    assert (
        offer_item_ui['items'][0]['title']
        == expected_localization[_OFFER_CARD_TITLE]
    )
    assert offer_item_ui['items'][0].get(
        'subtitle',
    ) == expected_localization.get(_OFFER_CARD_SUBTITLE)
    assert (
        offer_item_ui['items'][1]['text']
        == expected_localization[_OFFER_CARD_DESCRIPTION]
    )

    offer_ui = doc['driver_modes'][work_mode]['ui']

    assert (
        offer_ui['items'][0]['subtitle']
        == expected_localization[_OFFER_HEADER]
    )
    assert offer_ui['items'][1]['text'] == expected_localization[_OFFER_TEXT]

    memo_ui = doc['driver_modes'][work_mode]['memo_ui']

    assert memo_ui['items'][1]['text'] == expected_localization[_MEMO_TEXT]
    assert (
        memo_ui['items'][0]['subtitle'] == expected_localization[_MEMO_HEADER]
    )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders_template': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix_template': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'custom_orders_template': (
                offer_templates.DEFAULT_CUSTOM_ORDERS_TEMPLATE
            ),
            'prefix_bad': offer_templates.build_orders_template(
                card_title='bad.offer_card.title',
                card_subtitle='bad.offer_card.subtitle',
                card_description='bad.offer_card.description',
                screen_header='bad.offer_screen.header',
                screen_description='bad.offer_screen.text',
                memo_header='bad.memo_screen.header',
                memo_description='bad.memo_screen.text',
            ),
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'expected_item_count',
    [
        pytest.param(2, id='default'),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
                        'by_mode_class': {},
                        'by_work_mode': {
                            'orders': 'orders_template',
                            'driver_fix': 'driver_fix_template',
                            'custom_orders': 'prefix_bad',
                            'geobooking': 'geobooking_template',
                        },
                    },
                ),
            ],
            id='skip custom_orders due missing localization',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_localization_skip_bad(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        expected_item_count: int,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    assert len(doc['ui']['items']) == expected_item_count


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


_DEFAULT_ACCEPT_WARNING_KEYS = {
    'orders': {'__prefix__': ''},
    '__default__': {
        _OFFER_CARD_TITLE: 'offer_card.orders_title',
        _OFFER_CARD_SUBTITLE: 'offer_card.orders_subtitle',
        _OFFER_CARD_DESCRIPTION: 'offer_card.orders_description',
        _OFFER_HEADER: 'orders_offer_screen.header',
        _OFFER_TEXT: 'orders_offer_screen.text',
        _MEMO_HEADER: 'orders_memo_screen.header',
        _MEMO_TEXT: 'orders_memo_screen.text',
    },
}


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ENABLE_ACCEPT_WARNING=True,
    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
        '__default__': {
            'restrictions': [],
            'warnings': {
                'title': 'accept_warning.title',
                'message': 'accept_warning.message',
                'accept': 'accept_warning.accept',
                'reject': 'accept_warning.reject',
            },
        },
        'driver_fix': {
            'restrictions': [
                {
                    'interval_type': 'hourly',
                    'interval_count': 1,
                    'max_change_count': 1,
                },
            ],
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'expected_warning',
    [
        pytest.param(
            dict(
                {
                    'title': 'Точно хотите выбрать этот режим дохода?',
                    'message': (
                        'Вернуться в текущий режим вы сможете только'
                        ' через 1 часов'
                    ),
                    'accept_button_title': 'Хочу сменить',
                    'reject_button_title': 'Останусь',
                },
            ),
            id='default',
        ),
        pytest.param(
            dict(
                {
                    'title': 'Точно хотите выбрать этот режим дохода?(custom)',
                    'message': (
                        'Вернуться в текущий режим вы сможете только'
                        ' через 1 часов(custom)'
                    ),
                    'accept_button_title': 'Хочу сменить',
                    'reject_button_title': 'Останусь',
                },
            ),
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {
                            'restrictions': [],
                            'warnings': {
                                'title': 'accept_warning.title',
                                'message': 'accept_warning.message',
                                'accept': 'accept_warning.accept',
                                'reject': 'accept_warning.reject',
                            },
                        },
                        'driver_fix': {
                            'restrictions': [
                                {
                                    'interval_type': 'hourly',
                                    'interval_count': 1,
                                    'max_change_count': 1,
                                },
                            ],
                            'warnings': {
                                'title': 'accept_warning.title_custom',
                                'message': 'accept_warning.message_custom',
                                'accept': 'accept_warning.accept',
                                'reject': 'accept_warning.reject',
                            },
                        },
                    },
                ),
            ],
            id='custom',
        ),
        pytest.param(
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {'restrictions': []},
                    },
                ),
            ],
            id='no_check',
        ),
        pytest.param(
            dict(
                {
                    'title': 'Точно хотите выбрать этот режим дохода?',
                    'message': (
                        'Вернуться в текущий режим вы сможете только'
                        ' через 12 часов'
                    ),
                    'accept_button_title': 'Хочу сменить',
                    'reject_button_title': 'Останусь',
                },
            ),
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {
                            'restrictions': [],
                            'warnings': {
                                'title': 'accept_warning.title',
                                'message': 'accept_warning.message',
                                'accept': 'accept_warning.accept',
                                'reject': 'accept_warning.reject',
                            },
                        },
                        'driver_fix': {
                            'restrictions': [
                                {
                                    'interval_type': 'dayly',
                                    'interval_count': 1,
                                    'max_change_count': 1,
                                },
                            ],
                        },
                    },
                ),
            ],
            id='check_days',
        ),
        pytest.param(
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {'restrictions': []},
                        'driver_fix': {
                            'restrictions': [
                                {
                                    'interval_type': 'hourly',
                                    'interval_count': 1,
                                    'max_change_count': 1,
                                },
                            ],
                        },
                    },
                ),
            ],
            id='no_key_in_config',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_accept_warning_localization(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        expected_warning,
):
    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': _VIEW_OFFERS}

    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        reports = [
            ('2019-05-01T11:32:00+0300', 'driver_fix'),
            ('2019-05-01T11:31:00+0300', 'orders'),
            ('2019-05-01T11:30:00+0300', 'driver_fix'),
        ]
        for occured, mode in reports:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'dbid',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': 'id_rule1',
                            'shift_close_time': '00:01',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile, scenario.MOSCOW_POSITION,
    )
    assert response.status_code == 200

    doc = response.json()
    warning = doc['driver_modes']['orders']['ui']['accept_button'].get(
        'warning',
    )
    assert warning == expected_warning
