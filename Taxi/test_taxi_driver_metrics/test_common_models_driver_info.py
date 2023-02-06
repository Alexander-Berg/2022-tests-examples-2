# pylint: disable=too-many-lines
# pylint: disable=protected-access

import datetime
import typing as tp

import attr
import bson
import pytest

from taxi_driver_metrics.common.models import Blocking
from taxi_driver_metrics.common.models import BlockingType
from taxi_driver_metrics.common.models import DriverDataError
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events


TIMESTAMP = datetime.datetime.now().replace(microsecond=0)
BEGINNING_TIME = datetime.timedelta(days=2)
FROM_TIMESTAMP = TIMESTAMP - BEGINNING_TIME
TEST_REASON = 'just_a_test'
UDID_1 = '5b05621ee6c22ea2654849c9'
UDID_WITHOUT_ACTIVITY = '5b05621ee6c22ea2654849c1'
TST_EVENT_DESCR = Events.EventTypeDescriptor(
    Events.OrderEventType.OFFER_TIMEOUT.value,
)
TST_EID = 'tst_eid'
TST_OID = '5b05621ee6c22ea2654849c2'
TST_LICENSE1 = '1122YT32'
TST_LICENSE2 = '1122YT33'


def get_difference(left: tp.Any, right: tp.Any):
    rdict = attr.asdict(right)
    res = list()
    for key, val in attr.asdict(left).items():
        if key not in rdict or val != rdict[key]:
            res.append((key, val, rdict[key]))
    return res


