# coding: utf-8
import pytest

from dmp_suite import fin_utils as fu


def test_calculate_vat():
    with pytest.raises(ValueError):
        fu.calculate_vat(0, 1)
    with pytest.raises(ValueError):
        fu.calculate_vat(10, 0)
    with pytest.raises(ValueError):
        fu.calculate_vat(10, 15)
    assert 0 == fu.calculate_vat(0, 0)
    assert 0.5 == fu.calculate_vat(10.5, 10)
    assert 0.2 == pytest.approx(fu.calculate_vat(10.5, 10.3))


def test_calculate_discount():
    with pytest.raises(ValueError):
        fu.calculate_discount(10, 4)
    with pytest.raises(ValueError):
        fu.calculate_discount(10, 0)
    assert 0 == fu.calculate_discount(0, 0)
    assert 1 == fu.calculate_discount(0, 1)
    assert 0.5 == fu.calculate_discount(10.5, 11)
    assert 2.0 == fu.calculate_discount(10.5, 12.5)


def test_calculate_rate():
    assert fu.calculate_rate(0, 10) is None
    assert fu.calculate_rate(0, 0) is None
    assert 0 == fu.calculate_rate(10, 0)
    assert 1.5 == fu.calculate_rate(10, 15)
    assert 0.666666 == pytest.approx(fu.calculate_rate(15, 10))
    assert 0.677419 == pytest.approx(fu.calculate_rate(15.5, 10.5))


def test_calculate_dms_value():
    with pytest.raises(ValueError):
        fu.calculate_multiplier_value(0, 0)
    with pytest.raises(ValueError):
        fu.calculate_multiplier_value(10, 0)
    assert 10 == pytest.approx(fu.calculate_multiplier_value(100, 1.1))
    assert 0 == fu.calculate_multiplier_value(100, 1)
    assert 50.05 == pytest.approx(fu.calculate_multiplier_value(100.1, 1.5))
