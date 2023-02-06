import datetime

import pytz


def to_timestring(stamp=None):
    if stamp is None:
        stamp = datetime.datetime.utcnow()
    if stamp.tzinfo is None:
        stamp = datetime.datetime(*stamp.utctimetuple()[:6], tzinfo=pytz.utc)
    return stamp.strftime('%Y-%m-%dT%H:%M:%S%z')
