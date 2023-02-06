# pylint: disable=C0302
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates

_PARK_ID = 'testparkid'
_DRIVER_ID = 'uuid'

_ORDERS_RULE_ID = 'a883a23977484000b870f0cfcc84e1f9'
_GEOMODE_RULE_ID = 'a50906fca3ce4d5b82ff1e40c60724ff'
_CUSTOM_ORDERS_RULE_ID = '438a9fc006074759b6967ebe046fe5e0'
_DRIVER_FIX_RULE_ID = '1d2b25b551034441afa2ea2855876e9d'
_DRIVER_FIX_NO_GROUP_RULE_ID = 'd8005c7f9c7f42f5802e1b95fac9958b'
_GEOBOOKING_RULE_ID = '3abdfb8724f241d6934f865d100fb67f'
_GEOBOOKING2_RULE_ID = '8eecad6b50c74687bccf0c67570a3d45'

_DRIVER_FIX_OFFERS = {
    'offers': [
        {
            'title': 'За время1',
            'tariff_zone': 'moscow',
            'settings': {'rule_id': 'id_rule1', 'shift_close_time': '00:01'},
        },
        {
            'title': 'За время2',
            'tariff_zone': 'moscow',
            'settings': {'rule_id': 'id_rule2', 'shift_close_time': '00:01'},
        },
    ],
}

_DRIVER_FIX_RULE1_MODE_SETTINGS = {
    'rule_id': 'id_rule1',
    'shift_close_time': '00:01',
}

_DEFAULT_PARK_OFFERS_CONFIG = {
    'by_park_ids': [{}],
    'default': {
        'unsubscribe_permissions': {
            'offers_groups': ['taxi'],
            'work_modes': [],
        },
        'work_modes': [],
    },
}


def _make_park_offers_config(
        park_id: str,
        park_work_modes: List[str],
        default_work_modes: Optional[List[str]] = None,
        park_unsubscribe_permissions: Optional[Dict[str, Any]] = None,
        default_unsubscribe_permissions: Optional[Dict[str, Any]] = None,
):
    park_ids_item: Dict[str, Any] = {
        'park_ids': [park_id],
        'work_modes': park_work_modes,
    }
    if park_unsubscribe_permissions:
        park_ids_item['unsubscribe_permissions'] = park_unsubscribe_permissions

    _default_unsubscribe_permissions = {
        'offers_groups': ['taxi'],
        'work_modes': [],
    }

    if default_unsubscribe_permissions:
        _default_unsubscribe_permissions = default_unsubscribe_permissions

    default_work_modes_ = []

    if default_work_modes:
        default_work_modes_ = default_work_modes

    return {
        'by_park_ids': [park_ids_item],
        'default': {
            'unsubscribe_permissions': _default_unsubscribe_permissions,
            'work_modes': default_work_modes_,
        },
    }


