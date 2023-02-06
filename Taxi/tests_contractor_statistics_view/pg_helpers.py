import datetime

import psycopg2


def datetime_from_timestamp(
        timestamp,
        fmt='%Y-%m-%dT%H:%M:%S.%f%z',
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
):
    return datetime.datetime.strptime(timestamp, fmt).replace(tzinfo=tzinfo)
