import dataclasses
import decimal
from typing import Optional

import pytest

from billing_functions import consts
from billing_functions.functions.core import order
from billing_functions.functions.core import support_info

BillingType = consts.BillingType
ClientStatus = consts.OrderStatus
TaxiStatus = consts.OrderTaxiStatus
PaymentType = consts.PaymentType

ZERO = decimal.Decimal(0)


@dataclasses.dataclass(frozen=True)
class CostForCommissionContext:
    status: str = ClientStatus.FINISHED
    taxi_status: str = TaxiStatus.COMPLETE
    call_center_surcharge_inc_vat: Optional[decimal.Decimal] = None
    cost: decimal.Decimal = decimal.Decimal('100')
    cost_for_driver: Optional[decimal.Decimal] = None
    discount: Optional[decimal.Decimal] = None
    park_corp_vat: Optional[decimal.Decimal] = None
    payment_type: PaymentType = PaymentType.CARD
    tariff_minimal_cost: decimal.Decimal = decimal.Decimal('10')
    use_minimal_tariff_cost: bool = True


@dataclasses.dataclass(frozen=True)
class CostForSubventionContext:
    status: str = ClientStatus.FINISHED
    taxi_status: str = TaxiStatus.COMPLETE
    call_center_surcharge_inc_vat: Optional[decimal.Decimal] = None
    cost: decimal.Decimal = decimal.Decimal('100')
    cost_for_driver: Optional[decimal.Decimal] = None
    discount: Optional[decimal.Decimal] = None
    park_corp_vat: Optional[decimal.Decimal] = None
    payment_type: PaymentType = PaymentType.CARD


@pytest.mark.parametrize(
    'context, expected',
    (
        pytest.param(
            CostForCommissionContext(),
            support_info.Var(
                decimal.Decimal('100'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                ],
            ),
            id='from cost_for_client',
        ),
        pytest.param(
            CostForCommissionContext(cost_for_driver=decimal.Decimal('100')),
            support_info.Var(
                decimal.Decimal('100'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_driver',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                ],
            ),
            id='from cost_for_driver',
        ),
        pytest.param(
            CostForCommissionContext(status=ClientStatus.CANCELLED, cost=ZERO),
            support_info.Var(
                decimal.Decimal('10'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('10')],
                        reason='set_from_tariff_minimal',
                        details={},
                        value=decimal.Decimal('10'),
                    ),
                ],
            ),
            id='from tariff_minimal_cost',
        ),
        pytest.param(
            CostForCommissionContext(
                status=ClientStatus.CANCELLED,
                cost=ZERO,
                use_minimal_tariff_cost=False,
            ),
            support_info.Var(
                decimal.Decimal('0'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('0')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('0'),
                    ),
                ],
            ),
            id='not use tariff_minimal_cost',
        ),
        pytest.param(
            CostForCommissionContext(discount=decimal.Decimal('10')),
            support_info.Var(
                decimal.Decimal('110'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                    support_info.Operation(
                        op='add',
                        args=[decimal.Decimal('10')],
                        reason='add_discount',
                        details={},
                        value=decimal.Decimal('110'),
                    ),
                ],
            ),
            id='with discount',
        ),
        pytest.param(
            CostForCommissionContext(
                status=ClientStatus.CANCELLED.value,
                payment_type=PaymentType.CORP,
                park_corp_vat=decimal.Decimal('1.3'),
            ),
            support_info.Var(
                decimal.Decimal('130'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                    support_info.Operation(
                        op='add',
                        args=[decimal.Decimal('30')],
                        reason='add_corp_vat',
                        details={},
                        value=decimal.Decimal('130'),
                    ),
                ],
            ),
            id='with corp_vat',
        ),
    ),
)
def test_get_cost_for_commission(context, expected):
    actual = order.get_cost_for_commission(
        context,
        context.use_minimal_tariff_cost,
        context.call_center_surcharge_inc_vat,
    )
    assert actual == expected


