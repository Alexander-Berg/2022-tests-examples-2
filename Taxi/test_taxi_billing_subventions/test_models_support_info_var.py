import decimal
import operator

import pytest


from taxi import billing

from taxi_billing_subventions.common import models
from test_taxi_billing_subventions import helpers


@pytest.mark.nofilldb()
def test_create():
    value = helpers.money('100 RUB')
    var = models.Var(value, 'cost_for_driver')
    assert var.value == value
    assert var.calculations == [
        models.Calculation(
            op='set',
            args=[value],
            reason='cost_for_driver',
            details={},
            value=value,
        ),
    ]


@pytest.mark.nofilldb()
def test_set():
    initial = helpers.money('100 RUB')
    final = helpers.money('110 RUB')
    var = models.Var(initial, 'cost_for_driver')
    var = var.set(final, 'tariff_minimal')
    assert var.value == final
    assert var.calculations == [
        models.Calculation(
            op='set',
            args=[initial],
            reason='cost_for_driver',
            details={},
            value=initial,
        ),
        models.Calculation(
            op='set',
            args=[final],
            reason='tariff_minimal',
            details={},
            value=final,
        ),
    ]


def _build_calculations(op_name, initial_value, arg_value, expected_value):
    return [
        models.Calculation(
            op='set',
            args=[initial_value],
            reason='initial',
            details={},
            value=initial_value,
        ),
        models.Calculation(
            op=op_name,
            args=[arg_value],
            reason='change',
            details={},
            value=expected_value,
        ),
    ]


@pytest.mark.parametrize(
    'op, op_name, initial_value, arg_value, expected_value',
    [
        (
            operator.sub,
            'sub',
            helpers.money('100 RUB'),
            helpers.money('5 RUB'),
            helpers.money('95 RUB'),
        ),
        (
            operator.add,
            'add',
            helpers.money('100 RUB'),
            helpers.money('5 RUB'),
            helpers.money('105 RUB'),
        ),
        (
            operator.mul,
            'mul',
            helpers.money('100 RUB'),
            decimal.Decimal('1.2'),
            helpers.money('120 RUB'),
        ),
        (
            operator.truediv,
            'div',
            helpers.money('120 RUB'),
            decimal.Decimal('1.2'),
            helpers.money('100 RUB'),
        ),
    ],
)
@pytest.mark.nofilldb()
def test_op(op, op_name, initial_value, arg_value, expected_value):
    # pylint: disable=invalid-name
    var = models.Var(initial_value, 'initial')
    var = op(var, (arg_value, 'change'))
    assert var.value == expected_value
    if isinstance(arg_value, decimal.Decimal):
        arg_value = billing.Money(arg_value, billing.Money.NO_CURRENCY)
    expected_calculations = _build_calculations(
        op_name=op_name,
        initial_value=initial_value,
        arg_value=arg_value,
        expected_value=expected_value,
    )
    assert var.calculations == expected_calculations


@pytest.mark.nofilldb()
def test_serde():
    var = models.Var(helpers.money('100 RUB'), 'cost_for_driver')
    expected_json = {
        'value': {'amount': '100', 'currency': 'RUB'},
        'calculations': [
            {
                'op': 'set',
                'args': [{'amount': '100', 'currency': 'RUB'}],
                'reason': 'cost_for_driver',
                'details': {},
                'value': {'amount': '100', 'currency': 'RUB'},
            },
        ],
    }
    assert var.to_json() == expected_json
    assert models.Var.from_json(var.to_json()) == var
