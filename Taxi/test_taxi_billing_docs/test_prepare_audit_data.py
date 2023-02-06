import datetime

from taxi.billing.util import dates as billing_dates


def test_datetime():
    pit = datetime.datetime(2019, 9, 7)
    pit_ms = billing_dates.microseconds_from_timestamp(pit)
    group = pit_ms // 3600_000_000
    print(pit)
    print(pit_ms)
    print(group)


def test_pg_compare():
    # "2019-09-08 04:31:10.30864" -> 1567917070308640
    pit = datetime.datetime(2019, 9, 8, 4, 31, 10, 308640)
    pit_ms = billing_dates.microseconds_from_timestamp(pit)
    print(pit)
    print(pit_ms)
    print(pit_ms == 1567917070308640)


if __name__ == '__main__':
    test_datetime()
    test_pg_compare()
