import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_DRIVER_ID = 'uuid1'
_PARK_ID = 'parkid1'


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expect_fail, expected_profile',
    [
        pytest.param(
            False,
            'usual_orders',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                display_profile='usual_orders',
                            ),
                        ],
                    ),
                ),
            ],
            id='correct config',
        ),
        pytest.param(
            True,
            'usual_orders',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                display_profile='usual_orders',
                            ),
                        ],
                    ),
                ),
            ],
            id='endpoint error',
        ),
        pytest.param(
            False,
            'custom_orders',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [mode_rules.Patch(rule_name='custom_orders')],
                    ),
                ),
            ],
            id='no display profile in config',
        ),
        pytest.param(
            False,
            'orders',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                        saga_tools.SAGA_SETTINGS_ENABLE_COMPENSATION
                    ),
                ),
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [mode_rules.Patch(rule_name='custom_orders')],
                    ),
                ),
            ],
            id='compensate display profile',
        ),
    ],
)
async def test_subscription_saga_set_ui_profile(
        pgsql,
        mode_rules_data,
        mocked_time,
        stq_runner,
        mockserver,
        expect_fail: bool,
        expected_profile: str,
):
    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def driver_ui_profile(request):
        return mockserver.make_response(
            '{"status": "ok"}', status=500 if expect_fail else 200,
        )

    test_profile = driver.Profile(f'{_PARK_ID}_{_DRIVER_ID}')

    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, mock_driver_ui_profile=False)

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=expect_fail,
    )

    assert driver_ui_profile.times_called == 1
    request = driver_ui_profile.next_call()['request']
    assert request.json == {
        'display_mode': 'orders_type',
        'display_profile': expected_profile,
        'driver_profile_id': _DRIVER_ID,
        'park_id': _PARK_ID,
    }

    assert saga_tools.has_saga(test_profile, pgsql) == expect_fail

    if expect_fail:
        expect_fail = False

        await saga_tools.call_stq_saga_task(stq_runner, test_profile)

        assert driver_ui_profile.times_called == 1
        request = driver_ui_profile.next_call()['request']
        assert request.json == {
            'display_mode': 'orders_type',
            'display_profile': expected_profile,
            'driver_profile_id': _DRIVER_ID,
            'park_id': _PARK_ID,
        }

        assert not saga_tools.has_saga(test_profile, pgsql)
