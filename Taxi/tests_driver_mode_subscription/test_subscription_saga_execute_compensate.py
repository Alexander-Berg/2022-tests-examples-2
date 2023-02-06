import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_SAGA_SETTINGS = {
    'enable_saga_persistent': True,
    'allow_saga_compensation': True,
}

_SAGA_SETTINGS_SMALL_TIMEOUT = {
    'enable_saga_persistent': True,
    'allow_saga_compensation': True,
    'compensate_failed_saga_timeout_s': 1,
}

_SAGA_SETTINGS_BIG_TIMEOUT = {
    'enable_saga_persistent': True,
    'allow_saga_compensation': True,
    'compensate_failed_saga_timeout_s': 3,
}

_SAGA_SETTINGS_COMPENSATION_DISABLED = {
    'enable_saga_persistent': True,
    'allow_saga_compensation': False,
    'compensate_failed_saga_timeout_s': 1,
}

_DRIVER_MODE_RULES = mode_rules.patched(
    [
        mode_rules.Patch(
            rule_name='next_work_mode', features={'driver_fix': {}},
        ),
        mode_rules.Patch(
            rule_name='prev_work_mode', features={'driver_fix': {}},
        ),
    ],
)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'blocked_state.sql'],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS)
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_subscription_saga_execute_compensate_blocked(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
):
    test_profile = driver.Profile('parkid1_uuid1')

    assert saga_tools.has_saga(test_profile, pgsql)

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _driver_fix_v1_mode_prepare(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert _driver_fix_v1_mode_prepare.times_called == 1

    assert _driver_fix_v1_mode_on_start.times_called == 1

    assert _driver_fix_v1_mode_on_start.next_call()['request'].json == {
        'driver_profile_id': test_profile.profile_id(),
        'mode_settings': {'key': 'prevvalue'},
        'park_id': test_profile.park_id(),
    }

    assert not saga_tools.has_saga(test_profile, pgsql)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'failed_state.sql'],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.now('2020-04-04 14:00:03+01')
@pytest.mark.parametrize(
    'expect_execute',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS,
                ),
            ],
            id='no timeout in config',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                        _SAGA_SETTINGS_BIG_TIMEOUT
                    ),
                ),
            ],
            id='timeout not pass',
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                        _SAGA_SETTINGS_SMALL_TIMEOUT
                    ),
                ),
            ],
            id='timeout pass',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                        _SAGA_SETTINGS_COMPENSATION_DISABLED
                    ),
                ),
            ],
            id='timeout pass, compensate disabled',
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    files=['add_unrevertable_step.sql'],
                ),
            ],
            id='reach_unrevertable_stage',
        ),
    ],
)
async def test_subscription_saga_execute_compensate_failed(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
        expect_execute: bool,
):
    test_profile = driver.Profile('parkid1_uuid1')

    assert saga_tools.has_saga(test_profile, pgsql)

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_execute:
        assert _driver_fix_v1_mode_on_stop.times_called == 1
    else:
        assert _driver_fix_v1_mode_on_start.times_called == 1

    assert not saga_tools.has_saga(test_profile, pgsql)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'blocked_state.sql'],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS)
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_subscription_saga_execute_compensate_forbid(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
):
    test_profile = driver.Profile('parkid2_uuid2')

    scene = scenario.Scene({test_profile: driver.Mode('driver_fix')})
    scene.setup(mockserver, mocked_time)

    assert saga_tools.has_saga(test_profile, pgsql)

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert _driver_fix_v1_mode_on_stop.times_called == 1

    assert not saga_tools.has_saga(test_profile, pgsql)


@pytest.mark.pgsql(
    'driver_mode_subscription', files=['sagas.sql', 'blocked_state.sql'],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=_SAGA_SETTINGS)
async def test_subscription_saga_execute_compensate_save_results(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
):
    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _driver_fix_v1_mode_prepare(request):
        raise mockserver.TimeoutError()

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=True,
    )

    assert _driver_fix_v1_mode_prepare.times_called == 3

    assert _driver_fix_v1_mode_on_start.times_called == 1

    assert saga_tools.get_saga_steps_db_data(pgsql, 1) == [
        ('driver_fix_prepare_step', 'ok', 'failed'),
        ('driver_fix_start_step', 'ok', 'ok'),
        ('driver_fix_stop_step', 'ok', 'ok'),
        ('mode_change_step', 'blocked', 'ok'),
    ]

    @mockserver.json_handler('/driver-fix/v1/mode/prepare/')
    def _driver_fix_v1_mode_prepare_2(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=True,
    )

    assert _driver_fix_v1_mode_prepare_2.times_called == 1

    assert saga_tools.get_saga_steps_db_data(pgsql, 1) == [
        ('driver_fix_prepare_step', 'ok', 'blocked'),
        ('driver_fix_start_step', 'ok', 'ok'),
        ('driver_fix_stop_step', 'ok', 'ok'),
        ('mode_change_step', 'blocked', 'ok'),
    ]
