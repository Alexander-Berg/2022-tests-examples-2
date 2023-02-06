import datetime

import dateutil.parser

from taxi.util import dates

from fleet_drivers_scoring.utils import utils as scoring_utils


def date_parsed(x):
    if isinstance(x, str):
        try:
            return dateutil.parser.isoparse(x)
        except ValueError:
            return x
    if isinstance(x, list):
        return [date_parsed(y) for y in x]
    if isinstance(x, dict):
        return {k: date_parsed(v) for k, v in x.items()}
    return x


def fetch_all_checks(pgsql):
    with pgsql['fleet_drivers_scoring'].cursor() as cursor:
        cursor.execute('select * from fleet_drivers_scoring.checks;')
        return _fetch_dict(cursor)


def fetch_all_yt_updates(pgsql):
    with pgsql['fleet_drivers_scoring'].cursor() as cursor:
        cursor.execute('select * from fleet_drivers_scoring.yt_updates;')
        return _fetch_dict(cursor)


def fetch_all_yt_update_states(pgsql):
    with pgsql['fleet_drivers_scoring'].cursor() as cursor:
        cursor.execute('select * from fleet_drivers_scoring.yt_update_states;')
        return _fetch_dict(cursor)


def fetch_check_part(pgsql, part_id):
    with pgsql['fleet_drivers_scoring'].cursor() as cursor:
        cursor.execute(
            f'select * from fleet_drivers_scoring.check_parts '
            f'where id=\'{part_id}\';',
        )
        result = _fetch_dict(cursor)
    if not result:
        return None

    return result[0]


def fetch_rate_limit(pgsql, clid, period, rate_type):
    with pgsql['fleet_drivers_scoring'].cursor() as cursor:
        if period == scoring_utils.PeriodEnum.DAY.value:
            day = dates.utcnow().date()
        elif period == scoring_utils.PeriodEnum.WEEK.value:
            today = dates.utcnow()
            day = (today + datetime.timedelta(days=-(today.weekday()))).date()
        else:
            raise Exception('Wrong period parameter')
        cursor.execute(
            'SELECT * '
            'FROM fleet_drivers_scoring.rates '
            f'WHERE clid = \'{clid}\' AND '
            f'day = \'{day}\' AND '
            f'period = \'{period}\' AND '
            f'type = \'{rate_type}\'',
        )
        return _fetch_dict(cursor)


def execute_file(pgsql, load, file):
    with pgsql['fleet_drivers_scoring'].cursor() as cursor:
        cursor.execute(load(file))


def _fetch_dict(cursor):
    fields = [column.name for column in cursor.description]
    return [dict(zip(fields, row)) for row in cursor.fetchall()]
