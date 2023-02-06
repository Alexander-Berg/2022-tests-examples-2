import pytest

from taxi_etl.layer.yt.ods.dbtaxi.invoice.impl import get_user_cost_vat, get_tips_vat, get_paid_cancel_flg


def create_doc(user_to_pay_ride=None,
               user_to_pay_tips=None,
               without_vat_to_pay_ride=None,
               without_vat_to_pay_tips=None,
               type_=None,
               status=None):
    return dict(
        status=status,
        payment_tech=dict(
            type=type_,
            user_to_pay=dict(ride=user_to_pay_ride, tips=user_to_pay_tips),
            without_vat_to_pay=dict(ride=without_vat_to_pay_ride,
                                    tips=without_vat_to_pay_tips)
        ))


def test_get_user_cost_vat():
    test_date = dict()
    assert get_user_cost_vat(test_date) is None
    test_data = create_doc()
    assert get_user_cost_vat(test_data) is None
    test_date = create_doc(user_to_pay_ride=10000)
    assert get_user_cost_vat(test_date) is None
    test_data = create_doc(without_vat_to_pay_ride=10000)
    assert get_user_cost_vat(test_data) is None
    test_data = create_doc(user_to_pay_ride=10000,
                           without_vat_to_pay_ride=10000)
    assert 0 == get_user_cost_vat(test_data)
    test_data = create_doc(user_to_pay_ride=11000,
                           without_vat_to_pay_ride=10000)
    assert 0.1 == pytest.approx(get_user_cost_vat(test_data))


def test_get_tips_vat():
    test_date = dict()
    assert get_tips_vat(test_date) is None
    test_data = create_doc()
    assert get_tips_vat(test_data) is None
    test_date = create_doc(user_to_pay_tips=10000)
    assert get_tips_vat(test_date) is None
    test_data = create_doc(without_vat_to_pay_tips=10000)
    assert get_tips_vat(test_data) is None
    test_data = create_doc(user_to_pay_tips=10000,
                           without_vat_to_pay_tips=10000)
    assert 0 == get_tips_vat(test_data)
    test_data = create_doc(user_to_pay_tips=11000,
                           without_vat_to_pay_tips=10000)
    assert 0.1 == pytest.approx(get_tips_vat(test_data))


def test_get_paid_cancel_order_flg():
    doc = dict()
    assert get_paid_cancel_flg(doc) is False

    doc = create_doc(user_to_pay_ride=10)
    assert get_paid_cancel_flg(doc) is False

    doc = create_doc(status='success', user_to_pay_ride=10)
    assert get_paid_cancel_flg(doc) is False

    doc = create_doc(status='cancelled', user_to_pay_ride=10)
    assert get_paid_cancel_flg(doc) is True
