from replication_core import transform
from replication_core.mapping import exceptions
from taxi.util import dates

from replication.custom_models import testsuite_plugins


@transform.castfunction
def datetime_to_double(value):
    return dates.timestamp_us(value)


@transform.castfunction
def datetime_to_int(value):
    return int(dates.timestamp_us(value))


def int_to_string(value):
    return str(value)


def to_yson_or_none(value):
    return value


def decimal_to_x6_int(value):
    return int(value * 10 ** 6)


@transform.castfunction
def to_int_or_none(value):
    if not isinstance(value, (float, int)) or abs(value - int(value)) > 0:
        raise exceptions.CastError(
            'Value {!r} is not an integer'.format(value),
        )
    return int(value)


CAST = {
    'datetime_to_double': datetime_to_double,
    'datetime_to_int': datetime_to_int,
    'int_to_string': int_to_string,
    'to_yson_or_none': to_yson_or_none,
    'decimal_to_x6_int': decimal_to_x6_int,
    'to_int_or_none': to_int_or_none,
}
INPUT_TRANSFORM = testsuite_plugins.INPUT_TRANSFORM
