import datetime

import dateutil.parser
import pytz


class Timezone:
    UTC = pytz.utc
    MSK = pytz.timezone('Europe/Moscow')


def parse_time(as_str: str, default_tz='UTC') -> datetime.datetime:
    """
    Parses string with time of almost any format to datetime.datetime
    with awared timezone. You can compare returned datetimes between
    each other and don't care about difference in time zones.
    """
    _dt = dateutil.parser.parse(as_str)
    if not _dt.tzinfo:
        utc = pytz.timezone(default_tz)
        _dt = utc.localize(_dt)
    return _dt
