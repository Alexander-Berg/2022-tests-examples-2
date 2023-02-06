# pylint: disable=C0302
import datetime
import gzip
import json

import lz4.block as lz4
import pytest
import pytz

# pylint: disable=import-error
from driver_status.fbs.v2.orders import List as FbsOrderStatusesList
from driver_status.fbs.v2.orders import Status as FbsOrderStatusesStatus

# pylint: disable=import-only-modules
from tests_driver_status.enum_constants import ACTIVE_ORDER_STATUSES
from tests_driver_status.enum_constants import OrderStatus
from tests_driver_status.enum_constants import ProcessingStatus
import tests_driver_status.pg_helpers as helpers
import tests_driver_status.utils as utils
# pylint: enable=import-error,import-only-modules


FBS_STATUS_TO_STRING = {
    FbsOrderStatusesStatus.Status.None_: 'none',
    FbsOrderStatusesStatus.Status.Driving: 'driving',
    FbsOrderStatusesStatus.Status.Waiting: 'waiting',
    FbsOrderStatusesStatus.Status.Transporting: 'transporting',
    FbsOrderStatusesStatus.Status.Complete: 'complete',
    FbsOrderStatusesStatus.Status.Failed: 'failed',
    FbsOrderStatusesStatus.Status.Cancelled: 'cancelled',
    FbsOrderStatusesStatus.Status.Expired: 'expired',
    FbsOrderStatusesStatus.Status.Preexpired: 'preexpired',
    FbsOrderStatusesStatus.Status.Unknown: 'unknown',
}

