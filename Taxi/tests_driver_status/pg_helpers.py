# pylint: disable=wrong-import-order, import-error, import-only-modules
import datetime

import pytz

# pylint: disable=wrong-import-order, import-error, import-only-modules
from tests_driver_status.enum_constants import DriverStatus
from tests_driver_status.enum_constants import OrderStatus
from tests_driver_status.enum_constants import ProcessingStatus
# pylint: enable=wrong-import-order, import-error, import-only-modules


def make_drivers_insert_query(timestamp, start, count):

    rows = [
        f'({i}, \'parkid{i}\', \'driverid{i}\', \'{timestamp}\')'
        for i in range(start, start + count)
    ]
    values = ','.join(rows)
    return (
        'INSERT INTO ds.drivers'
        '(id, park_id, driver_id, updated_ts) '
        f'VALUES {values}'
    )


def make_statuses_insert_query(status, source, timestamp, start, count):
    rows = [
        f'({i}, \'{status}\', \'{source}\', \'{timestamp}\')'
        for i in range(start, start + count)
    ]
    values = ','.join(rows)
    return (
        'INSERT INTO ds.statuses'
        '(driver_id, status, source, updated_ts) '
        f'VALUES {values}'
    )


def make_orders_insert_query(status, timestamp, start, count):
    rows = [
        f'(\'order_id_{i}\', {i}, \'{status}\', 1, \'{timestamp}\')'
        for i in range(start, start + count)
    ]
    values = ','.join(rows)
    return (
        'INSERT INTO ds.orders'
        '(id, driver_id, status, provider_id, updated_ts) '
        f'VALUES {values}'
    )


def make_blocks_update_insert_query(timestamp, start, count):
    rows = [f'({i}, \'{timestamp}\')' for i in range(start, start + count)]
    values = ','.join(rows)
    return (
        'INSERT INTO ds.blocks_update(driver_id, checked_ts) '
        f'VALUES {values}'
    )


def make_blocks_insert_query(reason_id, timestamp, start, count):
    rows = [
        f'({i}, {reason_id}, \'{timestamp}\')'
        for i in range(start, start + count)
    ]
    values = ','.join(rows)
    return (
        'INSERT INTO ds.blocks(driver_id, reason_id, updated_ts) '
        f'VALUES {values}'
    )


def run_in_transaction(pgsql, queries):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('BEGIN')
    for query in queries:
        cursor.execute(query)
    cursor.execute('COMMIT')


def get_pg_driver_id(pgsql, park_id, driver_id):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT id '
        'FROM ds.drivers '
        f'WHERE park_id=\'{park_id}\' AND driver_id=\'{driver_id}\'',
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    return -1


def get_pg_driver_info(pgsql, internal_id):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT park_id, driver_id '
        'FROM ds.drivers '
        f'WHERE id = {internal_id}',
    )
    row = cursor.fetchone()
    if row:
        return (row[0], row[1])
    return -1


def check_drivers_table(pgsql, park_id, driver_id):
    pg_driver_id = get_pg_driver_id(pgsql, park_id, driver_id)
    assert pg_driver_id != -1
    return pg_driver_id


def get_status_row(pgsql, driver_id):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT status, source, updated_ts '
        'FROM ds.statuses '
        f'WHERE  driver_id=\'{driver_id}\'',
    )
    return cursor.fetchone()


def check_statuses_table(pgsql, driver_id, status, source, updated_ts):
    row = get_status_row(pgsql, driver_id)
    assert row is not None
    assert row[0] == DriverStatus.from_legacy(status)
    assert row[1] == source
    assert _to_utc(row[2]) == updated_ts


def external_provider_to_string(ext_provider_id):
    return {
        0: 'unknown',
        1: 'park',
        2: 'yandex',
        16: 'upup',
        128: 'formula',
        1024: 'offtaxi',
        524288: 'app',
    }.get(ext_provider_id, 'unknown')


