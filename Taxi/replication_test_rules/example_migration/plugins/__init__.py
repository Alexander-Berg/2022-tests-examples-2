import datetime

from replication_core.mapping import exceptions
from taxi.util import dates


def to_int_or_none(value):
    if value is None:
        return None
    if not isinstance(value, (float, int)) or abs(value - int(value)) > 0:
        raise exceptions.CastError(
            'Value {!r} is not an integer'.format(value),
        )
    return int(value)


def _dummy(value):
    return value


def _traverse_and_cast(value):
    if isinstance(value, list):
        cast_list = [_traverse_and_cast(subvalue) for subvalue in value]
        return cast_list
    if isinstance(value, dict):
        cast_dict = {
            _traverse_and_cast(subkey): _traverse_and_cast(subvalue)
            for subkey, subvalue in value.items()
        }
        return cast_dict
    if isinstance(value, datetime.datetime):
        return dates.timestamp_us(value)
    return value


def _upload_time(doc):
    return dates.timestamp_us(datetime.datetime.utcnow())


CAST = {
    'example_to_int_or_none': to_int_or_none,
    'example_to_yson_or_none': _dummy,
    'example_to_yson_safely': _traverse_and_cast,
}
INPUT_TRANSFORM = {'example_upload_time': _upload_time}
