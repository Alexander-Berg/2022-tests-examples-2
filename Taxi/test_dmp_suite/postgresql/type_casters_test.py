# coding: utf-8


from datetime import datetime
import pytz
from dmp_suite.postgresql.type_casters import (
    DATETIME_AS_STR,
    DATETIMETZ_AS_STR,
    DATETIMETZ_AS_UTC_OBJECT,
    DECIMAL_AS_FLOAT
)


# A typecaster has an (object, Cursor) -> object signature.
# A cursor, however, is never used by our casters, so we just pass `None`.
CURSOR = None


def test_datetime_as_str():
    assert (
        DATETIME_AS_STR(None, CURSOR)
        is None
    )
    assert (
        DATETIME_AS_STR("2019-01-01 00:00:00", CURSOR)
        == "2019-01-01 00:00:00.000000"
    )
    assert (
        DATETIME_AS_STR("2019-01-01 00:00:00.123", CURSOR)
        == "2019-01-01 00:00:00.123000"
    )
    assert (
        DATETIME_AS_STR("2019-01-01 00:00:00.123456", CURSOR)
        == "2019-01-01 00:00:00.123456"
    )


def test_datetimetz_as_str():
    assert (
        DATETIMETZ_AS_STR(None, CURSOR)
        is None
    )
    assert (
        DATETIMETZ_AS_STR("2019-01-01 18:47:02", CURSOR)
        == "2019-01-01 18:47:02.000000"
    )
    assert (
        DATETIMETZ_AS_STR("2019-01-01 18:47:02.970613", CURSOR)
        == "2019-01-01 18:47:02.970613"
    )
    assert (
        DATETIMETZ_AS_STR("2019-01-01 18:47:02.970613+03", CURSOR)
        == "2019-01-01 15:47:02.970613"
    )


def test_decimal_as_float():
    assert DECIMAL_AS_FLOAT(None, CURSOR) is None

    assert DECIMAL_AS_FLOAT("123", CURSOR) == 123
    assert isinstance(DECIMAL_AS_FLOAT("123", CURSOR), float)

    assert DECIMAL_AS_FLOAT("-123.5", CURSOR) == -123.5
    assert isinstance(DECIMAL_AS_FLOAT("-123.5", CURSOR), float)


def test_datetimetz_as_utc_object():
    assert DATETIMETZ_AS_UTC_OBJECT(None, CURSOR) is None

    assert DATETIMETZ_AS_UTC_OBJECT(
        "2019-12-12", CURSOR) == datetime(2019, 12, 12, 0, 0, tzinfo=pytz.utc)
    assert isinstance(DATETIMETZ_AS_UTC_OBJECT("2019-12-12", CURSOR), datetime)

    assert DATETIMETZ_AS_UTC_OBJECT(
        "2019-12-12 15:00:00.000000+3", CURSOR) == datetime(
        2019, 12, 12, 12, 0, tzinfo=pytz.utc)
    assert isinstance(DATETIMETZ_AS_UTC_OBJECT(
        "2019-12-12 15:00:00.000000+3", CURSOR), datetime)
