from datetime import timedelta

from nile.api.v1 import Record

from dmp_suite import datetime_utils as dtu

EFFECTIVE_DATETIME = dtu.parse_datetime('2017-05-02')
EFFECTIVE_START_DATETIME = dtu.parse_datetime('2017-01-01')
NEXT_EFFECTIVE_DATETIME = EFFECTIVE_DATETIME + timedelta(seconds=1)

# Test new only
new_only_records = [
    Record(
        a=1,
        b=2,
        c=None,
        d=None,
    )
]

new_only_expected = [
    Record(
        a=1,
        b=2,
        c=None,
        d=None,
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        effective_from_dttm=dtu.MIN_DATETIME_STRING,
        deleted_flg=False
    )
]

# Test old only
old_only_records_1 = [
    Record(
        a=2,
        b=2,
        c=None,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=True
    )
]
old_only_expected_1 = [
    Record(
        a=2,
        b=2,
        c=None,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=True
    )
]

old_only_records_2 = [
    Record(
        a=3,
        b=2,
        c=None,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    )
]
old_only_expected_2 = [
    Record(
        a=3,
        b=2,
        c=None,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.format_datetime(EFFECTIVE_DATETIME),
        deleted_flg=False
    ),
    Record(
        a=3,
        b=2,
        c=None,
        d=None,
        effective_from_dttm=dtu.format_datetime(NEXT_EFFECTIVE_DATETIME),
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=True
    )
]

# Test change NEW
change_new_records = [
    Record(
        a=4,
        b=2,
        c=None,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    ),
    Record(
        a=4,
        b=3,
        c=None,
        d=None,
    )
]

change_new_expected = [
    Record(
        a=4,
        b=2,
        c=None,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.format_datetime(EFFECTIVE_DATETIME),
        deleted_flg=False
    ),
    Record(
        a=4,
        b=3,
        c=None,
        d=None,
        effective_from_dttm=dtu.format_datetime(NEXT_EFFECTIVE_DATETIME),
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    )
]

# Test change UPDATE
change_update_records = [
    Record(
        a=5,
        b=2,
        c=1,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    ),
    Record(
        a=5,
        b=2,
        c=2,
        d=None,
    )
]
change_update_expected = [
    Record(
        a=5,
        b=2,
        c=2,
        d=None,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    )
]

# Test change IGNORE
change_ignore_records = [
    Record(
        a=6,
        b=2,
        c=2,
        d=1,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    ),
    Record(
        a=6,
        b=2,
        c=2,
        d=2,
    )
]
change_ignore_expected = [
    Record(
        a=6,
        b=2,
        c=2,
        d=1,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    )
]

# Test change IGNORE for a previously deleted record.
change_ignore_undeleted_records = [
    Record(
        a=7,
        b=2,
        c=2,
        d=1,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=True
    ),
    Record(
        a=7,
        b=2,
        c=2,
        d=2,
    )
]
change_ignore_undeleted_expected = [
    Record(
        a=7,
        b=2,
        c=2,
        d=1,
        effective_from_dttm='2017-05-01 00:00:00',
        effective_to_dttm=dtu.format_datetime(EFFECTIVE_DATETIME),
        deleted_flg=True
    ),
    Record(
        a=7,
        b=2,
        c=2,
        d=2,
        effective_from_dttm=dtu.format_datetime(NEXT_EFFECTIVE_DATETIME),
        effective_to_dttm=dtu.MAX_DATETIME_STRING,
        deleted_flg=False
    )
]

old_history = [
    Record(
        a=10,
        b=10,
        c=10,
        d=10,
        effective_to_dttm='2017-01-01 10:01:01',
        deleted_flg=True,
        effective_from_dttm='2017-01-01 01:01:01',
    )
]
