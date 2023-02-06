import decimal
import operator

import pytest

from taxi import billing


@pytest.mark.nofilldb()
def test_money_add():
    assert _money('1 RUB') + _money('2 RUB') == _money('3 RUB')


@pytest.mark.nofilldb()
def test_money_sub():
    assert _money('5 RUB') - _money('2 RUB') == _money('3 RUB')


@pytest.mark.nofilldb()
def test_money_mul():
    assert _money('5 RUB') * decimal.Decimal(2) == _money('10 RUB')


@pytest.mark.nofilldb()
def test_money_div():
    assert _money('10 RUB') / decimal.Decimal(2) == _money('5 RUB')


@pytest.mark.nofilldb()
def test_money_cmp():
    assert _money('5 RUB') == _money('5 RUB')
    assert _money('5 RUB') != _money('6 RUB')
    assert _money('5 RUB') < _money('6 RUB')
    assert _money('5 RUB') <= _money('6 RUB')
    assert _money('6 RUB') > _money('5 RUB')
    assert _money('6 RUB') >= _money('5 RUB')


@pytest.mark.nofilldb()
def test_money_zero():
    assert billing.Money.zero('RUB') == _money('0 RUB')


@pytest.mark.nofilldb()
def test_money_neg():
    assert -_money('5 RUB') == _money('-5 RUB')


@pytest.mark.nofilldb()
def test_money_accessors():
    money = _money('5 RUB')
    assert money.amount == decimal.Decimal(5)
    assert money.currency == 'RUB'


@pytest.mark.parametrize(
    'oper',
    [
        operator.add,
        operator.sub,
        operator.eq,
        operator.lt,
        operator.le,
        operator.gt,
        operator.ge,
    ],
)
@pytest.mark.nofilldb()
def test_money_currency_mismatch(oper):
    with pytest.raises(billing.CurrencyMismatch):
        oper(_money('5 RUB'), _money('300 USD'))


@pytest.mark.nofilldb()
def test_money_round():
    assert _money('10.12344 RUB').round() == _money('10.1234 RUB')
    assert _money('10.12345 RUB').round() == _money('10.1234 RUB')
    assert _money('10.12355 RUB').round() == _money('10.1236 RUB')


def _money(money_str: str) -> billing.Money:
    amount_str, currency = money_str.split()
    return billing.Money(decimal.Decimal(amount_str), currency)
