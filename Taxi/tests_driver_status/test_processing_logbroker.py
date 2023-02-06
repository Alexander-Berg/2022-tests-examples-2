import json

import pytest
import pytz

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import ACTIVE_ORDER_STATUSES
from tests_driver_status.enum_constants import OrderStatus
from tests_driver_status.enum_constants import ProcessingStatus
import tests_driver_status.pg_helpers as pg_helpers


ORDER_ID = 'some_order'


def _make_processing_event(
        alias_id,
        park_id,
        profile_id,
        status,
        processing_status,
        event_index,
        event_key=None,
):
    event = {
        'order_id': ORDER_ID,
        'status': processing_status,
        'event_index': event_index,
        'event_key': event_key or 'unimportant',
    }
    if alias_id:
        event['alias'] = alias_id
    if park_id:
        event['db_id'] = park_id
    if profile_id:
        event['driver_uuid'] = profile_id
    if status:
        event['taxi_status'] = status
    return event


@pytest.mark.parametrize(
    'status,processing_status',
    [
        # statuses set was taken from production DB
        pytest.param(OrderStatus.kDriving, ProcessingStatus.kAssigned),
        pytest.param(OrderStatus.kWaiting, ProcessingStatus.kAssigned),
        pytest.param(OrderStatus.kTransporting, ProcessingStatus.kAssigned),
        pytest.param(OrderStatus.kComplete, ProcessingStatus.kFinished),
        pytest.param(OrderStatus.kFailed, ProcessingStatus.kFinished),
        pytest.param(OrderStatus.kCancelled, ProcessingStatus.kFinished),
        pytest.param(OrderStatus.kExpired, ProcessingStatus.kFinished),
        pytest.param(OrderStatus.kDriving, ProcessingStatus.kCancelled),
        pytest.param(OrderStatus.kWaiting, ProcessingStatus.kCancelled),
        pytest.param(OrderStatus.kTransporting, ProcessingStatus.kCancelled),
    ],
)
async def test_pg_master_orders_store(
        taxi_driver_status,
        pgsql,
        processing_lb,
        mocked_time,
        status,
        processing_status,
):
    now = mocked_time.now().replace(tzinfo=pytz.utc)
    alias_id = 'alias1'
    park_id = 'park1'
    profile_id = 'profile1'

    assert pg_helpers.get_master_orders_count(pgsql) == 0

    event = _make_processing_event(
        alias_id, park_id, profile_id, status, processing_status, 1,
    )
    await processing_lb.push(event, now.timestamp())

    assert pg_helpers.get_master_orders_count(pgsql) == 1

    expected_status = (
        OrderStatus.kCancelled
        if status in ACTIVE_ORDER_STATUSES
        and processing_status == ProcessingStatus.kCancelled
        else status
    )
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        ORDER_ID,
        expected_status,
        'yandex',
        now,
    )


async def test_pg_master_orders_update_existing(
        taxi_driver_status, pgsql, processing_lb, mocked_time,
):
    alias_id = 'alias1'
    park_id = 'park1'
    profile_id = 'profile1'
    status1 = OrderStatus.kWaiting
    status2 = OrderStatus.kComplete
    processing_status = ProcessingStatus.kAssigned

    time1 = mocked_time.now().replace(tzinfo=pytz.utc)
    event1 = _make_processing_event(
        alias_id, park_id, profile_id, status1, processing_status, 1,
    )
    mocked_time.sleep(60)
    time2 = mocked_time.now().replace(tzinfo=pytz.utc)
    event2 = _make_processing_event(
        alias_id, park_id, profile_id, status2, processing_status, 2,
    )

    # 1. publish brand new event
    assert pg_helpers.get_master_orders_count(pgsql) == 0
    await processing_lb.push(event1, time1.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 1
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        ORDER_ID,
        status1,
        'yandex',
        time1,
    )

    # 2. publish event for the same order, check that data was updated
    await processing_lb.push(event2, time2.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 1
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        ORDER_ID,
        status2,
        'yandex',
        time2,
    )

    # 3. publish old event, check that data was not updated
    await processing_lb.push(event1, time1.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 1
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        ORDER_ID,
        status2,
        'yandex',
        time2,
    )


