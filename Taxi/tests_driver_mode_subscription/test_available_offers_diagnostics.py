# pylint: disable=C0302
import copy
import datetime as dt
import enum
import operator
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest
import pytz

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
'2019-05-01T05:00:00+00:00'
_NOW = dt.datetime(2020, 5, 5, 15, 15, 5, 0, tzinfo=pytz.utc)
_MINUTE_AGO = _NOW - dt.timedelta(minutes=1)

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
_GEOBOOKING_ITEM: Dict[str, Any] = {
    'availability': {'is_available': True, 'reasons': []},
    'description': '',
    'display': {'is_displayed': True, 'reasons': []},
    'mode_id': 'geobooking',
    'subscription': {
        'settings': {
            'type': 'geobooking',
            'values': {
                'rule_id': 'id_rule1',
                'shift_close_time': '00:00:00+00:00',
            },
        },
    },
    'subtitle': '',
    'title': 'За geobooking',
    'offers_group': 'taxi',
    'details': [
        'Ключевые параметры: тарифная зона: test_tariff_zone, '
        'субсидийная зона: test_subvention_geoarea, тег: '
        'no_free_slots_tag',
        'Занято мест: 0 из 50',
    ],
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

_ANY_OF_ERROR = 'У водителя нет ни одного из тегов: missed_tag'
_ALL_OF_ERROR = 'У водителя нет необходимых тегов: missed_tag'
_NONE_OF_ERROR = 'У водителя есть блокирующий тег: has_tag1'
_NOT_DISPLAYED_ERROR = 'Не отображается'


# TODO: this function can be removed for ApplyRules::DbOnly
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


class DriverProfileResponseType(enum.Enum):
    ALL_OK = 'ALL_OK'
    NO_VERSION = 'NO_VERSION'
    NO_PROFILE_DATA = 'NO_PROFILE_DATA'
    NO_PROFILE = 'NO_PROFILE'
    ERROR = 'ERROR'


class TaximeterPlatform(enum.Enum):
    IOS = 'ios'
    ANDROID = 'android'


def _mock_driver_profiles(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def handler(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'dbid_uuid',
                    'data': {'taximeter_platform': 'android'},
                },
            ],
        }

    return handler


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

    return [
        _driver_mode_index_mode_history,
        _mock_view_offer,
        _mock_driver_profiles(mockserver),
    ]


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_SETTINGS={'old_days': 5},
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.parametrize(
    'rules_patch, not_displayed_reasons, not_available_reasons',
    [
        pytest.param(
            {'offers_group': 'no_group'},
            ['Не указана группа режимов'],
            [_NOT_DISPLAYED_ERROR],
            id='rule without offers_group',
        ),
        pytest.param(
            {'offers_group': 'lavka'},
            [
                'Группа режимов "lavka" отличается от группы "taxi" текущего '
                'режима',
            ],
            [_NOT_DISPLAYED_ERROR],
            id='offers_group type in rule mismatched with current',
        ),
        pytest.param(
            {'stops_at': _MINUTE_AGO},
            None,
            ['Был доступен до 18:14'],
            id='expired rule',
        ),
        pytest.param({}, None, None, id='everything is ok'),
    ],
)
async def test_non_default_mode_settings(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        rules_patch: Dict[str, Any],
        not_displayed_reasons: Optional[List[str]],
        not_available_reasons: Optional[List[str]],
):
    driver_mode_rules = mode_rules.patched_mode_rules(
        'custom_orders', **rules_patch,
    )
    mode_rules_data.set_mode_rules(rules=driver_mode_rules)

    mode_geography_defaults.set_all_modes_available()

    mocked_services = _mock_services(mockserver, mocked_time)

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )

    for mock in mocked_services:
        assert mock.has_calls

    extra_item = copy.deepcopy(_EXTRA_ITEM)

    if not_displayed_reasons:
        extra_item['display']['is_displayed'] = False
        extra_item['display']['reasons'] = not_displayed_reasons

    if not_available_reasons:
        extra_item['availability']['is_available'] = False
        extra_item['availability']['reasons'] = not_available_reasons

    if 'offers_group' in rules_patch:
        extra_item['offers_group'] = rules_patch['offers_group']

    extra_item['display']['reasons'].sort()
    expected_modes = [
        _UBERDRIVER_MODE_ITEM,
        _ORDERS_MODE_ITEM,
        _DRIVER_FIX_ITEM,
        extra_item,
    ]

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.parametrize(
    'rule_condition, error_messages',
    [
        (None, None),
        ({'all_of': ['has_tag1', 'has_tag2']}, None),
        ({'any_of': ['has_tag1']}, None),
        ({'any_of': ['has_tag2']}, None),
        ({'none_of': ['missed_tag']}, None),
        ({'or': [{'all_of': ['has_tag2']}, {'any_of': ['missed_tag']}]}, None),
        (
            {
                'and': [
                    {'all_of': ['has_tag2']},
                    {'any_of': ['has_tag1', 'missed_tag']},
                ],
            },
            None,
        ),
        pytest.param(
            {'any_of': ['missed_tag']},
            [_ANY_OF_ERROR],
            id='any_of rule check',
        ),
        pytest.param(
            {'all_of': ['missed_tag', 'has_tag2']},
            [_ALL_OF_ERROR],
            id='all_of rule check',
        ),
        pytest.param(
            {'none_of': ['missed_tag', 'has_tag1']},
            [_NONE_OF_ERROR],
            id='none_of rule check',
        ),
        pytest.param(
            {
                'and': [
                    {'none_of': ['matched_rule']},
                    {'all_of': ['has_tag2', 'missed_tag']},
                    {'any_of': ['missed_tag']},
                ],
            },
            ['Одно из условий не выполнено', _ALL_OF_ERROR, _ANY_OF_ERROR],
            id='and logical rule check',
        ),
        pytest.param(
            {
                'or': [
                    {'none_of': ['has_tag1']},
                    {'all_of': ['has_tag2', 'missed_tag']},
                    {'any_of': ['missed_tag']},
                ],
            },
            [
                'Ни одно из условий не выполнено',
                _NONE_OF_ERROR,
                _ALL_OF_ERROR,
                _ANY_OF_ERROR,
            ],
            id='or logical rule check',
        ),
    ],
)
async def test_condition_settings(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        rule_condition: Optional[Dict[str, Any]],
        error_messages: Optional[List[str]],
):
    driver_mode_rules = mode_rules.patched_mode_rules(
        rule_name='custom_orders', condition=rule_condition,
    )
    mode_rules_data.set_mode_rules(rules=driver_mode_rules)

    mode_geography_defaults.set_all_modes_available()

    mocked_services = _mock_services(mockserver, mocked_time)
    common.make_driver_tags_mock(
        mockserver, ['has_tag1', 'has_tag2'], 'dbid', 'uuid',
    )

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )
    for mock in mocked_services:
        assert mock.has_calls

    extra_item = copy.deepcopy(_EXTRA_ITEM)

    if error_messages is not None:
        extra_item['availability']['is_available'] = False
        extra_item['availability']['reasons'] = [_NOT_DISPLAYED_ERROR]
        extra_item['display']['is_displayed'] = False
        extra_item['display']['reasons'] = error_messages

    extra_item['availability']['reasons'].sort()
    expected_modes = [
        _UBERDRIVER_MODE_ITEM,
        _ORDERS_MODE_ITEM,
        _DRIVER_FIX_ITEM,
        extra_item,
    ]

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES={
        'templates': {
            'orders_template': offer_templates.DEFAULT_ORDERS_TEMPLATE,
            'driver_fix_template': offer_templates.DEFAULT_DRIVER_FIX_TEMPLATE,
            'geobooking_template': offer_templates.DEFAULT_GEOBOOKING_TEMPLATE,
            'custom_orders_template': (
                offer_templates.DEFAULT_CUSTOM_ORDERS_TEMPLATE
            ),
            'new_rule': offer_templates.build_orders_template(
                card_title='new_rule.offer_card.title',
                card_subtitle='new_rule.offer_card.subtitle',
                card_description='new_rule.offer_card.description',
                screen_header='new_rule.offer_screen.header',
                screen_description='new_rule.offer_screen.text',
                memo_header='new_rule.memo_screen.header',
                memo_description='new_rule.memo_screen.text',
            ),
            'uberdriver_template': offer_templates.DEFAULT_UBERDRIVER_TEMPLATE,
        },
    },
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'custom_orders': 'custom_orders_template',
            'geobooking': 'geobooking_template',
            'new_rule': 'new_rule',
            'uberdriver': 'uberdriver_template',
        },
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched_mode_rules(rule_name='new_rule'),
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
async def test_missing_mode_translations(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
):

    mocked_services = _mock_services(mockserver, mocked_time)
    common.make_driver_tags_mock(
        mockserver, ['has_tag1', 'has_tag2'], 'dbid', 'uuid',
    )

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )
    for mock in mocked_services:
        assert mock.has_calls

    new_item = {
        'mode_id': 'new_rule',
        # fallback to mode_id on problems
        'title': 'new_rule',
        'subtitle': '',
        'description': '',
        'display': {
            'is_displayed': False,
            'reasons': [
                'Отсутствует перевод: Failed to localize '
                'keyset=driver_fix key=new_rule.offer_card.'
                'title locale=ru',
            ],
        },
        'subscription': {},
        'availability': {
            'is_available': False,
            'reasons': [_NOT_DISPLAYED_ERROR],
        },
        'offers_group': 'taxi',
    }
    expected_modes = [
        _UBERDRIVER_MODE_ITEM,
        _ORDERS_MODE_ITEM,
        _DRIVER_FIX_ITEM,
        new_item,
        _EXTRA_ITEM,
    ]

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)