def get_order_row(pgsql, order_id):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT driver_id, status, name as provider_name, updated_ts '
        'FROM ds.orders, ds.providers '
        'WHERE ds.orders.provider_id = ds.providers.id '
        f'AND ds.orders.id=\'{order_id}\'',
    )
    return cursor.fetchone()


def check_orders_table(
        pgsql, order_id, driver_id, status, provider_id, updated_ts,
):
    row = get_order_row(pgsql, order_id)
    assert row is not None
    assert row[0] == driver_id
    assert row[1] == status
    assert row[2] == external_provider_to_string(provider_id)
    assert _to_utc(row[3]) == updated_ts


def get_master_orders_row(pgsql, alias_id, db_contractor_id):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT alias_id, order_id, contractor_id, status, provider_id, '
        'event_ts, updated_ts '
        'FROM ds.master_orders '
        f'WHERE alias_id=\'{alias_id}\' '
        f'AND contractor_id=\'{db_contractor_id}\'',
    )
    return cursor.fetchone()


def check_master_orders_table(
        pgsql,
        alias_id,
        park_id,
        profile_id,
        order_id,
        status,
        provider,
        event_ts,
):
    db_contractor_id = check_drivers_table(pgsql, park_id, profile_id)
    db_provider_id = get_pg_provider_ids(pgsql)[provider]
    # Note: don't check updated_ts as it is set to NOW() in PG
    # and we can't mock it
    row = get_master_orders_row(pgsql, alias_id, db_contractor_id)
    assert row is not None
    assert row[0] == alias_id
    assert row[1] == order_id
    assert row[2] == db_contractor_id
    assert row[3] == status
    assert row[4] == db_provider_id
    # processing consumer has 1mks error on parsing timestamp from double
    assert abs(row[5] - event_ts) < datetime.timedelta(milliseconds=1)


def get_master_orders_count(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT count(*) FROM ds.master_orders')
    return cursor.fetchone()[0]


def get_blocked_reason_id(pgsql, reason):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        f'SELECT id FROM ds.blocked_reasons WHERE name = \'{reason}\'',
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    return -1


def check_blocked_reason_id(pgsql, reason):
    reason_id = get_blocked_reason_id(pgsql, reason)
    assert reason_id != -1
    return reason_id


def get_blocks_count(pgsql, blocked_reason=None):
    cursor = pgsql['driver-status'].cursor()
    if blocked_reason is None:
        cursor.execute('SELECT count(*) FROM ds.blocks')
    else:
        cursor.execute(
            'SELECT count(*) FROM ds.blocks, ds.blocked_reasons '
            'WHERE ds.blocks.reason_id = ds.blocked_reasons.id '
            f'AND ds.blocked_reasons.name = \'{blocked_reason}\'',
        )
    return cursor.fetchone()[0]


def _to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.UTC).replace(tzinfo=None)
    return stamp


def _upsert_statuses(pgsql, pg_driver_ids, statuses):
    query = """
            INSERT INTO ds.statuses(driver_id,status,source,updated_ts)
            VALUES
            """
    records = str()
    first = True
    for key, value in statuses.items():
        status = value.get('status')
        if not status:
            continue
        updated_ts_str = value.get('updated_ts', '1970-01-01 00:00:00.0+00')
        if not first:
            records += ','
        else:
            first = False
        records += '({},\'{}\',\'{}\',\'{}\')'.format(
            pg_driver_ids[key], status, 'service', updated_ts_str,
        )

    if not records:
        return

    query += (
        records
        + """
              ON CONFLICT (driver_id) DO UPDATE SET
              status = excluded.status,
              source = excluded.source,
              updated_ts = excluded.updated_ts;
             """
    )
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(query)