def _make_key_params_mock(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/rule_key_params')
    async def _mock_view_offer(request):
        return {
            'rules': [
                {
                    'rule_id': 'rule_id',
                    'key_params': {
                        'tariff_zone': 'next_zone',
                        'subvention_geoarea': 'next_area',
                        'tag': 'next_tag',
                    },
                },
            ],
        }


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'driver_fix': 'driver_fix_template',
            'driver_fix_no_group': 'driver_fix_template',
            'orders': 'orders_template',
            'custom_orders': 'custom_orders_template',
        },
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
            mode_rules.Patch(
                rule_name='driver_fix',
                rule_id=_DRIVER_FIX_RULE_ID,
                features={'driver_fix': {}},
                offers_group='eda',
            ),
            mode_rules.Patch(
                rule_name='driver_fix_no_group',
                rule_id=_DRIVER_FIX_NO_GROUP_RULE_ID,
                features={'driver_fix': {}},
                offers_group='no_group',
            ),
            mode_rules.Patch(
                rule_name='custom_orders', rule_id=_CUSTOM_ORDERS_RULE_ID,
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'driver_fix_no_group': 'driver_fix_template',
            'custom_orders': 'custom_orders_template',
            'geobooking': 'geobooking_template',
            'uberdriver': 'uberdriver_template',
        },
    },
)
@pytest.mark.parametrize(
    'current_mode, current_mode_settings, expected_modes',
    [
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID},
            id='default all denied',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        'someparkid', [],
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID, _CUSTOM_ORDERS_RULE_ID},
            id='default modes allowed',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        'someparkid',
                        [],
                        default_work_modes=['orders', 'custom_orders'],
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID},
            id='default modes allowed, but by park denied',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        [],
                        default_work_modes=['orders', 'custom_orders'],
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID, _CUSTOM_ORDERS_RULE_ID},
            id='default modes denied, but by park allowed',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID, ['orders', 'custom_orders'],
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID, _DRIVER_FIX_NO_GROUP_RULE_ID},
            id='show modes from different group',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID, ['orders', 'driver_fix_no_group'],
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID, _DRIVER_FIX_NO_GROUP_RULE_ID},
            id='allow unsubscribe for park modes',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID, _DRIVER_FIX_NO_GROUP_RULE_ID},
            id='allow unsubscribe for default work modes',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        'someparkid',
                        [],
                        default_work_modes=['orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {
                _CUSTOM_ORDERS_RULE_ID,
                _ORDERS_RULE_ID,
                _DRIVER_FIX_NO_GROUP_RULE_ID,
            },
            id='allow unsubscribe with default permission for group',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['custom_orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': ['taxi'],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {
                _CUSTOM_ORDERS_RULE_ID,
                _ORDERS_RULE_ID,
                _DRIVER_FIX_NO_GROUP_RULE_ID,
            },
            id='allow unsubscribe with default permission for mode',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['custom_orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': ['orders'],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {
                _CUSTOM_ORDERS_RULE_ID,
                _ORDERS_RULE_ID,
                _DRIVER_FIX_NO_GROUP_RULE_ID,
            },
            id='allow unsubscribe with park permission for group',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['custom_orders', 'driver_fix_no_group'],
                        park_unsubscribe_permissions={
                            'offers_groups': ['taxi'],
                            'work_modes': [],
                        },
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {
                _CUSTOM_ORDERS_RULE_ID,
                _ORDERS_RULE_ID,
                _DRIVER_FIX_NO_GROUP_RULE_ID,
            },
            id='allow unsubscribe with park permission for mode',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['custom_orders', 'driver_fix_no_group'],
                        park_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': ['orders'],
                        },
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'orders',
            None,
            {_ORDERS_RULE_ID},
            id='denied unsubscribe without permission',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['custom_orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'driver_fix_no_group',
            _DRIVER_FIX_RULE1_MODE_SETTINGS,
            {_DRIVER_FIX_NO_GROUP_RULE_ID, _CUSTOM_ORDERS_RULE_ID},
            id='current mode driver_fix_no_group without orders',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['custom_orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'driver_fix_no_group',
            _DRIVER_FIX_RULE1_MODE_SETTINGS,
            {_DRIVER_FIX_NO_GROUP_RULE_ID, _ORDERS_RULE_ID},
            id='current mode driver_fix_no_group with orders',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['orders', 'driver_fix_no_group'],
                        default_unsubscribe_permissions={
                            'offers_groups': [],
                            'work_modes': [],
                        },
                    ),
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_fleet_offers_park_config(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_authorizer,
        current_mode: str,
        current_mode_settings: Optional[Dict[str, Any]],
        expected_modes: Set[str],
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request,
            current_mode,
            mocked_time,
            mode_settings=current_mode_settings,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer_by_zone')
    async def _mock_view_offer(request):
        return _DRIVER_FIX_OFFERS

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/offers-list',
        json={
            'park_id': _PARK_ID,
            'driver_uuid': _DRIVER_ID,
            'tariff_zones': [{'name': 'moscow'}],
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200

    doc = response.json()

    actual_modes = set()

    for offer in doc['offers']:
        if 'unavailable_reason' not in offer:
            actual_modes.add(offer['id'])

    assert actual_modes == expected_modes


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
            mode_rules.Patch(
                rule_name='driver_fix',
                rule_id=_DRIVER_FIX_RULE_ID,
                features={'driver_fix': {}},
                offers_group='eda',
            ),
            mode_rules.Patch(
                rule_name='custom_orders', rule_id=_CUSTOM_ORDERS_RULE_ID,
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
        _PARK_ID, ['orders', 'custom_orders'],
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_fleet_show_only_current_selected_driver_fix_offer(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_authorizer,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request,
            'driver_fix',
            mocked_time,
            mode_settings=_DRIVER_FIX_RULE1_MODE_SETTINGS,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer_by_zone')
    async def _mock_view_offer(request):
        return _DRIVER_FIX_OFFERS

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/offers-list',
        json={
            'park_id': _PARK_ID,
            'driver_uuid': _DRIVER_ID,
            'tariff_zones': [{'name': 'moscow'}],
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200

    doc = response.json()

    assert doc == {
        'offers': [
            {
                'id': '1d2b25b551034441afa2ea2855876e9d',
                'is_selected': True,
                'name': 'За время1',
                'settings': {
                    'rule_id': 'id_rule1',
                    'shift_close_time': '00:01',
                },
            },
        ],
    }


@pytest.mark.config(
    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
        _PARK_ID, ['orders', 'driver_fix'],
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
            mode_rules.Patch(
                rule_name='driver_fix',
                rule_id=_DRIVER_FIX_RULE_ID,
                features={'driver_fix': {}},
            ),
        ],
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_fleet_offers_driver_fix_call(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_authorizer,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer_by_zone')
    async def _mock_offer_by_zone(request):
        return _DRIVER_FIX_OFFERS

    _make_key_params_mock(mockserver)

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/offers-list',
        json={
            'park_id': _PARK_ID,
            'driver_uuid': _DRIVER_ID,
            'tariff_zones': [{'name': 'moscow'}],
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200

    doc = response.json()

    assert doc == {
        'offers': [
            {'id': _ORDERS_RULE_ID, 'is_selected': True, 'name': 'За заказы'},
            {
                'id': _DRIVER_FIX_RULE_ID,
                'is_selected': False,
                'name': 'За время1',
                'settings': {
                    'rule_id': 'id_rule1',
                    'shift_close_time': '00:01',
                },
                'tariff_zone': {'localized_name': 'Москва', 'name': 'moscow'},
            },
            {
                'id': _DRIVER_FIX_RULE_ID,
                'is_selected': False,
                'name': 'За время2',
                'settings': {
                    'rule_id': 'id_rule2',
                    'shift_close_time': '00:01',
                },
                'tariff_zone': {'localized_name': 'Москва', 'name': 'moscow'},
            },
        ],
    }

    assert _mock_offer_by_zone.times_called == 1
    request = _mock_offer_by_zone.next_call()['request']

    assert request.headers['Accept-Language'] == 'ru'
    assert request.json == {
        'driver_profile_id': _DRIVER_ID,
        'park_id': _PARK_ID,
        'tariff_zones': ['moscow'],
    }


@pytest.mark.config(
    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
        _PARK_ID, ['orders', 'custom_orders', 'geobooking', 'geobooking2'],
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'custom_orders': 'custom_orders_template',
            'geobooking': 'geobooking_template',
            'geobooking2': 'geobooking_template',
            'uberdriver': 'uberdriver_template',
        },
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
            mode_rules.Patch(
                rule_name='geobooking',
                rule_id=_GEOBOOKING_RULE_ID,
                features={'geobooking': {}},
            ),
            mode_rules.Patch(
                rule_name='geobooking2',
                rule_id=_GEOBOOKING2_RULE_ID,
                features={'geobooking': {}},
            ),
            mode_rules.Patch(
                rule_name='driver_fix',
                rule_id=_DRIVER_FIX_RULE_ID,
                features={'driver_fix': {}},
            ),
            mode_rules.Patch(
                rule_name='custom_orders', rule_id=_CUSTOM_ORDERS_RULE_ID,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode, current_mode_setting, expected_offers',
    [
        pytest.param(
            'orders',
            None,
            [
                {
                    'id': _ORDERS_RULE_ID,
                    'is_selected': True,
                    'name': 'За заказы',
                },
                {
                    'id': _CUSTOM_ORDERS_RULE_ID,
                    'is_selected': False,
                    'name': 'Карточка.Заголовок(default)',
                },
            ],
            id='geobooking offers not supported',
        ),
        pytest.param(
            'geobooking',
            {'rule_id': 'rule_id'},
            [
                {
                    'id': _GEOBOOKING_RULE_ID,
                    'is_selected': True,
                    'name': 'За гарантии',
                    'settings': {'rule_id': 'rule_id'},
                },
                {
                    'id': _ORDERS_RULE_ID,
                    'is_selected': False,
                    'name': 'За заказы',
                },
                {
                    'id': _CUSTOM_ORDERS_RULE_ID,
                    'is_selected': False,
                    'name': 'Карточка.Заголовок(default)',
                },
            ],
            id='geobooking selected offer is shown',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_fleet_offers_show_selected_geobooking(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_authorizer,
        current_mode: str,
        current_mode_setting: Optional[Dict[str, Any]],
        expected_offers: List[Dict[str, Any]],
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request,
            current_mode,
            mocked_time,
            mode_settings=current_mode_setting,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer_by_zone')
    async def _mock_offer_by_zone(request):
        return _DRIVER_FIX_OFFERS

    _make_key_params_mock(mockserver)

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/offers-list',
        json={
            'park_id': _PARK_ID,
            'driver_uuid': _DRIVER_ID,
            'tariff_zones': [{'name': 'moscow'}],
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200

    doc = response.json()

    assert doc == {'offers': expected_offers}


@pytest.mark.config(
    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
        _PARK_ID, ['orders', 'driver_fix'],
    ),
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
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
            mode_rules.Patch(
                rule_name='driver_fix',
                rule_id=_DRIVER_FIX_RULE_ID,
                features={'driver_fix': {}},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'driver_work_modes_response, expected_offers',
    [
        pytest.param(
            [{'id': 'driver_fix', 'is_enabled': False}],
            [
                {
                    'id': _ORDERS_RULE_ID,
                    'is_selected': True,
                    'name': 'За заказы',
                },
                {
                    'id': _DRIVER_FIX_RULE_ID,
                    'is_selected': False,
                    'name': 'За время1',
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'tariff_zone': {
                        'localized_name': 'Москва',
                        'name': 'moscow',
                    },
                    'unavailable_reason': {
                        'text': 'Режим запрещен условиями работы',
                    },
                },
                {
                    'id': _DRIVER_FIX_RULE_ID,
                    'is_selected': False,
                    'name': 'За время2',
                    'settings': {
                        'rule_id': 'id_rule2',
                        'shift_close_time': '00:01',
                    },
                    'tariff_zone': {
                        'localized_name': 'Москва',
                        'name': 'moscow',
                    },
                    'unavailable_reason': {
                        'text': 'Режим запрещен условиями работы',
                    },
                },
            ],
            id='park disable driver_fix ',
        ),
        pytest.param(
            [{'id': 'driver_fix', 'is_enabled': True}],
            [
                {
                    'id': _ORDERS_RULE_ID,
                    'is_selected': True,
                    'name': 'За заказы',
                },
                {
                    'id': _DRIVER_FIX_RULE_ID,
                    'is_selected': False,
                    'name': 'За время1',
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'tariff_zone': {
                        'localized_name': 'Москва',
                        'name': 'moscow',
                    },
                },
                {
                    'id': _DRIVER_FIX_RULE_ID,
                    'is_selected': False,
                    'name': 'За время2',
                    'settings': {
                        'rule_id': 'id_rule2',
                        'shift_close_time': '00:01',
                    },
                    'tariff_zone': {
                        'localized_name': 'Москва',
                        'name': 'moscow',
                    },
                },
            ],
            id='park enabled driver_fix',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_fleet_offers_park_validation(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        driver_authorizer,
        driver_work_modes_response: Dict[str, Any],
        expected_offers: List[Dict[str, Any]],
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer_by_zone')
    async def _mock_offer_by_zone(request):
        return _DRIVER_FIX_OFFERS

    @mockserver.json_handler('/driver-work-modes/v1/work-modes/list')
    def _mock_driver_work_modes(request):
        return {'work_modes': driver_work_modes_response}

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/offers-list',
        json={
            'park_id': _PARK_ID,
            'driver_uuid': _DRIVER_ID,
            'tariff_zones': [{'name': 'moscow'}],
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200

    doc = response.json()

    assert doc == {'offers': expected_offers}

    assert _mock_driver_work_modes.times_called == 1


_DEFAULT_GEONODES = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'root',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'root',
        'parent_name': 'br_russia',
        'tariff_zones': ['moscow'],
    },
    {
        'name': 'br_samara',
        'name_en': 'Samara',
        'name_ru': 'Самара',
        'node_type': 'root',
        'parent_name': 'br_russia',
        'tariff_zones': ['samara'],
        'region_id': '51',
    },
    {
        'name': 'br_spb',
        'name_en': 'St. Petersburg',
        'name_ru': 'Cанкт-Петербург',
        'node_type': 'agglomeration',
        'parent_name': 'br_russia',
        'tariff_zones': ['spb'],
        'region_id': '2',
    },
]


@pytest.mark.geo_nodes(_DEFAULT_GEONODES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'driver_fix_geo': 'driver_fix_template',
            'custom_orders': 'custom_orders_template',
            'geobooking': 'geobooking_template',
            'uberdriver': 'uberdriver_template',
        },
    },
    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
        'work_modes_available_by_default': [
            'orders',
            'driver_fix',
            'geobooking',
            'uberdriver',
        ],
        'work_modes_always_available': [],
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
            mode_rules.Patch(
                rule_name='custom_orders', rule_id=_GEOMODE_RULE_ID,
            ),
            mode_rules.Patch(
                rule_name='driver_fix_geo',
                rule_id=_DRIVER_FIX_RULE_ID,
                features={'driver_fix': {}},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode, expected_offers',
    [
        pytest.param(
            'orders',
            [
                {
                    'id': _ORDERS_RULE_ID,
                    'is_selected': True,
                    'name': 'За заказы',
                },
                {
                    'id': _DRIVER_FIX_RULE_ID,
                    'is_selected': False,
                    'name': 'За время1',
                    'settings': {
                        'rule_id': 'id_rule_moscow',
                        'shift_close_time': '00:01',
                    },
                    'tariff_zone': {
                        'localized_name': 'Москва',
                        'name': 'moscow',
                    },
                },
                {
                    'id': _DRIVER_FIX_RULE_ID,
                    'is_selected': False,
                    'name': 'За время1',
                    'settings': {
                        'rule_id': 'id_rule_samara',
                        'shift_close_time': '00:01',
                    },
                    'tariff_zone': {
                        'localized_name': 'Самара',
                        'name': 'samara',
                    },
                },
                {
                    'id': _GEOMODE_RULE_ID,
                    'is_selected': False,
                    'name': 'Карточка.Заголовок(default)',
                    'tariff_zone': {
                        'localized_name': 'Москва',
                        'name': 'moscow',
                    },
                },
                {
                    'id': _GEOMODE_RULE_ID,
                    'is_selected': False,
                    'name': 'Карточка.Заголовок(default)',
                    'tariff_zone': {
                        'localized_name': 'Санкт-Петербург',
                        'name': 'spb',
                    },
                },
            ],
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID,
                        ['orders', 'custom_orders', 'driver_fix_geo'],
                    ),
                ),
            ],
            id='mode with geography offers available',
        ),
        pytest.param(
            'custom_orders',
            [
                {
                    'id': _GEOMODE_RULE_ID,
                    'is_selected': True,
                    'name': 'Карточка.Заголовок(default)',
                },
                {
                    'id': _ORDERS_RULE_ID,
                    'is_selected': False,
                    'name': 'За заказы',
                },
            ],
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_PARK_OFFERS=_make_park_offers_config(
                        _PARK_ID, ['orders', 'custom_orders'],
                    ),
                ),
            ],
            id='current mode with geography erase tariff zone',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_fleet_offers_multiple_tariffzones(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mockserver,
        mocked_time,
        pgsql,
        taxi_config,
        driver_authorizer,
        current_mode: str,
        expected_offers: List[Dict[str, Any]],
):
    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'driver_fix_geo', 'moscow', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'driver_fix_geo', 'samara', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'custom_orders', 'spb', True,
            ),
            geography_tools.ModeGeographyConfiguration(
                'custom_orders', 'moscow', True,
            ),
        ],
        pgsql,
    )

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, work_mode=current_mode, mocked_time=mocked_time,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer_by_zone')
    async def _mock_offer_by_zone(request):
        request_data = request.json
        tariff_zones = request_data['tariff_zones']
        offers = []

        for tariff_zone in tariff_zones:
            offers.append(
                {
                    'title': 'За время1',
                    'tariff_zone': tariff_zone,
                    'settings': {
                        'rule_id': 'id_rule_' + tariff_zone,
                        'shift_close_time': '00:01',
                    },
                },
            )

        return {'offers': offers}

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/offers-list',
        json={
            'park_id': _PARK_ID,
            'driver_uuid': _DRIVER_ID,
            'tariff_zones': [
                {'name': 'moscow'},
                {'name': 'spb'},
                {'name': 'samara'},
            ],
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200

    actual_response = response.json()

    assert actual_response == {'offers': expected_offers}
