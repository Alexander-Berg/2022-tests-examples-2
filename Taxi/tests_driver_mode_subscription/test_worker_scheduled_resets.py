import datetime as dt
import json
from typing import Optional
import uuid


import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_resets_tools as db_tools
from tests_driver_mode_subscription import scheduled_slots_tools

_SLOT_ID_1 = uuid.UUID('af31c824-066d-46df-981f-a8dc431d64e8')
_SLOT_ID_2 = uuid.UUID('a936b353-fcda-4b7a-b569-a7fb855819dd')

_QUOTA_ID = uuid.UUID('3fa85a34-34ec-4b54-b172-97738b9cc5df')

_DRIVER_ID = 'uuid0'
_PARK_ID = 'parkid0'
_UNIQUE_DRIVER_ID = 'test-driver-id'

_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'

_OFFER_IDENTITY_1 = {'slot_id': str(_SLOT_ID_1), 'rule_version': 1}
_OFFER_IDENTITY_2 = {'slot_id': str(_SLOT_ID_2), 'rule_version': 1}

_LOGISTIC_WORKSHIFTS_RULE_ID = 'e65516264faa4d2ca52fea538cb75bd1'

_SCHEDULED_CHANGE_REASON = 'scheduled_slot_stop'


@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.parametrize(
    'expected_task_call', (pytest.param(True, id='no settings'),),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        db_tools.insert_scheduled_resets(
            [
                db_tools.ScheduledReset(
                    'dbid0',
                    'uuid0',
                    _SCHEDULED_CHANGE_REASON,
                    dt.datetime.fromisoformat('2020-04-04T05:00:00+00:00'),
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_worker_scheduled_resets(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
        expected_task_call: bool,
):
    profiles = {
        driver.Profile('dbid0_uuid0'): driver.Mode(
            'driver_fix', mode_settings=common.MODE_SETTINGS,
        ),
        driver.Profile('dbid1_uuid1'): driver.Mode(
            'driver_fix', mode_settings=common.MODE_SETTINGS,
        ),
        driver.Profile('dbid2_uuid2'): driver.Mode('orders'),
    }
    scene = scenario.Scene(profiles=profiles, udid='some_unique_id')
    scene.setup(mockserver, mocked_time)

    @testpoint('scheduled-resets-testpoint')
    def task_testpoint(data):
        pass

    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task('scheduled-resets')

    if expected_task_call:
        assert task_testpoint.times_called == 1
        assert _handle_mode_set_cpp_testpoint.times_called == 1
        mode_set_data = _handle_mode_set_cpp_testpoint.next_call()['data']
        # external_ref is random uuid4
        expected_external_ref = mode_set_data['external_ref']
        assert mode_set_data == common.mode_set_testpoint_data(
            driver.Profile('dbid0_uuid0'),
            accept_language='ru',
            external_ref=expected_external_ref,
            active_since='2020-04-04T05:00:00+00:00',
            mode='orders',
            source=saga_tools.SOURCE_SCHEDULED_MODE_CHANGE,
            change_reason=_SCHEDULED_CHANGE_REASON,
        )
    else:
        assert _handle_mode_set_cpp_testpoint.times_called == 0
        assert task_testpoint.times_called == 0


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_RESETS={
        'work_interval_ms': 1000,
        'contractor_chunk_size': 30,
        'retry_interval_ms': 1000,
        'logistic_resubscription_enabled': True,
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
            mode_rules.Patch(rule_name='prev_work_mode', features={}),
        ],
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_ID_1.hex,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_1,
            _OFFER_IDENTITY_1,
            dt.datetime(2020, 4, 4, 5, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 6, 0, tzinfo=dt.timezone.utc),
            'some_quota_1',
            1,
            _PARK_ID,
            _DRIVER_ID,
        ),
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_ID_2.hex,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_2,
            _OFFER_IDENTITY_2,
            dt.datetime(2020, 4, 4, 6, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 4, 4, 7, 0, tzinfo=dt.timezone.utc),
            _QUOTA_ID.hex,
            1,
            _PARK_ID,
            _DRIVER_ID,
        ),
    ],
)
@pytest.mark.parametrize(
    'check_before_start_should_fail, check_before_start_fail_reason, '
    'expect_reset, expect_check_before_start_calls, expected_change_reason',
    [
        pytest.param(
            False,
            None,
            False,
            True,
            saga_tools.REASON_SCHEDULED_SLOT_RESUBSCRIBE,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets(
                            [
                                db_tools.ScheduledReset(
                                    _PARK_ID,
                                    _DRIVER_ID,
                                    _SCHEDULED_CHANGE_REASON,
                                    dt.datetime.fromisoformat(
                                        '2020-04-04T06:00:00+00:00',
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='Happy path',
        ),
        pytest.param(
            True,
            None,
            True,
            True,
            _SCHEDULED_CHANGE_REASON,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets(
                            [
                                db_tools.ScheduledReset(
                                    _PARK_ID,
                                    _DRIVER_ID,
                                    _SCHEDULED_CHANGE_REASON,
                                    dt.datetime.fromisoformat(
                                        '2020-04-04T06:00:00+00:00',
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='Fail with exception',
        ),
        pytest.param(
            False,
            'some reason',
            True,
            True,
            _SCHEDULED_CHANGE_REASON,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets(
                            [
                                db_tools.ScheduledReset(
                                    _PARK_ID,
                                    _DRIVER_ID,
                                    _SCHEDULED_CHANGE_REASON,
                                    dt.datetime.fromisoformat(
                                        '2020-04-04T06:00:00+00:00',
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='Fail with check error reason',
        ),
        pytest.param(
            False,
            None,
            True,
            False,
            'another_reset_reason',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        db_tools.insert_scheduled_resets(
                            [
                                db_tools.ScheduledReset(
                                    _PARK_ID,
                                    _DRIVER_ID,
                                    # only difference with happy path:
                                    # another change reason
                                    'another_reset_reason',
                                    dt.datetime.fromisoformat(
                                        '2020-04-04T06:00:00+00:00',
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='Don\'t resubscribe if reset reason is not scheduled_slot_stop',
        ),
    ],
)
@pytest.mark.now('2020-04-04T09:00:00+0300')
async def test_worker_scheduled_resets_unsubscribe(
        taxi_driver_mode_subscription,
        pgsql,
        testpoint,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        stq,
        check_before_start_should_fail: bool,
        check_before_start_fail_reason: Optional[str],
        expect_reset: bool,
        expect_check_before_start_calls: bool,
        expected_change_reason: str,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS, mode_settings=_OFFER_IDENTITY_1,
            ),
        },
        udid=_UNIQUE_DRIVER_ID,
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @testpoint('scheduled-resets-testpoint')
    def task_testpoint(data):
        pass

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/'
        'reservation/check-before-start',
    )
    def check_before_start_handler(request):
        nonlocal check_before_start_fail_reason
        nonlocal check_before_start_should_fail

        if check_before_start_should_fail:
            return mockserver.make_response(
                json.dumps(
                    {
                        'code': 'BAD_REQUEST',
                        'message': 'some error message',
                        'details': {
                            'title': 'some error title',
                            'text': 'some error text',
                        },
                    },
                ),
                400,
            )

        response = {
            'offer_identity': _OFFER_IDENTITY_2,
            'short_info': {
                'time_range': {
                    'begin': '2021-04-04T06:00:00+00:00',
                    'end': '2021-04-04T07:00:00+00:00',
                },
                'quota_id': str(_QUOTA_ID),
                'allowed_transport_types': ['auto', 'bicycle', 'pedestrian'],
            },
        }
        if check_before_start_fail_reason is not None:
            response['check_not_pass_reason'] = check_before_start_fail_reason

        return response

    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    await taxi_driver_mode_subscription.run_distlock_task('scheduled-resets')

    await task_testpoint.wait_call()

    if expect_check_before_start_calls:
        assert check_before_start_handler.has_calls
        check_before_start_request = check_before_start_handler.next_call()[
            'request'
        ].json

        # don't check coords here
        del check_before_start_request['contractor_position']
        assert check_before_start_request == {
            'contractor_id': {
                'park_id': profile.park_id(),
                'driver_profile_id': profile.profile_id(),
            },
            'offer_identity': _OFFER_IDENTITY_2,
        }

    assert _handle_mode_set_cpp_testpoint.times_called == 1
    mode_set_data = _handle_mode_set_cpp_testpoint.next_call()['data']

    # external_ref is random generated
    expected_idempotency_token = mode_set_data['external_ref']

    expected_mode = 'orders' if expect_reset else _LOGISTIC_WORKSHIFTS
    expected_mode_settings = None if expect_reset else _OFFER_IDENTITY_2

    assert mode_set_data == common.mode_set_testpoint_data(
        profile=profile,
        accept_language='ru',
        external_ref=expected_idempotency_token,
        active_since='2020-04-04T06:00:00+00:00',
        mode=expected_mode,
        mode_settings=expected_mode_settings,
        source=saga_tools.SOURCE_SCHEDULED_MODE_CHANGE,
        change_reason=expected_change_reason,
        compensation_policy=saga_tools.COMPENSATION_POLICY_FORBID,
    )

    assert stq.subscription_saga.has_calls
    stq_data = stq.subscription_saga.next_call()
    assert stq_data['kwargs']['dbid_uuid'] == {
        'dbid': profile.park_id(),
        'uuid': profile.profile_id(),
    }

    saga_data = saga_tools.get_saga_db_data(profile, pgsql)

    # don't check generated id
    expected_id = saga_data[0]

    assert saga_data == (
        expected_id,
        dt.datetime(2020, 4, 4, 6, 0),
        profile.park_id(),
        profile.profile_id(),
        _UNIQUE_DRIVER_ID,
        expected_mode,
        dt.datetime(2020, 4, 4, 6, 0),
        expected_mode_settings,
        expected_idempotency_token,
        'ru',
        None,
        saga_tools.COMPENSATION_POLICY_FORBID,
        saga_tools.SOURCE_SCHEDULED_MODE_CHANGE,
        expected_change_reason,
    )


@pytest.mark.parametrize(
    'should_fail', (pytest.param([True]), pytest.param([False])),
)
async def test_worker_scheduled_resets_errors_metric(
        taxi_driver_mode_subscription,
        testpoint,
        mockserver,
        taxi_driver_mode_subscription_monitor,
        should_fail,
):
    @testpoint('scheduled-resets-testpoint')
    def worker_testpoint(data):
        pass

    @testpoint('scheduled-resets-error-injection')
    def _error_injection_testpoint(data):
        return {'inject_failure': True}

    metrics_before = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-resets',
    )

    await taxi_driver_mode_subscription.run_distlock_task('scheduled-resets')

    await worker_testpoint.wait_call()

    metrics_after = await taxi_driver_mode_subscription_monitor.get_metric(
        'scheduled-resets',
    )

    expected_successes = 0 if should_fail else 1
    expected_errors = 1 if should_fail else 0

    assert (
        expected_successes
        == metrics_after['successes'] - metrics_before['successes']
    )
    assert (
        expected_errors == metrics_after['errors'] - metrics_before['errors']
    )
