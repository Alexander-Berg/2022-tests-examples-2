import dataclasses
import decimal
from typing import Any
from typing import Iterable
from typing import Optional

import pytest

from billing_functions import consts
from billing_functions.functions.core import support_info
from billing_functions.functions.core.commissions import entities
from billing_functions.functions.core.commissions import models
from billing_functions.repositories import commission_agreements
from test_billing_functions import var

ClientStatus = consts.OrderStatus
TaxiStatus = consts.OrderTaxiStatus
PaymentType = consts.PaymentType
CancellationSettings = commission_agreements.CancellationSettings
CancellationInterval = commission_agreements.CancellationInterval


Commission = models.Commission
Component = models.Component

_ZERO = decimal.Decimal('0')


@dataclasses.dataclass(frozen=True)
class Context(entities.CalculatorContext):
    is_applicable: bool
    cost: decimal.Decimal


def _make_context(
        is_applicable: bool = True,
        cost: decimal.Decimal = decimal.Decimal('100'),
        ind_bel_vat_rate: decimal.Decimal = None,
):
    return Context(**locals())


# pylint: disable=unsubscriptable-object
class Calculator(entities.StandardCalculator[Context]):
    def _is_applicable(self, context: Context) -> models.MatchResult:
        if context.is_applicable:
            return models.Match()
        return models.Mismatch(reason='some_reason')

    def _get_cost(self, context: Context) -> support_info.Var:
        return support_info.Var.make(context.cost, 'cost')

    def _get_vat_rate(self, context: Context) -> support_info.Var:
        return var.make_var('1.2')


# pylint: disable=unsubscriptable-object  # wait for pylint 2.5.3
class BisectCostConstraint(entities.CostConstraint[Any]):
    def apply(
            self, context: Any, cost: Optional[support_info.Var],
    ) -> Optional[support_info.Var]:
        del context  # unused
        assert cost is not None
        return support_info.Var(cost.value / 2, [])


# pylint: disable=unsubscriptable-object  # wait for pylint 2.5.3
class X2NetModifier(entities.Modifier[Any]):
    def apply(
            self, context: Any, commission: models.Commission,
    ) -> models.Commission:
        return models.Commission(
            value=commission.value * (decimal.Decimal('2'), 'x2_modifier'),
            vat=commission.vat * (decimal.Decimal('2'), 'x2_modifier'),
            vat_rate=commission.vat_rate,
            rate=commission.rate,
            cost=commission.cost,
            gross=commission.gross,
        )


class AlwaysBillable(entities.BillabilityCheck[Any]):
    def __init__(self, details: Optional[dict] = None):
        self._details = details

    def is_billable(
            self, context: entities.BillabilityCheckContext,
    ) -> models.MatchResult:
        del context  # unused
        return models.Match(self._details)


def _make_calculator(
        rate: entities.Rate = entities.RateFlat(decimal.Decimal('0.04')),
        contract_vat_rate: decimal.Decimal = decimal.Decimal('1.2'),
        billability_check: entities.BillabilityCheck = AlwaysBillable(),
        reduces_commission_limit_if_promocode: bool = False,
        cost_constraint: Optional[entities.CostConstraint[Context]] = None,
        modifiers: Optional[Iterable[entities.Modifier[Context]]] = None,
) -> Calculator:
    return Calculator(**locals())


