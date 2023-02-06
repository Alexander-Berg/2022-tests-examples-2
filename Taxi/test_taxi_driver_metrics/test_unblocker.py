import datetime
import operator

import pytest

from taxi_driver_metrics.common.models import blocking_journal
from taxi_driver_metrics.common.models import DriverDataError
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import unblocker


UDID_1 = '5b05621ee6c22ea2654849c9'
UDID_2 = '5b05621ee6c22ea2654849c0'
TIMESTAMP = datetime.datetime(2016, 5, 8, 10, 0, 0, 0)


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_process_unblocking_drivers(
        web_context, dms_mockserver, fake_event_provider,
):
    app = web_context

    driver_1 = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP,
    )
    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert driver_1.blocking_state
    assert driver_2.blocking_state
    assert driver_1.current_blocking
    assert driver_2.current_blocking

    await unblocker.UnblockingStqWorker(
        app, app.stq.driver_metrics_processing,
    ).do_work(task_id=unblocker.UNBLOCKING_DRIVERS_TASK_NAME)

    assert dms_mockserver.event_new.times_called == 2

    call_1 = dms_mockserver.event_new.next_call()['request'].json
    call_2 = dms_mockserver.event_new.next_call()['request'].json

    call_1, call_2 = sorted(
        (call_1, call_2), key=operator.itemgetter('unique_driver_id'),
    )

    assert UDID_2 in call_1['idempotency_token']
    assert call_1['type'] == 'blocking'
    assert call_1['unique_driver_id'] == UDID_2
    assert call_1['extra_data']['blocking_type'] == 'activity'

    assert UDID_1 in call_2['idempotency_token']
    assert call_2['type'] == 'blocking'
    assert call_2['unique_driver_id'] == UDID_1
    assert call_2['extra_data']['blocking_type'] == 'actions'

    driver_1 = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP,
    )
    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert not driver_1.blocking_state
    assert not driver_2.blocking_state
    assert not driver_1.current_blocking
    assert not driver_2.current_blocking


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(DRIVER_METRICS_UNBLOCK_WITHOUT_DMS=True),
            ],
        ),
        pytest.param(
            marks=[
                pytest.mark.config(DRIVER_METRICS_UNBLOCK_WITHOUT_DMS=False),
            ],
        ),
    ],
)
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_unblock_without_dms(
        web_context, mockserver, fake_event_provider,
):
    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    def new_event(*args, **kwargs):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _activity_values(*_a, **_kw):
        return mockserver.make_response(status=500)

    app = web_context

    driver_1 = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP, from_handler=False,
    )
    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP, from_handler=False,
    )
    assert driver_1.current_blocking
    assert driver_2.current_blocking
    assert driver_1.blocking_state
    assert driver_2.blocking_state

    should_unblock: bool = app.config.DRIVER_METRICS_UNBLOCK_WITHOUT_DMS

    await unblocker.UnblockingStqWorker(
        app, app.stq.driver_metrics_processing,
    ).do_work(task_id=unblocker.UNBLOCKING_DRIVERS_TASK_NAME)

    assert new_event.times_called == 6  # retries
    new_events_calls_kwargs = [
        new_event.next_call()['args'][0].json for _ in range(6)
    ]
    calls = sorted(
        new_events_calls_kwargs, key=operator.itemgetter('unique_driver_id'),
    )
    assert UDID_2 in calls[0]['idempotency_token']
    assert calls[0]['type'] == 'blocking'
    assert calls[0]['unique_driver_id'] == UDID_2
    assert calls[0]['extra_data']['blocking_type'] == 'activity'

    assert UDID_1 in calls[3]['idempotency_token']
    assert calls[3]['type'] == 'blocking'
    assert calls[3]['unique_driver_id'] == UDID_1
    assert calls[3]['extra_data']['blocking_type'] == 'actions'

    driver_1 = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP, from_handler=False,
    )
    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP, from_handler=False,
    )
    assert should_unblock != bool(driver_1.current_blocking)
    assert should_unblock != bool(driver_2.current_blocking)
    assert should_unblock != bool(driver_1.blocking_state)
    assert should_unblock != bool(driver_2.blocking_state)


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_no_activity_for_unblocking(
        web_context, dms_mockserver, fake_event_provider,
):
    app = web_context
    dms_mockserver.init_activity({UDID_2: 10})

    blocking = await blocking_journal.fetch_current_blocking(app, UDID_2)
    assert blocking

    driver = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == 10

    await unblocker.UnblockingStqWorker(
        app, app.stq.driver_metrics_processing,
    ).do_work(task_id=unblocker.UNBLOCKING_DRIVERS_TASK_NAME)

    driver = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == 10

    blocking = await blocking_journal.fetch_current_blocking(app, UDID_2)
    assert not blocking

    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert not driver_2.blocking_state


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_no_unblock_if_db_unavailable(
        web_context, dms_mockserver, fake_event_provider, patch,
):
    app = web_context

    driver = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.current_blocking
    assert driver.blocking_state

    @patch(
        'taxi_driver_metrics.common.models.'
        'driver_info.DriverInfo._commit_unique_driver_changes',
    )
    async def fake_update_unique(*args, **kwargs):
        raise DriverDataError()

    @patch('taxi_driver_metrics.common.models.blocking_journal.reset_blocking')
    async def reset_blocking(db, blocking, **kwargs):
        return

    await unblocker.UnblockingStqWorker(
        app, app.stq.driver_metrics_processing,
    ).do_work(task_id=unblocker.UNBLOCKING_DRIVERS_TASK_NAME)

    assert fake_update_unique.calls
    assert not reset_blocking.calls

    driver = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.current_blocking
    assert driver.blocking_state
