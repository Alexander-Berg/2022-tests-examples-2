# pylint: disable=import-only-modules
import datetime

import pytest
import pytz

from tests_driver_status.enum_constants import DriverStatus
from tests_driver_status.enum_constants import LegacyDriverStatus
from tests_driver_status.enum_constants import OrderStatus
from tests_driver_status.pg_helpers import datetime_to_ms


NOW = datetime.datetime.now(datetime.timezone.utc)
NOW_MS = datetime_to_ms(NOW)


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'req, expected',
    [
        pytest.param(
            {
                'items': [
                    {
                        'park_id': 'p0',
                        'driver_id': 'd0',
                        'status': LegacyDriverStatus.Online,
                    },
                    {
                        'park_id': 'p1',
                        'driver_id': 'd0',
                        'status': LegacyDriverStatus.Online,
                        'order_id': 'foobar',
                    },
                    {
                        'park_id': 'p0',
                        'driver_id': 'd2',
                        'status': LegacyDriverStatus.Busy,
                    },
                ],
            },
            {
                'statuses': [
                    {
                        'park_id': 'p0',
                        'driver_id': 'd0',
                        'status': DriverStatus.Online,
                        'updated_ts': NOW_MS,
                    },
                    {
                        'park_id': 'p1',
                        'driver_id': 'd0',
                        'status': DriverStatus.Online,
                        'updated_ts': NOW_MS,
                        'orders': [
                            {'id': 'foobar', 'status': OrderStatus.kDriving},
                        ],
                    },
                    {
                        'park_id': 'p0',
                        'driver_id': 'd2',
                        'status': DriverStatus.Busy,
                        'updated_ts': NOW_MS,
                    },
                    # Note that driver status hadn't been set and
                    # is implicitly considered "offline"
                    {
                        'park_id': 'p0',
                        'driver_id': 'd9',
                        'status': DriverStatus.Offline,
                    },
                ],
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
async def test_statuses_fetch(
        taxi_driver_status, mocked_time, req, expected, taxi_config,
):
    mocked_time.set(NOW)
    res = await taxi_driver_status.post('/v1/internal/status/bulk', req)
    assert res.status_code == 200

    await taxi_driver_status.invalidate_caches(clean_update=True)

    driver_ids = [
        {'park_id': item['park_id'], 'driver_id': item['driver_id']}
        for item in expected['statuses']
    ]
    res = await taxi_driver_status.post(
        '/v2/statuses', {'driver_ids': driver_ids},
    )

    assert res.status_code == 200
    assert res.json() == expected


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.config(
    DRIVER_STATUS_ORDERS_FEATURES={
        'merge_statuses': False,
        'start_by_processing': False,
        'order_status_db_lookup_for_notification': True,
        'finish_by_client': True,
    },
)
async def test_master_order_merge(taxi_driver_status, pgsql, mocked_time):
    mocked_time.set(datetime.datetime(2021, 3, 11, 12, 0, 0, tzinfo=pytz.utc))

    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'INSERT INTO ds.drivers(id, park_id, driver_id) VALUES '
        '(1, \'park1\', \'driver1\'),'
        '(2, \'park2\', \'driver2\'),'
        '(3, \'park3\', \'driver3\');',
    )
    cursor.execute(
        'INSERT INTO ds.statuses(driver_id, status, source, updated_ts)'
        ' VALUES '
        '(1, \'offline\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(2, \'online\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(3, \'busy\', \'client\', \'2021-03-11 15:00:00.0+03\');',
    )
    cursor.execute(
        'INSERT INTO ds.master_orders('
        'alias_id, contractor_id, status, provider_id, event_ts)'
        ' VALUES '
        # /v2/statuses don't ignore orders for offline
        '(\'alias1\', 1, \'driving\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # missing in orders - expected in result
        '(\'alias21\', 2, \'waiting\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # active in master_orders, inactive in orders - result active
        '(\'alias31\', 3, \'driving\', 1, \'2021-03-11 15:00:01.0+03\'),'
        # complete in master_orders, active in orders - result transporting
        '(\'alias32\', 3, \'complete\', 1, \'2021-03-11 15:00:03.0+03\'),'
        # inactive (but not complete) in master_orders, active in orders
        # result - active
        '(\'alias33\', 3, \'cancelled\', 1, \'2021-03-11 15:00:05.0+03\');',
    )
    cursor.execute(
        'INSERT INTO ds.orders(id, driver_id, status, provider_id, updated_ts)'
        ' VALUES '
        # /v2/statuses don't ignore orders for offline
        '(\'alias1\', 1, \'driving\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # missing in master_orders - expected in result
        '(\'alias22\', 2, \'driving\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # active in master_orders, inactive in orders - result active
        '(\'alias31\', 3, \'complete\', 1, \'2021-03-11 15:00:02.0+03\'),'
        # complete in master_orders, active in orders - result transporting
        '(\'alias32\', 3, \'driving\', 1, \'2021-03-11 15:00:04.0+03\'),'
        # inactive (but not complete) in master_orders, active in orders
        # result - active
        '(\'alias33\', 3, \'driving\', 1, \'2021-03-11 15:00:06.0+03\');',
    )

    await taxi_driver_status.invalidate_caches()

    driver_ids = [
        {'park_id': 'park1', 'driver_id': 'driver1'},
        {'park_id': 'park2', 'driver_id': 'driver2'},
        {'park_id': 'park3', 'driver_id': 'driver3'},
    ]
    response = await taxi_driver_status.post(
        '/v2/statuses', {'driver_ids': driver_ids},
    )
    assert response.status_code == 200

    result = response.json()['statuses']
    expected = [
        {
            'park_id': 'park1',
            'driver_id': 'driver1',
            'status': 'offline',
            'orders': [{'id': 'alias1', 'status': 'driving'}],
            'updated_ts': datetime_to_ms(
                datetime.datetime(2021, 3, 11, 12, 0, 0, tzinfo=pytz.utc),
            ),
        },
        {
            'park_id': 'park2',
            'driver_id': 'driver2',
            'status': 'online',
            'orders': [
                {'id': 'alias21', 'status': 'waiting'},
                {'id': 'alias22', 'status': 'driving'},
            ],
            'updated_ts': datetime_to_ms(
                datetime.datetime(2021, 3, 11, 12, 0, 0, tzinfo=pytz.utc),
            ),
        },
        {
            'park_id': 'park3',
            'driver_id': 'driver3',
            'status': 'busy',
            'orders': [
                {'id': 'alias31', 'status': 'driving'},
                {'id': 'alias32', 'status': 'transporting'},
                {'id': 'alias33', 'status': 'driving'},
            ],
            'updated_ts': datetime_to_ms(
                # /v2/statuses takes status TS and ignore order TSes
                datetime.datetime(2021, 3, 11, 12, 0, 0, tzinfo=pytz.utc),
            ),
        },
    ]

    def _sort(contractors):
        for contractor in contractors:
            orders = contractor.get('orders')
            if orders:
                orders.sort(key=lambda order: order['id'])
        contractors.sort(
            key=lambda contractor: contractor['park_id']
            + contractor['driver_id'],
        )
        return contractors

    assert _sort(result) == _sort(expected)
