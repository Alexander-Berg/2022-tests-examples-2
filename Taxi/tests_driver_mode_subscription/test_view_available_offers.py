# pylint: disable=C0302
# flake8: noqa
import copy
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import offer_templates

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()
_DRIVER_MODE_RULES_WITHOUT_CUSTOM = mode_rules.patched(
    patches=[
        mode_rules.Patch(
            rule_name='custom_orders',
            stops_at=datetime.datetime.fromisoformat(
                '2000-05-01T05:00:00+00:00',
            ),
        ),
    ],
)

_MODE_TEMPLATE_RELATIONS = {
    'by_mode_class': {},
    'by_work_mode': {
        'orders': 'orders_template',
        'driver_fix': 'driver_fix_template',
        'custom_orders': 'orders_template',
        'geobooking': 'geobooking_template',
    },
}

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
    {
        'offer_card': {
            'title': 'За время',
            'subtitle': 'Был доступен до 15 ноября',
            'description': 'Заработок зависит от времени работы',
            'is_new': False,
            'enabled': False,
            'disable_reason': 'Был доступен до 15 ноября',
        },
        'settings': {'rule_id': 'id_rule2', 'shift_close_time': '00:02'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
]

_VIEW_OFFERS_FOR_TIME_CHECK: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'За время 1',
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
    {
        'offer_card': {
            'title': 'За время 2',
            'subtitle': 'Доступен до 2 декабря',
            'description': 'Заработок зависит от времени работы',
            'is_new': True,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule2', 'shift_close_time': '00:02'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
    {
        'offer_card': {
            'title': 'Текущий режим',
            'subtitle': 'Доступен до 2 декабря',
            'description': 'Заработок зависит от времени работы',
            'is_new': True,
            'enabled': True,
        },
        'settings': {'rule_id': 'current_rule', 'shift_close_time': '00:02'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
]


def _set_mode_settings(response, rule_id):
    data = response['docs'][0]['data']
    if rule_id:
        data['settings'] = common.MODE_SETTINGS
        data['settings']['rule_id'] = rule_id


class DriverFixContext:
    def __init__(self):
        self.offers = _VIEW_OFFERS
        self.check_rule_id = False
        self.expected_rule_id: Optional[str] = None

    def set_offers(self, offers: List[Dict[str, Any]]):
        self.offers = offers

    def expect_rule_id(self, rule_id: Optional[str]):
        self.check_rule_id = True
        self.expected_rule_id = rule_id


@pytest.fixture(name='driver_fix_context')
def _driver_fix_context():
    return DriverFixContext()


@pytest.fixture(name='driver_fix')
def _mock_driver_fix(mockserver, driver_fix_context):
    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        doc = request.json
        assert doc['park_id'] == 'dbid'
        assert doc['driver_profile_id'] == 'uuid'
        if driver_fix_context.check_rule_id:
            if driver_fix_context.expected_rule_id:
                assert 'current_mode_settings' in doc
                assert (
                    doc['current_mode_settings']['rule_id']
                    == driver_fix_context.expected_rule_id
                )
            else:
                assert 'current_mode_settings' not in doc
        return {'offers': driver_fix_context.offers}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES_WITHOUT_CUSTOM)
@pytest.mark.parametrize(
    'mode, rule_id, expected_first_title, expected_mode_count',
    [
        pytest.param('driver_fix', 'id_rule1', 'За время', 3, id='driver_fix'),
        pytest.param('orders', None, 'За заказы', 3, id='orders'),
        pytest.param(None, None, 'За заказы', 3, id='None'),
        pytest.param(
            'custom_orders',
            None,
            'Карточка.Заголовок(default)',
            4,
            id='custom_orders customs off, but current not fail',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_mode(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        mode: str,
        rule_id: str,
        expected_first_title: str,
        expected_mode_count: int,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        if mode:
            response = common.mode_history_response(request, mode, mocked_time)
            _set_mode_settings(response, rule_id)
            return response
        common.mode_history_response(request, 'orders', mocked_time)
        return {'docs': [], 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200

    doc = response.json()
    ctor = doc['ui']['items']
    assert len(ctor) == expected_mode_count
    assert ctor[0]['items'][0]['type'] == 'tip_detail'
    assert ctor[0]['items'][0]['title'] == expected_first_title
    assert response.headers['X-Polling-Delay'] == '600'


_EMPTY_MODE_TEMPLATE_RELATIONS: Dict[str, Any] = {
    'by_mode_class': {},
    'by_work_mode': {},
}


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'card_number, expected_ctor_json',
    [
        (0, 'expected_card_offer_active.json'),
        (1, 'expected_card_offer_enabled.json'),
        (2, 'expected_card_offer_custom_enabled.json'),
        (3, 'expected_card_offer_disabled.json'),
    ],
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_card_constructor(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        load_json,
        card_number,
        expected_ctor_json,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'driver_fix', mocked_time,
        )
        _set_mode_settings(response, 'id_rule1')
        return response

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200

    doc = response.json()
    card_ctor = doc['ui']['items'][card_number]

    # in this test we interest only in UI-fields
    del card_ctor['payload']

    expected_ctor = load_json(expected_ctor_json)
    assert card_ctor == expected_ctor


def _get_query_component(url):
    pattern = '?id='
    i = url.rfind(pattern)
    return url[i + len(pattern) :]


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'card_number, expected_details_ui',
    [
        (0, 'expected_orders_offer_screen.json'),
        (1, _VIEW_OFFERS[0]['offer_screen']),
        (2, 'expected_custom_orders_offer_screen.json'),
        (3, _VIEW_OFFERS[1]['offer_screen']),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_details_screen_ui_items(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        load_json,
        card_number,
        expected_details_ui,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return {'docs': [], 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc['ui']['items'][card_number]['payload']['type'] == 'deeplink'
    link = doc['ui']['items'][card_number]['payload']['url']
    link_name = _get_query_component(link)
    details_ui = doc['driver_modes'][link_name]['ui']['items']

    if isinstance(expected_details_ui, str):
        expected_ui = load_json(expected_details_ui)
    else:
        expected_ui = expected_details_ui
    assert details_ui == expected_ui['items']


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'card_number, expected_deeplink_name, expected_meta',
    [
        (
            0,
            'orders',
            {
                'mode_type': 'orders_type',
                'mode_id': 'orders',
                'is_new': False,
                'is_selected': True,
                'ui': {
                    'accept_button': {
                        'title': 'Режим уже выбран',
                        'enabled': False,
                    },
                },
            },
        ),
        (
            1,
            'driver_fix_id_rule1',
            {
                'mode_type': 'driver_fix_type',
                'mode_id': 'driver_fix',
                'mode_settings': _VIEW_OFFERS[0]['settings'],
                'is_new': True,
                'is_selected': False,
                'ui': {'accept_button': {'title': 'Выбрать', 'enabled': True}},
            },
        ),
        (
            2,
            'custom_orders',
            {
                'mode_type': 'orders_type',
                'mode_id': 'custom_orders',
                'is_new': False,
                'is_selected': False,
                'ui': {'accept_button': {'title': 'Выбрать', 'enabled': True}},
            },
        ),
        (
            3,
            'driver_fix_id_rule2',
            {
                'mode_type': 'driver_fix_type',
                'mode_id': 'driver_fix',
                'mode_settings': _VIEW_OFFERS[1]['settings'],
                'is_new': False,
                'is_selected': False,
                'ui': {
                    'accept_button': {
                        'title': _VIEW_OFFERS[1]['offer_card'][
                            'disable_reason'
                        ],
                        'enabled': False,
                    },
                },
            },
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_details_screen_ui_metainfo(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        card_number,
        expected_deeplink_name,
        expected_meta,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return {'docs': [], 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc['ui']['items'][card_number]['payload']['type'] == 'deeplink'
    link = doc['ui']['items'][card_number]['payload']['url']
    link_name = _get_query_component(link)
    assert link_name == expected_deeplink_name

    assert link_name in doc['driver_modes']
    meta = doc['driver_modes'][link_name]
    # no interest in UI-fields in this test
    del meta['ui']['items']
    del meta['memo_ui']
    assert meta == expected_meta


PROMO_ENABLED = {
    'promo': {
        'promo_id': 'driver_fix_first_promo',
        'mode_id': 'driver_fix',
        'title_tanker_key': 'promo.title',
        'description_tanker_key': 'promo.description',
        'numbered_list_tanker_keys': [
            'promo.money_for_time_on_line',
            'promo.no_risks',
            'promo.higher_income',
        ],
        'button_title_tanker_key': 'promo.button_detailed',
        'image_url': 'promo_image.png',
    },
}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'driver_mode_id, expected_memo_ui',
    [
        ('orders', 'expected_orders_memo_screen.json'),
        ('driver_fix_id_rule1', _VIEW_OFFERS[0]['memo_screen']),
        ('custom_orders', 'expected_custom_orders_memo_screen.json'),
        ('driver_fix_id_rule2', _VIEW_OFFERS[1]['memo_screen']),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_memo_screen(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        load_json,
        driver_mode_id,
        expected_memo_ui,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return {'docs': [], 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    memo_ui = doc['driver_modes'][driver_mode_id]['memo_ui']

    if isinstance(expected_memo_ui, str):
        expected_ui = load_json(expected_memo_ui)
    else:
        expected_ui = expected_memo_ui

    assert memo_ui['items'] == expected_ui['items']

    if 'bottom_items' in expected_ui:
        expected_bottom_items = expected_ui['bottom_items']
    else:
        expected_bottom_items = [
            {
                'type': 'button',
                'title': 'Понятно',
                'accent': True,
                'horizontal_divider_type': 'none',
                'payload': {
                    'type': 'deeplink',
                    'url': 'taximeter://screen/main',
                },
            },
        ]
    assert memo_ui['bottom_items'] == expected_bottom_items


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES_WITHOUT_CUSTOM)
@pytest.mark.config(
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
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.parametrize(
    'card_number, rule, expected_ui, reports, expected_requests',
    [
        (
            0,
            'id_rule1',
            {'accept_button': {'title': 'Режим уже выбран', 'enabled': False}},
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix'),
                ('2019-05-01T11:31:00+0300', 'orders'),
                ('2019-05-01T11:30:00+0300', 'driver_fix'),
            ],
            1,  # 1 for get current mode
        ),
        (
            1,
            'id_rule2',
            {'accept_button': {'title': 'Превышен лимит', 'enabled': False}},
            [
                ('2019-05-01T11:33:00+0300', 'orders'),
                ('2019-05-01T11:32:00+0300', 'driver_fix'),
                ('2019-05-01T11:31:00+0300', 'orders'),
                ('2019-05-01T11:30:00+0300', 'driver_fix'),
            ],
            2,  # 1 for get current mode
        ),
        pytest.param(
            2,
            'id_rule1',
            {
                'accept_button': {
                    'title': 'Был доступен до 15 ноября',
                    'enabled': False,
                },
            },
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix'),
                ('2019-05-01T11:31:00+0300', 'orders'),
                ('2019-05-01T11:30:00+0300', 'driver_fix'),
            ],
            1,  # 1 for get current mode
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_details_screen_ui_metainfo_time_validation(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        card_number,
        rule,
        expected_ui,
        reports,
        expected_requests,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        for occured, mode in reports:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': rule,
                            'shift_close_time': '00:00:00+03:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc['ui']['items'][card_number]['payload']['type'] == 'deeplink'
    link = doc['ui']['items'][card_number]['payload']['url']
    link_name = _get_query_component(link)

    assert link_name in doc['driver_modes']
    meta = doc['driver_modes'][link_name]
    del meta['ui']['items']
    assert meta['ui'] == expected_ui

    assert _driver_mode_index_mode_history.times_called == expected_requests


_BUTTON_ENABLED = {'accept_button': {'title': 'Выбрать', 'enabled': True}}
_BUTTON_SELECTED = {
    'accept_button': {'title': 'Режим уже выбран', 'enabled': False},
}
_BUTTON_LIMIT = {
    'accept_button': {'title': 'Превышен лимит', 'enabled': False},
}


def _get_button_enabled_with_warning(hours: int):
    return {
        'accept_button': {
            'title': 'Выбрать',
            'enabled': True,
            'warning': {
                'title': 'Точно хотите выбрать этот режим дохода?',
                'message': (
                    f'Вернуться в текущий режим вы сможете только через {hours} '
                    'часов'
                ),
                'accept_button_title': 'Хочу сменить',
                'reject_button_title': 'Останусь',
            },
        },
    }


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES_WITHOUT_CUSTOM)
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
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.parametrize(
    'expected_ui, mode_history, expected_requests',
    [
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_ENABLED,
            },
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'current_rule'),
                ('2019-05-01T11:31:00+0300', 'orders', ''),
                ('2019-05-01T11:30:00+0300', 'driver_fix', 'id_rule1'),
            ],
            1,  # 1 for get current mode
            id='no_restrictions',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_ENABLED,
            },
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'current_rule'),
                ('2019-05-01T11:31:00+0300', 'orders', ''),
                ('2019-05-01T11:30:00+0300', 'driver_fix', 'id_rule1'),
            ],
            2,  # 1 for get current mode, 1 for accept button warning
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {'restrictions': []},
                        'driver_fix': {
                            'restrictions': [
                                {
                                    'interval_type': 'hourly',
                                    'interval_count': 1,
                                    'max_change_count': 3,
                                },
                            ],
                        },
                        'orders': {
                            'restrictions': [
                                {
                                    'interval_type': 'hourly',
                                    'interval_count': 1,
                                    'max_change_count': 2,
                                },
                            ],
                        },
                    },
                ),
            ],
            id='no_violations',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_LIMIT,
            },
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'current_rule'),
                ('2019-05-01T11:31:00+0300', 'orders', ''),
                ('2019-05-01T11:30:00+0300', 'driver_fix', 'id_rule1'),
            ],
            2,  # 1 for get current mode, 1 for accept button warning
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {
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
            id='same_mode_available_anyway',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_LIMIT,
                'driver_fix_id_rule1': _BUTTON_LIMIT,
                'driver_fix_id_rule2': _BUTTON_LIMIT,
                'orders': _BUTTON_SELECTED,
            },
            [
                ('2019-05-01T11:33:00+0300', 'orders', ''),
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'id_rule2'),
                ('2019-05-01T11:31:00+0300', 'orders', ''),
                ('2019-05-01T11:30:00+0300', 'driver_fix', 'id_rule1'),
            ],
            2,  # 1 for get current mode, 1 for accept button warning
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {'restrictions': []},
                        'driver_fix': {
                            'restrictions': [
                                {
                                    'interval_type': 'hourly',
                                    'interval_count': 1,
                                    'max_change_count': 2,
                                },
                            ],
                        },
                    },
                ),
            ],
            id='enter_different_modes',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_ENABLED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_SELECTED,
            },
            [
                ('2019-05-01T11:34:00+0300', 'orders', ''),
                ('2019-05-01T11:33:00+0300', 'driver_fix', 'id_rule2'),
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'id_rule1'),
                ('2019-05-01T11:31:00+0300', 'driver_fix', 'id_rule2'),
                ('2019-05-01T11:30:00+0300', 'driver_fix', 'id_rule1'),
            ],
            2,  # 1 for get current mode, 1 for accept button warning
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {'restrictions': []},
                        'driver_fix': {
                            'restrictions': [
                                {
                                    'interval_type': 'hourly',
                                    'interval_count': 1,
                                    'max_change_count': 2,
                                },
                            ],
                        },
                    },
                ),
            ],
            id='enter_same_modes',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_LIMIT,
                'custom_orders': _get_button_enabled_with_warning(hours=1),
            },
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'current_rule'),
                ('2019-05-01T11:31:00+0300', 'orders', ''),
            ],
            2,  # 1 for get current mode, 1 for accept button warning
            marks=[
                pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES),
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
                        },
                        'orders': {
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
            id='warning_for_different_available_modes',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
            },
            [
                ('2019-05-01T11:32:00+0300', 'driver_fix', 'current_rule'),
                ('2019-05-01T11:31:00+0300', 'orders', ''),
                ('2019-05-01T11:30:00+0300', 'driver_fix', 'id_rule1'),
            ],
            1,  # 1 for get current mode
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
                        '__default__': {'restrictions': []},
                        'orders': {
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
            id='skip_mode_with_daily_validation_without_tariff_zone',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_offers_time_validation_settings(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix_context,
        driver_fix,
        expected_ui,
        mode_history,
        expected_requests,
):
    driver_fix_context.set_offers(_VIEW_OFFERS_FOR_TIME_CHECK)

    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        for occured, mode, rule in mode_history:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': rule,
                            'shift_close_time': '00:00:00+03:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(mockserver)

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

    assert offers_ui == expected_ui

    assert _driver_mode_index_mode_history.times_called == expected_requests


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ENABLE_ACCEPT_WARNING=True,
    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
        '__default__': {'restrictions': []},
        'driver_fix': {
            'restrictions': [
                {
                    'interval_type': 'dayly',
                    'interval_count': 1,
                    'max_change_count': 1,
                },
            ],
            'warnings': {
                'title': 'accept_warning.title',
                'message': 'accept_warning.message',
                'accept': 'accept_warning.accept',
                'reject': 'accept_warning.reject',
            },
        },
        'orders': {
            'restrictions': [
                {
                    'interval_type': 'hourly',
                    'interval_count': 2,
                    'max_change_count': 1,
                },
            ],
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.parametrize(
    'expected_ui, trackstory_available, client_timezone_available, '
    'client_position_available',
    [
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_LIMIT,
                # 13:00 MSK is 14:00 in Samara
                'custom_orders': _get_button_enabled_with_warning(hours=10),
            },
            True,
            True,
            True,
            id='trackstory_position',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'orders': _BUTTON_LIMIT,
                'custom_orders': _BUTTON_ENABLED,
            },
            False,
            True,
            False,
            id='client_timezone_unsupported_but_not_fail',
        ),
        pytest.param(
            {
                'driver_fix_current_rule': _BUTTON_SELECTED,
                'driver_fix_id_rule1': _BUTTON_ENABLED,
                'driver_fix_id_rule2': _BUTTON_ENABLED,
                'orders': _BUTTON_LIMIT,
                # 13:00 MSK is 15:00 in Perm
                'custom_orders': _get_button_enabled_with_warning(hours=9),
            },
            False,
            True,
            True,
            id='client_position',
        ),
    ],
)
@pytest.mark.now('2019-05-01T13:00:00+0300')
async def test_offers_time_validation_timezone(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        driver_fix_context,
        driver_fix,
        expected_ui,
        trackstory_available,
        client_timezone_available,
        client_position_available,
):
    driver_fix_context.set_offers(_VIEW_OFFERS_FOR_TIME_CHECK)

    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        mode_history = [
            ('2019-05-01T12:00:00+0300', 'driver_fix', 'current_rule'),
            ('2019-05-01T11:00:00+0300', 'orders', ''),
        ]

        for occured, mode, rule in mode_history:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': rule,
                            'shift_close_time': '00:00:00+03:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    scenario.Scene.mock_driver_trackstory(
        mockserver, scenario.SAMARA_POSITION if trackstory_available else None,
    )

    params = {'park_id': 'dbid'}
    if client_position_available:
        # PERM (+5)
        params['lat'] = scenario.PERM_POSITION.lat
        params['lon'] = scenario.PERM_POSITION.lon
    if client_timezone_available:
        params['tz'] = 'Asia/Yekaterinburg'  # +5

    response = await taxi_driver_mode_subscription.get(
        'v1/view/available_offers',
        params=params,
        headers={
            **common.get_api_v1_headers(profile),
            'Accept-Language': 'ru',
        },
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

    assert offers_ui == expected_ui


_ON_ORDER = {
    'statuses': [
        {
            'status': 'busy',
            'park_id': 'dbid',
            'driver_id': 'uuid',
            'orders': [{'id': 'order_id', 'status': 'transporting'}],
        },
    ],
}

_WITHOUT_ORDER = {
    'statuses': [
        {
            'status': 'online',
            'park_id': 'dbid',
            'driver_id': 'uuid',
            'orders': [],
        },
    ],
}

_UNKNOWN_STATUS: Dict[str, Any] = {'statuses': []}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'config, expected_profiles_calls',
    [
        pytest.param(
            0,
            1,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=True,
                ),
            ],
        ),
        pytest.param(
            1,
            0,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'statuses_response, expected_button_states',
    [
        pytest.param(_WITHOUT_ORDER, [True, True]),
        pytest.param(_ON_ORDER, [False, True]),
        pytest.param(_UNKNOWN_STATUS, [True, True]),
    ],
)
async def test_details_screen_ui_check_not_on_order(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        config,
        driver_fix,
        statuses_response,
        expected_button_states,
        expected_profiles_calls,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        _set_mode_settings(response, '')
        return response

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return statuses_response

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    expected_button_state_dict = {
        True: (True, 'Выбрать'),
        False: (False, 'Вы сейчас на заказе'),
    }
    expected_button = expected_button_state_dict[
        expected_button_states[config]
    ]

    link_name = 'driver_fix_id_rule1'
    assert link_name in doc['driver_modes']
    button = doc['driver_modes'][link_name]['ui']['accept_button']
    assert (button['enabled'], button['title']) == expected_button

    assert _v2_statuses.times_called == expected_profiles_calls


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_CHECK_NOT_IN_REPOSITION={
        'modes': [],
        'tanker_keys': {
            '__default__': {
                'disable_button': 'offer_screen.button_in_reposition',
                'message_title': (
                    'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.title'
                ),
                'message_body': 'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.message',
            },
            'home': {
                'disable_button': 'offer_screen.button_in_reposition_home',
                'message_title': (
                    'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.title'
                ),
                'message_body': 'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.message',
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expected_button_state_index',
    [
        pytest.param(1),
        pytest.param(
            0,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                'driver_fix',
                                features={
                                    'reposition': {'profile': 'driver_fix'},
                                    'driver_fix': {},
                                },
                            ),
                        ],
                    ),
                ),
            ],
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                'orders',
                                features={'reposition': {'profile': 'orders'}},
                            ),
                        ],
                    ),
                ),
            ],
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                'driver_fix',
                                features={
                                    'reposition': {'profile': 'driver_fix'},
                                    'driver_fix': {},
                                },
                            ),
                            mode_rules.Patch(
                                'orders',
                                features={'reposition': {'profile': 'orders'}},
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'is_in_reposition,reposition_mode,expected_button_state_cases',
    [
        pytest.param(
            True,
            'SurgeCharge',
            [(False, 'Вы сейчас в состоянии перемещения'), (True, 'Выбрать')],
        ),
        pytest.param(
            True,
            'home',
            [(False, 'Вы сейчас в режиме ДОМОЙ'), (True, 'Выбрать')],
        ),
        pytest.param(False, '', [(True, 'Выбрать'), (True, 'Выбрать')]),
    ],
)
async def test_details_screen_ui_check_not_in_reposition(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        expected_button_state_index,
        driver_fix,
        is_in_reposition,
        reposition_mode,
        expected_button_state_cases,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        _set_mode_settings(response, '')
        return response

    @mockserver.json_handler('/reposition-api/v1/service/state')
    def _v1_service_state(request):
        if is_in_reposition:
            return {
                'active': True,
                'has_session': True,
                'mode': reposition_mode,
                'point': [37.6548, 55.6434],
                'submode': '',
            }
        return {'has_session': False}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    link_name = 'driver_fix_id_rule1'
    button = doc['driver_modes'][link_name]['ui']['accept_button']
    assert (button['enabled'], button['title']) == expected_button_state_cases[
        expected_button_state_index
    ]


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=offer_templates.DEFAULT_OFFER_TEMPLATES,
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=_MODE_TEMPLATE_RELATIONS,
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'current_mode,current_rule_id, expected_rule_id',
    [
        ('orders', '', None),
        ('driver_fix', 'id_rule_driver_fix1', 'id_rule_driver_fix1'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_pass_mode_settings(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        driver_fix_context,
        current_mode,
        current_rule_id,
        expected_rule_id,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, current_mode, mocked_time,
        )
        _set_mode_settings(response, current_rule_id)
        return response

    driver_fix_context.set_offers([])
    driver_fix_context.expect_rule_id(expected_rule_id)

    scenario.Scene.mock_driver_trackstory(mockserver)

    await common.get_available_offers(taxi_driver_mode_subscription, profile)


def _build_template_with_title(title: str):
    result = copy.deepcopy(offer_templates.DEFAULT_CUSTOM_ORDERS_TEMPLATE)
    result['model']['title'] = title
    return result


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders_template': _build_template_with_title(
                'prefix_orders.offer_card.title',
            ),
            'driver_fix_template': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'custom_orders': _build_template_with_title(
                'custom_orders.offer_card.title',
            ),
            'custom_orders_1': _build_template_with_title(
                'prefix_orders.offer_card.title',
            ),
            'custom_orders_2': _build_template_with_title(
                'custom_orders.offer_card.description',
            ),
            'custom_orders_3': _build_template_with_title(
                'custom_orders.offer_card.subtitle',
            ),
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'custom_orders': 'custom_orders',
            'custom_orders_1': 'custom_orders_1',
            'custom_orders_2': 'custom_orders_2',
            'custom_orders_3': 'custom_orders_3',
            'geobooking': 'geobooking_template',
        },
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('custom_orders_1'),
            mode_rules.Patch('custom_orders_2'),
            mode_rules.Patch('custom_orders_3'),
        ],
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_offers_sort(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_fix,
        driver_fix_context,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    driver_fix_context.set_offers(
        _VIEW_OFFERS
        + [
            {
                'offer_card': {
                    'title': 'Карточка.Заголовок(driver_fix)',
                    'subtitle': 'Доступен до 2 декабря',
                    'description': 'Заработок зависит от времени работы',
                    'is_new': False,
                    'enabled': True,
                },
                'settings': {
                    'rule_id': 'id_rule3',
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
            {
                'offer_card': {
                    'title': 'А за время',
                    'subtitle': 'Был доступен до 15 ноября',
                    'description': 'Заработок зависит от времени работы',
                    'is_new': False,
                    'enabled': False,
                    'disable_reason': 'Был доступен до 15 ноября',
                },
                'settings': {
                    'rule_id': 'id_rule4',
                    'shift_close_time': '00:02',
                },
                'offer_screen': {
                    'items': [
                        {'type': 'text', 'text': 'Подробности правила 2.'},
                    ],
                },
                'memo_screen': {
                    'items': [{'type': 'text', 'text': 'Memo правила 2'}],
                },
            },
            {
                'offer_card': {
                    'title': 'За время_',
                    'subtitle': 'Был доступен до 15 ноября',
                    'description': 'Заработок зависит от времени работы',
                    'is_new': False,
                    'enabled': False,
                    'disable_reason': 'Был доступен до 15 ноября',
                },
                'settings': {
                    'rule_id': 'id_rule5',
                    'shift_close_time': '00:02',
                },
                'offer_screen': {
                    'items': [
                        {'type': 'text', 'text': 'Подробности правила 2.'},
                    ],
                },
                'memo_screen': {
                    'items': [{'type': 'text', 'text': 'Memo правила 2'}],
                },
            },
        ],
    )

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    expected_titles = [
        'Карточка.Заголовок(custom)',  # active
        'За время',  # is new
        'Карточка.Заголовок(custom)',  # enabled
        'Карточка.Заголовок(default)',  # enabled
        'Карточка.Заголовок(driver_fix)',  # enabled
        'Карточка.Описание(default)',  # enabled
        'Карточка.Подзаголовок(default)',  # enabled
        'За время',  # disabled in group driver_fix
        'А за время',  # disabled in group driver_fix
        'За время_',  # disabled in group driver_fix
    ]

    item_titles = []

    for offer_item_ui in doc['ui']['items']:
        item_titles.append(offer_item_ui['items'][0]['title'])

    assert item_titles == expected_titles
