import datetime

import pytz

EPOCH = datetime.datetime.utcfromtimestamp(0)


def timestamp(stamp):
    return (stamp - EPOCH).total_seconds()


def to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.utc).replace(tzinfo=None)
    return stamp
