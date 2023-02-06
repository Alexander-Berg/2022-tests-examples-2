import datetime
from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_DBID = 'parkid0'
_UUID = 'uuid0'

_ORDERS_RULE_ID = 'a883a23977484000b870f0cfcc84e1f9'
_CUSTOM_ORDERS_RULE_ID = '438a9fc006074759b6967ebe046fe5e0'
_DRIVER_FIX_NO_GROUP_RULE_ID = 'd8005c7f9c7f42f5802e1b95fac9958b'
_GEOMODE_RULE_ID = '72019f80f2384c3488d1bd080cb2325b'

_DEFAULT_PARK_OFFERS_CONFIG = {
    'by_park_ids': [],
    'default': {
        'unsubscribe_permissions': {'offers_groups': [], 'work_modes': []},
        'work_modes': ['orders', 'driver_fix_no_group', 'geomode'],
    },
}

_DEFAULT_MODE_RULES = mode_rules.patched(
    [
        mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
        mode_rules.Patch(
            rule_name='driver_fix_no_group',
            rule_id=_DRIVER_FIX_NO_GROUP_RULE_ID,
            billing_mode='driver_fix',
            features={'driver_fix': {}},
            offers_group='no_group',
        ),
        mode_rules.Patch(
            rule_name='custom_orders', rule_id=_CUSTOM_ORDERS_RULE_ID,
        ),
        mode_rules.Patch(rule_name='geomode', rule_id=_GEOMODE_RULE_ID),
    ],
)


@pytest.mark.mode_rules(rules=_DEFAULT_MODE_RULES)
@pytest.mark.config(DRIVER_MODE_PARK_OFFERS=_DEFAULT_PARK_OFFERS_CONFIG)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_fleet_mode_set_change_reason(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        taxi_config,
        mocked_time,
):
    idempotency_token = 'idempotency_token'

    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('orders')}, udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time)

    request = {
        'park_id': test_profile.park_id(),
        'driver_uuid': test_profile.profile_id(),
        'offer': {
            'id': _DRIVER_FIX_NO_GROUP_RULE_ID,
            'settings': common.MODE_SETTINGS,
        },
    }
    headers = {
        'X-Idempotency-Token': idempotency_token,
        'Accept-Language': 'ru',
        'X-Ya-Service-Ticket': common.MOCK_TICKET,
    }

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/mode/change', json=request, headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == {}

    assert saga_tools.get_saga_db_data(test_profile, pgsql) == (
        1,
        datetime.datetime(2020, 5, 5, 10, 1),
        test_profile.park_id(),
        test_profile.profile_id(),
        'test-driver-id',
        'driver_fix_no_group',
        datetime.datetime(2020, 5, 5, 10, 1),
        common.MODE_SETTINGS,
        idempotency_token,
        'ru',
        None,
        saga_tools.COMPENSATION_POLICY_ALLOW,
        saga_tools.SOURCE_FLEET_MODE_CHANGE,
        'fleet_mode_change',
    )


@pytest.mark.mode_rules(rules=_DEFAULT_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_PARK_OFFERS=_DEFAULT_PARK_OFFERS_CONFIG,
    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
        'work_modes_available_by_default': [
            'orders',
            'custom_orders',
            'driver_fix_no_group',
        ],
        'work_modes_always_available': [],
    },
)
@pytest.mark.parametrize(
    'current_mode, offer, expected_code, expected_response',
    [
        pytest.param(
            'orders',
            {
                'id': _DRIVER_FIX_NO_GROUP_RULE_ID,
                'settings': common.MODE_SETTINGS,
            },
            200,
            {},
            id='good',
        ),
        pytest.param(
            'custom_orders',
            {
                'id': _DRIVER_FIX_NO_GROUP_RULE_ID,
                'settings': common.MODE_SETTINGS,
            },
            409,
            {
                'code': 'MODE_UNAVAILABLE',
                'message': 'Режим больше не доступен',
            },
            id='current mode unsubscribable',
        ),
        pytest.param(
            'orders',
            {'id': _CUSTOM_ORDERS_RULE_ID},
            409,
            {
                'code': 'MODE_UNAVAILABLE',
                'message': 'Режим больше не доступен',
            },
            id='unavailable mode',
        ),
        pytest.param(
            'orders',
            {
                'id': _DRIVER_FIX_NO_GROUP_RULE_ID,
                'settings': common.MODE_SETTINGS,
            },
            409,
            {
                'code': 'PARK_VALIDATION_FAILED',
                'message': 'Режим запрещен условиями работы',
            },
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': True,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
            id='park validation failed',
        ),
        pytest.param(
            'orders',
            {'id': _ORDERS_RULE_ID},
            200,
            {},
            id='no unused mode settings',
        ),
        pytest.param(
            'orders',
            {
                'id': _DRIVER_FIX_NO_GROUP_RULE_ID,
                'settings': {'wrong': 'settings'},
            },
            409,
            {
                'code': 'WRONG_MODE_SETTINGS',
                'message': 'Invalid mode settings',
            },
            id='invalid mode settings',
        ),
        pytest.param(
            'orders',
            {'id': _DRIVER_FIX_NO_GROUP_RULE_ID},
            409,
            {
                'code': 'WRONG_MODE_SETTINGS',
                'message': 'Invalid mode settings',
            },
            id='no required mode settings',
        ),
        pytest.param(
            'orders',
            {'id': _GEOMODE_RULE_ID},
            409,
            {
                'code': 'WRONG_TARIFF_ZONE',
                'message': 'Режим больше не доступен',
            },
            id='geo mode required tariff zone, but not provided',
        ),
        pytest.param(
            'geomode',
            {'id': _GEOMODE_RULE_ID, 'tariff_zone': {'name': 'moscow'}},
            200,
            {},
            id='geo mode',
        ),
    ],
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_fleet_mode_change(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mockserver,
        taxi_config,
        mocked_time,
        current_mode: str,
        offer: Dict[str, Any],
        expected_code: int,
        expected_response: Dict[str, Any],
):
    geography_tools.insert_mode_geography(
        [
            geography_tools.ModeGeographyConfiguration(
                'geomode', 'moscow', True,
            ),
        ],
        pgsql,
    )

    idempotency_token = 'idempotency_token'

    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode(current_mode)},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-work-modes/v1/work-modes/list')
    def _mock_driver_work_modes(request):
        return {'work_modes': [{'id': 'driver_fix', 'is_enabled': False}]}

    request = {
        'park_id': test_profile.park_id(),
        'driver_uuid': test_profile.profile_id(),
        'offer': offer,
    }
    headers = {
        'X-Idempotency-Token': idempotency_token,
        'Accept-Language': 'ru',
        'X-Ya-Service-Ticket': common.MOCK_TICKET,
    }

    response = await taxi_driver_mode_subscription.post(
        'v1/fleet/mode/change', json=request, headers=headers,
    )

    assert response.status_code == expected_code

    assert response.json() == expected_response
