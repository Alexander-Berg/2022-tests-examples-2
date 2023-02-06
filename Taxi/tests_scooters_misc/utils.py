import typing as tp


class AnyValue:
    def __init__(self):
        pass

    def __eq__(self, o):
        return True


def _create_query_param(name: str, casts: dict = None) -> str:
    casts = casts or {}
    if name not in casts:
        return '%s'
    return casts[name]()


def _get_query_with_args(
        item: dict,
        table: str,
        fields: tp.List[str],
        *,
        required: list = None,
        casts: dict = None,
) -> tp.Tuple[str, list]:
    required = required or []

    keys = []
    args = []

    for name in required:
        assert name in item, f'Field "{name}" is required'

    for key, value in item.items():
        assert key in fields, f'Field "{key}" not present in "{table}" table'
        keys.append(key)
        args.append(value)

    query = f"""
    INSERT INTO scooters_misc.{table} (
        {','.join(keys)}
    )
    VALUES (
        {','.join(_create_query_param(name, casts) for name in keys)}
    )
    RETURNING {','.join(fields)}
    """

    return query, args


def _merge_tuple_with_fields(fields, db_tuple) -> dict:
    assert len(fields) == len(db_tuple), 'len mismatch'
    return dict(zip(fields, db_tuple))


def try_flatten(items: list, flatten: bool):
    if not flatten or not items:
        return items

    assert len(items[0]) == 1, 'Only one field can be flattened'

    field = list(items[0])[0]
    return [item[field] for item in items]


RECHARGE_TASKS_FIELDS = [
    'id',
    'type',
    'status',
    'performer_id',
    'cargo_claim_id',
    'dispatch_version',
]

RECHARGE_ITEMS_FIELDS = [
    'id',
    'accumulator_status',
    'task_id',
    'vehicle_id',
    'vehicle_number',
    'accumulator_book_id',
    'cell_book_id',
    'accumulator_sn',
    'location',
    'cabinet_id',
    'depot_id',
    'cargo_point_id',
]

RECHARGE_HISTORY_FIELDS = [
    'id',
    'recharge_task_id',
    'recharge_item_id',
    'event_type',
    'occured_at_dt',
    'data',
]

DEPOTS_FIELDS = [
    'depot_id',
    'location',
    'city',
    'address',
    'created_at',
    'updated_at',
    'idempotency_token',
    'enabled',
    'timetable',
]

TACKLES_FIELDS = [
    'id',
    'kind',
    'depot_id',
    'performer_id',
    'recharge_task_id',
    'version',
]

VEHICLE_CONTROL_LOG_FIELDS = [
    'id',
    'timestamp',
    'user_id',
    'source',
    'vehicle_id',
    'action',
]