PG_DRIVER_STATUS_RECORDS = {
    ('driver001', 'park001'): {
        'orders': {
            'order_001': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
            },
            'order_002': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 1, tzinfo=pytz.utc,
                ),
            },
            'order_003': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver002', 'park001'): {
        'orders': {
            'order_004': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 1, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver003', 'park001'): {
        'orders': {
            'order_005': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 2, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver004', 'park001'): {
        'orders': {
            'order_006': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver005', 'park001'): {
        'orders': {
            'order_007': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 4, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver006', 'park001'): {
        'orders': {
            'order_008': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver007', 'park001'): {
        'orders': {
            'order_009': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver008', 'park001'): {
        'orders': {
            'order_010': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver009', 'park002'): {
        'orders': {
            'order_011': {
                'status': OrderStatus.kDriving,
                'provider': 'park',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver010', 'park002'): {
        'orders': {
            'order_012': {
                'status': OrderStatus.kDriving,
                'provider': 'park',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
            },
        },
    },
    ('driver011', 'park002'): {
        'orders': {
            'order_013': {
                'status': OrderStatus.kComplete,
                'provider': 'park',
                'updated_ts': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
            },
        },
    },
}

PG_PROCESSING_ORDERS_RECORDS = {
    'order_id_1': {
        'alias_id': 'order_006',
        'park_id': 'park001',
        'driver_id': 'driver004',
        'status': OrderStatus.kFailed,
        'processing_status': ProcessingStatus.kAssigned,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
        ),
    },
    'order_id_2': {
        'alias_id': 'order_007',
        'park_id': 'park001',
        'driver_id': 'driver005',
        'status': OrderStatus.kWaiting,
        'processing_status': ProcessingStatus.kAssigned,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 1, tzinfo=pytz.utc,
        ),
    },
    'order_id_3': {
        'alias_id': 'order_008',
        'park_id': 'park001',
        'driver_id': 'driver006',
        'status': OrderStatus.kTransporting,
        'processing_status': ProcessingStatus.kAssigned,
        'event_updated_ts': datetime.datetime(
            2019, 10, 3, 0, 1, 1, tzinfo=pytz.utc,
        ),
    },
}


def parse_response(data, compression_method):
    result = dict()
    decompression_methods = {
        'none': lambda x: x,
        'gzip': gzip.decompress,
        'lz4': lz4.decompress,
    }
    decompressed = decompression_methods.get(
        compression_method, gzip.decompress,
    )(data)
    response = FbsOrderStatusesList.List.GetRootAsList(decompressed, 0)
    result['revision'] = response.Revision()
    result['drivers'] = {}
    for i in range(0, response.ItemsLength()):
        item = response.Items(i)
        driver_id = (
            item.DriverId().decode('utf-8'),
            item.ParkId().decode('utf-8'),
        )
        if driver_id not in result['drivers']:
            result['drivers'][driver_id] = {}
        driver = result['drivers'][driver_id]
        driver[item.OrderId().decode('utf-8')] = {
            'provider': item.Provider().decode('utf-8'),
            'status': FBS_STATUS_TO_STRING[item.Status()],
            'updated_ts': item.UpdatedTs(),
        }
    return result


def check_updated_ts(expected, rcvd):
    assert rcvd['updated_ts'] == helpers.datetime_to_us(expected['updated_ts'])


async def handle_orders_updates(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
):
    # set mocked_time
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc))

    # wait mocked_time to be distributed all over the service
    await taxi_driver_status.tests_control(invalidate_caches=False)

    helpers.upsert_orders(pgsql, PG_DRIVER_STATUS_RECORDS)
    helpers.upsert_processing_orders(pgsql, PG_PROCESSING_ORDERS_RECORDS)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    mocked_time.set(datetime.datetime(2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc))
    await taxi_driver_status.invalidate_caches(clean_update=True)

    if 'revision' in req:
        req['revision'] = helpers.datetime_to_us(req['revision'])

    response = await taxi_driver_status.get('v2/orders/updates', params=req)
    assert response.status_code == expected['code']

    if expected['code'] != 200:
        return

    parsed_response = parse_response(
        response.content, req.get('compression', 'gzip'),
    )
    drivers = parsed_response.get('drivers')
    assert parsed_response['revision'] == helpers.datetime_to_us(
        expected['revision'],
    )

    processing_statuses = {
        (item['driver_id'], item['park_id']): item['status']
        for _, item in PG_PROCESSING_ORDERS_RECORDS.items()
    }

    if drivers:
        assert len(drivers) == len(expected['drivers'])
        for expected_key, expected_orders in expected['drivers'].items():
            assert expected_key in drivers
            orders = drivers[expected_key]
            assert len(expected_orders) == len(orders)
            for order_id, order_info in orders.items():
                assert order_id in expected_orders
                expected_order = PG_DRIVER_STATUS_RECORDS[expected_key][
                    'orders'
                ][order_id]
                assert expected_order['provider'] == order_info['provider']
                merge_statuses = taxi_config.get(
                    'DRIVER_STATUS_ORDERS_FEATURES',
                )['merge_statuses']
                if (
                        merge_statuses
                        and expected_key in processing_statuses
                        and processing_statuses[expected_key]
                        in ACTIVE_ORDER_STATUSES
                ):
                    assert (
                        processing_statuses[expected_key]
                        == order_info['status']
                    )
                else:
                    assert expected_order['status'] == order_info['status']
                check_updated_ts(expected_order, order_info)
    else:
        assert not expected['drivers']


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
    },
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {
                'revision': datetime.datetime(
                    1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc,
                ),
            },
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): [
                        'order_001',
                        'order_002',
                        'order_003',
                    ],
                    ('driver002', 'park001'): ['order_004'],
                    ('driver003', 'park001'): ['order_005'],
                    ('driver004', 'park001'): ['order_006'],
                    ('driver005', 'park001'): ['order_007'],
                    ('driver006', 'park001'): ['order_008'],
                    ('driver007', 'park001'): ['order_009'],
                    ('driver008', 'park001'): ['order_010'],
                    ('driver009', 'park002'): ['order_011'],
                    ('driver010', 'park002'): ['order_012'],
                    ('driver011', 'park002'): ['order_013'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 3, tzinfo=pytz.utc,
                ),
            },
            {
                'code': 200,
                'drivers': {
                    ('driver004', 'park001'): ['order_006'],
                    ('driver005', 'park001'): ['order_007'],
                    ('driver006', 'park001'): ['order_008'],
                    ('driver007', 'park001'): ['order_009'],
                    ('driver008', 'park001'): ['order_010'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 2, 5, tzinfo=pytz.utc,
                ),
            },
            {
                'code': 200,
                'drivers': {},
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 2, 5, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
async def test_incremental_update(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
):
    await handle_orders_updates(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'parts_count': 2,
            },
            {'code': 400},
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'part_no': 0,
            },
            {'code': 400},
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'part_no': 1,
            },
            {'code': 400},
        ),
        pytest.param(
            {
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 0, tzinfo=pytz.utc,
                ),
                'part_no': 1,
                'parts_count': 1,
            },
            {'code': 400},
        ),
    ],
)
async def test_wrong_requests(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
):
    await handle_orders_updates(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {'parts_count': 1, 'compression': 'lz4'},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): ['order_003'],
                    ('driver004', 'park001'): ['order_006'],
                    ('driver005', 'park001'): ['order_007'],
                    ('driver006', 'park001'): ['order_008'],
                    ('driver007', 'park001'): ['order_009'],
                    ('driver008', 'park001'): ['order_010'],
                    ('driver009', 'park002'): ['order_011'],
                    ('driver010', 'park002'): ['order_012'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 0, 'compression': 'none'},
            {
                'code': 200,
                'drivers': {
                    ('driver004', 'park001'): ['order_006'],
                    ('driver006', 'park001'): ['order_008'],
                    ('driver008', 'park001'): ['order_010'],
                    ('driver010', 'park002'): ['order_012'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 1},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): ['order_003'],
                    ('driver005', 'park001'): ['order_007'],
                    ('driver007', 'park001'): ['order_009'],
                    ('driver009', 'park002'): ['order_011'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 0},
            {
                'code': 200,
                'drivers': {
                    ('driver006', 'park001'): ['order_008'],
                    ('driver009', 'park002'): ['order_011'],
                    ('driver010', 'park002'): ['order_012'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 1},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): ['order_003'],
                    ('driver004', 'park001'): ['order_006'],
                    ('driver007', 'park001'): ['order_009'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 2},
            {
                'code': 200,
                'drivers': {
                    ('driver005', 'park001'): ['order_007'],
                    ('driver008', 'park001'): ['order_010'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
@pytest.mark.config(
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
async def test_clean_update(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
):
    await handle_orders_updates(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {'parts_count': 1, 'compression': 'lz4'},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): ['order_003'],
                    ('driver004', 'park001'): ['order_006'],
                    ('driver005', 'park001'): ['order_007'],
                    ('driver006', 'park001'): ['order_008'],
                    ('driver007', 'park001'): ['order_009'],
                    ('driver008', 'park001'): ['order_010'],
                    ('driver009', 'park002'): ['order_011'],
                    ('driver010', 'park002'): ['order_012'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 0, 'compression': 'none'},
            {
                'code': 200,
                'drivers': {
                    ('driver004', 'park001'): ['order_006'],
                    ('driver006', 'park001'): ['order_008'],
                    ('driver008', 'park001'): ['order_010'],
                    ('driver010', 'park002'): ['order_012'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 2, 'part_no': 1},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): ['order_003'],
                    ('driver005', 'park001'): ['order_007'],
                    ('driver007', 'park001'): ['order_009'],
                    ('driver009', 'park002'): ['order_011'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 0},
            {
                'code': 200,
                'drivers': {
                    ('driver006', 'park001'): ['order_008'],
                    ('driver009', 'park002'): ['order_011'],
                    ('driver010', 'park002'): ['order_012'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 5, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 1},
            {
                'code': 200,
                'drivers': {
                    ('driver001', 'park001'): ['order_003'],
                    ('driver004', 'park001'): ['order_006'],
                    ('driver007', 'park001'): ['order_009'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 6, tzinfo=pytz.utc,
                ),
            },
        ),
        pytest.param(
            {'parts_count': 3, 'part_no': 2},
            {
                'code': 200,
                'drivers': {
                    ('driver005', 'park001'): ['order_007'],
                    ('driver008', 'park001'): ['order_010'],
                },
                'revision': datetime.datetime(
                    2019, 10, 3, 0, 1, 7, tzinfo=pytz.utc,
                ),
            },
        ),
    ],
)
@pytest.mark.config(
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
async def test_merged_clean_update(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
):
    await handle_orders_updates(
        pgsql, mocked_time, taxi_config, taxi_driver_status, req, expected,
    )


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
async def test_orders_status_gaps(
        taxi_driver_status, pgsql, testpoint, mocked_time,
):
    timestamps_str = {
        'now_ts': '2021-03-11 15:00:00.0+03',
        'revision_ts': '2021-03-11 14:57:00.0+03',
        'client_updated_ts': '2021-03-11 14:55:00.0+03',
        'master_updated_ts': '2021-03-11 14:56:01.0+03',
    }

    mocked_time.set(utils.parse_date_str(timestamps_str['now_ts']))

    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'INSERT INTO ds.drivers(id, park_id, driver_id) VALUES '
        '(1, \'park1\', \'driver1\');',
    )
    cursor.execute(
        'INSERT INTO ds.orders(id, driver_id, status, provider_id, updated_ts)'
        ' VALUES '
        '(\'alias_1\', 1, \'driving\', 3, \''
        + timestamps_str['client_updated_ts']
        + '\');',
    )

    await taxi_driver_status.invalidate_caches(clean_update=True)

    body = {
        'park_id': 'park1',
        'profile_id': 'driver1',
        'alias_id': 'alias_1',
        'order_id': 'order_1',
        'status': OrderStatus.kTransporting,
        'provider': 'yandex',
        'timestamp': utils.date_str_to_ms(timestamps_str['master_updated_ts']),
    }
    response = await taxi_driver_status.post(
        'v2/order/store', data=json.dumps(body),
    )
    assert response.status_code == 200

    await taxi_driver_status.invalidate_caches(clean_update=True)
    response = await taxi_driver_status.get(
        'v2/orders/updates',
        params={
            'compression': 'lz4',
            'revision': utils.date_str_to_us(timestamps_str['revision_ts']),
        },
    )
    assert response.status_code == 200

    parsed_response = parse_response(response.content, 'lz4')
    drivers = parsed_response['drivers']
    assert drivers == {
        ('driver1', 'park1'): {
            'alias_1': {
                'provider': 'yandex',
                'status': 'transporting',
                'updated_ts': utils.date_str_to_us(
                    timestamps_str['master_updated_ts'],
                ),
            },
        },
    }


@pytest.mark.now('2019-10-03T00:01:10+0000')
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
async def test_master_orders_full_update(
        taxi_driver_status, pgsql, mocked_time, testpoint,
):
    @testpoint('aggregated-orders-tp')
    def _aggregated_cache_update(cookie):
        pass

    now = mocked_time.now().replace(tzinfo=pytz.UTC)
    sec = datetime.timedelta(seconds=1)
    revision = helpers.datetime_to_us(now - 10 * sec)

    master_orders = {
        # missing in ds.orders, expected in result
        ('driver000', 'park011'): {
            'order_001': {
                'status': OrderStatus.kDriving,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 5 * sec,
            },
        },
        # not expected in partition 0
        ('driver001', 'park011'): {
            'order_001': {
                'status': OrderStatus.kTransporting,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 6 * sec,
            },
        },
        # has updated_ts before requested revision, not expected in result
        ('driver002', 'park011'): {
            'order_001': {
                'status': OrderStatus.kTransporting,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 11 * sec,
            },
        },
        # active in ds.master_orders
        # inactive in ds.orders (see PG_DRIVER_STATUS_RECORDS)
        # result is active => expected in result
        ('driver002', 'park001'): {
            'order_004': {
                'status': OrderStatus.kWaiting,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 5 * sec,
            },
        },
        # complete in ds.master_orders
        # active (driving) in ds.orders
        # result is complete => expected in result
        ('driver004', 'park001'): {
            'order_006': {
                'status': OrderStatus.kComplete,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 4 * sec,
            },
        },
        # inactive, but not complete in ds.master_orders
        # active (driving) in ds.orders
        # result is driving (finish_by_client flag) => expected in result
        ('driver006', 'park001'): {
            'order_008': {
                'status': OrderStatus.kCancelled,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 6 * sec,
            },
        },
        # not expected in partition 0
        ('driver009', 'park002'): {
            'order_011': {
                'status': OrderStatus.kTransporting,
                'provider': 'park',
                'event_ts': now - 8 * sec,
                'updated_ts': now - 8 * sec,
            },
        },
        # park order, complete in ds.master_orders
        # driving in ds.orders
        # result is driving => expected in result
        ('driver010', 'park002'): {
            'order_012': {
                'status': OrderStatus.kComplete,
                'provider': 'park',
                'event_ts': now - 8 * sec,
                'updated_ts': now - 8 * sec,
            },
        },
        # not expected in partition 0
        ('driver011', 'park002'): {
            'order_013': {
                'status': OrderStatus.kWaiting,
                'provider': 'park',
                'event_ts': now - 8 * sec,
                'updated_ts': now - 8 * sec,
            },
        },
    }
    helpers.upsert_master_orders(pgsql, master_orders)
    helpers.upsert_orders(pgsql, PG_DRIVER_STATUS_RECORDS)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    await _aggregated_cache_update.wait_call()

    req = {
        'revision': revision,
        'parts_count': 2,
        'part_no': 0,
        'compression': 'lz4',
    }
    response = await taxi_driver_status.get('v2/orders/updates', params=req)
    assert response.status_code == 200

    parsed_response = parse_response(response.content, 'lz4')
    assert parsed_response['revision'] == helpers.datetime_to_us(now - 3 * sec)

    assert parsed_response['drivers'] == {
        ('driver000', 'park011'): {
            'order_001': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver002', 'park001'): {
            'order_004': {
                'status': OrderStatus.kWaiting,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver004', 'park001'): {
            'order_006': {
                'status': OrderStatus.kTransporting,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 7 * sec),
            },
        },
        ('driver006', 'park001'): {
            'order_008': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 5 * sec),
            },
        },
        # missing in ds.master_orders, see ds.orders
        ('driver008', 'park001'): {
            'order_010': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 3 * sec),
            },
        },
        # park order
        ('driver010', 'park002'): {
            'order_012': {
                'status': OrderStatus.kDriving,
                'provider': 'park',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
    }


@pytest.mark.now('2019-10-03T00:01:10+0000')
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
async def test_master_orders_incr_update(
        taxi_driver_status, pgsql, mocked_time, testpoint,
):
    @testpoint('aggregated-orders-tp')
    def _aggregated_cache_update(cookie):
        pass

    now = mocked_time.now().replace(tzinfo=pytz.UTC)
    sec = datetime.timedelta(seconds=1)
    revision = helpers.datetime_to_us(now - 11 * sec)

    master_orders = {
        # missing in ds.orders, expected in result
        ('driver000', 'park011'): {
            'order_001': {
                'status': OrderStatus.kDriving,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 6 * sec,
            },
        },
        # has updated_ts before requested revision, not expected in result
        ('driver002', 'park011'): {
            'order_001': {
                'status': OrderStatus.kTransporting,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 12 * sec,
            },
        },
        # active in ds.master_orders
        # inactive in ds.orders (see PG_DRIVER_STATUS_RECORDS)
        # get event timestamp as max from both sources
        ('driver002', 'park001'): {
            'order_004': {
                'status': OrderStatus.kWaiting,
                'event_ts': now - 10 * sec,
                'updated_ts': now - 5 * sec,
            },
        },
        # complete in ds.master_orders
        # active (driving) in ds.orders
        # result is complete and get max event TS from both sources
        ('driver004', 'park001'): {
            'order_006': {
                'status': OrderStatus.kComplete,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 4 * sec,
            },
        },
        # inactive, but not complete in ds.master_orders
        # active (driving) in ds.orders
        # get event timestamp as max from both sources
        ('driver006', 'park001'): {
            'order_008': {
                'status': OrderStatus.kCancelled,
                'event_ts': now - 8 * sec,
                'updated_ts': now - 6 * sec,
            },
        },
        # park order
        # transporting in ds.master_orders
        # driving in ds.orders
        # expected transporting and max TS
        ('driver009', 'park002'): {
            'order_011': {
                'status': OrderStatus.kTransporting,
                'provider': 'park',
                'event_ts': now - 8 * sec,
                'updated_ts': now - 8 * sec,
            },
        },
        # park order, complete in ds.master_orders
        # driving in ds.orders
        # expected is driving and max TS
        ('driver010', 'park002'): {
            'order_012': {
                'status': OrderStatus.kComplete,
                'provider': 'park',
                'event_ts': now - 8 * sec,
                'updated_ts': now - 8 * sec,
            },
        },
        # park order, waiting in ds.master_orders
        # complete in ds.orders
        # expected complete and TS from ds.orders
        ('driver011', 'park002'): {
            'order_013': {
                'status': OrderStatus.kWaiting,
                'provider': 'park',
                'event_ts': now - 8 * sec,
                'updated_ts': now - 8 * sec,
            },
        },
    }
    helpers.upsert_master_orders(pgsql, master_orders)
    helpers.upsert_orders(pgsql, PG_DRIVER_STATUS_RECORDS)
    await taxi_driver_status.invalidate_caches(clean_update=True)
    await _aggregated_cache_update.wait_call()

    # missing 'part_count' => incremental
    req = {'revision': revision, 'compression': 'lz4'}
    response = await taxi_driver_status.get('v2/orders/updates', params=req)
    assert response.status_code == 200

    parsed_response = parse_response(response.content, 'lz4')
    assert parsed_response['revision'] == helpers.datetime_to_us(now - 3 * sec)

    assert parsed_response['drivers'] == {
        ('driver001', 'park001'): {
            'order_001': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 10 * sec),
            },
            'order_002': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 9 * sec),
            },
            'order_003': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver000', 'park011'): {
            'order_001': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver002', 'park001'): {
            'order_004': {
                'status': OrderStatus.kWaiting,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 9 * sec),
            },
        },
        ('driver003', 'park001'): {
            'order_005': {
                'status': OrderStatus.kComplete,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver004', 'park001'): {
            'order_006': {
                'status': OrderStatus.kTransporting,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 7 * sec),
            },
        },
        ('driver005', 'park001'): {
            'order_007': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 6 * sec),
            },
        },
        ('driver006', 'park001'): {
            'order_008': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 5 * sec),
            },
        },
        ('driver007', 'park001'): {
            'order_009': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 4 * sec),
            },
        },
        ('driver008', 'park001'): {
            'order_010': {
                'status': OrderStatus.kDriving,
                'provider': 'yandex',
                'updated_ts': helpers.datetime_to_us(now - 3 * sec),
            },
        },
        ('driver009', 'park002'): {
            'order_011': {
                'status': OrderStatus.kTransporting,
                'provider': 'park',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver010', 'park002'): {
            'order_012': {
                'status': OrderStatus.kDriving,
                'provider': 'park',
                'updated_ts': helpers.datetime_to_us(now - 8 * sec),
            },
        },
        ('driver011', 'park002'): {
            'order_013': {
                'status': OrderStatus.kComplete,
                'provider': 'park',
                'updated_ts': helpers.datetime_to_us(now - 10 * sec),
            },
        },
    }


# pylint: enable=redefined-outer-name
