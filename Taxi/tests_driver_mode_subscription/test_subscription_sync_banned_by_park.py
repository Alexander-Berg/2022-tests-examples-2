import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_DRIVER_MODE_RULES = mode_rules.default_mode_rules()

_UNSUBSCRIBE_REASONS = {
    'banned_by_park': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {'type': 'banned_by_park'},
        },
    },
}


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
        'check_enabled': True,
        'subscription_sync_enabled': False,
        'reschedule_timeshift_ms': 60,
    },
    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=_UNSUBSCRIBE_REASONS,
)
@pytest.mark.parametrize(
    'task_mode, mode_enabled_by_park, mode_has_no_group, expect_unsubscribe, '
    'expect_reschedule',
    (
        pytest.param(
            'driver_fix', True, False, False, True, id='not banned by park',
        ),
        pytest.param(
            'driver_fix', False, False, True, False, id='banned by park',
        ),
        pytest.param(
            'some_mode',
            False,
            False,
            False,
            False,
            id='task has different mode',
        ),
        pytest.param(
            'driver_fix', False, True, True, False, id='banned by park',
        ),
    ),
)
async def test_banned_by_park_sync_stq(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        stq,
        stq_runner,
        mockserver,
        mocked_time,
        testpoint,
        pgsql,
        mode_enabled_by_park: bool,
        expect_reschedule: bool,
        expect_unsubscribe: bool,
        task_mode: str,
        mode_has_no_group: bool,
):
    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    driver_profile = driver.Profile('parkid0_uuid')
    scene = scenario.Scene(
        profiles={driver_profile: driver.Mode('driver_fix')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-work-modes/v1/work-modes/list')
    def _work_modes_list(request):
        response = {
            'work_modes': [
                {'id': 'driver_fix', 'is_enabled': mode_enabled_by_park},
            ],
        }
        return response

    kwargs = {
        'park_driver_id': driver_profile.dbid_uuid(),
        'event_time': {'$date': '2020-04-09T15:36:22.996Z'},
        'mode_id': task_mode,
        'reschedule_ms': 2000,
        'accept_language': 'ru',
        'unsubscribe_reason': 'banned_by_park',
    }

    if mode_has_no_group:
        cursor = pgsql['driver_mode_subscription'].cursor()
        cursor.execute(
            'UPDATE config.mode_rules SET offers_group_id = null WHERE mode_id'
            ' = (SELECT id FROM config.modes WHERE name = \'driver_fix\')',
        )

    await stq_runner.subscription_sync.call(
        task_id='sample_task', kwargs=kwargs,
    )

    if expect_unsubscribe:
        assert stq.subscription_sync.times_called == 0
        assert _handle_mode_set_cpp_testpoint.times_called == 1
        mode_set_data = _handle_mode_set_cpp_testpoint.next_call()['data']
        # external_ref is random uuid4
        expected_external_ref = mode_set_data['external_ref']
        assert mode_set_data == common.mode_set_testpoint_data(
            driver_profile,
            accept_language='ru',
            external_ref=expected_external_ref,
            active_since='2019-05-01T09:00:00+00:00',
            mode='orders',
            source=saga_tools.SOURCE_SUBSCRIPTION_SYNC,
            change_reason='banned_by_park',
        )
    else:
        assert _handle_mode_set_cpp_testpoint.times_called == 0
        if expect_reschedule:
            assert stq.subscription_sync.times_called == 1
        else:
            assert stq.subscription_sync.times_called == 0
