# pylint: disable=protected-access

import datetime

import bson
import pytest

from taxi_driver_metrics.common.models import Blocking
from taxi_driver_metrics.common.models import BlockingType
from taxi_driver_metrics.common.models import DmsEventsProvider
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models import run_dms_processing
from taxi_driver_metrics.common.models.rules import rule_utils


TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)
BEFORE = TIMESTAMP - datetime.timedelta(seconds=10)
UDID = '5b05621ee6c22ea2654849c9'
CONFIG_ACTIVITY_CHANGE = 2
CONFIG_COMPLETE_SCORES_CHANGE = 2
MANUAL_ACTIVITY_SET = 88
MANUAL_ACTIVITY_ADD = 1
AMNESTY_DEFAULT = 60
AMNESTY_CS_DEFAULT = 0


ORDER_EVENT_RAW = {
    'order_id': 'order_id',
    'order_alias_id': 'order_alias_id',
    'driver_id': 'driver_id',
    'unique_driver_id': bson.ObjectId(UDID),
    'license': 'LFROM1',
    'field': 'c',
    'driver_points': 4,
    'city_id': 'city_id',
    'nearest_zone': 'bangladesh',
    'current_dp': 93,
    'time_to_a': int(123),
    'distance_to_a': int(123),
    'ride_start_time': datetime.datetime(2016, 9, 1, 13, 0),
    'ride_finish_time': datetime.datetime(2016, 9, 1, 20, 0),
    'created': TIMESTAMP,
    'destination_points': [],
    'processed': False,
    'tariff_class': 'vip',
}

ORDER_EVENT = Events.OrderEvent(
    descriptor=Events.EventTypeDescriptor(
        Events.OrderEventType.COMPLETE.value,
    ),
    timestamp=TIMESTAMP,
    event_id='1991',
    entity_id=UDID,
    order_id='393j3393j939j394',
    activity_value=93,
    tariff_class='vip',
)

SERVICE_ABSOLUTE_SET_ACTIVITY_EVENT = Events.ServiceManualEvent(
    timestamp=TIMESTAMP,
    event_id='1991',
    entity_id=UDID,
    order_id='393j3393j939j394',
    operation=Events.ServiceManualEventType.SET_ACTIVITY_VALUE,
    mode=Events.ManualValueMode.ABSOLUTE,
    value=MANUAL_ACTIVITY_SET,
)


SERVICE_ABSOLUTE_SET_LOYALTY_EVENT = Events.ServiceManualEvent(
    timestamp=TIMESTAMP,
    event_id='1991',
    entity_id=UDID,
    order_id='393j3393j939j394',
    operation=Events.ServiceManualEventType.SET_LOYALTY_VALUE,
    mode=Events.ManualValueMode.ADDITIVE,
    value=89121602900,
)


SERVICE_ADDITIVE_SET_ACTIVITY_EVENT = Events.ServiceManualEvent(
    timestamp=TIMESTAMP,
    event_id='1991',
    entity_id=UDID,
    order_id='393j3393j939j394',
    operation=Events.ServiceManualEventType.SET_ACTIVITY_VALUE,
    mode=Events.ManualValueMode.ADDITIVE,
    value=MANUAL_ACTIVITY_ADD,
)


async def _get_driver(app, event_fetcher) -> DriverInfo:
    return await DriverInfo.make(
        app,
        unique_driver_id=UDID,
        event_fetcher=event_fetcher,
        driver_history_from_timestamp=TIMESTAMP,
        fetch_events_history=False,
        fetch_tags=True,
        fetch_blocking_history=True,
    )


