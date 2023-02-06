import datetime
import json
import typing as tp

from dateutil import parser as dateparser
import pytz


EVENT_FIELDS = [
    'id',
    'type',
    'polygon_id',
    'occured_at',
    'extra',
    'location',
    'iteration',
    'region',
    'version',
]

ITERATIONS_FIELDS = [
    'id',
    'region',
    'created_at',
    'scooters_to_relocate',
    'parking_places_to_dropoff',
]


def _merge_tuple_with_fields(fields, db_tuple) -> dict:
    assert len(fields) == len(db_tuple), f'{len(fields)} != {len(db_tuple)}'
    return dict(zip(fields, db_tuple))


def _create_query_param(name: str, casts: dict = None) -> str:
    casts = casts or {}
    if name not in casts:
        return '%s'
    return casts[name]()


def _get_insert_query_with_args(
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
    INSERT INTO scooters_ops_relocation.{table} (
        {','.join(keys)}
    )
    VALUES (
        {','.join(_create_query_param(name, casts) for name in keys)}
    )
    RETURNING {','.join(fields)}
    """

    return query, args


def get_events(pgsql, *, fields=None):
    fields = fields or EVENT_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops_relocation.events
    WHERE
        TRUE
    ORDER BY id ASC
    """

    cursor = pgsql['scooters_ops_relocation'].cursor()
    cursor.execute(sql)

    return [_merge_tuple_with_fields(fields, row) for row in cursor.fetchall()]


def add_event(pgsql, event: dict):
    if 'extra' in event:
        event['extra'] = json.dumps(event['extra'])

    cursor = pgsql['scooters_ops_relocation'].cursor()
    query, args = _get_insert_query_with_args(
        event,
        'events',
        EVENT_FIELDS,
        required=['id', 'type', 'occured_at', 'location'],
        casts={'location': lambda: 'CAST(\'%s\' AS POINT)'},
    )
    cursor.execute(query, args)

    return _merge_tuple_with_fields(EVENT_FIELDS, cursor.fetchone())


def get_iterations(pgsql, *, fields=None):
    fields = fields or ITERATIONS_FIELDS

    sql = f"""
    SELECT
        {','.join(fields)}
    FROM
        scooters_ops_relocation.iterations
    WHERE
        TRUE
    ORDER BY id ASC
    """

    cursor = pgsql['scooters_ops_relocation'].cursor()
    cursor.execute(sql)

    return [_merge_tuple_with_fields(fields, row) for row in cursor.fetchall()]


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
