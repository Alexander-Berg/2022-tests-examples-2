import decimal

from eats_integration_offline_orders.internal import types

DecimalFloat = types.DecimalFloat


def test_init():
    obj = DecimalFloat(0.1)
    assert obj._decimal == decimal.Decimal('0.1')  # pylint:disable=W0212


def test_str():
    assert str(DecimalFloat(0.3)) == '0.3'


def test_add():
    result = DecimalFloat(0.1) + DecimalFloat(0.1)
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(0.2)

    result = DecimalFloat(0.1) + 0.1
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(0.2)


def test_radd():
    result = 0.1 + DecimalFloat(0.1)
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(0.2)


def test_mul():
    result = DecimalFloat(1.1) * DecimalFloat(3)
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(3.3)

    result = DecimalFloat(1.1) * 3
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(3.3)


def test_rmul():
    result = 1.1 * DecimalFloat(3)
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(3.3)


def test_truediv():
    result = DecimalFloat(3.3) / DecimalFloat(3)
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(1.1)

    result = DecimalFloat(3.3) / 3
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(1.1)


def test_rtruediv():
    result = 3.3 / DecimalFloat(3)
    assert isinstance(result, DecimalFloat)
    assert result == DecimalFloat(1.1)
