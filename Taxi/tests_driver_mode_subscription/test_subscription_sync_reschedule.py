import datetime
import json
from typing import Any
from typing import Dict


import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

# sha256sum parkid0_uuiddriver_fixbanned_by_park
_SHA256_TASK_ID = (
    '3bf1368cffeb14b64b80775139bbf668fb33f0f151ff52c7bcc04c47a18ec77c'
)

_OLD_SETTINGS = {'sync_settings': {'check_type': 'banned_by_park'}}

_OLD_KWARGS = {
    'accept_language': 'ru',
    'driver_profile_id': 'uuid',
    'park_id': 'parkid0',
    'reschedule_ms': 3000,
    'settings': json.dumps(_OLD_SETTINGS),
    'mode_id': 'driver_fix',
    'mode_settings': '{"key":"value"}',
    'event_time': {'$date': '2020-04-09T15:36:22.996Z'},
}

_NEW_KWARGS = {
    'accept_language': 'ru',
    'park_driver_id': 'parkid0_uuid',
    'reschedule_ms': 3000,
    'unsubscribe_reason': 'banned_by_park',
    'mode_id': 'driver_fix',
    'event_time': {'$date': '2020-04-09T15:36:22.996Z'},
}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
        'check_enabled': True,
        'reschedule_timeshift_ms': 3000,
        'subscription_sync_enabled': True,
    },
)
@pytest.mark.parametrize(
    'stq_params', [pytest.param(_NEW_KWARGS, id='just_reschedule')],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
async def test_sync_stq_reschedule(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        stq,
        stq_runner,
        mockserver,
        mocked_time,
        stq_params: Dict[str, Any],
):
    driver_profile = driver.Profile('parkid0_uuid')
    scene = scenario.Scene(
        profiles={
            driver_profile: driver.Mode(
                'driver_fix',
                mode_settings={'key1': 'value1'},
                started_at_iso='2020-07-29T00:00:00+00:00',
            ),
        },
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-work-modes/v1/work-modes/list')
    def _work_modes_list(request):
        response = {'work_modes': [{'id': 'driver_fix', 'is_enabled': True}]}
        return response

    await stq_runner.subscription_sync.call(
        task_id=_SHA256_TASK_ID, kwargs=stq_params,
    )

    stq_data = stq.subscription_sync.next_call()
    assert stq_data['queue'] == 'subscription_sync'
    assert stq_data['eta'] == datetime.datetime(2019, 5, 1, 9, 0, 3)
    assert stq_data['id'] == _SHA256_TASK_ID
    # This because call go to /stq-agent/queues/api/reschedule
    assert not stq_data['kwargs']
    assert not stq_data['args']
