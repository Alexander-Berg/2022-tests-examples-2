import binascii
import datetime

import pytest

DRIVERS_CHUNKS_COUNT = 8


def _make_dbid_uuid(dbid, uuid):
    return '{}_{}'.format(dbid, uuid)


def _calc_chunk_id(dbid_uuid):
    return binascii.crc32(dbid_uuid.encode('utf8')) % DRIVERS_CHUNKS_COUNT


@pytest.mark.experiments3(filename='config3.json')
@pytest.mark.config(BUSY_DRIVERS_DRIVERS_CHUNKS_COUNT=DRIVERS_CHUNKS_COUNT)
@pytest.mark.parametrize(
    'dbid,uuid,max_destinations_left',
    [('dbid1', 'uuid1', 1), ('dbid2', 'uuid2', 1), ('dbid3', 'uuid3', 1)],
)
async def test_busy_drivers_order_event_stq_task(
        dbid, uuid, max_destinations_left, stq_runner, pgsql,
):

    sql_select_template = (
        'SELECT * FROM busy_drivers.order_meta WHERE order_id = {order_id}'
    )

    stq_task_kwargs = {
        'event': 'assign',
        'order_meta': {
            'order_id': 'order_id',
            'performer': {
                'dbid': dbid,
                'uuid': uuid,
                'tariff_class': 'econom',
            },
            'tariff_zone': 'moscow',
            'taxi_status': 'transporting',
            'destinations': [[12.34, 56.78], [42.42, 42.42], [52.42, 32.42]],
            'destinations_statuses': [],
            'updated': datetime.datetime.now(),
            'event_index': 0,
            'mystery_shopper': True,
            'special_requirements': ['thermobag_delivery'],
        },
    }
    destinations_left = len(stq_task_kwargs['order_meta']['destinations'])

    expected_driver_id = _make_dbid_uuid(dbid, uuid)
    expected_chunk_id = _calc_chunk_id(expected_driver_id)

    # Add order-meta to psql buffer

    await stq_runner.busy_drivers_order_events.call(
        task_id='busy_drivers_order_events', kwargs=stq_task_kwargs,
    )

    cursor = pgsql['busy_drivers'].cursor()

    cursor.execute(sql_select_template.format(order_id='order_id'))
    rows = cursor.fetchall()

    pg_colnames = [desc[0] for desc in cursor.description]
    pg_order = dict(zip(pg_colnames, rows[0]))

    status = (
        'pending' if destinations_left <= max_destinations_left else 'skip'
    )
    assert len(rows) == 1
    assert pg_order['driver_id'] == expected_driver_id
    assert pg_order['order_status'] == status
    assert (
        pg_order['destinations']
        == '{"(12.34,56.78)","(42.42,42.42)","(52.42,32.42)"}'
    )
    assert pg_order['chunk_id'] == expected_chunk_id
    assert pg_order['special_requirements'] == ['thermobag_delivery']
    assert pg_order['cargo_ref_id'] is None
    assert pg_order['transport_type'] is None

    # Update order-meta in psql buffer mimicking autoreorder

    performer = {
        'dbid': 'reordered_dbid',
        'uuid': 'reordered_uuid',
        'tariff_class': 'business',
        'transport_type': 'car',
    }
    expected_driver_id = _make_dbid_uuid(performer['dbid'], performer['uuid'])
    expected_chunk_id = _calc_chunk_id(expected_driver_id)

    stq_task_kwargs['event'] = 'change'
    stq_task_kwargs['order_meta']['performer'] = performer
    stq_task_kwargs['order_meta']['tariff_zone'] = 'moscow'
    stq_task_kwargs['order_meta']['destinations'] = [[12.34, 56.78]]
    stq_task_kwargs['order_meta']['destinations_statuses'] = [False]
    stq_task_kwargs['order_meta']['updated'] = datetime.datetime.now()
    stq_task_kwargs['order_meta']['event_index'] = 1
    stq_task_kwargs['order_meta']['cargo_ref_id'] = 'cargo_ref_id'
    destinations_left = len(stq_task_kwargs['order_meta']['destinations'])

    await stq_runner.busy_drivers_order_events.call(
        task_id='busy_drivers_order_events', kwargs=stq_task_kwargs,
    )

    cursor.execute(sql_select_template.format(order_id='order_id'))
    rows = cursor.fetchall()

    pg_order = dict(zip(pg_colnames, rows[0]))

    assert len(rows) == 1
    assert pg_order['driver_id'] == expected_driver_id
    assert pg_order['order_status'] == 'pending'
    assert pg_order['destinations'] == '{"(12.34,56.78)"}'
    assert pg_order['chunk_id'] == expected_chunk_id
    assert pg_order['tariff_zone'] == 'moscow'
    assert pg_order['tariff_class'] == 'business'
    assert pg_order['cargo_ref_id'] == 'cargo_ref_id'
    assert pg_order['transport_type'] == 'car'

    # Remove order-meta from psql buffer

    stq_task_kwargs['event'] = 'finish'
    stq_task_kwargs['order_meta']['updated'] = datetime.datetime.now()
    stq_task_kwargs['order_meta']['event_index'] = 2
    destinations_left = len(stq_task_kwargs['order_meta']['destinations'])

    await stq_runner.busy_drivers_order_events.call(
        task_id='busy_drivers_order_events', kwargs=stq_task_kwargs,
    )

    cursor.execute(sql_select_template.format(order_id='order_id'))
    rows = cursor.fetchall()

    pg_order = dict(zip(pg_colnames, rows[0]))

    assert len(rows) == 1
    assert pg_order['driver_id'] == expected_driver_id
    assert pg_order['order_status'] == 'finished'
