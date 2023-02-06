import datetime

import dateutil.parser


def parse_timestamp(value: str) -> datetime.datetime:
    return dateutil.parser.parse(value)
