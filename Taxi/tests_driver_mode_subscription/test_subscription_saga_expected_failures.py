import datetime as dt
from typing import Optional

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_NOW = '2020-05-01T12:00:00+00:00'


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        saga_tools.make_insert_saga_query(
            started_at=dt.datetime.fromisoformat(_NOW)
            - dt.timedelta(seconds=5),
            park_id='parkid1',
            driver_id='uuid1',
            next_mode='prev_work_mode',
            next_mode_timepoint='2020-04-04 14:00:00+01',
            next_mode_settings={'rule_id': 'next_rule'},
            prev_mode='prev_work_mode',
            prev_mode_timepoint='2020-04-02 13:00:00+01',
            prev_mode_settings={'rule_id': 'prev_rule'},
            source=saga_tools.SOURCE_SERVICE_MODE_CHANGE,
        ),
    ],
)
@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'expect_saga_failure, expect_reschedule_at',
    (
        pytest.param(
            True,
            None,
            id='expected failures disabled',
            marks=[
                pytest.mark.config(DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={}),
            ],
        ),
        pytest.param(
            True,
            None,
            id='step failures leads to failure, because saga too old',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
                        'expected_failures_to_failed_saga_delay_s': 4,
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            dt.datetime(2020, 5, 1, 12, 0, 1),
            id='step failures expected default resheduled',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
                        'expected_failures_to_failed_saga_delay_s': 6,
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            dt.datetime(2020, 5, 1, 12, 0, 10),
            id='step failures expected resheduled interval',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
                        'expected_failures_to_failed_saga_delay_s': 6,
                        'expected_failures_saga_retry_interval_s': 10,
                    },
                ),
            ],
        ),
    ),
)
async def test_subscription_saga_expected_failures(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        stq,
        taxi_config,
        mockserver,
        expect_saga_failure: bool,
        expect_reschedule_at: Optional[dt.datetime],
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode',
                    features={'reposition': {'profile': 'some_profile_1'}},
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode',
                    features={'reposition': {'profile': 'some_profile_2'}},
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
        '/reposition-api/internal/reposition-api/v1/service/driver_work_mode',
    )
    def _reposition_driver_mode(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'ERROR'},
        )

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=expect_saga_failure,
    )

    assert _reposition_driver_mode.has_calls

    if expect_reschedule_at:
        assert stq.subscription_saga.times_called == 1
        stq_data = stq.subscription_saga.next_call()
        assert stq_data['queue'] == 'subscription_saga'
        assert stq_data['eta'] == expect_reschedule_at
        assert stq_data['id'] == test_profile.dbid_uuid()
        # This because call go to /stq-agent/queues/api/reschedule
        assert not stq_data['kwargs']
        assert not stq_data['args']
    else:
        assert stq.subscription_saga.times_called == 0
