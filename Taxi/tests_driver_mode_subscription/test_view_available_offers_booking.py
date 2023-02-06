import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_LONG_AGO = '2000-05-01T05:00:00+00:00'

_DRIVER_MODE_RULES = mode_rules.patched(
    patches=[
        mode_rules.Patch(rule_name='geobooking', features={'geobooking': {}}),
        mode_rules.Patch(
            rule_name='custom_orders',
            stops_at=datetime.datetime.fromisoformat(_LONG_AGO),
        ),
        mode_rules.Patch(
            rule_name='driver_fix',
            stops_at=datetime.datetime.fromisoformat(_LONG_AGO),
        ),
    ],
)


_VIEW_OFFERS_GEOBOOKING: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'title1',
            'description': 'description',
            'is_new': False,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule1'},
        'key_params': {
            'tariff_zone': 'test_tariff_zone',
            'subvention_geoarea': 'test_subvention_geoarea',
            'tag': 'no_free_slots_tag',
        },
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 1.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 1'}]},
    },
    {
        'offer_card': {
            'title': 'title2',
            'description': 'description',
            'is_new': False,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule2'},
        'key_params': {
            'tariff_zone': 'test_tariff_zone',
            'subvention_geoarea': 'test_subvention_geoarea',
            'tag': 'test_tag',
        },
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
]

_VIEW_OFFERS_DRIVER_FIX: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'title1',
            'description': 'description',
            'is_new': False,
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
            'title': 'title2',
            'description': 'description',
            'is_new': False,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule2', 'shift_close_time': '00:01'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
]


def get_item_with_id(ui_items: List[Dict[str, Any]], item_id: str):
    return next((item for item in ui_items if item['id'] == item_id), None)


def get_item_free_slot_text(card_ctor: Dict[str, Any]):
    return card_ctor['items'][2]['title']


