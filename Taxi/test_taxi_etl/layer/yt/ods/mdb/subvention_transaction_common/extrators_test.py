# coding: utf-8
import pytest

from taxi_etl.layer.yt.ods.mdb.subvention_transaction_common.extractors import (
    get_dms_value,
    get_billing_value,
    get_subsidy_value_w_commission,
    get_subsidy_value_wo_commission,
    get_dmd_value
)


def test_get_dms_value():
    doc = dict(cv=1)
    assert get_dms_value(doc) is None

    doc = dict(dms=1.06, cv=1)
    assert 0.06 == pytest.approx(get_dms_value(doc))

    doc = dict(dms=1.06, cv=1, ds=0.5)
    assert 0.03 == pytest.approx(get_dms_value(doc))

    doc = dict(dms=1.06, cv=1, ps=0.5)
    assert 0.03 == pytest.approx(get_dms_value(doc))

    doc = dict(dms='1.06', cv='1', ds='0.5', ps='0.2')
    assert 0.018 == pytest.approx(get_dms_value(doc))


def test_get_dmd_value():
    doc = dict(donate_discounts_multiplier=1.06, c='2019-05-01 23:23:23')
    assert get_dmd_value(doc) is None

    doc = dict(ds=1, c='2019-05-01 23:23:23')
    assert get_dmd_value(doc) is None

    doc = dict(donate_discounts_multiplier=1.06, ds=1, c='2019-05-01 23:23:23')
    assert get_dmd_value(doc) == pytest.approx(0.06)

    doc = dict(donate_discounts_multiplier=1.06,
               ds=1,
               c='2019-05-01 23:23:23')
    assert get_dmd_value(doc) == pytest.approx(0.06)

    doc = dict(donate_discounts_multiplier=1.06,
               ds=0.5,
               c='2019-05-01 23:23:23')
    assert get_dmd_value(doc) == pytest.approx(0.03)

    doc = dict(donate_discounts_multiplier='1.06',
               ds='0.5',
               c='2019-05-01 23:23:23')
    assert get_dmd_value(doc) == pytest.approx(0.03)

    doc = dict(donate_discounts_multiplier=1.06,
               dms=1.1,
               ds=0.5,
               c='2019-04-01 10:10:10')
    assert get_dmd_value(doc) == pytest.approx(0.05)

    doc = dict(dms=1.1, ds=0.5, c='2019-04-01 15:15:15')
    assert get_dmd_value(doc) == pytest.approx(0.05)

    doc = dict(dms=1.1, ds=0.5, c='2018-12-01 15:15:15')
    assert get_dmd_value(doc) is None


def test_get_billing_value():
    doc = dict(cv=1, c='2018-01-01 21:21:21')
    assert 1 == get_billing_value(doc)

    doc = dict(dms=1.06, cv=1, c='2018-01-01 21:21:21')
    assert 1.06 == pytest.approx(get_billing_value(doc))

    doc = dict(dms=1.06, cv=1, ds=0.5, c='2018-01-01 21:21:21')
    assert 1.03 == pytest.approx(get_billing_value(doc))

    doc = dict(dms=1.06, cv=1, ps=0.5, c='2018-01-01 21:21:21')
    assert 1.03 == pytest.approx(get_billing_value(doc))

    doc = dict(dms='1.06', cv='1', ds='0.5', ps='0.2', c='2018-01-01 21:21:21')
    assert 1.018 == pytest.approx(get_billing_value(doc))

    doc = dict(cv=1,
               dms=1.1,
               ds=0.5,
               donate_discounts_multiplier=1.3,
               c='2019-05-01 23:23:23')
    assert get_billing_value(doc) == pytest.approx(1.2)

    doc = dict(cv=1, dms=1.1, ds=0.5, c='2019-01-01 20:20:20')
    assert get_billing_value(doc) == pytest.approx(1.1)


def test_get_subsidy_value_w_commission():
    doc = dict(cv=1)
    assert 1 == get_subsidy_value_w_commission(doc)

    doc = dict(cv=1, sc=0.5)
    assert 1 == pytest.approx(get_subsidy_value_w_commission(doc))

    doc = dict(cv=1, ds=0.5)
    assert 0.5 == pytest.approx(get_subsidy_value_w_commission(doc))

    doc = dict(cv='1', ds='0.5', ps='0.5')
    assert 0 == get_subsidy_value_w_commission(doc)

    doc = dict(cv=1, ds=0.5, ps=0.1)
    assert 0.4 == pytest.approx(get_subsidy_value_w_commission(doc))

    doc = dict(cv=1, ps=0.1)
    assert 0.9 == pytest.approx(get_subsidy_value_w_commission(doc))


def test_get_subsidy_value_wo_commission():
    doc = dict(cv=1)
    assert 1 == get_subsidy_value_wo_commission(doc)

    doc = dict(cv='1', sc='0.5')
    assert 1.5 == pytest.approx(get_subsidy_value_wo_commission(doc))
