import datetime as dt
import decimal
from typing import Optional
from unittest import mock

import pytest

from billing_functions import consts
from billing_functions.functions.core import support_info
from billing_functions.functions.core.commissions import base
from billing_functions.functions.core.commissions import models
from billing_functions.functions.core.commissions import taximeter
from billing_functions.repositories import commission_agreements
from test_billing_functions import var

Commission = models.Commission
Component = models.Component
RawRate = commission_agreements.Rate
RawRateAbsolute = commission_agreements.RateAbsolute


@pytest.fixture(name='make_taximeter_agreement')
def _make_taximeter_agreement(make_agreement):
    def _builder(
            rate: RawRate, unrealized_commission: Optional[decimal.Decimal],
    ):
        return make_agreement(
            kind=consts.CommissionKind.ABSOLUTE_VALUE.value,
            group=consts.CommissionGroup.TAXIMETER.value,
            rate=rate,
            unrealized_commission=unrealized_commission,
        )

    return _builder


def make_context(
        driver_with_promocode: bool = False, cost_for_commission: str = '200',
) -> taximeter.Context:
    return taximeter.Context(
        ind_bel_vat_rate=None,
        cancel_distance=None,
        cancelled_at=None,
        cancelled_with_captcha=False,
        need_dispatcher_acceptance=False,
        cost=decimal.Decimal(100),
        due=dt.datetime(2022, 5, 31, tzinfo=dt.timezone.utc),
        payment_type=consts.PaymentType.CARD,
        status=consts.OrderStatus.FINISHED.value,
        taxi_status=consts.OrderTaxiStatus.COMPLETE.value,
        billing_type=consts.BillingType.NORMAL,
        marketing_level=frozenset([]),
        driver_with_promocode=driver_with_promocode,
        commission_limit_if_promocode=decimal.Decimal(1),
        driver_with_workshift=False,
        rebate_rate=None,
        should_calc_unrealized_if_rebate=False,
        corp_vat_rate=None,
        is_order_successful=True,
        is_paid_cancel_for_user=False,
        is_order_cancelled=False,
        cost_for_commission=var.make_var(cost_for_commission),
    )


def _make_base_commission(
        value: support_info.Var,
        commission_discount: Component = Component.zeroed(),
):
    return Commission(
        value=value,
        commission_discount=commission_discount,
        gross=Component(value.value, decimal.Decimal()),
        vat=var.make_var('0'),
        vat_rate=var.make_var('1'),
        cost=None,
        rate=None,
    )


@pytest.mark.parametrize(
    'agreement_attrs, base_commission, expected_commission',
    [
        pytest.param(
            dict(
                rate=RawRateAbsolute(decimal.Decimal(10)),
                unrealized_commission=None,
            ),
            _make_base_commission(value=var.make_var('1')),
            Commission(
                gross=Component(decimal.Decimal('10'), decimal.Decimal('1')),
                value=var.make_var(
                    '10', [('set', '10', 'set_from_value', '10')],
                ),
                vat=var.make_var(
                    '1', [('set', '1', 'set_from_mul_by_vat_rate', '1')],
                ),
                vat_rate=var.make_var(
                    '1.1', [('set', '1.1', 'set_from_contract_rate', '1.1')],
                ),
                cost=None,
                rate=None,
            ),
        ),
        pytest.param(
            dict(
                rate=RawRateAbsolute(decimal.Decimal(10)),
                unrealized_commission=decimal.Decimal(30),
            ),
            _make_base_commission(value=var.make_var('1')),
            Commission(
                gross=Component(decimal.Decimal('30'), decimal.Decimal('3')),
                commission_discount=Component(
                    decimal.Decimal('20'), decimal.Decimal('2'),
                ),
                value=var.make_var(
                    '10', [('set', '10', 'set_from_value', '10')],
                ),
                vat=var.make_var(
                    '1', [('set', '1', 'set_from_mul_by_vat_rate', '1')],
                ),
                vat_rate=var.make_var(
                    '1.1', [('set', '1.1', 'set_from_contract_rate', '1.1')],
                ),
                cost=None,
                rate=None,
            ),
        ),
        pytest.param(
            dict(
                rate=RawRateAbsolute(decimal.Decimal(10)),
                unrealized_commission=decimal.Decimal(5),
            ),
            _make_base_commission(value=var.make_var('1')),
            Commission(
                gross=Component(decimal.Decimal('10'), decimal.Decimal('1')),
                value=var.make_var(
                    '10', [('set', '10', 'set_from_value', '10')],
                ),
                vat=var.make_var(
                    '1', [('set', '1', 'set_from_mul_by_vat_rate', '1')],
                ),
                vat_rate=var.make_var(
                    '1.1', [('set', '1.1', 'set_from_contract_rate', '1.1')],
                ),
                cost=None,
                rate=None,
            ),
        ),
        pytest.param(
            dict(
                rate=RawRateAbsolute(decimal.Decimal('10')),
                unrealized_commission=decimal.Decimal('30'),
            ),
            _make_base_commission(value=var.make_var('0')),
            Commission(
                gross=Component.zeroed(),
                value=var.make_var(
                    '0', [('set', '0', 'set_from_no_base_commission', '0')],
                ),
                vat=var.make_var(
                    '0', [('set', '0', 'set_from_no_base_commission', '0')],
                ),
                vat_rate=var.make_var(
                    '1', [('set', '1', 'set_from_no_base_commission', '1')],
                ),
                cost=None,
                rate=None,
            ),
            id='no base commission - no taximeter',
        ),
    ],
)
def test_calc_gaap_commission(
        agreement_attrs,
        base_commission,
        expected_commission,
        make_taximeter_agreement,
):
    raw_agreement = make_taximeter_agreement(**agreement_attrs)
    base_calculator = mock.Mock(spec=base.Calculator)
    base_calculator.calculate = mock.Mock(return_value=base_commission)
    base_agreement = mock.Mock(spec=base.Agreement)
    base_agreement.get_calculator = mock.Mock(return_value=base_calculator)
    agreement = taximeter.Agreement(raw_agreement, base_agreement, True)
    commission = agreement.get_calculator().calculate(make_context())
    assert commission == expected_commission
