from collections import namedtuple
from demand_etl.layer.yt.ods.msdata.subscription_hist.impl import merge_intervals

PlusRecord = namedtuple('PlusRecord', [
    'yandex_uid',
    'utc_valid_from_dttm',
    'utc_valid_to_dttm',
    'plus_flg',
    'state_status_name',
    'declared_state_name'
])


def test_merge_intervals():
    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2021-01-02 00:00:00', b'2021-01-10 00:00:00', True, b'churned', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-02 00:00:00',
                'utc_valid_to_dttm': b'9999-12-31 23:59:59', 'plus_flg': False},
           ]

    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2020-03-10 00:00:00', b'2020-07-15 00:00:00', False, b'active', b'premium'),
        PlusRecord(b'1', b'2020-10-12 00:00:00', b'2021-02-10 00:00:00', True, b'churned', b'premium'),
        PlusRecord(b'1', b'2021-01-16 00:00:00', b'2021-12-10 00:00:00', False, b'churned', b'trial'),
        PlusRecord(b'1', b'2021-04-12 00:00:00', b'2021-05-10 00:00:00', True, b'active', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2020-03-10 00:00:00',
                'utc_valid_to_dttm': b'2021-04-11 23:59:59', 'plus_flg': False},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-04-12 00:00:00',
                'utc_valid_to_dttm': b'2021-05-10 00:00:00', 'plus_flg': True},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-10 00:00:01',
                'utc_valid_to_dttm': b'9999-12-31 23:59:59', 'plus_flg': False},
           ]

    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2021-01-02 00:00:00', b'2021-01-10 00:00:00', True, b'active', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-02 00:00:00',
                'utc_valid_to_dttm': b'2021-01-10 00:00:00', 'plus_flg': True},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-10 00:00:01',
                'utc_valid_to_dttm': b'9999-12-31 23:59:59', 'plus_flg': False},
           ]

    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2021-01-02 00:00:00', b'2021-04-15 00:00:00', True, b'active', b'premium'),
        PlusRecord(b'1', b'2021-02-22 00:00:00', b'2050-12-07 00:00:00', True, b'active', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-02 00:00:00',
                'utc_valid_to_dttm': b'2050-12-07 00:00:00', 'plus_flg': True},
           ]

    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2014-01-12 00:00:00', b'2021-04-15 00:00:00', False, b'active', b'premium'),
        PlusRecord(b'1', b'2015-02-03 00:00:00', b'2017-09-30 00:00:00', True, b'active', b'premium'),
        PlusRecord(b'1', b'2020-10-17 00:00:00', b'2021-06-02 00:00:00', True, b'active', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2014-01-12 00:00:00',
                'utc_valid_to_dttm': b'2015-02-02 23:59:59', 'plus_flg': False},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2015-02-03 00:00:00',
                'utc_valid_to_dttm': b'2017-09-30 00:00:00', 'plus_flg': True},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2017-09-30 00:00:01',
                'utc_valid_to_dttm': b'2020-10-16 23:59:59', 'plus_flg': False},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2020-10-17 00:00:00',
                'utc_valid_to_dttm': b'2021-06-02 00:00:00', 'plus_flg': True},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-06-02 00:00:01',
                'utc_valid_to_dttm': b'9999-12-31 23:59:59', 'plus_flg': False},
           ]

    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2021-08-21 00:00:00', b'2021-08-21 23:59:59', True, b'active', b'premium'),
        PlusRecord(b'1', b'2021-08-22 00:00:00', b'2021-08-22 23:59:59', True, b'active', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-08-21 00:00:00',
                'utc_valid_to_dttm': b'2021-08-22 23:59:59', 'plus_flg': True},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-08-23 00:00:00',
                'utc_valid_to_dttm': b'9999-12-31 23:59:59', 'plus_flg': False},
           ]

    assert list(merge_intervals(b'1', [
        PlusRecord(b'1', b'2021-08-21 00:00:00', b'2021-08-21 23:59:59', False, b'active', b'premium'),
        PlusRecord(b'1', b'2021-08-22 00:00:00', b'2021-08-22 23:59:59', True, b'active', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-08-21 00:00:00',
                'utc_valid_to_dttm': b'2021-08-21 23:59:59', 'plus_flg': False},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-08-22 00:00:00',
                'utc_valid_to_dttm': b'2021-08-22 23:59:59', 'plus_flg': True},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-08-23 00:00:00',
                'utc_valid_to_dttm': b'9999-12-31 23:59:59', 'plus_flg': False},
           ]
