import datetime


def _select_query_string(**ids):
    query = (
        'SELECT *, order_meta.order_meta, '
        'dispatched_performer.dispatched_performer '
        'FROM dispatch_buffer.dispatch_meta '
        'LEFT JOIN dispatch_buffer.order_meta '
        'ON dispatch_meta.id = order_meta.id '
        'LEFT JOIN dispatch_buffer.dispatched_performer '
        'ON dispatch_meta.id = dispatched_performer.id '
    )
    exists_conditions = False
    for key, value in ids.items():
        if exists_conditions:
            query += f' AND {key}=\'{value}\' '
        else:
            query += f' WHERE {key}=\'{value}\' '
            exists_conditions = True
    return query


def select_named(pgsql, **ids):
    cursor = pgsql['driver_dispatcher'].conn.cursor()

    query = _select_query_string(**ids)
    cursor.execute(query)
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def _insert_query(pgsql, table_name, **column_value):
    cursor = pgsql['driver_dispatcher'].cursor()
    query = f'INSERT INTO dispatch_buffer.{table_name} '
    columns = ''
    values = ''
    for column, value in column_value.items():
        columns += column + ','
        values += (
            f'\'{value}\','
            if not (
                isinstance(value, str)
                and ((value[0] == '(') or (value.startswith('ROW(')))
            )
            else value + ','
        )
    columns = columns[:-1]
    values = values[:-1]

    query += f'({columns}) VALUES ({values}) RETURNING {table_name}.id'

    cursor.execute(query)
    return list(r for r in cursor)[0][0]


def insert_order(pgsql, **column_value):
    order_meta_values = {}
    dispatched_performer_values = {}
    if column_value.get('order_meta'):
        order_meta_values['order_meta'] = column_value['order_meta']
        column_value.pop('order_meta')

    if column_value.get('dispatched_performer'):
        dispatched_performer_values['dispatched_performer'] = column_value[
            'dispatched_performer'
        ]
        column_value.pop('dispatched_performer')

    cursor = pgsql['driver_dispatcher'].cursor()
    cursor.execute('BEGIN;')

    storage_id = _insert_query(pgsql, 'dispatch_meta', **column_value)

    if order_meta_values:
        order_meta_values['id'] = storage_id
        _insert_query(pgsql, 'order_meta', **order_meta_values)

    if dispatched_performer_values:
        dispatched_performer_values['id'] = storage_id
        _insert_query(
            pgsql, 'dispatched_performer', **dispatched_performer_values,
        )

    cursor.execute('COMMIT;')


def update_first_dispatch_run_value(
        pgsql, first_dispatch_run, offer_id, user_id,
):
    cursor = pgsql['driver_dispatcher'].conn.cursor()
    cursor.execute(
        f"""
    UPDATE dispatch_buffer.dispatch_meta
    SET first_dispatch_run='{first_dispatch_run}'
    WHERE user_id='{user_id}' AND offer_id='{offer_id}';
  """,
    )


def delete_by_user_id(pgsql, user_id):
    cursor = pgsql['driver_dispatcher'].conn.cursor()
    cursor.execute(
        f"""
    DELETE FROM dispatch_buffer.dispatch_meta
    WHERE user_id='{user_id}';
  """,
    )


def clear_db(pgsql):
    cursor = pgsql['driver_dispatcher'].conn.cursor()
    cursor.execute('TRUNCATE TABLE dispatch_buffer.dispatch_meta CASCADE;')
    cursor.execute('TRUNCATE TABLE dispatch_buffer.order_meta CASCADE;')
    cursor.execute(
        'TRUNCATE TABLE dispatch_buffer.dispatched_performer CASCADE;',
    )


def strip_tz(origin_dt):
    origin_dt = origin_dt - origin_dt.utcoffset()
    origin_dt.replace(tzinfo=None)
    return origin_dt


def assert_sorted(lhs, rhs):
    assert sorted(lhs) == sorted(rhs)


def compare_dicts(left_dict, right_dict):
    left_dict = {
        k: left_dict[k] for k in left_dict if left_dict[k] is not None
    }
    right_dict = {
        k: right_dict[k] for k in right_dict if right_dict[k] is not None
    }

    for k in left_dict:
        if isinstance(left_dict[k], dict):
            assert compare_dicts(left_dict[k], right_dict.get(k))
        else:
            if isinstance(left_dict[k], list):
                if isinstance(right_dict[k], list):
                    assert_sorted(left_dict[k], right_dict[k])
                else:
                    assert False
                continue
            elif isinstance(right_dict[k], list):
                assert False
                continue

            if isinstance(left_dict[k], datetime.datetime):
                left_dict[k] = datetime.datetime.strftime(
                    strip_tz(left_dict[k]), '%Y-%m-%dT%H:%M:%S.%fZ',
                )
            if isinstance(right_dict.get(k), datetime.datetime):
                right_dict[k] = datetime.datetime.strftime(
                    strip_tz(right_dict[k]), '%Y-%m-%dT%H:%M:%S.%fZ',
                )

            assert left_dict[k] == right_dict.get(k)

    return True


def datetime_form_string(datetime_string):
    if len(datetime_string) == 8:
        return datetime.datetime.strptime(datetime_string, '%H:%M:%S')
    return datetime.datetime.strptime(datetime_string, '%H:%M:%S.%f')


def total_milliseconds(datetime_value):
    return (
        (datetime_value.days * 86400 + datetime_value.seconds) * 10 ** 6
        + datetime_value.microseconds
    ) / 10 ** 3


def timeout_from_string(timeout_string):
    start_time = datetime.datetime(1900, 1, 1)
    datetime_value = datetime_form_string(timeout_string)
    return total_milliseconds(datetime_value - start_time)


def callback_from_string(callback_string):
    callback_fields = callback_string[1:-1].split(',')
    url = callback_fields[0]
    timeout_ms = int(timeout_from_string(callback_fields[1]))
    attempts = int(callback_fields[2])
    return dict(url=url, timeout_ms=timeout_ms, attempts=attempts)


def agglomeration_settings(agglomeration, settings):
    return {
        'name': 'dispatch_buffer_agglomeration_settings',
        'consumers': ['lookup_dispatch/agglomeration_settings'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': agglomeration,
                'value': {**settings},
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': agglomeration,
                                    'arg_name': 'agglomeration',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                },
            },
        ],
        'default_value': {},
    }