@pytest.mark.pgsql('driver_mode_subscription', files=['one_reserved_slot.sql'])
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'driver_fix_2': 'driver_fix_template',
            'custom_orders': 'custom_orders_template',
            'geobooking': 'geobooking_template',
            'geobooking_2': 'geobooking_template',
        },
    },
)
@pytest.mark.parametrize(
    'expected_unfree_slots_names',
    (
        pytest.param(
            {'driver_fix_id_rule1'},
            id='driver_fix with different limits on same rule_id',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='driver_fix',
                                features={
                                    'driver_fix': {},
                                    'booking': {
                                        'slot_policy': 'mode_settings_rule_id',
                                    },
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='driver_fix_2',
                                features={
                                    'driver_fix': {},
                                    'booking': {
                                        'slot_policy': 'mode_settings_rule_id',
                                    },
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_DRIVER_FIX_SLOTS={
                        'default': {'limit': 1},
                        'modes': {
                            'driver_fix': {
                                'default': {'limit': 2},
                                'rules': {'id_rule1': {'limit': 1}},
                            },
                            'driver_fix_2': {
                                'default': {'limit': 2},
                                'rules': {'id_rule1': {'limit': 2}},
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            {'geobooking_id_rule1'},
            id='geobooking with slot_policy mode_settings_rule_id',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='geobooking',
                                features={
                                    'geobooking': {},
                                    'booking': {
                                        'slot_policy': 'mode_settings_rule_id',
                                    },
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='geobooking_2',
                                features={
                                    'geobooking': {},
                                    'booking': {
                                        'slot_policy': 'mode_settings_rule_id',
                                    },
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                            mode_rules.Patch(
                                rule_name='driver_fix',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_DRIVER_FIX_SLOTS={
                        'default': {'limit': 1},
                        'modes': {
                            'geobooking': {
                                'default': {'limit': 2},
                                'rules': {'id_rule1': {'limit': 1}},
                            },
                            'geobooking_2': {
                                'default': {'limit': 2},
                                'rules': {'id_rule1': {'limit': 2}},
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            {'geobooking_id_rule1'},
            id='geobooking with slot_policy key_params',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='geobooking',
                                features={
                                    'geobooking': {},
                                    'booking': {'slot_policy': 'key_params'},
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                            mode_rules.Patch(
                                rule_name='driver_fix',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_SLOTS={
                        'default': {'kickoff_percent': 100, 'limit': 50},
                        'tariff_zones': {
                            'test_tariff_zone': {
                                'subvention_geoareas': {
                                    'test_subvention_geoarea': {
                                        'tags': {
                                            'test_tag': {'limit': 2},
                                            'no_free_slots_tag': {'limit': 1},
                                        },
                                    },
                                },
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            {'geobooking_id_rule1', 'geobooking_id_rule2'},
            id='geobooking with slot_policy contractor_tariff_zone',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='geobooking',
                                features={
                                    'geobooking': {},
                                    'booking': {
                                        'slot_policy': (
                                            'contractor_tariff_zone'
                                        ),
                                    },
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='geobooking_2',
                                features={
                                    'geobooking': {},
                                    'booking': {
                                        'slot_policy': (
                                            'contractor_tariff_zone'
                                        ),
                                    },
                                },
                            ),
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                            mode_rules.Patch(
                                rule_name='driver_fix',
                                stops_at=datetime.datetime.fromisoformat(
                                    _LONG_AGO,
                                ),
                            ),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_TARIFF_ZONE_SLOTS={
                        'default': {'limit': 2},
                        'modes': {
                            'geobooking': {
                                'default': {'limit': 2},
                                'tariff_zones': {'moscow': {'limit': 1}},
                            },
                            'geobooking_2': {
                                'default': {'limit': 2},
                                'tariff_zones': {
                                    'moscow': {'limit': 2},
                                    'spb': {'limit': 1},
                                },
                            },
                        },
                    },
                ),
                pytest.mark.geoareas(filename='geoareas_moscow.json'),
                pytest.mark.tariffs(filename='tariffs.json'),
            ],
        ),
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_available_offers_free_slots(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        expected_unfree_slots_names: Set[str],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/geobooking_offer')
    async def _mock_geobooking_view_offer(request):
        return {'offers': _VIEW_OFFERS_GEOBOOKING}

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_driver_fix_view_offer(request):
        return {'offers': _VIEW_OFFERS_DRIVER_FIX}

    scenario.Scene.mock_driver_trackstory(mockserver, scenario.MOSCOW_POSITION)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200

    doc = response.json()

    assert doc['ui']['items'][0]['id'] == 'orders'

    assert len(doc['ui']['items']) > 1

    # first element is selected orders and do not have free slots
    for card_ctor in doc['ui']['items'][1:]:
        if card_ctor['id'] in expected_unfree_slots_names:
            assert get_item_free_slot_text(card_ctor) == 'Нет свободных мест'
        else:
            assert get_item_free_slot_text(card_ctor) == 'Есть свободные места'


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='geobooking',
                features={
                    'geobooking': {},
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                },
            ),
            mode_rules.Patch(
                rule_name='custom_orders',
                features={
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                },
            ),
            mode_rules.Patch(
                rule_name='driver_fix',
                stops_at=datetime.datetime.fromisoformat(_LONG_AGO),
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'trackstory_error, trackstory_position, client_position, '
    'expected_mode_ids',
    [
        pytest.param(
            scenario.ServiceError.NoError,
            scenario.MOSCOW_POSITION,
            None,
            {
                'orders',
                'custom_orders',
                'geobooking_id_rule1',
                'geobooking_id_rule2',
            },
            id='all good',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            None,
            {'orders'},
            id='no position',
        ),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            scenario.MOSCOW_POSITION,
            None,
            {'orders'},
            id='trackstory timeout',
        ),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            scenario.MOSCOW_POSITION,
            scenario.MOSCOW_POSITION,
            {
                'orders',
                'custom_orders',
                'geobooking_id_rule1',
                'geobooking_id_rule2',
            },
            id='trackstory timeout with fallback to client position',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            scenario.PERM_POSITION,
            None,
            {'orders'},
            id='no tariff zone',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_available_offers_skip_failed_modes(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        trackstory_position: Optional[common.Position],
        client_position: Optional[common.Position],
        trackstory_error: scenario.ServiceError,
        expected_mode_ids: Set[str],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/geobooking_offer')
    async def _mock_geobooking_view_offer(request):
        return {'offers': _VIEW_OFFERS_GEOBOOKING}

    driver_trackstory_mock = scenario.Scene.mock_driver_trackstory(
        mockserver, trackstory_position, trackstory_error,
    )

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile, client_position,
    )
    assert response.status_code == 200

    doc = response.json()

    actual_mode_ids = set()

    for card_ctor in doc['ui']['items']:
        actual_mode_ids.add(card_ctor['id'])

    assert actual_mode_ids == expected_mode_ids

    if trackstory_error == scenario.ServiceError.NoError:
        assert driver_trackstory_mock.times_called == 1
    else:
        assert driver_trackstory_mock.times_called == 3
