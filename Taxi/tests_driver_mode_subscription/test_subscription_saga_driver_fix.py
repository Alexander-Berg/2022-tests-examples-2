from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


def check_driver_fix_request(
        request: Dict[str, Any],
        driver_profile: driver.Profile,
        mode_settings: Dict[str, Any],
):
    assert request == {
        'driver_profile_id': driver_profile.profile_id(),
        'mode_settings': mode_settings,
        'park_id': driver_profile.park_id(),
    }


# Duplicates the one from static/.../sagas.sql
_PREV_SETTINGS = {
    'shift_close_time': '00:00:00+03:00',
    'rule_id': 'prev_rule_id',
}
_NEXT_SETTINGS = {
    'shift_close_time': '00:00:00+03:00',
    'rule_id': 'next_rule_id',
}


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expect_stop_driver_fix, expect_start_driver_fix',
    (
        pytest.param(False, False, id='no feature, no driver_fix calls'),
        pytest.param(True, False, id='stop driver_fix from prev mode'),
        pytest.param(False, True, id='start driver_fix in next mode'),
        pytest.param(True, True, id='stop and start'),
    ),
)
async def test_subscription_saga_driver_fix(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        expect_stop_driver_fix: bool,
        expect_start_driver_fix: bool,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode',
                    features={'driver_fix': {}}
                    if expect_start_driver_fix
                    else None,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode',
                    features={'driver_fix': {}}
                    if expect_stop_driver_fix
                    else None,
                ),
            ],
        ),
    )

    test_profile = driver.Profile(f'parkid1_uuid1')

    await taxi_driver_mode_subscription.invalidate_caches()

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _v1_driver_fix_mode_prepare(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_stop_driver_fix:
        on_stop_request = _driver_fix_v1_mode_on_stop.next_call()['request']
        check_driver_fix_request(
            on_stop_request.json, test_profile, _PREV_SETTINGS,
        )

    if expect_start_driver_fix:
        prepare_request = _v1_driver_fix_mode_prepare.next_call()['request']
        check_driver_fix_request(
            prepare_request.json, test_profile, _NEXT_SETTINGS,
        )

        on_start_request = _driver_fix_v1_mode_on_start.next_call()['request']
        check_driver_fix_request(
            on_start_request.json, test_profile, _NEXT_SETTINGS,
        )

    assert not _driver_fix_v1_mode_on_stop.has_calls
    assert not _v1_driver_fix_mode_prepare.has_calls
    assert not _driver_fix_v1_mode_on_start.has_calls


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'blocked_state.sql'],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'prev_mode_has_driver_fix, next_mode_has_driver_fix, '
    'expect_prepare_driver_fix',
    (
        pytest.param(
            True, True, True, id='compensate stop driver_fix from prev mode',
        ),
        pytest.param(
            False, True, False, id='compensate start driver_fix in next mode',
        ),
        pytest.param(
            True, False, False, id='compensate stop driver_fix in prev mode',
        ),
    ),
)
async def test_subscription_saga_driver_fix_compensate(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        prev_mode_has_driver_fix: bool,
        next_mode_has_driver_fix: bool,
        expect_prepare_driver_fix: bool,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode',
                    features={'driver_fix': {}}
                    if next_mode_has_driver_fix
                    else None,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode',
                    features={'driver_fix': {}}
                    if prev_mode_has_driver_fix
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

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _v1_driver_fix_mode_prepare(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if prev_mode_has_driver_fix:
        on_start_request = _driver_fix_v1_mode_on_start.next_call()['request']
        check_driver_fix_request(
            on_start_request.json, test_profile, _PREV_SETTINGS,
        )

    if next_mode_has_driver_fix:
        on_stop_request = _driver_fix_v1_mode_on_stop.next_call()['request']
        check_driver_fix_request(
            on_stop_request.json, test_profile, _NEXT_SETTINGS,
        )

    if expect_prepare_driver_fix:
        prepare_request = _v1_driver_fix_mode_prepare.next_call()['request']
        check_driver_fix_request(
            prepare_request.json, test_profile, _PREV_SETTINGS,
        )

    assert not _driver_fix_v1_mode_on_stop.has_calls
    assert not _v1_driver_fix_mode_prepare.has_calls
    assert not _driver_fix_v1_mode_on_start.has_calls


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_subscription_saga_driver_fix_call_order(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode', features={'driver_fix': {}},
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode', features={'driver_fix': {}},
                ),
            ],
        ),
    )

    await taxi_driver_mode_subscription.invalidate_caches()

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )

    scene.setup(mockserver, mocked_time, mock_dmi_set=False)

    @mockserver.json_handler(
        r'/(driver-mode-index|driver-fix)(?P<name>.+)', regex=True,
    )
    def handlers_mock(request, name):
        if name == '/v1/mode/subscribe':
            return request.json
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert handlers_mock.next_call()['name'] == '/v1/mode/on_stop/'
    assert handlers_mock.next_call()['name'] == '/v1/mode/subscribe'
    assert handlers_mock.next_call()['name'] == '/v1/mode/on_start/'

    assert not handlers_mock.has_calls
