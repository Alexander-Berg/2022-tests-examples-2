import datetime
import typing as tp

from dateutil import parser as dateparser
import pytz


REPAIR_FIELDS = [
    'repair_id',
    'status',
    'performer_id',
    'depot_id',
    'vehicle_id',
    'started_at',
    'completed_at',
]

VEHICLE_INFO_FIELDS = ['repair_id', 'mileage']

JOB_FIELDS = [
    'job_id',
    'repair_id',
    'status',
    'type',
    'started_at',
    'completed_at',
]


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
    INSERT INTO scooters_ops_repair.{table} (
        {','.join(keys)}
    )
    VALUES (
        {','.join(_create_query_param(name, casts) for name in keys)}
    )
    RETURNING {','.join(fields)}
    """

    return query, args


def _merge_tuple_with_fields(fields, db_tuple) -> dict:
    assert len(fields) == len(db_tuple), f'{len(fields)} != {len(db_tuple)}'
    return dict(zip(fields, db_tuple))


def _try_flatten(items: list, flatten: bool):
    if not flatten or not items:
        return items

    assert len(items[0]) == 1, 'Only one field can be flattened'

    field = list(items[0])[0]
    return [item[field] for item in items]


def add_vehicle_info(pgsql, vehicle_info):
    cursor = pgsql['scooters_ops_repair'].cursor()
    query, args = _get_query_with_args(
        vehicle_info,
        'vehicle_infos',
        VEHICLE_INFO_FIELDS,
        required=['repair_id'],
    )
    cursor.execute(query, args)


def add_job(pgsql, job):
    cursor = pgsql['scooters_ops_repair'].cursor()
    query, args = _get_query_with_args(
        job, 'jobs', JOB_FIELDS, required=['job_id', 'repair_id'],
    )
    cursor.execute(query, args)


def get_vehicle_info(pgsql, repair_ids=None, *, fields=None, flatten=False):
    fields = fields or VEHICLE_INFO_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops_repair.vehicle_infos
    """
    if repair_ids is not None:
        sql = sql + 'WHERE repair_id = ANY(%(repair_ids)s)'
    sql += ' ORDER BY repair_id'
    cursor = pgsql['scooters_ops_repair'].cursor()

    cursor.execute(sql, {'repair_ids': repair_ids or []})
    return _try_flatten(
        [
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ],
        flatten,
    )


def add_repair(pgsql, repair):
    vehicle_info = None
    if 'vehicle_info' in repair:
        vehicle_info = repair.pop('vehicle_info')
    jobs = None
    if 'jobs' in repair:
        jobs = repair.pop('jobs')

    cursor = pgsql['scooters_ops_repair'].cursor()
    query, args = _get_query_with_args(repair, 'repairs', REPAIR_FIELDS)
    cursor.execute(query, args)

    if vehicle_info is not None:
        vehicle_info.setdefault('repair_id', repair['repair_id'])
        add_vehicle_info(pgsql, vehicle_info)

    if jobs is not None:
        for job in jobs:
            job.setdefault('repair_id', repair['repair_id'])
            add_job(pgsql, job)


def get_repairs(
        pgsql,
        ids=None,
        *,
        fields=None,
        flatten=False,
        vehicle_info_params=None,
):
    fields = fields or REPAIR_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops_repair.repairs
    """
    if ids is not None:
        sql = sql + 'WHERE repair_id = ANY(%(ids)s)'
    sql += ' ORDER BY repair_id'
    cursor = pgsql['scooters_ops_repair'].cursor()

    cursor.execute(sql, {'ids': ids or []})
    result = _try_flatten(
        list(
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ),
        flatten,
    )

    assert (
        vehicle_info_params is None or 'repair_id' in fields
    ), 'Cannot get vehicle_info without repair_id in fields'
    if vehicle_info_params is not None:
        for repair in result:
            vehicle_info = get_vehicle_info(
                pgsql, repair_ids=[repair['repair_id']],
            )[0]
            vehicle_info.pop('repair_id')
            repair['vehicle_info'] = vehicle_info

    return result


def get_jobs(pgsql, ids=None, repair_ids=None, *, fields=None, flatten=False):
    fields = fields or JOB_FIELDS
    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops_repair.jobs
    """
    if ids is not None:
        sql = sql + 'WHERE job_id = ANY(%(ids)s)'
    elif repair_ids is not None:
        sql += 'WHERE repair_id = ANY(%(repair_ids)s)'
    sql += ' ORDER BY repair_id'
    cursor = pgsql['scooters_ops_repair'].cursor()

    cursor.execute(sql, {'ids': ids or [], 'repair_ids': repair_ids or []})
    return _try_flatten(
        [
            _merge_tuple_with_fields(fields, item_tuple)
            for item_tuple in cursor.fetchall()
        ],
        flatten,
    )


def parse_timestring_aware(
        timestring: str, timezone: str = 'Europe/Moscow',
) -> datetime.datetime:
    time = dateparser.parse(timestring)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    utctime = time.astimezone(pytz.utc)
    return utctime


class AnyValue:
    def __init__(self):
        pass

    def __eq__(self, o):
        return True


class AnyNotNoneValue:
    def __init__(self):
        pass

    def __eq__(self, o):
        return o is not None
