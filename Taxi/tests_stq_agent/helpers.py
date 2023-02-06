import datetime

import dateutil.parser

from tests_plugins import utils

FAR_FUTURE_TIMESTAMP = 16725225600.0
STQ_TASKS_EXECUTION_TIMEOUT = 60
ABANDONED_TIMEOUT = 20
FAILS_COUNT_THRESHOLD = 4

_EPOCH = datetime.datetime.utcfromtimestamp(0)


def to_timestamp(time_point):
    if isinstance(time_point, str):
        time_point = utils.to_utc(dateutil.parser.parse(time_point))
    return (time_point - _EPOCH).total_seconds()
