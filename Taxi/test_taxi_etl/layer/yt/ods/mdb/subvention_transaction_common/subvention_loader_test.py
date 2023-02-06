# coding: utf-8
from taxi_etl.layer.yt.ods.mdb.subvention_transaction_common.subvention_detail_loader \
    import _get_details


def test_get_details():
    assert [] == list(_get_details([]))

    test_data = [dict(ri='r1', t='a', v='10'),
                 dict(ri='r1', t='a', v=20),
                 dict(ri='r2', t='a', v=20),
                 dict(ri='r3', v=20),
                 dict(ri='r3', v=30),
                 dict(ri='r4', v=30)]

    expected_data = [('r1', 'a', 30),
                     ('r2', 'a', 20),
                     ('r3', None, 50),
                     ('r4', None, 30)]

    assert expected_data == list(_get_details(test_data))
