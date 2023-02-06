from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_NOW = '2020-04-04T14:00:00+00:00'

_DRIVER_MODE_FEATURES_DRIVER_FIX_EXCLUSIVE = {
    '__default__': {'is_exclusive': False},
    'driver_fix': {'is_exclusive': True},
}

_DRIVER_MODE_RULES = mode_rules.patched(
    [
        mode_rules.Patch(
            rule_name='doctor_fix',
            billing_mode='driver_fix',
            billing_mode_rule='doctor@driver_fix',
            display_mode='driver_fix',
            features={'driver_fix': {}},
        ),
        mode_rules.Patch(
            rule_name='driver_fix',
            display_mode='driver_fix',
            features={'driver_fix': {}},
        ),
        mode_rules.Patch(
            rule_name='driver_fix_no_group',
            display_mode='driver_fix',
            features={'driver_fix': {}},
            offers_group='no_group',
        ),
    ],
)


def check_external_ref_different(driver_mode_index_mode_set_mock):
    external_ref_set = set()
    assert driver_mode_index_mode_set_mock.has_calls
    while driver_mode_index_mode_set_mock.has_calls:
        mode_set_request = driver_mode_index_mode_set_mock.next_call()[
            'request'
        ]
        external_ref = mode_set_request.json['external_ref']
        assert external_ref not in external_ref_set
        external_ref_set.add(external_ref)


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_FEATURES=_DRIVER_MODE_FEATURES_DRIVER_FIX_EXCLUSIVE,
)
@pytest.mark.parametrize(
    'profiles, saga_profile, expected_profiles, expected_stop_calls',
    [
        pytest.param(
            {
                driver.Profile('dbid0_uuid0'): driver.Mode(
                    'driver_fix', mode_settings=common.MODE_SETTINGS,
                ),
                driver.Profile('dbid1_uuid1'): driver.Mode(
                    'doctor_fix', mode_settings=common.MODE_SETTINGS,
                ),
                driver.Profile('dbid2_uuid2'): driver.Mode('orders'),
            },
            driver.Profile('dbid0_uuid0'),
            {
                driver.Profile('dbid0_uuid0'): driver.Mode(
                    'orders', started_at_iso='2020-04-04T13:00:00+00:00',
                ),
                driver.Profile('dbid1_uuid1'): driver.Mode(
                    'doctor_fix', mode_settings=common.MODE_SETTINGS,
                ),
                driver.Profile('dbid2_uuid2'): driver.Mode('orders'),
            },
            [
                {
                    'driver_profile_id': 'uuid0',
                    'mode_settings': {'key': 'prev_value'},
                    'park_id': 'dbid0',
                },
            ],
            id='subscribe_to_orders_one_profile',
        ),
        pytest.param(
            {
                driver.Profile('dbid1_uuid1'): driver.Mode('orders'),
                driver.Profile('dbid3_uuid3'): driver.Mode(
                    'driver_fix', mode_settings=common.MODE_SETTINGS,
                ),
                driver.Profile('dbid2_uuid2'): driver.Mode(
                    'doctor_fix', mode_settings=common.MODE_SETTINGS,
                ),
                driver.Profile('dbid4_uuid4'): driver.Mode(
                    'driver_fix_no_group', started_at_iso=_NOW,
                ),
            },
            driver.Profile('dbid3_uuid3'),
            {
                driver.Profile('dbid1_uuid1'): driver.Mode('orders'),
                driver.Profile('dbid3_uuid3'): driver.Mode(
                    'doctor_fix', started_at_iso='2020-04-04T13:00:00+00:00',
                ),
                driver.Profile('dbid2_uuid2'): driver.Mode(
                    'orders', started_at_iso=_NOW,
                ),
                driver.Profile('dbid4_uuid4'): driver.Mode(
                    'driver_fix_no_group', started_at_iso=_NOW,
                ),
            },
            [
                {
                    'driver_profile_id': 'uuid3',
                    'mode_settings': {'key': 'prev_value'},
                    'park_id': 'dbid3',
                },
                {
                    'driver_profile_id': 'uuid2',
                    'mode_settings': common.MODE_SETTINGS,
                    'park_id': 'dbid2',
                },
            ],
            id='unsubscribe_one_profile_by_driver_fix_feature',
        ),
    ],
)
async def test_subscription_saga_exclusive_features(
        profiles: Dict[driver.Profile, driver.Mode],
        saga_profile: driver.Profile,
        expected_profiles: Dict[driver.Profile, driver.Mode],
        expected_stop_calls: List[Dict[str, Any]],
        taxi_driver_mode_subscription,
        mode_rules_data,
        mockserver,
        mocked_time,
        stq_runner,
):
    scene = scenario.Scene(profiles=profiles, udid='some_unique_id')
    scene.setup(mockserver, mocked_time)

    await scene.verify_profile_modes(profiles=profiles)

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _v1_driver_fix_mode_prepare(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, saga_profile)

    for profile in profiles:
        if profile != saga_profile:
            await saga_tools.call_stq_saga_task(stq_runner, profile)

    assert scene.profiles == expected_profiles

    for request in expected_stop_calls:
        on_stop_request = _driver_fix_v1_mode_on_stop.next_call()['request']
        assert on_stop_request.json == request

    assert not _driver_fix_v1_mode_on_stop.has_calls

    check_external_ref_different(scene.driver_mode_index_mode_set_mock)