def get_pg_provider_ids(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT name, id FROM ds.providers;')
    result = dict()
    for row in cursor:
        result[row[0]] = row[1]
    return result


def _get_pg_blocked_reasons_ids(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT name, id FROM ds.blocked_reasons;')
    result = dict()
    for row in cursor:
        result[row[0]] = row[1]
    return result


def _upsert_orders(pgsql, pg_driver_ids, data):
    pg_provider_ids = get_pg_provider_ids(pgsql)
    query = """
            INSERT INTO ds.orders(id,driver_id,status,provider_id,updated_ts)
            VALUES
            """
    records = str()
    first = True
    for driver_id, driver_info in data.items():
        orders = driver_info.get('orders')

        if not orders:
            continue

        for order_id, order_info in orders.items():
            updated_ts_str = str(
                order_info.get(
                    'updated_ts',
                    datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
                ),
            )
            if not first:
                records += ','
            else:
                first = False
            records += '(\'{}\',{},\'{}\',\'{}\',\'{}\')'.format(
                order_id,
                pg_driver_ids[driver_id],
                order_info.get('status', 'none'),
                pg_provider_ids[order_info.get('provider', 'yandex')],
                updated_ts_str,
            )

    if not records:
        return

    query += (
        records
        + """
              ON CONFLICT ON CONSTRAINT unique_id_driver_id DO UPDATE SET
              driver_id = excluded.driver_id,
              status = excluded.status,
              provider_id = excluded.provider_id,
              updated_ts = excluded.updated_ts;
             """
    )
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(query)


def _upsert_processing_orders(pgsql, pg_driver_ids, data):
    query = """
            INSERT INTO ds.processing_orders(id,alias_id,driver_id,
            status,processing_status,event_updated_ts,updated_ts,event_index)
            VALUES
            """
    records = []
    for order_id, info in data.items():
        driver_id_str = 'null'
        if 'driver_id' in info and 'park_id' in info:
            driver_id_str = '\'{}\''.format(
                pg_driver_ids[info['driver_id'], info['park_id']],
            )
        alias_id_str = (
            '\'{}\''.format(info['alias_id']) if 'alias_id' in info else 'null'
        )
        status = '\'{}\''.format(info.get('status', OrderStatus.kNone))
        processing_status = '\'{}\''.format(
            info.get('processing_status', ProcessingStatus.kPending),
        )
        event_updated_ts_str = '\'{}\''.format(
            info.get(
                'event_updated_ts',
                datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
            ),
        )
        updated_ts_str = '\'{}\''.format(
            info.get(
                'updated_ts',
                datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
            ),
        )
        event_index = str(info.get('event_index', 0))
        # orders = driver_info.get('orders'))
        records.append(
            '({},{},{},{},{},{},{},{})'.format(
                '\'{}\''.format(order_id),
                alias_id_str,
                driver_id_str,
                status,
                processing_status,
                event_updated_ts_str,
                updated_ts_str,
                event_index,
            ),
        )

    if not records:
        return

    records_str = ','.join(records)
    query += (
        records_str
        + """
              ON CONFLICT (id) DO UPDATE SET
                  id = excluded.id,
                  alias_id = excluded.alias_id,
                  driver_id = excluded.driver_id,
                  event_index = excluded.event_index,
                  status = excluded.status,
                  processing_status = excluded.processing_status,
                  updated_ts = excluded.updated_ts,
                  event_updated_ts = excluded.event_updated_ts;
         """
    )
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(query)


def _upsert_master_orders(pgsql, contractor_db_ids, data):
    provider_db_ids = get_pg_provider_ids(pgsql)
    query = """
            INSERT INTO ds.master_orders
            (alias_id, order_id, contractor_id, status,
            provider_id, event_ts, updated_ts)
            VALUES
            """
    records = []
    for contractor_id, orders in data.items():
        for alias_id, order_info in orders.items():
            order_id = order_info.get('order_id')
            order_id_str = f'\'{order_id}\'' if order_id else 'null'
            contractor_db_id = contractor_db_ids[contractor_id]
            status = order_info['status']
            provider_db_id = provider_db_ids[
                order_info.get('provider', 'yandex')
            ]
            event_ts_str = str(
                order_info.get(
                    'event_ts',
                    datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
                ),
            )
            updated_ts_str = str(
                order_info.get(
                    'updated_ts',
                    datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.utc),
                ),
            )

            records.append(
                f'(\'{alias_id}\',{order_id_str},{contractor_db_id},'
                f'\'{status}\',{provider_db_id},'
                f'\'{event_ts_str}\',\'{updated_ts_str}\')',
            )

    records_str = ','.join(records)
    query += records_str
    query += """
             ON CONFLICT ON CONSTRAINT unique_performer_order DO UPDATE SET
             status = excluded.status,
             provider_id = excluded.provider_id,
             event_ts = excluded.event_ts,
             updated_ts = excluded.updated_ts;
             """

    cursor = pgsql['driver-status'].cursor()
    cursor.execute(query)


def _upsert_blocks(pgsql, pg_driver_ids, data):
    pg_reason_ids = _get_pg_blocked_reasons_ids(pgsql)
    query = """
            INSERT INTO ds.blocks(driver_id,reason_id,updated_ts)
            VALUES
            """
    records = str()
    first = True
    for driver_id, driver_info in data.items():
        blocks = driver_info.get('blocks')
        if not blocks:
            continue
        for reason, updated_ts in blocks.items():
            updated_ts_str = str(updated_ts)
            if not first:
                records += ','
            else:
                first = False
            records += '(\'{}\',{},\'{}\')'.format(
                pg_driver_ids[driver_id],
                pg_reason_ids[reason],
                updated_ts_str,
            )

    if not records:
        return

    query += (
        records
        + """
              ON CONFLICT ON CONSTRAINT blocks_pkey DO UPDATE SET
              driver_id = excluded.driver_id,
              reason_id = excluded.reason_id,
              updated_ts = excluded.updated_ts;
             """
    )
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(query)


def _get_pg_driver_ids(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('SELECT driver_id, park_id, id FROM ds.drivers;')
    result = {}
    for row in cursor:
        result[(row[0], row[1])] = row[2]
    return result


def get_pg_driver_statuses(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT'
        ' ds.drivers.park_id AS park_id,'
        ' ds.drivers.driver_id AS driver_id,'
        ' ds.statuses.status, ds.statuses.updated_ts'
        ' FROM ds.statuses'
        ' LEFT JOIN ds.drivers'
        ' ON ds.statuses.driver_id = ds.drivers.id',
    )
    result = {}
    for row in cursor:
        result[(row[1], row[0])] = {'status': row[2], 'updated_ts': row[3]}
    return result


def get_pg_orders(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT'
        ' ds.orders.id AS alias_id,'
        ' ds.drivers.park_id,'
        ' ds.drivers.driver_id,'
        ' status,'
        ' ds.orders.updated_ts,'
        ' ds.providers.name AS provider'
        ' FROM ds.orders'
        ' LEFT JOIN ds.drivers'
        ' ON ds.orders.driver_id = ds.drivers.id'
        ' LEFT JOIN ds.providers'
        ' ON ds.providers.id = ds.orders.provider_id',
    )
    result = {}
    for row in cursor:
        key = (row[2], row[1])
        if key not in result:
            result[key] = {}
        result[key][row[0]] = {
            'status': row[3],
            'updated_ts': row[4],
            'provider': row[5],
        }
    return result


def get_pg_master_orders(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT'
        ' ds.master_orders.alias_id,'
        ' ds.master_orders.order_id,'
        ' ds.drivers.park_id,'
        ' ds.drivers.driver_id,'
        ' ds.master_orders.status,'
        ' ds.providers.name,'
        ' ds.master_orders.event_ts'
        ' FROM ds.master_orders'
        ' LEFT JOIN ds.drivers'
        ' ON ds.master_orders.contractor_id = ds.drivers.id'
        ' LEFT JOIN ds.providers'
        ' ON ds.master_orders.provider_id = ds.providers.id',
    )
    result = {}
    for row in cursor:
        key = (row[0], row[2], row[3])
        result[key] = {
            'order_id': row[1],
            'status': row[4],
            'provider': row[5],
            'event_ts': datetime_to_ms(row[6]),
        }
    return result


def get_pg_order_providers(pgsql, park_id, driver_id):
    driver_pg_id = _get_pg_driver_ids(pgsql)[(driver_id, park_id)]
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(
        'SELECT name'
        ' FROM ds.orders'
        ' JOIN ds.providers'
        ' ON ds.providers.id = ds.orders.provider_id'
        ' WHERE ds.orders.driver_id = \'{}\''.format(driver_pg_id),
    )
    result = []
    for row in cursor:
        result.append(row)
    return result


def _insert_pg_driver_ids(pgsql, drivers):
    query = """
            INSERT INTO ds.drivers(park_id,driver_id)
            VALUES
            """
    first = True
    for driver in drivers:
        if not first:
            query += ','
        else:
            first = False
        query += f'(\'{driver[1]}\',\'{driver[0]}\')'
    query += 'ON CONFLICT ON CONSTRAINT unique_park_driver DO NOTHING;'
    cursor = pgsql['driver-status'].cursor()
    cursor.execute(query)


def _insert_and_get_pg_driver_ids(pgsql, data):
    _insert_pg_driver_ids(pgsql, data)
    return _get_pg_driver_ids(pgsql)


def datetime_to_ms(_dt):
    return int(_dt.timestamp() * 1000)


def datetime_to_us(_dt):
    return int(_dt.timestamp() * 1000000)


def upsert_drivers(pgsql, drivers):
    _insert_pg_driver_ids(pgsql, drivers)


def upsert_statuses(pgsql, data):
    if not data:
        return

    result = _insert_and_get_pg_driver_ids(pgsql, data)
    _upsert_statuses(pgsql, result, data)


def upsert_orders(pgsql, data):
    if not data:
        return

    result = _insert_and_get_pg_driver_ids(pgsql, data)
    _upsert_orders(pgsql, result, data)


def upsert_blocks(pgsql, data):
    result = _insert_and_get_pg_driver_ids(pgsql, data)
    _upsert_blocks(pgsql, result, data)


def upsert_processing_orders(pgsql, data):
    drivers = []
    for _, info in data.items():
        if 'driver_id' in info and 'park_id' in info:
            drivers.append((info['driver_id'], info['park_id']))
    result = _insert_and_get_pg_driver_ids(pgsql, drivers)
    _upsert_processing_orders(pgsql, result, data)


def upsert_master_orders(pgsql, data):
    if not data:
        return

    contractor_db_ids = _insert_and_get_pg_driver_ids(pgsql, data)
    _upsert_master_orders(pgsql, contractor_db_ids, data)


def clear_master_orders(pgsql):
    cursor = pgsql['driver-status'].cursor()
    cursor.execute('DELETE FROM ds.master_orders;')


def to_input_repr(events):
    if not events:
        return {}

    converted = {}
    for event in events:
        profile_id = event.get('profile_id')
        park_id = event.get('park_id')
        status = event.get('status')
        updated_ts = event.get('updated_ts')
        orders = event.get('orders')

        if any(
                [
                    item is None
                    for item in [profile_id, park_id, status, updated_ts]
                ],
        ):
            continue
        if not DriverStatus.contains(status):
            continue

        key = (profile_id, park_id)
        if key not in converted:
            converted[key] = {}

        converted[key]['status'] = status
        converted[key]['updated_ts'] = updated_ts

        if orders is not None:
            result_orders = {}
            for order in orders:
                order_id = order.get('order_id')
                alias_id = order.get('alias_id')
                order_status = order.get('status')
                provider = order.get('provider')

                if (
                        not alias_id
                        or not order_status
                        or not OrderStatus.contains(order_status)
                ):
                    continue

                order_value = {
                    'status': order_status,
                    'updated_ts': updated_ts,
                }
                if order_id is not None:
                    order_value['order_id'] = order_id
                if provider is not None:
                    order_value['provider'] = provider
                result_orders[alias_id] = order_value
            if 'orders' not in converted[key]:
                converted[key]['orders'] = {}
            for alias_id, order_info in result_orders.items():
                converted[key]['orders'][alias_id] = order_info
    return converted