# pylint: disable=protected-access
@pytest.mark.config(
    DRIVER_METRICS_ENABLE_TAG_FETCHER=True,
    DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.parametrize(
    'event',
    [
        ORDER_EVENT,
        SERVICE_ABSOLUTE_SET_ACTIVITY_EVENT,
        SERVICE_ADDITIVE_SET_ACTIVITY_EVENT,
    ],
)
@pytest.mark.parametrize('starting_activity', [10, 90])
# is driver already blocked?
@pytest.mark.parametrize('current_block', [None, 'actions', 'activity'])
# type of event processing
async def test_activity_supertest(
        stq3_context,
        dms_mockserver,
        starting_activity,
        event,
        current_block,
        tags_service_mock,
        event_provider,
        fake_event_provider,
        predict_activity,
):
    def upload_check(*args, **kwargs):
        assert False, 'Must not be called'

    tags_patch = tags_service_mock(upload_check=upload_check, tags=[])
    app = stq3_context

    dms_mockserver.init_activity({UDID: starting_activity})
    driver = await _get_driver(app, fake_event_provider([]))
    dispatch_id = await predict_activity(
        udid=driver.udid, event_map={'order_complete': CONFIG_ACTIVITY_CHANGE},
    )
    event.dispatch_id = dispatch_id
    assert driver.activity == starting_activity

    blocking = None
    if current_block:
        blocking = Blocking(
            until=BEFORE,
            type=BlockingType(current_block),
            reason='initial',
            record_id=None,
            zone='bangladesh',
            rule_name='rule_name',
        )
        await rule_utils.process_single_blocking(
            app,
            blocking,
            driver,
            event=Events.OrderEvent(
                event_id='bad_event',
                timestamp=BEFORE,
                entity_id=UDID,
                zone='bangladesh',
            ),
        )
        await driver._apply_blocking_state(app.mongo, blocking)

    driver = await _get_driver(app, fake_event_provider([]))
    # check starting parameters
    assert driver.activity == starting_activity
    if current_block:
        assert len(driver.current_blocking) == 1
        current = driver.current_blocking[0]
        assert current.until == blocking.until
        assert current.type == blocking.type
        assert current.reason == blocking.reason
        assert current.record_id
        assert current.zone == blocking.zone
        assert current.rule_name == blocking.rule_name
    else:
        assert driver.current_blocking == []

    await event_provider.save_event(event)

    await run_dms_processing(app, 999)
    assert tags_patch.tags_match.times_called
    assert dms_mockserver.event_complete.times_called == 1

    complete_call = dms_mockserver.event_complete.next_call()['request'].json

    driver = await _get_driver(app, fake_event_provider([]))
    unblock_increment = 0
    if starting_activity == 10 and current_block != 'activity':
        # we assume driver was unblocked but activity didnt go through
        unblock_increment = AMNESTY_DEFAULT - starting_activity

    if event == ORDER_EVENT:
        # activity_change is 2 because we use config
        assert (
            complete_call['activity']['increment']
            == unblock_increment + CONFIG_ACTIVITY_CHANGE
        )
        actual_increment = unblock_increment + CONFIG_ACTIVITY_CHANGE
        assert driver.activity == starting_activity + actual_increment
    if event in (
            SERVICE_ADDITIVE_SET_ACTIVITY_EVENT,
            SERVICE_ABSOLUTE_SET_ACTIVITY_EVENT,
    ):
        # it should only unblock if result puts you above threshold
        activity_change = unblock_increment
        if event.mode == Events.ManualValueMode.ADDITIVE:
            activity_change += event.value
            new_activity = starting_activity + unblock_increment + event.value
        else:  # ABSOLUTE
            activity_change = event.value - starting_activity
            new_activity = event.value
        assert complete_call['activity']['increment'] == activity_change
        assert driver.activity == new_activity

        # it should only unblock if result puts you above threshold
        if new_activity > 30 and current_block == 'activity':
            assert not driver.current_blocking
        elif current_block:
            assert driver.current_blocking


# pylint: disable=protected-access
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
async def test_activity_for_unblocking_event(
        stq3_context, dms_mockserver, fake_event_provider,
):
    app = stq3_context

    dms_mockserver.init_activity({UDID: 5})
    event_provider = DmsEventsProvider(app)

    driver = await DriverInfo.make(
        app, UDID, fake_event_provider([]), TIMESTAMP,
    )

    assert driver.activity == 5
    assert not driver.current_blocking

    await event_provider.save_event(
        Events.BlockingEvent(
            event_id='event_id',
            timestamp=TIMESTAMP,
            entity_id=UDID,
            blocking_type=BlockingType.BY_ACTIVITY,
        ),
    )

    await run_dms_processing(app, 1)

    assert dms_mockserver.event_complete.times_called

    driver = await DriverInfo.make(
        app, UDID, fake_event_provider([]), TIMESTAMP,
    )
    assert driver.activity == 60


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=0,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DRIVER_METRICS_USE_NEW_PROCESSOR_PERCENTS=100,
            ),
        ),
    ],
)
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'dms_activity': {'from': 0, 'to': 100, 'salt': 'no salt'},
    },
)
async def test_loyalty_manual_big_value(
        stq3_context, dms_mockserver, fake_event_provider,
):
    app = stq3_context

    dms_mockserver.init_activity({UDID: 5})
    event_provider = DmsEventsProvider(app)

    await DriverInfo.make(app, UDID, fake_event_provider([]), TIMESTAMP)

    await event_provider.save_event(SERVICE_ABSOLUTE_SET_LOYALTY_EVENT)

    await run_dms_processing(app, 1)

    assert dms_mockserver.event_complete.next_call()['request'].json == {
        'activity': {'increment': 55, 'value_to_set': 60},
        'event_id': 1,
        'loyalty_increment': 0,  # no increment
        'ticket_id': 1,
        'unique_driver_id': '5b05621ee6c22ea2654849c9',
    }
