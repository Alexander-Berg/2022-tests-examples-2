import datetime
from typing import List
from typing import Optional


_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
_START_EPOCH = datetime.datetime.strptime(
    '1970-01-01T00:00:00+0000', _TIMESTAMP_FORMAT,
)


class WearinessConfig:
    def __init__(
            self,
            long_rest_m: int,
            max_no_rest_m: int,
            max_work_m: int,
            working_statuses: Optional[List[str]] = None,
            working_order_statuses: Optional[List[str]] = None,
    ):
        self.long_rest_m = long_rest_m
        self.max_no_rest_m = max_no_rest_m
        self.max_work_m = max_work_m
        self.working_statuses = working_statuses or ['online', 'busy']
        self.working_order_statuses = working_order_statuses or [
            'driving',
            'waiting',
            'transporting',
        ]


def add_experiment(experiments3, config: WearinessConfig):
    experiments3.add_config(
        consumers=['driver-weariness'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='driver_weariness_bounds',
        default_value={
            'max_work_m': config.max_work_m,
            'long_rest_m': config.long_rest_m,
            'max_no_rest_m': config.max_no_rest_m,
            'working_statuses': config.working_statuses,
            'working_order_statuses': config.working_order_statuses,
        },
    )


def insert_range(
        dbid_uuid: str, begin: datetime.datetime, end: datetime.datetime,
) -> str:
    return (
        f'INSERT INTO weariness.working_ranges '
        f'(park_driver_profile_id, range_begin, range_end)'
        f' VALUES '
        f'(\'{dbid_uuid}\', \'{begin.isoformat()}\', \'{end.isoformat()}\')'
    )


async def activate_task(
        taxi_driver_weariness, task_name: str, response_code: int = 200,
):
    response = await taxi_driver_weariness.post(
        'service/cron', {'task_name': task_name},
    )
    assert response.status_code == response_code


def insert_driver(driver_id: int, dbid_uuid: str) -> str:
    return (
        f'INSERT INTO weariness.unique_driver_ids '
        f'VALUES ({driver_id}, \'{dbid_uuid}\')'
    )


def insert_coordinate(
        driver_id: int, lon: float, lat: float, updated: datetime.datetime,
) -> str:
    return (
        f'INSERT INTO weariness.driver_order_coords '
        f'VALUES ({driver_id}, {lon}, {lat}, \'{updated}\')'
    )


def select_working_ranges(db, profiles=None):
    where = ''
    if profiles:
        profile_list = ['\'' + profile + '\'' for profile in profiles]
        where = (
            ' WHERE park_driver_profile_id IN (' + ','.join(profile_list) + ')'
        )

    cursor = db.cursor()
    cursor.execute(
        'SELECT park_driver_profile_id, range_begin, range_end '
        'FROM weariness.working_ranges ' + where,
    )

    ranges = {}
    for row in cursor:
        profile = row[0]
        range_begin = row[1].strftime(_TIMESTAMP_FORMAT)
        range_end = row[2].strftime(_TIMESTAMP_FORMAT)
        ranges.setdefault(profile, dict())[range_begin] = range_end

    return ranges


def select_whitelist(db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT unique_driver_id, author, ttl'
        ' FROM weariness.whitelist'
        ' ORDER BY unique_driver_id',
    )

    whitelist = []
    for row in cursor:
        whitelist.append(
            {
                'unique_driver_id': row[0],
                'author': row[1],
                'ttl': row[2].isoformat() + '+0000',
            },
        )
    return whitelist


def str_to_sec(datetime_str):
    timestamp = datetime.datetime.strptime(datetime_str, _TIMESTAMP_FORMAT)
    unix_timestamp = (timestamp - _START_EPOCH).total_seconds()
    return unix_timestamp
