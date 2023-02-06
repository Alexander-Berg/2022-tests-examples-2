# pylint: disable=import-only-modules
import datetime

import pytest
import pytz

from tests_driver_status.enum_constants import LegacyDriverStatus


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
            {'park': 'p0'},
            {'free': 1, 'busy': 1, 'onorder': 2},
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
            {'park': 'p1'},
            {'free': 1, 'busy': 0, 'onorder': 1},
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

    res = await taxi_driver_status.post('/v2/statuses/park', req)

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
        '(3, \'park3\', \'driver3\'),'
        '(4, \'park4\', \'driver4\'),'
        '(5, \'park5\', \'driver5\'),'
        '(6, \'park6\', \'driver6\');',
    )
    cursor.execute(
        'INSERT INTO ds.statuses(driver_id, status, source, updated_ts) '
        'VALUES '
        '(1, \'offline\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(2, \'online\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(3, \'busy\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(4, \'online\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(5, \'busy\', \'client\', \'2021-03-11 15:00:00.0+03\'),'
        '(6, \'online\', \'client\', \'2021-03-11 15:00:00.0+03\');',
    )
    cursor.execute(
        'INSERT INTO ds.master_orders('
        'alias_id, contractor_id, status, provider_id, event_ts)'
        ' VALUES '
        # don't account offline contractors
        '(\'alias1\', 1, \'driving\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # missing in orders - account in result
        '(\'alias2\', 2, \'waiting\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # active in master_orders, inactive in orders - result active
        '(\'alias4\', 4, \'driving\', 1, \'2021-03-11 15:00:01.0+03\'),'
        # complete in master_orders, active in orders - result transporting
        '(\'alias5\', 5, \'complete\', 1, \'2021-03-11 15:00:03.0+03\'),'
        # inactive (but not complete) in master_orders, active in orders
        # result - active
        '(\'alias6\', 6, \'cancelled\', 1, \'2021-03-11 15:00:05.0+03\');',
    )
    cursor.execute(
        'INSERT INTO ds.orders(id, driver_id, status, provider_id, updated_ts)'
        ' VALUES '
        # don't account offline contractors
        '(\'alias1\', 1, \'driving\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # missing in master_orders - account in result
        '(\'alias3\', 3, \'driving\', 1, \'2021-03-11 15:00:00.0+03\'),'
        # active in master_orders, inactive in orders - result active
        '(\'alias4\', 4, \'complete\', 1, \'2021-03-11 15:00:02.0+03\'),'
        # complete in master_orders, active in orders - result transporting
        '(\'alias5\', 5, \'driving\', 1, \'2021-03-11 15:00:04.0+03\'),'
        # inactive (but not complete) in master_orders, active in orders
        # result - active
        '(\'alias6\', 6, \'driving\', 1, \'2021-03-11 15:00:06.0+03\');',
    )

    await taxi_driver_status.invalidate_caches()

    res = await taxi_driver_status.post('/v2/statuses/park', {'park': 'park1'})
    assert res.status_code == 200
    assert res.json() == {'free': 0, 'busy': 0, 'onorder': 0}

    res = await taxi_driver_status.post('/v2/statuses/park', {'park': 'park2'})
    assert res.status_code == 200
    assert res.json() == {'free': 0, 'busy': 0, 'onorder': 1}

    res = await taxi_driver_status.post('/v2/statuses/park', {'park': 'park3'})
    assert res.status_code == 200
    assert res.json() == {'free': 0, 'busy': 0, 'onorder': 1}

    res = await taxi_driver_status.post('/v2/statuses/park', {'park': 'park4'})
    assert res.status_code == 200
    assert res.json() == {'free': 0, 'busy': 0, 'onorder': 1}

    res = await taxi_driver_status.post('/v2/statuses/park', {'park': 'park5'})
    assert res.status_code == 200
    assert res.json() == {'free': 0, 'busy': 0, 'onorder': 1}

    res = await taxi_driver_status.post('/v2/statuses/park', {'park': 'park6'})
    assert res.status_code == 200
    assert res.json() == {'free': 0, 'busy': 0, 'onorder': 1}