@pytest.mark.now('2016-05-06T12:00:00.0')
@pytest.mark.filldb(unique_drivers='common')
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAG_FETCHER=True)
@pytest.mark.config(
    DRIVER_METRICS_COMPLETE_SCORES_SETTINGS={
        '__default__': {'initial_value': 10},
    },
)
@pytest.mark.parametrize(
    'udid, result',
    [
        (
            UDID_1,
            DriverInfo(
                udid=UDID_1,
                blocking_history=[
                    Blocking(
                        datetime.datetime(2016, 5, 6, 10),
                        BlockingType.BY_ACTIONS,
                        record_id=bson.ObjectId('5b05621ee6c22ea2654849c3'),
                        zone='spb',
                        rule_name='actions_block_1',
                        reason='bad_blocking_reason',
                    ),
                    Blocking(
                        datetime.datetime(2016, 5, 6, 10),
                        BlockingType.BY_ACTIVITY,
                        record_id=bson.ObjectId('5b05621ee6c22ea2654849c2'),
                        zone='spb',
                        rule_name='activity_block_3',
                        reason='low_activity',
                    ),
                ],
                blocking_state=Blocking(
                    datetime.datetime(2016, 5, 3, 0, 0),
                    BlockingType.BY_ACTIVITY,
                    reason='bad_blocking_reason',
                ),
                events=[
                    Events.OrderEvent(
                        timestamp=TIMESTAMP,
                        descriptor=TST_EVENT_DESCR,
                        event_id='tst12',
                        entity_id=UDID_1,
                    ),
                    Events.OrderEvent(
                        timestamp=FROM_TIMESTAMP,
                        descriptor=TST_EVENT_DESCR,
                        event_id='tst12',
                        entity_id=UDID_1,
                    ),
                    Events.OrderEvent(
                        timestamp=FROM_TIMESTAMP,
                        descriptor=TST_EVENT_DESCR,
                        event_id='tst12',
                        entity_id=UDID_1,
                    ),
                ],
                activity=93,
                activity_blocking_counter=1,
                tags={'tags::good_driver', 'tags::lucky'},
            ),
        ),
        # check if activity is
        (
            UDID_WITHOUT_ACTIVITY,
            DriverInfo(
                udid=UDID_WITHOUT_ACTIVITY,
                blocking_history=[
                    Blocking(
                        datetime.datetime(2016, 5, 6, 9, 0),
                        BlockingType.BY_ACTIVITY,
                        reason='low_activity',
                        record_id=bson.ObjectId('5b05621ee6c22ea2654840c1'),
                        zone='spb',
                        rule_name='activity_block_2',
                    ),
                    Blocking(
                        datetime.datetime(2016, 5, 4, 11, 0),
                        BlockingType.BY_ACTIVITY,
                        reason='low_activity',
                        record_id=bson.ObjectId('5b05621ee6c22ea2654849c9'),
                        zone='spb',
                        rule_name='activity_block_1',
                    ),
                ],
                blocking_state=Blocking(
                    datetime.datetime(2016, 5, 3, 0, 0),
                    BlockingType.BY_ACTIVITY,
                    reason='bad_blocking_reason',
                ),
                events=[
                    Events.OrderEvent(
                        timestamp=TIMESTAMP,
                        descriptor=TST_EVENT_DESCR,
                        event_id='tst12',
                        entity_id=UDID_1,
                    ),
                    Events.OrderEvent(
                        timestamp=FROM_TIMESTAMP,
                        descriptor=TST_EVENT_DESCR,
                        event_id='tst12',
                        entity_id=UDID_1,
                    ),
                    Events.OrderEvent(
                        timestamp=FROM_TIMESTAMP,
                        descriptor=TST_EVENT_DESCR,
                        event_id='tst12',
                        entity_id=UDID_1,
                    ),
                ],
                activity=100,
                activity_blocking_counter=2,
                tags={'tags::good_driver', 'tags::lucky'},
            ),
        ),
    ],
)
async def test_maker(
        web_context,
        dms_mockserver,
        udid: str,
        result: tp.Any,
        fake_event_provider,
        tags_service_mock,
        event_equals,
):
    app = web_context
    dms_mockserver.init_activity({UDID_1: 93})
    tags_service_mock()
    driver = await DriverInfo.make(
        app,
        udid,
        fake_event_provider(
            [
                Events.OrderEvent(
                    timestamp=FROM_TIMESTAMP,
                    entity_id=UDID_1,
                    descriptor=TST_EVENT_DESCR,
                    event_id='tst12',
                ),
                Events.OrderEvent(
                    timestamp=TIMESTAMP,
                    descriptor=TST_EVENT_DESCR,
                    event_id='tst12',
                    entity_id=UDID_1,
                ),
                Events.OrderEvent(
                    timestamp=FROM_TIMESTAMP,
                    entity_id=UDID_1,
                    descriptor=TST_EVENT_DESCR,
                    event_id='tst12',
                ),
            ],
        ),
        FROM_TIMESTAMP,
    )

    driver_events, driver.events = driver.events, []
    result_events, result.events = result.events, []

    for ev1, ev2 in zip(driver_events, result_events):
        event_equals(ev1, ev2)

    await driver.fetch_tags(app)
    assert driver == result


@pytest.mark.filldb(unique_drivers='common')
async def test_maker_missing(web_context, fake_event_provider):
    with pytest.raises(DriverDataError):
        await DriverInfo.make(
            web_context,
            '5b05621ee6c22ea2654848c0',
            fake_event_provider([]),
            FROM_TIMESTAMP,
            from_handler=False,
        )


