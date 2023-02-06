import decimal

import pytest

from transactions.internal import payment_handler

CompositeSum = payment_handler.CompositeSum
Sum = payment_handler.Sum


@pytest.mark.nofilldb
def test_decimal_sum():
    decimal_sum = payment_handler.decimal_sum  # pylint: disable=W0212
    assert decimal_sum('123.45') == decimal.Decimal('123.45')
    assert decimal_sum(1234567) == decimal.Decimal('123.4567')


@pytest.mark.nofilldb
def test_sum_bool():
    assert not Sum({})
    assert not Sum({'a': 0})
    assert Sum({'a': 1})
    assert Sum({'a': 1, 'b': -1})


@pytest.mark.nofilldb
def test_sum_includes():
    assert Sum({'a': 10}).includes(Sum({'a': 10}))
    assert Sum({'a': 10}).includes(Sum({'a': 9}))
    assert not Sum({'a': 8}).includes(Sum({'a': 9}))
    assert not Sum({'a': 10}).includes(Sum({'b': 20}))


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'transaction_sum, to_refund, e_this_refund, e_left_to_refund',
    [
        (
            {'ride': '100', 'tips': '10'},
            {'ride': '100', 'burgers': '50'},
            {'ride': '100'},
            {'burgers': '50'},
        ),
        (
            {'ride': '100', 'tips': '10'},
            {'ride': '120', 'tips': '6'},
            {'ride': '100', 'tips': '6'},
            {'ride': '20'},
        ),
        (
            {'ride': '100', 'tips': '10'},
            {'burgers': '120', 'milk': '6'},
            None,
            {'burgers': '120', 'milk': '6'},
        ),
    ],
)
def test_calc_transaction_refund(
        transaction_sum, to_refund, e_this_refund, e_left_to_refund,
):
    transaction = {'sum': transaction_sum}
    to_refund = payment_handler.Sum(to_refund)
    e_left_to_refund = payment_handler.Sum(e_left_to_refund)
    this_refund, left_to_refund = payment_handler.calc_transaction_refund(
        transaction, to_refund,
    )
    if e_this_refund is None:
        assert this_refund is None
    else:
        e_this_refund = payment_handler.Sum(e_this_refund)
        assert e_this_refund.items() == this_refund.items()
    assert not e_left_to_refund - left_to_refund


@pytest.mark.nofilldb
def test_composite_sum_bool():
    assert not CompositeSum({})
    assert not CompositeSum(
        {'card': {'a': 0}, 'personal_wallet': {'b': 0, 'c': 0}},
    )
    assert not CompositeSum({'card': {'a': 0}, 'personal_wallet': {}})
    assert CompositeSum({'card': {'a': 1}, 'personal_wallet': {}})
    assert CompositeSum({'card': {'a': 1}, 'personal_wallet': {'a': 0}})
    assert CompositeSum({'card': {'a': 1}, 'personal_wallet': {'a': -1}})


@pytest.mark.nofilldb
def test_composite_sum_includes():
    assert CompositeSum({'card': {'a': 10}}).includes(
        CompositeSum({'card': {'a': 10}}),
    )
    assert CompositeSum({'card': {'a': 10}}).includes(
        CompositeSum({'card': {'a': 9}}),
    )
    assert not CompositeSum({'card': {'a': 8}}).includes(
        CompositeSum({'card': {'a': 9}}),
    )
    assert not CompositeSum({'card': {'a': 10}}).includes(
        CompositeSum({'card': {'b': 20}}),
    )
    assert not CompositeSum({'card': {'a': 10}}).includes(
        CompositeSum({'personal_wallet': {'a': 10}}),
    )
    assert CompositeSum(
        {'card': {'a': 10}, 'personal_wallet': {'b': 10}},
    ).includes(CompositeSum({'card': {'a': 9}, 'personal_wallet': {'b': 9}}))
