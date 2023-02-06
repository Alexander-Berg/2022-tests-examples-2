import datetime
from enum import Enum
import time


def _sleep(seconds=0.05):
    time.sleep(seconds)


def wait_for_correct(retries=10, period=0.05):
    def wrap_wait_for_correct(func):
        def wrapped(*args, **kwargs):
            for _ in range(retries):
                f = func(*args, **kwargs)
                if f:
                    break
                _sleep(period)
            return f

        return wrapped

    return wrap_wait_for_correct


class Units(Enum):
    DAYS = 0
    MINUTES = 1
    SECONDS = 2
    HOURS = 3
    MILLISECONDS = 4


def to_timestamp(dt, units=Units.SECONDS, divider=1):
    time_delta = datetime.timedelta(seconds=1)
    if units == Units.MINUTES:
        time_delta = datetime.timedelta(minutes=1)
    elif units == Units.HOURS:
        time_delta = datetime.timedelta(hours=1)
    elif units == Units.MILLISECONDS:
        time_delta = datetime.timedelta(milliseconds=1)
    elif units == Units.DAYS:
        time_delta = datetime.timedelta(days=1)

    return int((dt - datetime.datetime(1970, 1, 1)) / time_delta / divider)


def check_dict_is_subdict(dict_, subdict):
    for key, value in subdict.items():
        assert key in dict_
        assert value == dict_[key]
