# pylint: disable=missing-docstring,invalid-name,redefined-outer-name

"""Functions for dates transform"""
import calendar
import datetime
import re
import typing

from dateutil import parser as dateparser
from dateutil import tz
import pytz

EPOCH = datetime.datetime.utcfromtimestamp(0)
WEEKDAY_TANKER_KEYS = {
    0: 'weekday.monday',
    1: 'weekday.tuesday',
    2: 'weekday.wednesday',
    3: 'weekday.thursday',
    4: 'weekday.friday',
    5: 'weekday.saturday',
    6: 'weekday.sunday',
}
_DURATION_STR_PATTERN = re.compile(
    r'(?:(?P<days>\d+)d)?'
    r'(?:(?P<hours>\d+)h)?'
    r'(?:(?P<minutes>\d+)m)?'
    r'(?:(?P<seconds>\d+)s)?',
)


_now_stamp: typing.Optional[datetime.datetime] = None


def utcnow() -> datetime.datetime:
    if _now_stamp is not None:
        return _now_stamp
    return datetime.datetime.utcnow()


def timestamp(stamp, timezone='Europe/Moscow', milli=False):
    """
    Return UNIX timestmap
    :param stamp: datetime
    :param timezone: timezone from pytz
    :param milli: if True function return timestamp with milliseconds
    :return: UNIX timestamp
    """
    return calendar.timegm(localize(stamp, timezone=timezone).timetuple()) * (
        1000 if milli else 1
    )


def localize(stamp=None, timezone='Europe/Moscow'):
    """
    localize timestamp
    :param stamp: datetime
    :param timezone: timezone from pytz
    :return:
    """
    if stamp is None:
        stamp = utcnow()
    elif not isinstance(stamp, datetime.datetime):  # datetime.date
        stamp = datetime.datetime(stamp.year, stamp.month, stamp.day)

    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=pytz.utc)

    return stamp.astimezone(pytz.timezone(timezone))


def timestring(
        stamp=None,
        timezone='Europe/Moscow',
        time_format='%Y-%m-%dT%H:%M:%S%z',
):
    """Format timestamp to string with given format

    :param stamp: datetime (если naive, то считается, что это UTC!)
    :param timezone: timezone
    :param format: format for timestamp
    :return: string with time
    """
    return localize(stamp=stamp, timezone=timezone).strftime(time_format)


def parse_timestring(time_string, timezone='Europe/Moscow'):
    """Parse timestring into naive UTC

    :param time_string: in ISO-8601 format
    :param timezone: if time_string contains no timezone, this argument is used
    :return: naive time in UTC
    """
    time = dateparser.parse(time_string)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    utctime = time.astimezone(pytz.utc).replace(tzinfo=None)

    return utctime


def parse_timestring_aware(
        timestring: str, timezone: str = 'Europe/Moscow',
) -> datetime.datetime:
    """Parse timestring into aware UTC

    :param timestring: in ISO-8601 format
    :param timezone: if timestring contains no timezone, this argument is used
    :return: aware time in UTC
    """
    time = dateparser.parse(timestring)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    utctime = time.astimezone(pytz.utc)

    return utctime


def timestring_to_iso(timestring: str):
    """Parse timestring into json-compatible ISO-8601 format

    :param timestring
    :return: time string in json-compatible ISO-8601 format
    """
    time = dateparser.parse(timestring)
    if time.tzinfo is None:
        time = time.replace(tzinfo=pytz.UTC)
    return time.isoformat()


def parse_duration_string(duration_string):
    """Parse duration string into timedelta object

    :param duration_string: string like 1d2h3m4s
    :return: datetime.timedelta(days=1, hours=2, minutes=3, seconds=4)"""

    if duration_string == '':
        raise ValueError('Cannot parse empty string')

    match = _DURATION_STR_PATTERN.fullmatch(duration_string)

    if match is None:
        raise ValueError('Cannot parse {}'.format(duration_string))

    timedelta_kwargs = {
        k: int(v) for k, v in match.groupdict().items() if v is not None
    }

    return datetime.timedelta(**timedelta_kwargs)


def offset_from_utc(time):
    """
    In terms that UTC + offset = localtime
    :param time: datetime.datetime
    :return: datetime.timedelta
    """
    utctime = time.astimezone(pytz.utc).replace(tzinfo=None)
    localtime = time.replace(tzinfo=None)
    return localtime - utctime


def get_local_datetime(timestamp_unix, timezone):
    """
    Return naive datetime of specified unix timestamp for specified timezone
    :type timestamp_unix: float
    :param timestamp_unix: float
    :type timezone: str
    :param timezone: str
    :rtype: datetime.datetime
    """
    date_time = datetime.datetime.utcfromtimestamp(timestamp_unix)
    return naive_utc_to_naive_tz(date_time, timezone)


def naive_utc_to_naive_tz(stamp, timezone):
    """
    :param stamp: datetime
    :param timezone: str
    :return:
    """
    return localize(stamp, timezone).replace(tzinfo=None)


def naive_tz_to_naive_utc(timestamp, tz='Europe/Moscow'):
    """
    :type timestamp: datetime.datetime
    :type tz: str
    :rtype: datetime.datetime
    """
    return naive_tz_to_aware_utc(timestamp, tz).replace(tzinfo=None)


def naive_tz_to_aware_utc(timestamp, tz='Europe/Moscow'):
    """
    :type timestamp: datetime.datetime
    :type tz: str
    :rtype: datetime.datetime
    """
    tz_obj = pytz.timezone(tz)
    return tz_obj.localize(timestamp).astimezone(pytz.utc)


