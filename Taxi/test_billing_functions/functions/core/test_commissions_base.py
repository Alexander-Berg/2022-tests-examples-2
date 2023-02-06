import datetime as dt
import decimal
from typing import Optional

import pytest

from billing_functions import consts
from billing_functions.functions.core.commissions import base
from billing_functions.functions.core.commissions import models
from billing_functions.repositories import commission_agreements
from test_billing_functions import var

Commission = models.Commission
BaseCommission = models.BaseCommission
Component = models.Component
RawRate = commission_agreements.Rate
RawRateFlat = commission_agreements.RateFlat


def _make_modifier(acquiring_rate: Optional[decimal.Decimal] = None):
    return base.SubtractAcquiring(**locals())


def _make_context(
        billing_type: consts.BillingType = consts.BillingType.NORMAL,
        payment_type: consts.PaymentType = consts.PaymentType.CARD,
):
    return base.SubtractAcquiringContext(**locals())


@pytest.mark.parametrize(
    'modifier, context, commission, expected_commission',
    [
        pytest.param(
            _make_modifier(),
            _make_context(),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            id='nothing modified due to not asymp',
        ),
        pytest.param(
            _make_modifier(),
            _make_context(billing_type=consts.BillingType.CANCELLED),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            id='nothing modified due to cancelled billing type',
        ),
        pytest.param(
            _make_modifier(),
            _make_context(payment_type=consts.PaymentType.CASH),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            id='nothing modified due to not card-like payment type',
        ),
        pytest.param(
            _make_modifier(acquiring_rate=decimal.Decimal('0.05')),
            _make_context(),
            Commission(
                value=var.make_var('10'),
                vat=var.make_var('2'),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
            ),
            Commission(
                value=var.make_var(
                    '5', [('sub', '5', 'sub_acquiring_commission', '5')],
                ),
                vat=var.make_var(
                    '1', [('sub', '1', 'sub_acquiring_vat', '1')],
                ),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('5'), decimal.Decimal('1')),
            ),
            id='subtracted acquiring rate',
        ),
    ],
)
def test_subtract_agent_and_acquiring(
        modifier, context, commission, expected_commission,
):
    actual = modifier.apply(context, commission)
    assert actual == expected_commission


@pytest.mark.json_obj_hook(
    Context=base.Context,
    # raw agreement
    Agreement=commission_agreements.Agreement,
    RateFlat=commission_agreements.RateFlat,
    CancellationSettings=commission_agreements.CancellationSettings,
    CancellationInterval=commission_agreements.CancellationInterval,
    BrandingDiscount=commission_agreements.BrandingDiscount,
    CostInfoBoundaries=commission_agreements.CostInfoBoundaries,
    CostInfoAbsolute=commission_agreements.CostInfoAbsolute,
    # agreements
    Base=base.Agreement,
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        'test_data.json',
        'test_data_with_driver_promocode.json',
        'test_data_with_driver_workshift.json',
        'test_data_with_rebate.json',
    ],
)
def test_calc_commission_from_subvention(test_data_json, *, load_py_json):
    test_data = load_py_json(test_data_json)
    context: base.Context = test_data['context']
    subvention: decimal.Decimal = test_data['subvention']
    agreement: base.Agreement = load_py_json('agreement.json')
    commission, unrealized = (
        agreement.calc_commission_and_unrealized_from_subvention(
            context, subvention,
        )
    )
    expected_results = test_data['expected']
    assert commission == expected_results['commission']
    assert unrealized == expected_results['unrealized']


@pytest.fixture(name='make_base_agreement')
def _make_base_agreement(make_agreement):
    def _builder(
            unrealized_rate: Optional[decimal.Decimal] = decimal.Decimal(
                '0.2',
            ),
    ):
        return make_agreement(
            kind=consts.CommissionKind.FIXED_RATE.value,
            group=consts.CommissionGroup.BASE.value,
            rate=RawRateFlat(decimal.Decimal('0.05')),
            unrealized_rate=unrealized_rate,
            vat_rate=decimal.Decimal('1.2'),
        )

    return _builder


