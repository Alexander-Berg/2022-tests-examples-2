import datetime
import pytest

import dateutil.tz as tz

from sandbox.projects.common import time_utils


@pytest.fixture
def datetime_object_with_utc_tz():
    return datetime.datetime(
        year=2021,
        month=1,
        day=1,
        hour=1,
        minute=1,
        second=1,
        microsecond=111111,
        tzinfo=tz.tzutc(),
    )


@pytest.fixture
def datetime_object_with_utc_tz__iso_str_with_z():
    return "2021-01-01T01:01:01.111111Z"


@pytest.fixture
def datetime_object_with_utc_tz__iso_str_with_numerical_offset():
    return "2021-01-01T01:01:01.111111+00:00"


def test__datetime_to_iso__force_z(
    datetime_object_with_utc_tz,
    datetime_object_with_utc_tz__iso_str_with_z,
):

    result_iso_dt = time_utils.datetime_to_iso(datetime_object_with_utc_tz, force_z=True)

    assert result_iso_dt == datetime_object_with_utc_tz__iso_str_with_z


def test__datetime_to_iso__no_force(
    datetime_object_with_utc_tz,
    datetime_object_with_utc_tz__iso_str_with_numerical_offset,
):

    result_iso_dt = time_utils.datetime_to_iso(datetime_object_with_utc_tz, force_z=False)

    assert result_iso_dt == datetime_object_with_utc_tz__iso_str_with_numerical_offset


def test__datetime_utc():
    now = time_utils.datetime_utc()

    assert now.tzinfo is not None
    assert now.tzinfo == tz.UTC


@pytest.mark.parametrize(
    "datetime_str,expected_timestamp", [
        ("2021-07-26T14:17:47.014346+00:00", 1627309067),  # ISO format
        ("2021-07-26T14:17:47.014346+0000", 1627309067),  # Startrek issue time format
        ("2021-07-26T14:17:47+00:00", 1627309067),  # ISO with integer seconds (RMDEV-2416, RMDEV-1999)
        ("2021-07-26T14:17:47.014346Z", 1627309067),  # ISO with Z for timezone
        ("2021-07-26T14:17:47Z", 1627309067),  # ISO with Z for timezone and integer seconds (RMDEV-2416, RMDEV-1999)
        ("2021-07-26T17:17:47.014346+03:00", 1627309067),  # ISO with non-zero timezone
        ("2021-07-26T14:17:47.014346", 1627309067),  # ISO with no timezone (assume UTC)
        ("26.07.2021 14:17:47.014346 +00:00", 1627309067),  # human
        ("26.07.2021 17:17:47.014346 +03:00", 1627309067),  # human with non-zero timezone
        ("26 Jul 2021 14:17:47 UTC", 1627309067),  # insane
    ]
)
def test__to_unixtime(datetime_str, expected_timestamp):

    f_name = "to_unixtime"

    result = time_utils.to_unixtime(datetime_str)

    call_str = "{name}('{arg}') = {result}".format(
        name=f_name,
        arg=datetime_str,
        result=result,
    )

    assert result, "{} - empty result".format(call_str)
    assert isinstance(result, int), "{} - unexpected type {}".format(call_str, type(result))
    assert result == expected_timestamp, "{} != {} (expected value)".format(call_str, expected_timestamp)
