# pylint: disable=wrong-import-order, import-error, import-only-modules
import datetime

import pytest
import pytz

from tests_driver_status.enum_constants import OrderStatus
from tests_driver_status.enum_constants import ProcessingStatus
import tests_driver_status.pg_helpers as helpers


PG_PROCESSING_ORDERS_RECORDS = {
    'order_id_1': {
        'alias_id': 'alias_id_1',
        'park_id': 'parkid1',
        'driver_id': 'driverid1',
        'status': OrderStatus.kTransporting,
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_2': {
        'alias_id': 'alias_id_2',
        'park_id': 'parkid3',
        'driver_id': 'driverid3',
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 1, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_3': {
        'park_id': 'parkid2',
        'driver_id': 'driverid2',
        'status': OrderStatus.kTransporting,
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_4': {
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_5': {
        'alias_id': 'alias_id_5',
        'status': OrderStatus.kTransporting,
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_6': {
        'alias_id': 'alias_id_6',
        'park_id': 'parkid4',
        'driver_id': 'driverid4',
        'status': OrderStatus.kNone,
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_7': {
        'alias_id': 'alias_id_7',
        'park_id': 'parkid5',
        'driver_id': 'driverid5',
        'status': OrderStatus.kUnknown,
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
    'order_id_8': {
        'alias_id': 'alias_id_7',
        'park_id': 'parkid5',
        'driver_id': 'driverid5',
        'status': OrderStatus.kFailed,
        'processing_status': ProcessingStatus.kPending,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc),
    },
}


PG_PROCESSING_ORDERS_INCREMENT = {
    'order_id_1': {
        'alias_id': 'alias_id_1',
        'park_id': 'parkid1',
        'driver_id': 'driverid1',
        'status': OrderStatus.kComplete,
        'processing_status': ProcessingStatus.kFinished,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc),
    },
    'order_id_2': {
        'alias_id': 'alias_id_2',
        'park_id': 'parkid3',
        'driver_id': 'driverid3',
        'processing_status': ProcessingStatus.kCancelled,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc),
    },
    'order_id_3': {
        'park_id': 'parkid2',
        'driver_id': 'driverid2',
        'status': OrderStatus.kTransporting,
        'processing_status': ProcessingStatus.kAssigned,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc),
    },
    'order_id_4': {
        'park_id': 'parkid10',
        'driver_id': 'driverid10',
        'status': OrderStatus.kWaiting,
        'processing_status': ProcessingStatus.kAssigned,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
        ),
        'updated_ts': datetime.datetime(2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc),
    },
}


def _merge_records(prev, new):
    merged = prev.copy()
    for order_id, info in new.items():
        merged[order_id] = info
    return merged


def _convert_to_expected(records):
    converted = dict()
    for order_id, info in records.items():
        if (
                'alias_id' not in info
                or 'park_id' not in info
                or 'driver_id' not in info
                or 'status' not in info
        ):
            continue
        if (
                info['status'] == OrderStatus.kNone
                or info['status'] == OrderStatus.kUnknown
        ):
            continue
        alias_id = info['alias_id']
        order_info = {
            'park_id': info['park_id'],
            'driver_id': info['driver_id'],
            'status': info['status'],
            'order_id': order_id,
            'updated_ts': helpers.datetime_to_us(info['event_updated_ts']),
        }
        converted[alias_id] = order_info
    return converted


def _convert_cache_result(data):
    converted = {}
    for item in data:
        order_id = item['alias_id']
        order_info = {
            'park_id': item['park_id'],
            'driver_id': item['driver_id'],
            'status': item['status'],
            'order_id': item['order_id'],
            'updated_ts': item['updated_ts'],
        }
        converted[order_id] = order_info
    return converted


def _get_orders_count(data):
    count = 0
    for item in data:
        count += len(data[item].get('orders', {}))
    return count


# pylint: disable=redefined-outer-name
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_PG_CACHES={
        '__default__': {
            'full_update': {'chunk_size': 0, 'correction_ms': 10000},
            'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
        },
        'driver-orders-cache': {
            'full_update': {'chunk_size': 0, 'correction_ms': 10000},
            'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
        },
        'processing-orders-cache': {
            'full_update': {'chunk_size': 0, 'correction_ms': 10000},
            'incremental_update': {'chunk_size': 0, 'correction_ms': 1000},
        },
    },
)
async def test_cache_updates(
        pgsql, testpoint, mocked_time, taxi_driver_status,
):
    @testpoint('processing_orders_testpoint')
    def _processing_orders_testpoint(data):
        pass

    await taxi_driver_status.enable_testpoints()

    # set mocked_time
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc))

    # wait mocked_time to be distributed all over the service
    await taxi_driver_status.tests_control(invalidate_caches=False)

    # drop initial call of testpoint
    _processing_orders_testpoint.flush()

    # FULL UPDATE
    helpers.upsert_processing_orders(pgsql, PG_PROCESSING_ORDERS_RECORDS)
    await taxi_driver_status.invalidate_caches(clean_update=True)

    result = await _processing_orders_testpoint.wait_call()
    converted = _convert_cache_result(result['data']['records'])
    expected = _convert_to_expected(PG_PROCESSING_ORDERS_RECORDS)
    assert converted == expected

    # INCREMENTAL UPDATE
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc))

    helpers.upsert_processing_orders(pgsql, PG_PROCESSING_ORDERS_INCREMENT)
    await taxi_driver_status.invalidate_caches(clean_update=False)

    result = await _processing_orders_testpoint.wait_call()
    converted = _convert_cache_result(result['data']['records'])
    merged_records = _merge_records(
        PG_PROCESSING_ORDERS_RECORDS, PG_PROCESSING_ORDERS_INCREMENT,
    )
    expected = _convert_to_expected(merged_records)
    assert converted == expected