@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='custom_orders',
                features={'reposition': {'profile': 'custom_orders'}},
            ),
            mode_rules.Patch(
                rule_name='geobooking', features={'geobooking': {}},
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_RULES_BLOCKING_TAGS={'custom_orders': {'tags': ['frauder']}},
    DRIVER_MODE_SUBSCRIPTION_CHECK_NOT_IN_REPOSITION={
        'modes': ['custom_orders'],
        'tanker_keys': {
            '__default__': {
                'disable_button': 'offer_screen.button_in_reposition',
                'message_title': (
                    'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.title'
                ),
                'message_body': (
                    'set_by_session.error.'
                    'CHECK_NOT_IN_REPOSITION_FAILED.message'
                ),
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=True,
    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
        'check_enabled': True,
        'subscription_sync_enabled': False,
        'reschedule_timeshift_ms': 60,
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
async def test_display_checks(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
):
    mocked_services = _mock_services(mockserver, mocked_time)

    @mockserver.json_handler('/driver-work-modes/v1/work-modes/list')
    def _work_modes_list(request):
        return {'work_modes': [{'id': 'custom_orders', 'is_enabled': False}]}

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'busy',
                    'park_id': 'dbid',
                    'driver_id': 'uuid',
                    'orders': [{'id': 'order_id', 'status': 'transporting'}],
                },
            ],
        }

    @mockserver.json_handler('/reposition-api/v1/service/state')
    def _v1_service_state(request):
        return {
            'active': True,
            'has_session': True,
            'mode': 'SurgeCharge',
            'point': [37.6548, 55.6434],
            'submode': '',
        }

    common.make_driver_tags_mock(
        mockserver, ['good_tag', 'frauder'], 'dbid', 'uuid',
    )

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )
    for mock in mocked_services:
        assert mock.has_calls

    extra_item_reasons = [
        # reposition check
        'Водитель имеет незавершенный режим перемещения',
        # tags block
        'У водителя есть блокирующий тег',
    ]

    expected_modes = [
        copy.deepcopy(_UBERDRIVER_MODE_ITEM),
        copy.deepcopy(_ORDERS_MODE_ITEM),
        copy.deepcopy(_DRIVER_FIX_ITEM),
        copy.deepcopy(_GEOBOOKING_ITEM),
        copy.deepcopy(_EXTRA_ITEM),
    ]

    for mode in expected_modes:
        if mode['display']['is_displayed'] is False:
            continue
        mode['availability']['is_available'] = False
        # not_on_order check
        mode['availability']['reasons'].append('Водитель выполняет заказ')
        if mode['mode_id'] == _DRIVER_FIX_ITEM['mode_id']:
            # park validation expect to fail on driver_fix mode
            mode['availability']['reasons'].append(
                'Режим запрещен настройками парка',
            )

        if mode['mode_id'] == 'custom_orders':
            mode['availability']['reasons'] += extra_item_reasons
        mode['availability']['reasons'].sort()

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)


