# pylint: disable=import-only-modules
import datetime

import pytest
import pytz

from tests_driver_status.enum_constants import LegacyDriverStatus
from tests_driver_status.pg_helpers import datetime_to_ms


def _to_comparable(contractors):
    result = dict()
    for contractor in contractors:
        item = {'status': contractor['status']}
        if 'orders' in contractor:
            orders = dict()
            for order in contractor['orders']:
                if order['status'] not in orders:
                    orders[order['status']] = 1
                else:
                    orders[order['status']] += 1
            item['orders'] = orders
        result[contractor['profile_id']] = item
    return result


@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'state, req, expected',
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
                        'park_id': 'p0',
                        'driver_id': 'd1',
                        'status': LegacyDriverStatus.Online,
                        'order_id': 'foobar',
                    },
                    {
                        'park_id': 'p0',
                        'driver_id': 'd2',
                        'status': LegacyDriverStatus.Busy,
                    },
                    {
                        'park_id': 'p0',
                        'driver_id': 'd3',
                        'status': LegacyDriverStatus.Busy,
                        'order_id': 'barfoo',
                    },
                ],
            },
            {'park_id': 'p0'},
            {
                'd0': {'status': 'online'},
                'd1': {'status': 'online', 'orders': {'driving': 1}},
                'd2': {'status': 'busy'},
                'd3': {'status': 'busy', 'orders': {'driving': 1}},
            },
        ),
        pytest.param(
            {
                'items': [
                    {
                        'park_id': 'p1',
                        'driver_id': 'd0',
                        'status': LegacyDriverStatus.Online,
                    },
                    {
                        'park_id': 'p0',
                        'driver_id': 'd1',
                        'status': LegacyDriverStatus.Online,
                        'order_id': 'foobar',
                    },
                    {
                        'park_id': 'p0',
                        'driver_id': 'd2',
                        'status': LegacyDriverStatus.Busy,
                    },
                    {
                        'park_id': 'p1',
                        'driver_id': 'd3',
                        'status': LegacyDriverStatus.Busy,
                        'order_id': 'barfoo',
                    },
                ],
            },
            {'park_id': 'p1'},
            {
                'd0': {'status': 'online'},
                'd3': {'status': 'busy', 'orders': {'driving': 1}},
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
        taxi_driver_status, state, req, expected, taxi_config,
):
    res = await taxi_driver_status.post('/v1/internal/status/bulk', state)
    assert res.status_code == 200

    await taxi_driver_status.invalidate_caches(clean_update=True)

    res = await taxi_driver_status.get('/v2/park/statuses', params=req)

    assert res.status_code == 200
    result = res.json()
    assert result['park_id'] == req['park_id']
    assert _to_comparable(result['contractors']) == expected


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
        '(2, \'park1\', \'driver2\'),'
        '(3, \'park1\', \'driver3\');',
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
        # offline - not expected in result
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
        # offline - not expected in result
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

    response = await taxi_driver_status.get(
        '/v2/park/statuses', params={'park_id': 'park1'},
    )
    assert response.status_code == 200
    assert response.json()['park_id'] == 'park1'
    result = response.json()['contractors']
    expected = [
        {
            'profile_id': 'driver2',
            'status': 'online',
            'orders': [{'status': 'waiting'}, {'status': 'driving'}],
            'updated_ts': datetime_to_ms(
                datetime.datetime(2021, 3, 11, 12, 0, 0, tzinfo=pytz.utc),
            ),
        },
        {
            'profile_id': 'driver3',
            'status': 'busy',
            'orders': [
                {'status': 'driving'},
                {'status': 'transporting'},
                {'status': 'driving'},
            ],
            'updated_ts': datetime_to_ms(
                # max TS of status and merged orders
                datetime.datetime(2021, 3, 11, 12, 0, 6, tzinfo=pytz.utc),
            ),
        },
    ]

    def _sort(contractors):
        for contractor in contractors:
            orders = contractor.get('orders')
            if orders:
                orders.sort(key=lambda order: order['status'])
        contractors.sort(key=lambda contractor: contractor['profile_id'])
        return contractors

    assert _sort(result) == _sort(expected)
