from collections import namedtuple
from demand_etl.layer.yt.ods.msdata.user_declared_state.impl import merge_states

StatusRecord = namedtuple('StatusRecord', [
    'yandex_uid',
    'utc_valid_from_dttm',
    'utc_valid_to_dttm',
    'declared_state_name'
])


def test_merge_states():
    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-01-02 00:00:00', b'2021-01-10 00:00:00', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-02 00:00:00',
                'utc_valid_to_dttm': b'2021-01-10 00:00:00', 'declared_state_name': b'trial'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-01-02 00:00:00', b'2021-01-10 00:00:00', b'trial'),
        StatusRecord(b'1', b'2021-01-07 00:00:00', b'2021-01-14 00:00:00', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-02 00:00:00',
                'utc_valid_to_dttm': b'2021-01-14 00:00:00', 'declared_state_name': b'trial'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-01-02 00:00:00', b'2021-01-10 00:00:00', b'trial'),
        StatusRecord(b'1', b'2021-01-12 00:00:00', b'2021-01-14 00:00:00', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-02 00:00:00',
                'utc_valid_to_dttm': b'2021-01-10 00:00:00', 'declared_state_name': b'trial'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-01-12 00:00:00',
                'utc_valid_to_dttm': b'2021-01-14 00:00:00', 'declared_state_name': b'trial'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-07-01 00:00:00', b'trial'),
        StatusRecord(b'1', b'2021-06-01 00:00:00', b'2021-08-01 00:00:00', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-06-01 00:00:00',
                'utc_valid_to_dttm': b'2021-08-01 00:00:00', 'declared_state_name': b'premium'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-31 23:59:59', 'declared_state_name': b'trial'}
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-07-01 00:00:00', b'premium'),
        StatusRecord(b'1', b'2021-06-01 00:00:00', b'2021-08-01 00:00:00', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-07-01 00:00:00', 'declared_state_name': b'premium'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-07-01 00:00:01',
                'utc_valid_to_dttm': b'2021-08-01 00:00:00', 'declared_state_name': b'trial'}
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-01 23:59:59', b'premium'),
        StatusRecord(b'1', b'2021-05-02 00:00:00', b'2021-05-02 23:59:59', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-01 23:59:59', 'declared_state_name': b'premium'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-02 00:00:00',
                'utc_valid_to_dttm': b'2021-05-02 23:59:59', 'declared_state_name': b'trial'}
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-01 23:59:59', b'premium'),
        StatusRecord(b'1', b'2021-05-02 00:00:00', b'2021-05-02 23:59:59', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-02 23:59:59', 'declared_state_name': b'premium'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-01 23:59:59', b'premium'),
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-01 23:59:59', b'reactivation'),
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-01 23:59:59', b'trial'),
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-01 23:59:59', b'transactional'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-01 23:59:59', 'declared_state_name': b'reactivation'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-10 00:00:00', b'premium'),
        StatusRecord(b'1', b'2021-05-05 00:00:00', b'2021-05-15 00:00:00', b'trial'),
        StatusRecord(b'1', b'2021-05-10 00:00:00', b'2021-05-20 00:00:00', b'premium'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-20 00:00:00', 'declared_state_name': b'premium'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-10 00:00:00', b'trial'),
        StatusRecord(b'1', b'2021-05-05 00:00:00', b'2021-05-15 00:00:00', b'premium'),
        StatusRecord(b'1', b'2021-05-10 00:00:00', b'2021-05-20 00:00:00', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-05 00:00:00',
                'utc_valid_to_dttm': b'2021-05-15 00:00:00', 'declared_state_name': b'premium'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-04 23:59:59', 'declared_state_name': b'trial'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-15 00:00:01',
                'utc_valid_to_dttm': b'2021-05-20 00:00:00', 'declared_state_name': b'trial'},
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2021-05-01 00:00:00', b'2021-05-10 00:00:00', b'premium'),
        StatusRecord(b'1', b'2021-05-05 00:00:00', b'2021-05-15 00:00:00', b'trial'),
        StatusRecord(b'1', b'2021-05-08 00:00:00', b'2021-05-20 00:00:00', b'premium'),
        StatusRecord(b'1', b'2021-05-10 00:00:00', b'2021-05-25 00:00:00', b'trial'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-01 00:00:00',
                'utc_valid_to_dttm': b'2021-05-20 00:00:00', 'declared_state_name': b'premium'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-20 00:00:01',
                'utc_valid_to_dttm': b'2021-05-25 00:00:00', 'declared_state_name': b'trial'}
           ]

    assert list(merge_states(b'1', [
        StatusRecord(b'1', b'2019-09-11 07:00:08', b'2019-12-27 20:59:59', b'trial'),
        StatusRecord(b'1', b'2019-11-27 06:56:24', b'2019-12-27 20:59:59', b'premium'),
        StatusRecord(b'1', b'2021-03-08 00:00:00', b'2021-05-28 23:59:59', b'premium'),
        StatusRecord(b'1', b'2019-12-31 11:50:10', b'2020-02-05 20:59:59', b'reactivation'),
        StatusRecord(b'1', b'2020-06-09 00:00:00', b'2020-07-09 23:59:59', b'reactivation'),
        StatusRecord(b'1', b'2020-10-08 00:00:00', b'2020-11-06 23:59:59', b'reactivation'),
        StatusRecord(b'1', b'2021-02-07 00:00:00', b'2021-03-07 23:59:59', b'reactivation'),
        StatusRecord(b'1', b'2021-05-29 00:00:00', b'2021-09-25 23:59:59', b'reactivation'),
    ])) == [
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2019-12-31 11:50:10',
                'utc_valid_to_dttm': b'2020-02-05 20:59:59', 'declared_state_name': b'reactivation'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2020-06-09 00:00:00',
                'utc_valid_to_dttm': b'2020-07-09 23:59:59', 'declared_state_name': b'reactivation'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2020-10-08 00:00:00',
                'utc_valid_to_dttm': b'2020-11-06 23:59:59', 'declared_state_name': b'reactivation'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-02-07 00:00:00',
                'utc_valid_to_dttm': b'2021-03-07 23:59:59', 'declared_state_name': b'reactivation'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-05-29 00:00:00',
                'utc_valid_to_dttm': b'2021-09-25 23:59:59', 'declared_state_name': b'reactivation'},
                {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2019-11-27 06:56:24',
                 'utc_valid_to_dttm': b'2019-12-27 20:59:59', 'declared_state_name': b'premium'},
                {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2021-03-08 00:00:00',
                 'utc_valid_to_dttm': b'2021-05-28 23:59:59', 'declared_state_name': b'premium'},
               {'yandex_uid': b'1', 'utc_valid_from_dttm': b'2019-09-11 07:00:08',
                'utc_valid_to_dttm': b'2019-11-27 06:56:23', 'declared_state_name': b'trial'}
           ]