@pytest.mark.now('2016-05-06T12:00:00.0')
@pytest.mark.filldb(unique_drivers='common')
async def test_common(web_context, fake_event_provider):
    driver = await DriverInfo.make(
        web_context,
        UDID_1,
        fake_event_provider(
            [
                Events.OrderEvent(
                    timestamp=FROM_TIMESTAMP,
                    event_id=TST_EID,
                    zone='tst12',
                    descriptor=TST_EVENT_DESCR,
                    entity_id=UDID_1,
                ),
                Events.OrderEvent(
                    timestamp=TIMESTAMP,
                    event_id=TST_EID,
                    zone='tst12',
                    descriptor=TST_EVENT_DESCR,
                    entity_id=UDID_1,
                ),
                Events.OrderEvent(
                    timestamp=FROM_TIMESTAMP,
                    event_id=TST_EID,
                    zone='tst12',
                    descriptor=TST_EVENT_DESCR,
                    entity_id=UDID_1,
                ),
            ],
        ),
        FROM_TIMESTAMP,
        from_handler=False,
    )
    assert driver.events_num == 3
    assert driver.get_zone_for_last_event() == 'tst12'
    assert driver.get_expired_blocking_count(BlockingType.BY_ACTIVITY) == 1
    assert not driver.get_active_blocking(BlockingType.BY_ACTIVITY)


@pytest.mark.now('2016-05-06T12:00:00.0')
@pytest.mark.filldb(unique_drivers='common')
async def test_update_blocking_state(web_context, fake_event_provider):
    async def get_driver():
        return await DriverInfo.make(
            web_context,
            UDID_1,
            fake_event_provider([]),
            FROM_TIMESTAMP,
            from_handler=False,
        )

    driver = await get_driver()
    # check if race with the activity value
    assert driver.blocking_state
    assert driver.get_expired_blocking_count(BlockingType.BY_ACTIVITY) == 1
    # the same blocking
    await driver._apply_blocking_state(
        web_context.mongo,
        Blocking(
            until=driver.blocking_state.until,
            type=BlockingType.BY_ACTIVITY,
            reason=driver.blocking_state.reason,
        ),
    )
    assert not driver.ud_updater

    # reset blocking
    await driver._apply_blocking_state(web_context.mongo, None)
    assert driver.ud_updater.empty()

    driver = await get_driver()
    assert not driver.blocking_state

    await driver._apply_blocking_state(
        web_context.mongo,
        Blocking(
            until=TIMESTAMP, reason=TEST_REASON, type=BlockingType.BY_ACTIONS,
        ),
    )

    driver = await get_driver()
    assert driver.blocking_state
    assert driver.blocking_state.until == TIMESTAMP
    assert driver.blocking_state.reason == TEST_REASON
    assert driver.blocking_state.type == BlockingType.BY_ACTIONS


def test_methods():
    driver = DriverInfo(
        UDID_1,
        blocking_history=[
            Blocking(
                datetime.datetime(2016, 5, 6, 10), BlockingType.BY_ACTIONS,
            ),
            Blocking(
                datetime.datetime(2016, 5, 6, 10),
                BlockingType.BY_ACTIVITY,
                rule_name='tst',
            ),
            Blocking(
                datetime.datetime(2016, 5, 5, 10), BlockingType.BY_ACTIONS,
            ),
            Blocking(
                datetime.datetime(2016, 5, 4, 10), BlockingType.BY_ACTIONS,
            ),
        ],
    )
    assert driver.get_last_blocking('tst').until == datetime.datetime(
        2016, 5, 6, 10,
    )
    assert driver.get_expired_blocking_count(BlockingType.BY_ACTIONS) == 3
    assert driver.get_expired_blocking_count(BlockingType.BY_ACTIVITY) == 0
    assert (
        driver.get_expired_blocking_count(
            BlockingType.BY_ACTIONS, datetime.datetime(2016, 5, 5),
        )
        == 2
    )


@pytest.mark.config(DRIVER_METRICS_ENABLE_TAG_FETCHER=True)
@pytest.mark.parametrize('dbid', ['123', None])
@pytest.mark.parametrize('uuid', ['123', None])
async def test_tags(web_context, tags_service_mock, dbid, uuid):
    tags_patch = tags_service_mock()
    driver = DriverInfo(UDID_1)
    await driver.fetch_tags(web_context, dbid=dbid, uuid=uuid)
    if dbid and uuid:
        assert tags_patch.driver_tags_match_profile.times_called
    else:
        assert tags_patch.tags_match.times_called
