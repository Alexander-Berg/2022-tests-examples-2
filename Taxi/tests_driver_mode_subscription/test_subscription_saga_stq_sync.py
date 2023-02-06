import datetime

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_NOW = '2019-05-01T05:00:00+00:00'

# sha256sum parkid1_uuid1driver_fixbanned_by_park
_SHA256_TASK_ID = (
    'e71dd529e2f416506a8c761f45329c807659b77747a275ea4a7a165b2e771a79'
)


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched([mode_rules.Patch(rule_name='prev_work_mode')]),
)
@pytest.mark.parametrize(
    'expect_sync_call',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'subscription_sync_enabled': True,
                        'reschedule_timeshift_ms': 7000,
                        'check_enabled': True,
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
                        'subscription_sync_enabled': False,
                        'reschedule_timeshift_ms': 7000,
                        'check_enabled': True,
                    },
                ),
            ],
        ),
    ],
)
async def test_subscription_saga_stq_sync_config(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mockserver,
        mocked_time,
        stq_runner,
        stq,
        expect_sync_call: bool,
):
    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _v1_driver_fix_mode_prepare(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    new_work_mode = 'driver_fix'
    prev_work_mode = 'prev_work_mode'
    test_profile = driver.Profile('parkid1_uuid1')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode(prev_work_mode)},
    )
    scene.setup(mockserver, mocked_time)

    await taxi_driver_mode_subscription.invalidate_caches()

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_sync_call:
        assert stq.subscription_sync.times_called == 1

        stq_data = stq.subscription_sync.next_call()
        assert stq_data['queue'] == 'subscription_sync'
        assert stq_data['id'] == _SHA256_TASK_ID
        assert stq_data['eta'] == datetime.datetime(2019, 5, 1, 5, 0, 7)

        stq_kwargs = stq_data['kwargs']
        del stq_kwargs['log_extra']
        assert stq_kwargs == {
            'mode_id': new_work_mode,
            'park_driver_id': test_profile.dbid_uuid(),
            'event_time': {'$date': '2020-04-04T13:00:00.000Z'},
            'reschedule_ms': 7000,
            'accept_language': 'ru',
            'unsubscribe_reason': 'banned_by_park',
        }
    else:
        assert stq.subscription_sync.times_called == 0
