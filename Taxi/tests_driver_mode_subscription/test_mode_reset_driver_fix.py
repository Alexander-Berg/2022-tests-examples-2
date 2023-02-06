import datetime
from typing import Dict

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

_RESET_BECAUSE_EXPIRED = common.ResetModeRequest(
    reason='driver_fix_expired', language=None,
)

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()

_CURRENT_MODE = driver.Mode(
    'driver_fix', mode_settings={'rule_id': 'current_rule_id'},
)

_UNSUBSCRIBE_REASONS = {
    'driver_fix_expired': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {'type': 'driver_fix_expired'},
        },
    },
}


@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'default_mode, expected_mode, extected_title',
    [pytest.param('orders', 'orders', 'За заказы', id='reset to orders')],
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

    response = await _RESET_BECAUSE_EXPIRED.post(
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
        change_reason='driver_fix_expired',
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
        'driver_fix_expired',
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
            _RESET_BECAUSE_EXPIRED,
            200,
            common.build_reset_mode_response(
                'orders', 'orders_type', _MONTH_AGO,
            ),
            id='already default',
        ),
        pytest.param(
            'custom_orders',
            _RESET_BECAUSE_EXPIRED,
            200,
            common.build_reset_mode_response(
                'custom_orders', 'orders_type', _MONTH_AGO,
            ),
            id='no driver_fix feature',
        ),
    ],
)
async def test_preserve_current_mode_if_no_driver_fix_feature(
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


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='driver_fix_park',
                billing_mode='driver_fix',
                billing_mode_rule='driver_fix',
                display_mode='driver_fix',
                display_profile='driver_fix',
                offers_group=None,
                features={'driver_fix': {}},
                starts_at=_TEPOCH,
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_GROUPS=mode_groups.values(
        [
            mode_groups.Group(
                name='taxi', orders_provider='taxi', reset_modes=['orders'],
            ),
            mode_groups.Group(
                name='lavka', orders_provider='lavka', reset_modes=['lavka'],
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'reset_request, expected_code, expected_response',
    [
        pytest.param(
            common.ResetModeRequest(reason='driver_fix_expired'),
            200,
            common.build_reset_mode_response('orders', 'orders_type', _NOW),
        ),
        pytest.param(
            common.ResetModeRequest(),
            400,
            {'code': _NO_MODE_MATCHED_CODE, 'message': _NO_MODE_MATCHED_MSG},
        ),
    ],
)
async def test_mode_reset_driver_fix_no_group(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        pgsql,
        driver_authorizer,
        reset_request: common.ResetModeRequest,
        expected_code: int,
        expected_response: Dict[str, str],
):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'UPDATE config.mode_rules SET offers_group_id = null WHERE mode_id = '
        '(SELECT id FROM config.modes WHERE name = \'driver_fix_park\')',
    )

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                work_mode='driver_fix_park', started_at_iso=_MONTH_AGO,
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
