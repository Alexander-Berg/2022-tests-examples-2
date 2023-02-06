from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


def check_logistics_stop_request(
        request: Dict[str, Any], driver_profile: driver.Profile,
):
    assert request == {
        'contractor_id': {
            'driver_profile_id': driver_profile.profile_id(),
            'park_id': driver_profile.park_id(),
        },
    }


def check_logistics_start_request(
        request: Dict[str, Any],
        driver_profile: driver.Profile,
        mode_settings: Dict[str, Any],
):
    assert request == {
        'contractor_id': {
            'driver_profile_id': driver_profile.profile_id(),
            'park_id': driver_profile.park_id(),
        },
        'offer_identity': mode_settings,
    }


_PREV_SLOT_ID = 'b1aca90a-360f-499c-87bc-53fa41e58470'
_NEXT_SLOT_ID = '1b488dd5-24d9-48bb-8bfa-65c013755a22'

_PREV_SETTINGS = {'slot_id': _PREV_SLOT_ID, 'rule_version': 1}
_NEXT_SETTINGS = {'slot_id': _NEXT_SLOT_ID, 'rule_version': 2}


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expect_stop_logistics, expect_start_logistics',
    (
        pytest.param(False, False, id='no feature, no logistics calls'),
        pytest.param(True, False, id='stop logistics from prev mode'),
        pytest.param(False, True, id='start logistics in next mode'),
        pytest.param(True, True, id='stop and start'),
    ),
)
async def test_subscription_saga_logistic_workshifts(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        expect_stop_logistics: bool,
        expect_start_logistics: bool,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode',
                    features={'logistic_workshifts': {}}
                    if expect_start_logistics
                    else None,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode',
                    features={'logistic_workshifts': {}}
                    if expect_stop_logistics
                    else None,
                ),
            ],
        ),
    )

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler(
        r'/(logistic-supply-conductor/internal/v1/courier/)(?P<name>.+)',
        regex=True,
    )
    def handlers_mock(request, name):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_stop_logistics:
        on_stop_call = handlers_mock.next_call()
        assert on_stop_call['name'] == 'on-workshift-stop/'
        check_logistics_stop_request(
            on_stop_call['request'].json, test_profile,
        )

    if expect_start_logistics:
        on_start_call = handlers_mock.next_call()
        assert on_start_call['name'] == 'on-workshift-start/'
        check_logistics_start_request(
            on_start_call['request'].json, test_profile, _NEXT_SETTINGS,
        )

    assert not handlers_mock.has_calls


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'blocked_state.sql'],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'prev_mode_has_logistic_workshifts, next_mode_has_logistic_workshifts ',
    (
        pytest.param(
            True,
            True,
            id='compensate stop/start, logistic_workshifts in prev/next mode',
        ),
        pytest.param(
            False,
            True,
            id='compensate start, logistic_workshifts in next mode',
        ),
        pytest.param(
            True,
            False,
            id='compensate stop, logistic_workshifts in prev mode',
        ),
    ),
)
async def test_subscription_saga_logistic_workshifts_compensate(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        prev_mode_has_logistic_workshifts: bool,
        next_mode_has_logistic_workshifts: bool,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode',
                    features={'logistic_workshifts': {}}
                    if next_mode_has_logistic_workshifts
                    else None,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode',
                    features={'logistic_workshifts': {}}
                    if prev_mode_has_logistic_workshifts
                    else None,
                ),
            ],
        ),
    )

    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                saga_tools.SAGA_SETTINGS_ENABLE_COMPENSATION
            ),
        ),
    )
    await taxi_driver_mode_subscription.invalidate_caches()

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler(
        r'/(logistic-supply-conductor/internal/v1/courier/)(?P<name>.+)',
        regex=True,
    )
    def handlers_mock(request, name):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if next_mode_has_logistic_workshifts:
        on_stop_call = handlers_mock.next_call()
        assert on_stop_call['name'] == 'on-workshift-stop/'
        check_logistics_stop_request(
            on_stop_call['request'].json, test_profile,
        )

    if prev_mode_has_logistic_workshifts:
        on_start_call = handlers_mock.next_call()
        assert on_start_call['name'] == 'on-workshift-start/'
        check_logistics_start_request(
            on_start_call['request'].json, test_profile, _PREV_SETTINGS,
        )

    assert not handlers_mock.has_calls