@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_RULES_BLOCKING_TAGS={'driver_fix': {'tags': ['frauder']}},
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
async def test_display_checks_exceptions(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
):
    mocked_services = _mock_services(mockserver, mocked_time)

    common.make_driver_tags_mock(
        mockserver,
        ['frauder'],
        'dbid',
        'uuid',
        common.ServiceError.ServerError,
    )

    scenario.Scene.mock_driver_trackstory(mockserver, driver_position=None)

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )
    for mock in mocked_services:
        assert mock.has_calls

    driver_fix_item = copy.deepcopy(_DRIVER_FIX_ITEM)

    driver_fix_item['availability']['is_available'] = False
    driver_fix_item['availability']['reasons'] = [
        'При проведении проверки произошла ошибка',
    ]
    driver_fix_item['display']['is_displayed'] = True

    expected_modes = [
        _UBERDRIVER_MODE_ITEM,
        _ORDERS_MODE_ITEM,
        driver_fix_item,
        _EXTRA_ITEM,
    ]

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.parametrize(
    'driver_fix_raise_error, not_displayed_reasons',
    [
        pytest.param(
            True, ['Ошибка получения офферов'], id='fetch offers error',
        ),
        pytest.param(False, ['Отсутствуют офферы'], id='no offers'),
    ],
)
async def test_always_show_mode_with_offers(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        driver_fix_raise_error: bool,
        not_displayed_reasons: List[str],
):
    _mock_services(mockserver, mocked_time)

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        if driver_fix_raise_error:
            raise mockserver.TimeoutError()
        return {'offers': []}

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )

    driver_fix_item = copy.deepcopy(_DRIVER_FIX_ITEM)

    driver_fix_item['availability']['is_available'] = False
    driver_fix_item['availability']['reasons'] = [_NOT_DISPLAYED_ERROR]
    driver_fix_item['display']['is_displayed'] = False
    driver_fix_item['display']['reasons'] = not_displayed_reasons
    # clear data that can fetched only from offer
    driver_fix_item['subtitle'] = ''
    driver_fix_item['description'] = ''
    driver_fix_item['subscription'].pop('settings')

    expected_modes = [
        _UBERDRIVER_MODE_ITEM,
        _ORDERS_MODE_ITEM,
        driver_fix_item,
        _EXTRA_ITEM,
    ]

    _compare_result(_exclude_rule_id(response['driver_modes']), expected_modes)


