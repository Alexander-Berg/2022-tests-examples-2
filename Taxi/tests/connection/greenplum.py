# coding: utf-8
import pytest

from connection.greenplum import connection


def convert_msk_to_utc(literal_timestamp):
    sql = """
      select ('{literal_timestamp}'::timestamp
               at time zone 'Europe/Moscow'
               at time zone 'UTC')::text
                 as value
    """.format(literal_timestamp=literal_timestamp)
    return next(connection.query(sql))["value"]


@pytest.mark.slow
def test_msk_to_utc():
    # We lived in UTC+3 in 2018.
    assert convert_msk_to_utc("2018-08-01 10:00:00") == "2018-08-01 07:00:00"
    assert convert_msk_to_utc("2018-02-01 10:00:00") == "2018-02-01 07:00:00"
    # We lived in UTC+4 in 2014.
    assert convert_msk_to_utc("2014-08-01 10:00:00") == "2014-08-01 06:00:00"
    assert convert_msk_to_utc("2014-02-01 10:00:00") == "2014-02-01 06:00:00"
    # We lived with DST in 2010.
    assert convert_msk_to_utc("2010-08-01 10:00:00") == "2010-08-01 06:00:00"
    assert convert_msk_to_utc("2010-02-01 10:00:00") == "2010-02-01 07:00:00"
