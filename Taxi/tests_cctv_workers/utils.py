import datetime

from dateutil import parser
import pytz


def parse_date_str(date_str):
    return parser.parse(date_str).astimezone(pytz.UTC)


def date_str_to_sec(date_str):
    return int(parse_date_str(date_str).timestamp())


def date_from_ms(stamp):
    return datetime.datetime.fromtimestamp(stamp / 1000.0, pytz.UTC)
