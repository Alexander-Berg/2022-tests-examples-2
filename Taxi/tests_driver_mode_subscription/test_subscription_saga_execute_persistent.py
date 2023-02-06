import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

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
    'driver_mode_subscription', files=['sagas.sql', 'state.sql'],
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={'enable_saga_persistent': True},
)
async def test_subscription_saga_load_prev_execute_results(
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
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert _driver_fix_v1_mode_on_stop.times_called == 0

    assert _driver_fix_v1_mode_prepare.times_called == 1

    assert _driver_fix_v1_mode_on_start.times_called == 1


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={'enable_saga_persistent': True},
)
async def test_subscription_saga_save_execute_results_if_error(
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
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        raise mockserver.TimeoutError()

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=True,
    )

    assert _driver_fix_v1_mode_on_stop.times_called == 3

    assert _driver_fix_v1_mode_prepare.times_called == 1

    assert _driver_fix_v1_mode_on_start.times_called == 0

    assert saga_tools.get_saga_steps_db_data(pgsql, 1) == [
        ('driver_fix_prepare_step', 'ok', None),
        ('driver_fix_stop_step', 'failed', None),
    ]

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start_2(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error'},
        )

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop_2(request):
        return {}

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=True,
    )

    assert _driver_fix_v1_mode_on_stop_2.times_called == 1

    assert _driver_fix_v1_mode_prepare.times_called == 1

    assert _driver_fix_v1_mode_on_start_2.times_called == 1

    assert saga_tools.get_saga_steps_db_data(pgsql, 1) == [
        ('driver_fix_prepare_step', 'ok', None),
        ('driver_fix_start_step', 'blocked', None),
        ('driver_fix_stop_step', 'ok', None),
        ('mode_change_step', 'ok', None),
        ('ui_profile_change_step', 'ok', None),
    ]