def make_context(
        driver_with_promocode: bool = False, cost_for_commission: str = '200',
) -> base.Context:
    return base.Context(
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


@pytest.mark.parametrize(
    'agreement_attrs, context, expected_commission',
    [
        pytest.param(
            {},
            make_context(),
            BaseCommission(
                gross=Component(decimal.Decimal('40'), decimal.Decimal('8')),
                commission_discount=Component(
                    decimal.Decimal('30'), decimal.Decimal('6'),
                ),
                value=var.make_var(
                    '10', [('set', '10', 'set_from_mul_cost_by_rate', '10')],
                ),
                vat=var.make_var(
                    '2', [('set', '2', 'set_from_mul_by_vat_rate', '2')],
                ),
                vat_rate=var.make_var(
                    '1.2', [('set', '1.2', 'set_from_contract_rate', '1.2')],
                ),
                cost=var.make_var('200'),
                rate=var.make_var(
                    '0.05',
                    [('set', '0.05', 'set_from__billing_type_rate', '0.05')],
                ),
                eventual_cost=decimal.Decimal('200'),
            ),
        ),
        pytest.param(
            {},
            make_context(driver_with_promocode=True),
            BaseCommission(
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
                promocode_discount=Component(
                    value=decimal.Decimal('9.166666666666666666666666667'),
                    vat=decimal.Decimal('1.833333333333333333333333333'),
                ),
                value=var.make_var(
                    '0.8333333333333333333333333333',
                    [
                        (
                            'set',
                            '0.8333333333333333333333333333',
                            'set_from_driver_promocode_commission',
                            '0.8333333333333333333333333333',
                        ),
                    ],
                ),
                vat=var.make_var(
                    '0.1666666666666666666666666667',
                    [
                        (
                            'set',
                            '0.1666666666666666666666666667',
                            'set_from_driver_promocode',
                            '0.1666666666666666666666666667',
                        ),
                    ],
                ),
                vat_rate=var.make_var(
                    '1.2', [('set', '1.2', 'set_from_contract_rate', '1.2')],
                ),
                cost=var.make_var('200'),
                unrealized=Component(
                    value=decimal.Decimal('9.166666666666666666666666667'),
                    vat=decimal.Decimal('1.833333333333333333333333333'),
                ),
                unrealized_without_discount_value=decimal.Decimal(
                    '9.166666666666666666666666667',
                ),
                rate=var.make_var(
                    '0.05',
                    [('set', '0.05', 'set_from__billing_type_rate', '0.05')],
                ),
                eventual_cost=decimal.Decimal('200'),
            ),
            id='no unrealized discount because commission for both rates is 1',
        ),
        pytest.param(
            {},
            make_context(driver_with_promocode=True, cost_for_commission='10'),
            BaseCommission(
                gross=Component(
                    decimal.Decimal('0.8333333333333333333333333333'),
                    decimal.Decimal('0.1666666666666666666666666667'),
                ),
                commission_discount=Component(
                    value=decimal.Decimal('0.3333333333333333333333333333'),
                    vat=decimal.Decimal('0.0666666666666666666666666667'),
                ),
                value=var.make_var(
                    '0.5',
                    [('set', '0.5', 'set_from_mul_cost_by_rate', '0.5')],
                ),
                vat=var.make_var(
                    '0.1', [('set', '0.1', 'set_from_mul_by_vat_rate', '0.1')],
                ),
                vat_rate=var.make_var(
                    '1.2', [('set', '1.2', 'set_from_contract_rate', '1.2')],
                ),
                cost=var.make_var('10'),
                rate=var.make_var(
                    '0.05',
                    [('set', '0.05', 'set_from__billing_type_rate', '0.05')],
                ),
                eventual_cost=decimal.Decimal('10'),
            ),
            id=(
                'there is unrealized discount because '
                'of commission for unrealized rate is 1'
                'but for real rate is 0.6'
            ),
        ),
        pytest.param(
            dict(unrealized_rate=None),
            make_context(),
            BaseCommission(
                gross=Component(decimal.Decimal('10'), decimal.Decimal('2')),
                value=var.make_var(
                    '10', [('set', '10', 'set_from_mul_cost_by_rate', '10')],
                ),
                vat=var.make_var(
                    '2', [('set', '2', 'set_from_mul_by_vat_rate', '2')],
                ),
                vat_rate=var.make_var(
                    '1.2', [('set', '1.2', 'set_from_contract_rate', '1.2')],
                ),
                cost=var.make_var('200'),
                rate=var.make_var(
                    '0.05',
                    [('set', '0.05', 'set_from__billing_type_rate', '0.05')],
                ),
                eventual_cost=decimal.Decimal('200'),
            ),
            id='no unrealized rate',
        ),
    ],
)
def test_calc_gaap_commission(
        agreement_attrs, context, expected_commission, make_base_agreement,
):
    base_agreement = make_base_agreement(**agreement_attrs)
    agreement = base.Agreement(base_agreement, None, True)
    commission = agreement.get_calculator().calculate(context)
    assert commission == expected_commission
