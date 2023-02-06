import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_groups
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_NO_MODE_MATCHED_CODE = 'NO_MATCHING_MODE_FOUND'
_NO_MODE_MATCHED_MSG = 'no mode matched requested params'

_NOW = '2020-07-30T05:00:00+00:00'
_TNOW = datetime.datetime.fromisoformat(_NOW)
_TNOW_NO_OFFSET = datetime.datetime(2020, 7, 30, 5, 0, 0)
_INBETWEEN = '2020-07-29T00:00:00+00:00'
_TINBETWEEN = datetime.datetime.fromisoformat(_INBETWEEN)
_MONTH_AGO = '2020-06-29T00:00:00+00:00'
_TMONTH_AGO = datetime.datetime.fromisoformat(_MONTH_AGO)
_EPOCH = '1970-01-01T00:00:00+00:00'
_TEPOCH = datetime.datetime.fromisoformat(_EPOCH)

_RESET_BECAUSE_VIOLATIONS = common.ResetModeRequest(
    reason='geobooking_violations', language=None,
)

_DRIVER_MODE_RULES = mode_rules.patched(
    [mode_rules.Patch(rule_name='geobooking', features={'geobooking': {}})],
)

_CURRENT_MODE = driver.Mode(
    'geobooking', mode_settings={'rule_id': 'current_rule_id'},
)

_UNSUBSCRIBE_REASONS = {
    'geobooking_violations': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {'type': 'geobooking_violations'},
        },
    },
}


def _make_key_params_mock(mockserver, tag: str):
    @mockserver.json_handler('/driver-fix/v1/view/rule_key_params')
    async def _mock_view_offer(request):
        return {
            'rules': [
                {
                    'rule_id': 'current_rule_id',
                    'key_params': {
                        'tariff_zone': 'current_zone',
                        'subvention_geoarea': 'current_area',
                        'tag': tag,
                    },
                },
            ],
        }


def _configure_slot_limits(
        limit: Optional[int], kickoff_percent: Optional[int],
):
    _driver_mode_booking_slots: Dict[str, Any] = {
        'default': {'kickoff_percent': 100, 'limit': 10},
        'tariff_zones': {},
    }

    if not (limit or kickoff_percent):
        return _driver_mode_booking_slots

    _subvention_geoareas: Dict[str, Any] = {
        'subvention_geoareas': {'current_area': {'tags': {'ten_slots': {}}}},
    }

    _ten_slots_tag = _subvention_geoareas['subvention_geoareas'][
        'current_area'
    ]['tags']['ten_slots']

    if limit:
        _ten_slots_tag['limit'] = limit
    if kickoff_percent:
        _ten_slots_tag['kickoff_percent'] = kickoff_percent

    _driver_mode_booking_slots['tariff_zones'][
        'current_zone'
    ] = _subvention_geoareas

    return _driver_mode_booking_slots


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['reservation_ten_slots.sql'],
)
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'default_mode, expected_mode, extected_title',
    [
        pytest.param(
            'orders',
            'orders',
            'За заказы',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_SLOTS=_configure_slot_limits(
                        None, None,
                    ),
                ),
            ],
            id='reset to default limit',
        ),
        pytest.param(
            'orders',
            'orders',
            'За заказы',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_SLOTS=_configure_slot_limits(
                        limit=10, kickoff_percent=None,
                    ),
                ),
            ],
            id='reset to ten limit',
        ),
        pytest.param(
            'orders',
            'orders',
            'За заказы',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_SLOTS=_configure_slot_limits(
                        limit=20, kickoff_percent=50,
                    ),
                ),
            ],
            id='reset to kickoff limit',
        ),
    ],
)
async def test_mode_reset(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        testpoint,
        pgsql,
        stq,
        driver_authorizer,
        default_mode: str,
        expected_mode: str,
        extected_title: str,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: _CURRENT_MODE})
    scene.setup(mockserver, mocked_time, driver_authorizer)
    _make_key_params_mock(mockserver, 'ten_slots')
    taxi_config.set_values(
        dict(
            DRIVER_MODE_GROUPS={
                'taxi': {
                    'orders_provider': 'taxi',
                    'reset_modes': [default_mode],
                },
            },
            DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=_UNSUBSCRIBE_REASONS,
        ),
    )
    await taxi_driver_mode_subscription.invalidate_caches()

    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    response = await _RESET_BECAUSE_VIOLATIONS.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    response_code = response.status_code
    response_body = response.json()

    assert response_code == 200
    assert response_body == {
        'active_mode': expected_mode,
        'active_mode_type': 'orders_type',
        'active_since': _NOW,
    }

    assert _handle_mode_set_cpp_testpoint.times_called == 1
    mode_set_data = _handle_mode_set_cpp_testpoint.next_call()['data']
    assert mode_set_data == common.mode_set_testpoint_data(
        test_profile,
        accept_language='ru',
        external_ref='idempotency_key',
        active_since=_NOW,
        mode=expected_mode,
        source=saga_tools.SOURCE_SERVICE_MODE_RESET,
        change_reason='geobooking_violations',
    )

    assert saga_tools.get_saga_db_data(test_profile, pgsql) == (
        1,
        _TNOW_NO_OFFSET,
        test_profile.park_id(),
        test_profile.profile_id(),
        scene.udid,
        expected_mode,
        _TNOW_NO_OFFSET,
        None,
        'idempotency_key',
        'ru',
        None,
        saga_tools.COMPENSATION_POLICY_FORBID,
        saga_tools.SOURCE_SERVICE_MODE_RESET,
        'geobooking_violations',
    )


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['reservation_ten_slots.sql'],
)
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_GROUPS=mode_groups.values(
        [
            mode_groups.Group(
                name='taxi', orders_provider='taxi', reset_modes=['orders'],
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_SLOTS=_configure_slot_limits(
                        limit=11, kickoff_percent=None,
                    ),
                ),
            ],
            id='has free slot',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_BOOKING_SLOTS=_configure_slot_limits(
                        limit=21, kickoff_percent=50,
                    ),
                ),
            ],
            id='has free slot with kickoff',
        ),
    ],
)
async def test_preserve_geobooking(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: _CURRENT_MODE})
    scene.setup(mockserver, mocked_time, driver_authorizer)
    _make_key_params_mock(mockserver, 'ten_slots')

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await _RESET_BECAUSE_VIOLATIONS.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    assert response.status_code == 200
    assert response.json() == common.build_reset_mode_response(
        'geobooking', 'orders_type', _EPOCH,
    )


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['reservation_ten_slots.sql'],
)
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_GROUPS=mode_groups.values(
        [
            mode_groups.Group(
                name='taxi', orders_provider='taxi', reset_modes=['orders'],
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode, reset_request, expected_code, expected_response',
    [
        pytest.param(
            'orders',
            _RESET_BECAUSE_VIOLATIONS,
            200,
            common.build_reset_mode_response(
                'orders', 'orders_type', _MONTH_AGO,
            ),
            id='already default',
        ),
        pytest.param(
            'driver_fix',
            _RESET_BECAUSE_VIOLATIONS,
            200,
            common.build_reset_mode_response(
                'driver_fix', 'driver_fix_type', _MONTH_AGO,
            ),
            id='no geobooking feature',
        ),
    ],
)
async def test_preserve_current_mode_if_no_geobooking_feature(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
        current_mode: str,
        reset_request: common.ResetModeRequest,
        expected_code: int,
        expected_response: Dict[str, str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                work_mode=current_mode, started_at_iso=_MONTH_AGO,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await reset_request.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    assert expected_code == response.status_code
    assert expected_response == response.json()
