# coding: utf-8

from taxi_etl.layer.yt.ods.mdb.commission_transaction import loader


def test_get_commission_discount_value_wo_vat():
    doc = dict(commission_discount=1)
    assert 1 == loader.get_commission_discount_value_wo_vat(doc)

    doc = dict(cvwd=2, cv=1)
    assert 1 == loader.get_commission_discount_value_wo_vat(doc)

    doc = dict(cvwd=2, cv=2)
    assert 0 == loader.get_commission_discount_value_wo_vat(doc)

    doc = dict(commission_discount='3', cvwd='2', cv='1')
    assert 3 == loader.get_commission_discount_value_wo_vat(doc)

    doc = dict(cv=2)
    assert loader.get_commission_discount_value_wo_vat(doc) is None


def test_get_commission_discount_value_wo_vat_ccy():
    doc = dict()
    assert loader.get_commission_discount_value_wo_vat_ccy(doc) is None

    doc = dict(cc_cvwd=2, cc_cv=1)
    assert 1 == loader.get_commission_discount_value_wo_vat_ccy(doc)

    doc = dict(cc_cvwd='2', cc_cv='2')
    assert 0 == loader.get_commission_discount_value_wo_vat_ccy(doc)

    doc = dict(cc_cv=1)
    assert loader.get_commission_discount_value_wo_vat_ccy(doc) is None


def test_get_unrealized_commission_discount_value_wo_vat():
    doc = dict()
    assert loader.get_unrealized_commission_discount_value_wo_vat(doc) is None

    doc = dict(unrealized_commission_without_discount=2,
               unrealized_commission=1)
    assert 1 == loader.get_unrealized_commission_discount_value_wo_vat(doc)

    doc = dict(unrealized_commission_without_discount='2',
               unrealized_commission='2')
    assert 0 == loader.get_unrealized_commission_discount_value_wo_vat(doc)

    doc = dict(unrealized_commission=1)
    assert loader.get_unrealized_commission_discount_value_wo_vat(doc) is None


def test_get_commission_discount_rate():
    doc = dict()
    assert loader.get_commission_discount_rate(doc) is None

    doc = dict(cos='10')
    assert loader.get_commission_discount_rate(doc) is None

    doc = dict(cv='10')
    assert loader.get_commission_discount_rate(doc) is None

    doc = dict(cos=10, cv='1')
    assert loader.get_commission_discount_rate(doc) is None

    doc = dict(cos=10, cv=1, commission_discount='0.5')
    assert 0.5 / 10 == loader.get_commission_discount_rate(doc)

    doc = dict(cos=10, cv=1, cvwd='1.5')
    assert 0.5 / 10 == loader.get_commission_discount_rate(doc)

    doc = dict(cos=10, cv=1, cvwd=1)
    assert 0 == loader.get_commission_discount_rate(doc)


def test_get_commission_vat_value():
    doc = dict()
    assert loader.get_commission_vat_value(doc) is None

    doc = dict(vat=1)
    assert 1 == loader.get_commission_vat_value(doc)

    doc = dict(cvwv=2, cv=1)
    assert 1 == loader.get_commission_vat_value(doc)

    doc = dict(cvwv=2, cv=2)
    assert 0 == loader.get_commission_vat_value(doc)

    doc = dict(vat='3', cvwv='2', cv='1')
    assert 3 == loader.get_commission_vat_value(doc)

    doc = dict(cv=2)
    assert loader.get_commission_vat_value(doc) is None


def test_get_commission_vat_value_ccy():
    doc = dict()
    assert loader.get_commission_vat_value_ccy(doc) is None

    doc = dict(cc_cvwv=2, cc_cv=1)
    assert 1 == loader.get_commission_vat_value_ccy(doc)

    doc = dict(cc_cvwv='2', cc_cv='2')
    assert 0 == loader.get_commission_vat_value_ccy(doc)

    doc = dict(cc_cv=1)
    assert loader.get_commission_vat_value_ccy(doc) is None
