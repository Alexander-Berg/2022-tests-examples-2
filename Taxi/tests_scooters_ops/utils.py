import datetime

from dateutil import parser as dateparser
import pytz


class AnyValue:
    def __init__(self):
        pass

    def __eq__(self, o):
        return True


class AnyNotNoneValue:
    def __init__(self):
        pass

    def __eq__(self, o):
        return o is not None


def extra_item_type_by_job_type(job_type):
    return 'accumulators' if job_type == 'pickup_batteries' else 'cells'


def init_ui_status_by_job_type(job_type):
    return 'booked' if job_type == 'pickup_batteries' else 'pickuped'


def success_booking_status_by_job_type(
        job_type,
):  # pylint: disable=invalid-name
    return 'pickuped' if job_type == 'pickup_batteries' else 'returned'


def assert_partial_diff(test, expected, path=''):
    assert isinstance(test, type(expected)) or isinstance(
        expected, AnyValue,
    ), (
        f'Types of arguments must be equal. {type(test)} != {type(expected)}. '
        f'Path: {path}'
    )
    if isinstance(expected, dict):
        for key in expected:
            assert key in test, f'Key "{key}" not test by path "{path}"'
            assert_partial_diff(test[key], expected[key], path + f'[{key}]')
    elif isinstance(expected, (list, tuple)):
        assert len(test) >= len(
            expected,
        ), f'length mismatch: {test}, {expected}'
        for i, value in enumerate(expected):
            assert_partial_diff(test[i], value, path + f'[{i}]')
    else:
        assert test == expected, f'"{test}" != "{expected}". Path: {path}'


def parse_timestring_aware(
        timestring: str, timezone: str = 'Europe/Moscow',
) -> datetime.datetime:
    time = dateparser.parse(timestring)
    if time.tzinfo is None:
        time = pytz.timezone(timezone).localize(time)
    utctime = time.astimezone(pytz.utc)
    return utctime