def add_recharge_task(pgsql, task):
    cursor = pgsql['scooter_backend'].cursor()
    query, args = _get_query_with_args(
        task,
        'recharge_tasks',
        RECHARGE_TASKS_FIELDS,
        required=['id', 'status'],
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(RECHARGE_TASKS_FIELDS, cursor.fetchone())


def add_recharge_item(pgsql, item):
    cursor = pgsql['scooter_backend'].cursor()
    query, args = _get_query_with_args(
        item,
        'recharge_items',
        RECHARGE_ITEMS_FIELDS,
        required=['id'],
        casts={'location': lambda: 'CAST(\'%s\' AS POINT)'},
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(RECHARGE_ITEMS_FIELDS, cursor.fetchone())


def add_recharge_history_record(pgsql, record):
    cursor = pgsql['scooter_backend'].cursor()
    query, args = _get_query_with_args(
        record,
        'recharge_history',
        RECHARGE_HISTORY_FIELDS,
        required=['recharge_task_id', 'event_type', 'id'],
    )

    cursor.execute(query, args)
    return _merge_tuple_with_fields(RECHARGE_HISTORY_FIELDS, cursor.fetchone())


def add_depot(pgsql, depot):
    cursor = pgsql['scooter_backend'].cursor()
    query, args = _get_query_with_args(
        depot,
        'depots',
        DEPOTS_FIELDS,
        casts={
            'location': lambda: 'CAST(\'%s\' AS POINT)',
            'timetable': lambda: 'CAST(%s AS scooters_misc.timetable_item[])',
        },
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(DEPOTS_FIELDS, cursor.fetchone())


def get_recharge_task(pgsql, task_id, *, fields=None):
    fields = fields or RECHARGE_TASKS_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.recharge_tasks
    WHERE
        id = %(recharge_task_id)s
    """
    cursor = pgsql['scooter_backend'].cursor()

    cursor.execute(sql, {'recharge_task_id': task_id})
    return _merge_tuple_with_fields(fields, cursor.fetchone())


def get_all_recharge_tasks(
        pgsql, *, fields=None, order_by: str = 'id', flatten=False,
):
    fields = fields or RECHARGE_TASKS_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.recharge_tasks
    ORDER BY {order_by}
    """
    cursor = pgsql['scooter_backend'].cursor()
    cursor.execute(sql)

    return try_flatten(
        list(
            _merge_tuple_with_fields(fields, task_tuple)
            for task_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_recharge_items(
        pgsql, *, ids=None, task_id=None, fields=None, flatten=False,
):
    assert (ids is None) != (task_id is None), 'Use ids or task_id'

    fields = fields or RECHARGE_ITEMS_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.recharge_items
    WHERE
        id = ANY(%(ids)s)
        OR task_id = %(task_id)s
    ORDER BY id
    """
    cursor = pgsql['scooter_backend'].cursor()

    # -100500 is 100% absent task_id
    cursor.execute(sql, {'ids': ids or [], 'task_id': task_id or '-100500'})

    return try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_all_recharge_items(pgsql, *, fields=None, flatten=False):
    fields = fields or RECHARGE_ITEMS_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.recharge_items
    ORDER BY id
    """
    cursor = pgsql['scooter_backend'].cursor()

    cursor.execute(sql)

    return try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_recharge_history_points(
        pgsql,
        *,
        recharge_task_ids=None,
        recharge_item_ids=None,
        fields=None,
        flatten=False,
):
    assert (
        not recharge_item_ids or not recharge_task_ids
    ), 'either recharge_task_ids or recharge_item_ids must be setted'
    fields = fields or RECHARGE_HISTORY_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.recharge_history
    WHERE
        recharge_task_id = ANY(%(task_ids)s)
        OR
        recharge_item_id = ANY(%(item_ids)s)
    ORDER BY occured_at_dt
    """

    cursor = pgsql['scooter_backend'].cursor()
    cursor.execute(
        sql,
        {
            'task_ids': recharge_task_ids or [],
            'item_ids': recharge_item_ids or [],
        },
    )

    return try_flatten(
        [
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ],
        flatten,
    )


def get_depot(pgsql, depot_id, *, fields=None):
    fields = fields or DEPOTS_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.depots
    WHERE
        scooters_misc.depots.depot_id = %(depot_id)s
    """

    cursor = pgsql['scooter_backend'].cursor()

    cursor.execute(sql, {'depot_id': depot_id})

    return cursor.fetchall()


def init_task_status_by_flow(flow):
    return (
        'cargo:pickup_arrived'
        if flow == 'pickup'
        else 'cargo:delivery_arrived'
    )


def init_accumulator_status_by_flow(flow):
    return 'booked' if flow == 'pickup' else 'pickuped'


def pending_accumulator_status_by_flow(flow):  # pylint: disable=invalid-name
    return 'pickup_pending' if flow == 'pickup' else 'return_pending'


def success_accumulator_status_by_flow(flow):  # pylint: disable=invalid-name
    return 'pickuped' if flow == 'pickup' else 'returned'


def booking_id_by_flow(
        flow, acc_book_id='accumulator_book_id', cell_book_id='cell_book_id',
):
    return acc_book_id if flow == 'pickup' else cell_book_id


def tag_by_task_type(task_type):
    if task_type == 'recharge':
        return 'battery_low'
    if task_type == 'dead':
        return 'dead'

    raise ValueError(f'Bad task type: {type}')


def add_drive_area(
        pgsql,
        area_id: str,
        area_coords: list,
        area_tags: tp.Optional[list] = None,
):
    sql = """
    INSERT INTO public.drive_areas (
        area_id,
        area_coords,
        area_tags,
        revision
    )
    VALUES (
        %(area_id)s,
        %(area_coords)s,
        %(area_tags)s,
        1
    )
    """

    pgsql['scooter_backend'].cursor().execute(
        sql,
        {
            'area_id': area_id,
            'area_coords': ' '.join(map(str, area_coords)),
            'area_tags': ', '.join(area_tags or []),
        },
    )


def get_claims_journal_cursor(pgsql):
    cursor = pgsql['scooter_backend'].cursor()
    cursor.execute(
        'SELECT cursor FROM scooters_misc.cargo_statuses_fetch_cursor',
    )
    result = cursor.fetchall()
    assert len(result) in [0, 1]
    if result:
        return result[0][0]
    return None


def set_workflow_last_run_time(pgsql, workflow: str, seconds_ago: int):
    query = f"""
    INSERT INTO scooters_misc.workflows(name, last_run)
    VALUES ('{workflow}', NOW() - INTERVAL '{seconds_ago}')
        ON CONFLICT(name) DO UPDATE
       SET last_run = NOW() - INTERVAL '{seconds_ago}';
    """
    cursor = pgsql['scooter_backend'].cursor()
    cursor.execute(query)


def add_claims_journal_cursor(pgsql, journal_cursor):
    pgsql['scooter_backend'].cursor().execute(
        'INSERT INTO scooters_misc.cargo_statuses_fetch_cursor(cursor) '
        f'VALUES (\'{journal_cursor}\')',
    )


def add_tackle(pgsql, tackle):
    cursor = pgsql['scooter_backend'].cursor()
    query, args = _get_query_with_args(
        tackle, 'tackles', TACKLES_FIELDS, required=['id', 'kind'],
    )
    cursor.execute(query, args)


def get_tackles(pgsql, *, ids=None, task_id=None, fields=None, flatten=False):
    assert (ids is None) != (task_id is None), 'Use ids or task_id'

    fields = fields or TACKLES_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.tackles
    WHERE
        id = ANY(%(ids)s)
        OR recharge_task_id = %(task_id)s
    ORDER BY id
    """
    cursor = pgsql['scooter_backend'].cursor()

    # -100500 is 100% absent task_id
    cursor.execute(sql, {'ids': ids or [], 'task_id': task_id or '-100500'})

    return try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )


def get_drive_cursor(pgsql, *, name: str) -> tp.Optional[int]:
    sql = f"""
    SELECT
        drive_cursor as cursor
    FROM
        scooters_misc.drive_tables_cursors
    WHERE
        drive_table = %(name)s
    LIMIT 1
    """
    cursor = pgsql['scooter_backend'].cursor()

    cursor.execute(sql, {'name': name})
    result = cursor.fetchone()

    if result:
        return result[0]

    return None


def get_vehicle_control_log(
        pgsql, *, vehicle_ids: list, fields=None, flatten=False,
):
    fields = fields or VEHICLE_CONTROL_LOG_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_misc.vehicle_control_log
    WHERE
        vehicle_id = ANY(%(vehicle_ids)s)
    ORDER BY id
    """
    cursor = pgsql['scooter_backend'].cursor()

    cursor.execute(sql, {'vehicle_ids': vehicle_ids or []})

    return try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )
