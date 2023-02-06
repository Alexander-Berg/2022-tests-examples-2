import datetime

from dateutil import parser
from dateutil import tz


def parse_date_str(date_str):
    return parser.parse(date_str).astimezone(tz.tzutc())


def date_to_sec(date_value):
    return int(date_value.timestamp())


def date_to_ms(date_value):
    return int(date_value.timestamp() * 1000)


def date_to_us(date_value):
    return int(date_value.timestamp() * 1000000)


def date_str_to_sec(date_str):
    return date_to_sec(parse_date_str(date_str))


def date_str_to_ms(date_str):
    return date_to_ms(parse_date_str(date_str))


def date_str_to_us(date_str):
    return date_to_us(parse_date_str(date_str))


def date_from_ms(stamp):
    return datetime.datetime.fromtimestamp(stamp / 1000.0, tz.tzutc())


_ORDERS_TZ = tz.gettz('Europe/Moscow')


def with_orders_tz(stamp):
    assert stamp.tzinfo is None
    return stamp.replace(tzinfo=_ORDERS_TZ)
