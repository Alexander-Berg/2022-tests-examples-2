from datetime import datetime

from dmp_suite.yt.migration.utils import parse_yt_datetime_attr, format_yt_datetime_attr


def test_to_parse_yt_datetime_attr():
    dttm_expected = datetime(1997, 5, 31)

    date_string = format_yt_datetime_attr(dttm_expected)
    assert isinstance(date_string, str)

    dttm = parse_yt_datetime_attr(date_string)
    assert dttm == dttm_expected


def test_from_format_yt_datetime_attr():
    date_string_expected = '2021-09-22T11:42:40.457373Z'

    dttm = parse_yt_datetime_attr(date_string_expected)
    assert isinstance(dttm, datetime)

    date_string_actual = format_yt_datetime_attr(dttm)
    assert date_string_actual == date_string_expected
