import decimal
import operator

import pytest

from billing_functions.functions.core import support_info


@pytest.mark.nofilldb()
def test_create():
    value = decimal.Decimal(100)
    var = support_info.Var.make(value, 'cost_for_driver')
    assert var.value == value
    assert var.mutations == [
        support_info.Operation(
            op='set',
            args=[value],
            reason='set_from_cost_for_driver',
            details={},
            value=value,
        ),
    ]


@pytest.mark.nofilldb()
def test_set():
    initial = decimal.Decimal(100)
    final = decimal.Decimal(110)
    var = support_info.Var.make(initial, 'cost_for_driver')
    var = var.set(final, 'tariff_minimal')
    assert var.value == final
    assert var.mutations == [
        support_info.Operation(
            op='set',
            args=[initial],
            reason='set_from_cost_for_driver',
            details={},
            value=initial,
        ),
        support_info.Operation(
            op='set',
            args=[final],
            reason='set_from_tariff_minimal',
            details={},
            value=final,
        ),
    ]


def _build_calculations(op_name, initial_value, arg_value, expected_value):

    pref = ''
    if op_name in ('mul', 'div'):
        pref = 'by_'

    return [
        support_info.Operation(
            op='set',
            args=[initial_value],
            reason='set_from_initial',
            details={},
            value=initial_value,
        ),
        support_info.Operation(
            op=op_name,
            args=[arg_value],
            reason=op_name + '_' + pref + 'change',
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
            decimal.Decimal('100'),
            decimal.Decimal('5'),
            decimal.Decimal('95'),
        ),
        (
            operator.add,
            'add',
            decimal.Decimal('100'),
            decimal.Decimal('5'),
            decimal.Decimal('105'),
        ),
        (
            operator.mul,
            'mul',
            decimal.Decimal('100'),
            decimal.Decimal('1.2'),
            decimal.Decimal('120'),
        ),
        (
            operator.truediv,
            'div',
            decimal.Decimal('120'),
            decimal.Decimal('1.2'),
            decimal.Decimal('100'),
        ),
    ],
)
@pytest.mark.nofilldb()
def test_op(op, op_name, initial_value, arg_value, expected_value):
    # pylint: disable=invalid-name
    var = support_info.Var.make(initial_value, 'initial')
    var = op(var, (arg_value, 'change'))
    assert var.value == expected_value

    expected_calculations = _build_calculations(
        op_name=op_name,
        initial_value=initial_value,
        arg_value=arg_value,
        expected_value=expected_value,
    )
    assert var.mutations == expected_calculations


@pytest.mark.nofilldb()
def test_serde():
    var_instance = support_info.Var.make(
        decimal.Decimal('100'), 'cost_for_driver',
    )
    expected_json = {
        'value': {'amount': '100', 'currency': 'RUB'},
        'calculations': [
            {
                'op': 'set',
                'args': [{'amount': '100', 'currency': 'RUB'}],
                'reason': 'set_from_cost_for_driver',
                'details': {},
                'value': {'amount': '100', 'currency': 'RUB'},
            },
        ],
    }
    assert var_instance.to_json('RUB') == expected_json