async def test_pg_master_orders_record_key(
        taxi_driver_status, pgsql, processing_lb, mocked_time,
):
    now = mocked_time.now().replace(tzinfo=pytz.utc)
    alias_id1 = 'alias1'
    alias_id2 = 'alias2'
    park_id = 'park1'
    profile_id1 = 'profile1'
    profile_id2 = 'profile2'
    status = OrderStatus.kWaiting
    processing_status = ProcessingStatus.kAssigned

    assert pg_helpers.get_master_orders_count(pgsql) == 0

    event1 = _make_processing_event(
        alias_id1, park_id, profile_id1, status, processing_status, 1,
    )
    await processing_lb.push(event1, now.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 1
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id1,
        park_id,
        profile_id1,
        ORDER_ID,
        status,
        'yandex',
        now,
    )

    event2 = _make_processing_event(
        alias_id1, park_id, profile_id2, status, processing_status, 1,
    )
    await processing_lb.push(event2, now.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 2
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id1,
        park_id,
        profile_id2,
        ORDER_ID,
        status,
        'yandex',
        now,
    )

    event3 = _make_processing_event(
        alias_id2, park_id, profile_id1, status, processing_status, 1,
    )
    await processing_lb.push(event3, now.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 3
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id2,
        park_id,
        profile_id1,
        ORDER_ID,
        status,
        'yandex',
        now,
    )


async def test_pg_master_orders_autoreordering(
        taxi_driver_status, pgsql, processing_lb, mocked_time,
):
    now = mocked_time.now().replace(tzinfo=pytz.utc)
    alias_id1 = 'alias1'
    alias_id2 = 'alias2'
    alias_id3 = 'alias3'
    park_id = 'park1'
    profile_id1 = 'profile1'
    profile_id2 = 'profile2'
    profile_id3 = 'profile3'
    status = OrderStatus.kWaiting
    processing_status = ProcessingStatus.kAssigned
    event_index1 = 1
    event_index2 = 3
    # event3 will be inserted via /v2/order/store
    event_index4 = 2

    assert pg_helpers.get_master_orders_count(pgsql) == 0

    event1 = _make_processing_event(
        alias_id1,
        park_id,
        profile_id1,
        status,
        processing_status,
        event_index1,
    )
    await processing_lb.push(event1, now.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 1
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id1,
        park_id,
        profile_id1,
        ORDER_ID,
        status,
        'yandex',
        now,
    )

    event2 = _make_processing_event(
        alias_id2,
        park_id,
        profile_id2,
        status,
        processing_status,
        event_index2,
    )
    await processing_lb.push(event2, now.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 2
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id2,
        park_id,
        profile_id2,
        ORDER_ID,
        status,
        'yandex',
        now,
    )

    # insert event by /v2/status/store
    # to make event_index be NULL
    body = {
        'park_id': park_id,
        'profile_id': profile_id3,
        'alias_id': alias_id3,
        'order_id': ORDER_ID,
        'status': status,
        'provider': 'yandex',
    }
    response = await taxi_driver_status.post(
        'v2/order/store', data=json.dumps(body),
    )
    assert response.status_code == 200

    # send handle_autoreordering with event_index3 (=2)
    # between event_index1 (=1) and event_index2 (=3)
    # expected: record for alias1 is cancelled,
    # while records for alias2 and alias3 stay unchanged
    event4 = _make_processing_event(
        None,
        None,
        None,
        None,
        ProcessingStatus.kPending,
        event_index4,
        'handle_autoreordering',
    )
    await processing_lb.push(event4, now.timestamp())
    assert pg_helpers.get_master_orders_count(pgsql) == 3
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id1,
        park_id,
        profile_id1,
        ORDER_ID,
        OrderStatus.kCancelled,
        'yandex',
        now,
    )
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id2,
        park_id,
        profile_id2,
        ORDER_ID,
        status,
        'yandex',
        now,
    )
    pg_helpers.check_master_orders_table(
        pgsql,
        alias_id3,
        park_id,
        profile_id3,
        ORDER_ID,
        status,
        'yandex',
        now,
    )