@pytest.mark.parametrize(
    'context, calculator, expected_commission',
    [
        pytest.param(
            _make_context(is_applicable=False),
            _make_calculator(),
            Commission.zeroed_with_details(
                models.Mismatch(reason='some_reason'),
            ),
            id='not applicable',
        ),
        pytest.param(
            _make_context(),
            _make_calculator(
                rate=entities.RateFlat(decimal.Decimal('0.04')),
                billability_check=AlwaysBillable({'why': 'because'}),
            ),
            Commission(
                value=var.make_var(
                    '4', [('set', '4.0', 'set_from_mul_cost_by_rate', '4.0')],
                ),
                vat=var.make_var(
                    '0.8', [('set', '0.8', 'set_from_mul_by_vat_rate', '0.8')],
                ),
                vat_rate=var.make_var('1.2'),
                cost=var.make_var(
                    '100', [('set', '100', 'set_from_cost', '100')],
                ),
                rate=var.make_var(
                    '0.04',
                    [
                        (
                            'set',
                            '0.04',
                            'set_from_rate',
                            '0.04',
                            {'why': 'because'},
                        ),
                    ],
                ),
                gross=Component(decimal.Decimal('4'), decimal.Decimal('0.8')),
            ),
            id='flat rate',
        ),
        pytest.param(
            _make_context(),
            _make_calculator(
                rate=entities.RateAbsolute(decimal.Decimal('10')),
                billability_check=AlwaysBillable({'why': 'because'}),
            ),
            Commission(
                value=var.make_var(
                    '10',
                    [
                        (
                            'set',
                            '10',
                            'set_from_value',
                            '10',
                            {'why': 'because'},
                        ),
                    ],
                ),
                vat=var.make_var(
                    '2', [('set', '2', 'set_from_mul_by_vat_rate', '2')],
                ),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var(
                    '100', [('set', '100', 'set_from_cost', '100')],
                ),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            id='absolute rate',
        ),
        pytest.param(
            _make_context(),
            _make_calculator(cost_constraint=BisectCostConstraint()),
            Commission(
                value=var.make_var(
                    '2', [('set', '2', 'set_from_mul_cost_by_rate', '2')],
                ),
                vat=var.make_var(
                    '0.4', [('set', '0.4', 'set_from_mul_by_vat_rate', '0.4')],
                ),
                vat_rate=var.make_var('1.2'),
                rate=var.make_var(
                    '0.04', [('set', '0.04', 'set_from_rate', '0.04')],
                ),
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('2'), decimal.Decimal('0.4')),
            ),
            id='cost constraint apply',
        ),
        pytest.param(
            _make_context(),
            _make_calculator(modifiers=[X2NetModifier()]),
            Commission(
                value=var.make_var(
                    '8',
                    [
                        ('set', '4.0', 'set_from_mul_cost_by_rate', '4.0'),
                        ('mul', '2', 'mul_by_x2_modifier', '8'),
                    ],
                ),
                vat=var.make_var(
                    '1.6',
                    [
                        ('set', '0.8', 'set_from_mul_by_vat_rate', '0.8'),
                        ('mul', '2', 'mul_by_x2_modifier', '1.6'),
                    ],
                ),
                vat_rate=var.make_var('1.2'),
                rate=var.make_var(
                    '0.04', [('set', '0.04', 'set_from_rate', '0.04')],
                ),
                cost=var.make_var(
                    '100', [('set', '100', 'set_from_cost', '100')],
                ),
                gross=Component(decimal.Decimal('4'), decimal.Decimal('0.8')),
            ),
            id='modifiers apply',
        ),
    ],
)
def test_calculator(context, calculator, expected_commission):
    assert calculator.calculate(context) == expected_commission


@pytest.mark.parametrize(
    'level, expected_level, expected_rate',
    (
        (frozenset(), frozenset(), _ZERO),
        (frozenset(['xxx']), frozenset(), _ZERO),
        (
            frozenset(['lightbox']),
            frozenset(['lightbox']),
            decimal.Decimal('0.02'),
        ),
        (
            frozenset(['lightbox', 'xxx']),
            frozenset(['lightbox']),
            decimal.Decimal('0.02'),
        ),
        (
            frozenset(['lightbox', 'co_branding']),
            frozenset(['co_branding', 'lightbox']),
            decimal.Decimal('0.04'),
        ),
        (
            frozenset(['lightbox', 'co_branding', 'xxx']),
            frozenset(['co_branding', 'lightbox']),
            decimal.Decimal('0.04'),
        ),
    ),
)
def test_branding_discounts_match(level, expected_level, expected_rate):
    entity = entities.BrandingDiscounts(
        [
            (frozenset(['co_branding', 'lightbox']), decimal.Decimal('0.04')),
            (frozenset(['lightbox']), decimal.Decimal('0.02')),
        ],
    )
    assert entity.match(level) == entities.BrandingDiscount(
        expected_level, expected_rate,
    )


@pytest.mark.parametrize(
    'context, lower_bound, upper_bound, raw_cost, expected_constrained_cost',
    [
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=None,
                payment_type=consts.PaymentType.CARD,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            15,
            15,
            id='do nothing',
        ),
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=None,
                payment_type=consts.PaymentType.CARD,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            5,
            max(10, 5),
            id='too low',
        ),
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=None,
                payment_type=consts.PaymentType.CARD,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            25,
            min(20, 25),
            id='too high',
        ),
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=decimal.Decimal(1),
                payment_type=consts.PaymentType.CORP,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            21,
            20,  # min(20 * 1, 21)
            id='corp with zero vat rate',
        ),
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=decimal.Decimal('1.2'),
                payment_type=consts.PaymentType.CORP,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            21,
            21,  # min(20 * 1.2, 21)
            id='corp with vat: norm',
        ),
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=decimal.Decimal('1.2'),
                payment_type=consts.PaymentType.CORP,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            11,
            12,  # max(10 * 1.2, 12)
            id='corp with vat: too low',
        ),
        pytest.param(
            entities.BoundedCostConstraintContext(
                corp_vat_rate=decimal.Decimal('1.2'),
                payment_type=consts.PaymentType.CORP,
                billing_type=consts.BillingType.NORMAL,
            ),
            10,
            20,
            25,
            24,  # min(20 * 1.2, 24)
            id='corp with vat: too high',
        ),
    ],
)
def test_cost_constraints(
        context, lower_bound, upper_bound, raw_cost, expected_constrained_cost,
):
    constraint = entities.BoundedCostConstraint(lower_bound, upper_bound)

    actual_constrained_cost = constraint.apply(context, var.make_var(raw_cost))
    assert actual_constrained_cost.value == expected_constrained_cost
