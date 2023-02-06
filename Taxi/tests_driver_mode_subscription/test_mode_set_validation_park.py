from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

DRIVER_FIX_SETTINGS = {'rule_id': 'id', 'shift_close_time': '00:00:00+03:00'}

_NOW = '2019-05-01T05:00:00+00:00'


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'driver_work_modes_response, expect_success, '
    'expect_driver_work_modes_call',
    [
        pytest.param(
            {'work_modes': []},
            True,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': False,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            {'work_modes': [{'id': 'driver_fix', 'is_enabled': True}]},
            True,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': False,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            {'work_modes': [{'id': 'driver_fix', 'is_enabled': False}]},
            True,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': False,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            {'work_modes': [{'id': 'driver_fix', 'is_enabled': True}]},
            True,
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': True,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            {'work_modes': []},
            False,
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': True,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            {'work_modes': [{'id': 'driver_fix', 'is_enabled': False}]},
            False,
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'check_enabled': True,
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 60,
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
async def test_mode_set_ban_validation(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        driver_authorizer,
        taxi_config,
        set_by_session: bool,
        driver_work_modes_response: Dict[str, Any],
        expect_driver_work_modes_call: bool,
        expect_success: bool,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler('/driver-work-modes/v1/work-modes/list')
    def _work_modes_list(request):
        return driver_work_modes_response

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='driver_fix',
        mode_settings=DRIVER_FIX_SETTINGS,
        set_by_session=set_by_session,
    )

    if expect_driver_work_modes_call:
        assert _work_modes_list.times_called == 1
        work_mode_request = _work_modes_list.next_call()['request']
        assert work_mode_request.query == {
            'driver_profile_id': test_profile.profile_id(),
            'park_id': test_profile.park_id(),
        }
    else:
        assert _work_modes_list.times_called == 0

    if expect_success:
        assert response.status_code == 200
    else:
        assert response.status_code == 423
        response_body = response.json()
        if set_by_session:
            assert response_body == {
                'code': 'PARK_VALIDATION_FAILED',
                'localized_message': 'Парк запретил вам режим.',
                'localized_message_title': 'Парк запретил',
            }
        else:
            assert response_body['code'] == 'PARK_VALIDATION_FAILED'
            assert response_body['message'] == 'mode disabled in this park'
        assert 'details' not in response_body