_VIEW_OFFERS_FOR_TIME_CHECK: List[Dict[str, Any]] = [
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


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2019-05-05T02:00:00+03:00')
@pytest.mark.mode_rules(rules=mode_rules.patched([]))
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_TIME_VALIDATION_SETTINGS={
        '__default__': {'restrictions': []},
        'custom_orders': {
            'restrictions': [
                {
                    'interval_type': 'hourly',
                    'interval_count': 2,
                    'max_change_count': 1,
                },
            ],
        },
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
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'trackstory_available, admin_position_available, position, '
    'expect_available',
    [
        pytest.param(
            True,
            False,
            scenario.MOSCOW_POSITION,
            True,
            id='trackstory_position_moscow',
        ),
        pytest.param(
            True,
            False,
            scenario.SAMARA_POSITION,
            False,
            id='trackstory_position_samara',
        ),
        pytest.param(
            False,
            True,
            scenario.MOSCOW_POSITION,
            True,
            id='admin_position_moscow',
        ),
        pytest.param(
            False,
            True,
            scenario.SAMARA_POSITION,
            False,
            id='admin_position_samara',
        ),
        pytest.param(
            False,
            False,
            scenario.MOSCOW_POSITION,
            True,
            id='default_position',
        ),
    ],
)
async def test_time_validation_timezone(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        trackstory_available: bool,
        admin_position_available: bool,
        position: common.Position,
        expect_available: bool,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        mode_history = [
            ('2019-05-05T01:00:00+0300', 'driver_fix', 'current_rule'),
            ('2019-05-05T00:00:00+0300', 'custom_orders', ''),
            ('2019-05-04T23:00:00+0300', 'orders', ''),
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

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    def _mock_view_offer(request):
        doc = request.json
        assert doc['park_id'] == 'dbid'
        assert doc['driver_profile_id'] == 'uuid'
        return {'offers': _VIEW_OFFERS_FOR_TIME_CHECK}

    scenario.Scene.mock_driver_trackstory(mockserver, position)

    _mock_driver_profiles(mockserver)

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription,
        'dbid',
        'uuid',
        position=position if admin_position_available else None,
    )

    driver_modes = list(
        filter(
            lambda mode: mode['mode_id'] in ('orders', 'custom_orders'),
            response['driver_modes'],
        ),
    )

    expected_modes = [
        copy.deepcopy(_ORDERS_MODE_ITEM),
        copy.deepcopy(_EXTRA_ITEM),
    ]

    for mode in expected_modes:
        if mode['mode_id'] == 'custom_orders' or not expect_available:
            mode['availability']['is_available'] = False
            mode['availability']['reasons'].append(
                'Превышено число входов в режим',
            )

    _compare_result(_exclude_rule_id(driver_modes), expected_modes)


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_CHECK_NOT_IN_REPOSITION={
        'modes': [],
        'tanker_keys': {
            '__default__': {
                'disable_button': 'offer_screen.button_in_reposition',
                'message_title': (
                    'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.title'
                ),
                'message_body': (
                    'set_by_session.error.'
                    'CHECK_NOT_IN_REPOSITION_FAILED.message'
                ),
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched_mode_rules(
        rule_name='driver_fix',
        features={
            'driver_fix': {},
            'reposition': {'profile': 'reposition_profile'},
        },
        condition={'any_of': ['match']},
    ),
)
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.parametrize(
    'driver_tag, expect_check_call',
    [
        pytest.param('match', True, id='displayed mode'),
        pytest.param('mismatch', False, id='not displayed mode'),
    ],
)
async def test_availability_checks_for_not_displayed_mode(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        driver_tag: str,
        expect_check_call: int,
):
    mocked_services = _mock_services(mockserver, mocked_time)

    common.make_driver_tags_mock(mockserver, [driver_tag], 'dbid', 'uuid')

    @mockserver.json_handler('/reposition-api/v1/service/state')
    def _reposition_mock(request):
        return {
            'active': True,
            'has_session': True,
            'mode': 'SurgeCharge',
            'point': [37.6548, 55.6434],
            'submode': '',
        }

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )

    assert len(response['driver_modes']) == 4

    for mock in mocked_services:
        assert mock.has_calls

    if expect_check_call:
        assert _reposition_mock.times_called == 1
    else:
        assert _reposition_mock.times_called == 0


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.parametrize(
    'position_from_admin, position, position_time, ' 'expected_position_info',
    [
        pytest.param(None, None, None, None, id='no position'),
        pytest.param(
            None,
            scenario.MOSCOW_POSITION,
            _NOW,
            {
                'position': [37.601434, 55.737636],
                'source': 'current',
                'tariff_zone': {'name': 'moscow'},
            },
            id='have current position',
        ),
        pytest.param(
            scenario.SAMARA_POSITION,
            None,
            None,
            {
                'position': [50.11, 53.18],
                'source': 'admin',
                'tariff_zone': {'name': 'samara'},
            },
            id='admin position',
        ),
        pytest.param(
            None,
            scenario.SAMARA_POSITION,
            _NOW - dt.timedelta(hours=2),
            {
                'position': [50.11, 53.18],
                'source': 'historic',
                'tariff_zone': {'name': 'samara'},
            },
            id='history position',
        ),
        pytest.param(
            scenario.SAMARA_POSITION,
            scenario.MOSCOW_POSITION,
            _NOW,
            {
                'position': [50.11, 53.18],
                'source': 'admin',
                'tariff_zone': {'name': 'samara'},
            },
            id='prefer position from admin',
        ),
    ],
)
async def test_position_info(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        position_from_admin: Optional[common.Position],
        position: Optional[common.Position],
        position_time: Optional[dt.datetime],
        expected_position_info: Optional[Dict[str, Any]],
):
    _mock_services(mockserver, mocked_time)

    scenario.Scene.mock_driver_trackstory(
        mockserver,
        driver_position=position,
        driver_position_time=position_time,
    )

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription,
        'dbid',
        'uuid',
        position=position_from_admin,
    )

    driver_fix_request = _mock_view_offer.next_call()['request']

    if expected_position_info:
        assert response['position_info'] == expected_position_info
        assert (
            float(driver_fix_request.args['lon'])
            == expected_position_info['position'][0]
        )
        assert (
            float(driver_fix_request.args['lat'])
            == expected_position_info['position'][1]
        )
    else:
        assert 'position_info' not in response
        assert 'lon' not in driver_fix_request.args
        assert 'lat' not in driver_fix_request.args


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_CHECK_NOT_IN_REPOSITION={
        'modes': [],
        'tanker_keys': {
            '__default__': {
                'disable_button': 'offer_screen.button_in_reposition',
                'message_title': (
                    'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.title'
                ),
                'message_body': (
                    'set_by_session.error.'
                    'CHECK_NOT_IN_REPOSITION_FAILED.message'
                ),
            },
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {},
    },
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now(_NOW.strftime(_TIME_FORMAT))
async def test_availability_checks_missing_template(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
):
    _mock_services(mockserver, mocked_time)

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await common.available_offers_diagnostics(
        taxi_driver_mode_subscription, 'dbid', 'uuid',
    )

    assert len(response['driver_modes']) == 4
    assert {
        mode['display']['is_displayed'] for mode in response['driver_modes']
    } == {False}
    assert (
        {
            ','.join(mode['display']['reasons'])
            for mode in response['driver_modes']
        }
        == {
            'Не указана группа режимов',
            'Отсутствует перевод:'
            ' template for work mode custom_orders not found',
            'Отсутствует перевод: template for work mode driver_fix not found',
            'Отсутствует перевод: template for work mode orders not found',
        }
    )