def naive_utc_to_aware_utc(stamp: datetime.datetime):
    """
    :param stamp: datetime.datetime tz naive object in utc
    :return: datetime.datetime tz aware object in utc
    """
    return stamp.replace(tzinfo=pytz.utc)


def naive_utc_to_aware_utc_or_none(stamp):
    if stamp is None:
        return None
    return naive_utc_to_aware_utc(stamp)


def aware_to_naive_utc(stamp: datetime.datetime):
    return stamp.astimezone(pytz.utc).replace(tzinfo=None)


def timestamp_us(stamp):
    """Convert datetime object to unix timestamp with microseconds.
    """
    return (to_utc(stamp) - EPOCH).total_seconds()


def to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.utc).replace(tzinfo=None)
    return stamp


def to_utc_or_none(stamp):
    if stamp is None:
        return None
    return to_utc(stamp)


def relative_mins(from_datetime, to_datetime):
    secs_delta = (to_datetime - from_datetime).total_seconds()
    return secs_to_min(secs_delta)


def secs_to_min(secs):
    # done alike in mobile clients to unify output
    return int(secs / 60)


def day_start(dt, utc_offset: str = None):
    """
    :param dt: datetime
    :param utc_offset: string
    :return: naive time
    """
    if utc_offset:
        tz_offset = tz.gettz(f'UTC{utc_offset}')
        dt = dt.astimezone(tz=tz_offset)
    return dt.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def day_end(date):
    """
    :param stamp: date
    :return: datetime in utc
    """
    return datetime.datetime.combine(date, datetime.datetime.max.time())


def today_start(dt=None, timezone='Europe/Moscow'):
    """Return today's start datetime
    """
    return day_start(localize(dt, timezone=timezone))


def tomorrow_start(dt=None, timezone='Europe/Moscow'):
    return today_start(dt, timezone=timezone) + datetime.timedelta(days=1)


def this_month_start(dt=None, timezone='Europe/Moscow'):
    """Return datetime for start of this month
    """
    dt = localize(dt, timezone=timezone)

    # localize again, since tz of `dt` may differ from tz of month start
    month_start = localize(
        datetime.datetime(dt.year, dt.month, 1), timezone=timezone,
    )
    # some day we'll need this hack for western timezones (-XX00)
    if month_start.day != 1:
        month_start += datetime.timedelta(days=1)
    return month_start.replace(hour=0, minute=0, second=0, microsecond=0)


def last_month_start(utc_offset: str = None):
    """
    :return: datetime in utc
    """
    tz_offset = None
    if utc_offset:
        tz_offset = tz.gettz(f'UTC{utc_offset}')
    now = datetime.datetime.now(tz=tz_offset)
    return day_start(
        (now.replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
    )


def last_month_end(utc_offset: str = None):
    """
    :return: datetime in utc
    """
    tz_offset = None
    if utc_offset:
        tz_offset = tz.gettz(f'UTC{utc_offset}')
    now = datetime.datetime.now(tz=tz_offset)
    return day_end(now.replace(day=1) - datetime.timedelta(days=1))


def weekday_tanker(date):
    """Return a formatted week day name"""
    return WEEKDAY_TANKER_KEYS[date.weekday()]


def weekday_short_tanker(date: datetime.datetime) -> str:
    """Return tanker key for short week day name"""
    return f'helpers.weekday_{date.weekday() + 1}_short'


def expired_from(
        date: datetime.datetime,
        now: typing.Optional[datetime.datetime] = None,
        **timedelta_kwargs,
) -> bool:
    """Return `True` if long time from `date` to `now`.

    >>> now = datetime.datetime.utcnow()
    >>> date = now - datetime.timedelta(seconds=2)
    >>> expired_from(date, now=now, seconds=1)
    True
    >>> expired_from(date, now=now, seconds=3)
    False
    """
    if now is None:
        now = datetime.datetime.utcnow()
    return now > date + datetime.timedelta(**timedelta_kwargs)


def _set_now_stamp(stamp: typing.Optional[datetime.datetime] = None):
    global _now_stamp  # pylint: disable=global-statement
    _now_stamp = stamp


def divide_without_reminder(
        date: datetime.datetime, delta: datetime.timedelta,
) -> datetime.datetime:
    """
    >>> divide_without_reminder(
    ...     datetime.datetime(2019, 8, 30, 12, 16, 30, 99),
    ...     datetime.timedelta(hours=1),
    ... )
    datetime.datetime(2019, 8, 30, 12, 0)
    """
    delta_seconds = delta.total_seconds()
    naive_timestamp = (
        date.replace(tzinfo=pytz.utc).timestamp()
        // delta_seconds
        * delta_seconds
    )
    naive_datetime = datetime.datetime.utcfromtimestamp(naive_timestamp)
    return naive_datetime.replace(tzinfo=date.tzinfo)


def is_aware(date: datetime.datetime) -> bool:
    return date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None


def is_naive(date: datetime.datetime) -> bool:
    return not is_aware(date)


def utc_with_tz() -> datetime.datetime:
    """ Return datetime with tz in utc."""
    return naive_utc_to_aware_utc(utcnow())


def unix_utc_to_datetime_with_tz(timestamp_unix: int) -> datetime.datetime:
    """ Convert unix utc timestamp in current local datetime with tz."""
    return naive_utc_to_aware_utc(
        datetime.datetime.utcfromtimestamp(timestamp_unix),
    )


def unix_utc_timestamp() -> int:
    """ Returns unix timestamp in seconds in UTC."""
    return int(timestamp_us(utc_with_tz()))