@pytest.mark.parametrize(
    'context, expected',
    (
        pytest.param(
            CostForSubventionContext(),
            support_info.Var(
                decimal.Decimal('100'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                ],
            ),
            id='from cost_for_client',
        ),
        pytest.param(
            CostForSubventionContext(cost_for_driver=decimal.Decimal('100')),
            support_info.Var(
                decimal.Decimal('100'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_driver',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                ],
            ),
            id='from cost_for_driver',
        ),
        pytest.param(
            CostForSubventionContext(discount=decimal.Decimal('10')),
            support_info.Var(
                decimal.Decimal('110'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                    support_info.Operation(
                        op='add',
                        args=[decimal.Decimal('10')],
                        reason='add_discount',
                        details={},
                        value=decimal.Decimal('110'),
                    ),
                ],
            ),
            id='with discount',
        ),
        pytest.param(
            CostForSubventionContext(
                status=ClientStatus.CANCELLED.value,
                payment_type=PaymentType.CORP,
                park_corp_vat=decimal.Decimal('1.3'),
            ),
            support_info.Var(
                decimal.Decimal('130'),
                [
                    support_info.Operation(
                        op='set',
                        args=[decimal.Decimal('100')],
                        reason='set_from_cost_for_client',
                        details={},
                        value=decimal.Decimal('100'),
                    ),
                    support_info.Operation(
                        op='add',
                        args=[decimal.Decimal('30')],
                        reason='add_corp_vat',
                        details={},
                        value=decimal.Decimal('130'),
                    ),
                ],
            ),
            id='with corp_vat',
        ),
    ),
)
def test_get_cost_for_subvention(context, expected):
    actual = order.get_cost_for_subvention(
        context, context.call_center_surcharge_inc_vat,
    )
    assert actual == expected


@dataclasses.dataclass(frozen=True)
class GetBillingTypeContext(CostForCommissionContext):
    status: str = ClientStatus.FINISHED.value
    taxi_status: str = TaxiStatus.COMPLETE.value
    cost: decimal.Decimal = decimal.Decimal('10')
    payment_type: PaymentType = PaymentType.CARD
    zero_cost_for_commission: bool = False


@pytest.mark.parametrize(
    'context, ng_mode, expected',
    (
        pytest.param(
            GetBillingTypeContext(taxi_status=TaxiStatus.FAILED.value),
            False,
            BillingType.CANCELLED,
            id='cancelled if cancelled by driver',
        ),
        pytest.param(
            GetBillingTypeContext(
                status=ClientStatus.CANCELLED.value, cost=ZERO,
            ),
            False,
            BillingType.CANCELLED,
            id='cancelled if cancelled by client with zero order cost',
        ),
        pytest.param(
            GetBillingTypeContext(
                taxi_status=TaxiStatus.CANCELLED.value, cost=ZERO,
            ),
            False,
            BillingType.CANCELLED,
            id='cancelled if cancelled by dispatcher with zero order cost',
        ),
        pytest.param(
            GetBillingTypeContext(
                status=ClientStatus.CANCELLED.value,
                payment_type=PaymentType.CASH,
            ),
            False,
            BillingType.CANCELLED,
            id='cancelled if cash-run',
        ),
        pytest.param(
            GetBillingTypeContext(cost=ZERO, zero_cost_for_commission=True),
            False,
            BillingType.EXPIRED,
            id='expired if zero order cost and cost for commission',
        ),
        pytest.param(
            GetBillingTypeContext(taxi_status=TaxiStatus.CANCELLED.value),
            False,
            BillingType.NORMAL,
            id='normal if paid cancel when order cancelled by dispatcher',
        ),
        pytest.param(
            GetBillingTypeContext(status=ClientStatus.CANCELLED.value),
            False,
            BillingType.NORMAL,
            id='normal if paid cancel when order cancelled by client',
        ),
        pytest.param(
            GetBillingTypeContext(),
            False,
            BillingType.NORMAL,
            id='happy path',
        ),
        pytest.param(
            GetBillingTypeContext(taxi_status=TaxiStatus.FAILED.value),
            True,
            BillingType.CANCELLED,
            id='cancelled if cancelled by driver',
        ),
        pytest.param(
            GetBillingTypeContext(
                status=ClientStatus.CANCELLED.value, cost=ZERO,
            ),
            True,
            BillingType.CANCELLED,
            id='cancelled if cancelled by client with zero order cost',
        ),
        pytest.param(
            GetBillingTypeContext(
                taxi_status=TaxiStatus.CANCELLED.value, cost=ZERO,
            ),
            True,
            BillingType.CANCELLED,
            id='cancelled if cancelled by dispatcher with zero order cost',
        ),
        pytest.param(
            GetBillingTypeContext(
                status=ClientStatus.CANCELLED.value,
                payment_type=PaymentType.CASH,
            ),
            True,
            BillingType.CANCELLED,
            id='cancelled if cash-run',
        ),
        pytest.param(
            GetBillingTypeContext(cost=ZERO, zero_cost_for_commission=True),
            True,
            BillingType.NORMAL,
            id='normal if zero order cost and cost for commission',
        ),
        pytest.param(
            GetBillingTypeContext(
                cost=ZERO,
                zero_cost_for_commission=True,
                taxi_status=TaxiStatus.EXPIRED,
            ),
            True,
            BillingType.EXPIRED,
            id='expired if status expired',
        ),
        pytest.param(
            GetBillingTypeContext(taxi_status=TaxiStatus.CANCELLED.value),
            True,
            BillingType.NORMAL,
            id='normal if paid cancel when order cancelled by dispatcher',
        ),
        pytest.param(
            GetBillingTypeContext(status=ClientStatus.CANCELLED.value),
            True,
            BillingType.NORMAL,
            id='normal if paid cancel when order cancelled by client',
        ),
        pytest.param(
            GetBillingTypeContext(), True, BillingType.NORMAL, id='happy path',
        ),
    ),
)
def test_get_billing_type(context, ng_mode, expected):
    actual = order.get_billing_type(context, ng_mode)
    assert actual == expected


@dataclasses.dataclass(frozen=True)
class CalcBalanceChangeContext:
    cost: decimal.Decimal = decimal.Decimal('10')
    cost_for_driver: Optional[decimal.Decimal] = None
    payment_type: PaymentType = PaymentType.CARD
    park_corp_vat: Optional[decimal.Decimal] = None


@pytest.mark.parametrize(
    'context, expected',
    [
        pytest.param(
            CalcBalanceChangeContext(
                cost_for_driver=ZERO,
                payment_type=PaymentType.CORP,
                park_corp_vat=decimal.Decimal(1),
            ),
            ZERO,
            id='zero `cost_for_driver` is not ignored',
        ),
    ],
)
def test_calc_balance_change(context, expected):
    actual = order.calc_balance_change(context)
    assert actual == expected
