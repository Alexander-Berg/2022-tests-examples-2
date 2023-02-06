# coding: utf-8
from taxi_etl.layer.yt.ods.mdb.childchair_rent_transaction.loader import get_vat_value


def test_get_vat_value():
    assert get_vat_value(dict()) is None
    assert get_vat_value(dict(cur_rent=10)) is None
    assert 5 == get_vat_value(dict(cur_rent='10', cur_without_vat='5'))
    assert 0.5 == get_vat_value(dict(cur_rent=1, cur_without_vat=0.5))
