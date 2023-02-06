from collections import namedtuple
from os import environ
from demand_etl.layer.yt.ods.msdata.opk_plus_hist.impl import reduce_opk

OpkRecord = namedtuple('OpkRecord', [
    'yandex_uid',
    'field_dt',
    'days_of_active_number'
])


def test_reduce_opk():
    environ['END_DATE'] = '2021-11-13'

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-01-02', 2),
        OpkRecord(b'1', b'2021-01-03', 1),
        OpkRecord(b'1', b'2021-01-04', 0),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-01-02', 'msk_end_date': b'2021-01-04'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-01-05', 'msk_end_date': b'2021-11-13'}
           ]

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-05-06', 30),
        OpkRecord(b'1', b'2021-05-07', 0),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-05-06', 'msk_end_date': b'2021-05-07'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-05-08', 'msk_end_date': b'2021-11-13'}
           ]

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-10-11', 3),
        OpkRecord(b'1', b'2021-10-12', 11),
        OpkRecord(b'1', b'2021-10-13', 10),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-10-11', 'msk_end_date': b'2021-10-13'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-10-14', 'msk_end_date': b'2021-11-13'}
           ]

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-03-11', 1),
        OpkRecord(b'1', b'2021-03-12', 0),
        OpkRecord(b'1', b'2021-10-11', 10),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-03-11', 'msk_end_date': b'2021-03-12'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-03-13', 'msk_end_date': b'2021-10-10'},
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-10-11', 'msk_end_date': b'2021-10-11'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-10-12', 'msk_end_date': b'2021-11-13'}
           ]

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-11-12', 15),
        OpkRecord(b'1', b'2021-11-13', 14),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-11-12', 'msk_end_date': b'2021-11-27'}
           ]

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-11-12', 15),
        OpkRecord(b'1', b'2021-11-13', -1),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-11-12', 'msk_end_date': b'2021-11-13'}
           ]

    assert list(reduce_opk(b'1', [
        OpkRecord(b'1', b'2021-10-01', -3),
        OpkRecord(b'1', b'2021-10-02', -4),
        OpkRecord(b'1', b'2021-10-20', 10),
        OpkRecord(b'1', b'2021-10-21', -4),
    ])) == [
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-10-01', 'msk_end_date': b'2021-10-02'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-10-03', 'msk_end_date': b'2021-10-19'},
               {'yandex_uid': b'1', 'plus_flg': True, 'msk_start_date': b'2021-10-20', 'msk_end_date': b'2021-10-21'},
               {'yandex_uid': b'1', 'plus_flg': False, 'msk_start_date': b'2021-10-22', 'msk_end_date': b'2021-11-13'}
           ]
