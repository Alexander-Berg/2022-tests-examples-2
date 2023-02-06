import dataclasses

import pytest

from billing_functions.functions.core.commissions import acquiring
from billing_functions.functions.core.commissions import base
from billing_functions.functions.core.commissions import call_center
from billing_functions.functions.core.commissions import hiring
from billing_functions.functions.core.commissions import models
from billing_functions.functions.core.commissions import taximeter
from billing_functions.repositories import commission_agreements


@dataclasses.dataclass(frozen=True)
class Context(
        acquiring.Context,
        # base.Context,
        call_center.Context,
        hiring.Context,
        taximeter.Context,
):
    pass


@pytest.mark.json_obj_hook(
    Context=Context,
    SupportInfoHiring=commission_agreements.SupportInfoHiring,
    # raw agreement
    HiringInfo=commission_agreements.Query.HiringInfo,
    Agreement=commission_agreements.Agreement,
    RateFlat=commission_agreements.RateFlat,
    RateAbsolute=commission_agreements.RateAbsolute,
    RateAsymptotic=commission_agreements.RateAsymptotic,
    CancellationSettings=commission_agreements.CancellationSettings,
    CancellationInterval=commission_agreements.CancellationInterval,
    BrandingDiscount=commission_agreements.BrandingDiscount,
    CostInfoBoundaries=commission_agreements.CostInfoBoundaries,
    CostInfoAbsolute=commission_agreements.CostInfoAbsolute,
    # agreements
    Base=base.Agreement,
    Hiring=hiring.Agreement,
    Acquiring=acquiring.Agreement,
    Taximeter=taximeter.Agreement,
    CallCenter=call_center.Agreement,
    CallCenterRate=call_center.Rate,
    # result
    Component=models.Component,
    Commission=models.Commission,
    BaseCommission=models.BaseCommission,
)
@pytest.mark.parametrize(
    'agreement_json, order_json, expected_commission_json',
    [
        # fixed
        (
            'fixed_rate/agreement.json',
            'order_context.json',
            'fixed_rate/expected_commission_and_vat.json',
        ),
        (
            'fixed_rate/agreement.json',
            'order_with_rebate_context.json',
            'fixed_rate/expected_commission_and_vat_for_rebate.json',
        ),
        (
            'fixed_rate/agreement.json',
            'too_high_cost_order_context.json',
            'fixed_rate/expected_high_cost_commission_and_vat.json',
        ),
        (
            'fixed_rate/agreement.json',
            'too_low_cost_order_context.json',
            'fixed_rate/expected_low_cost_commission_and_vat.json',
        ),
        (
            'fixed_rate/agreement.json',
            'order_with_driver_promocode_context.json',
            'fixed_rate/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'fixed_rate/agreement.json',
            'order_with_driver_workshift_context.json',
            'fixed_rate/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'fixed_rate/agreement.json',
            'not_billable_order_context.json',
            'fixed_rate/expected_not_billable_commission_and_vat.json',
        ),
        # absolute
        (
            'absolute_value/agreement.json',
            'order_context.json',
            'absolute_value/expected_commission_and_vat.json',
        ),
        (
            'absolute_value/agreement.json',
            'order_with_driver_promocode_context.json',
            'absolute_value/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'absolute_value/agreement.json',
            'order_with_driver_workshift_context.json',
            'absolute_value/expected_commission_and_vat_driver_workshift.json',
        ),
        # asymptotic
        (
            'asymptotic_rate/agreement.json',
            'order_context.json',
            'asymptotic_rate/expected_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/agreement_for_card_order.json',
            'card_order_context.json',
            'asymptotic_rate/expected_card_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/agreement.json',
            'too_high_cost_order_context.json',
            'asymptotic_rate/expected_high_cost_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/agreement.json',
            'too_low_cost_order_context.json',
            'asymptotic_rate/expected_low_cost_commission_and_vat.json',
        ),
        (
            'asymptotic_rate/agreement.json',
            'order_with_driver_promocode_context.json',
            'asymptotic_rate/'
            'expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'asymptotic_rate/agreement.json',
            'order_with_driver_workshift_context.json',
            'asymptotic_rate/'
            'expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'call_center/agreement.json',
            'order_context.json',
            'call_center/expected_commission_and_vat.json',
        ),
        (
            'call_center/agreement.json',
            'order_with_driver_promocode_context.json',
            'call_center/expected_commission_and_vat.json',
        ),
        (
            'call_center/agreement.json',
            'order_with_driver_workshift_context.json',
            'call_center/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'hiring/agreement.json',
            'order_context.json',
            'hiring/expected_commission_and_vat_with_hiring.json',
        ),
        (
            'hiring/agreement.json',
            'order_with_hiring_with_rent_context.json',
            'hiring/expected_commission_and_vat_with_hiring_with_rent.json',
        ),
        (
            'hiring/agreement.json',
            'order_with_rebate_context.json',
            'hiring/expected_commission_and_vat_for_rebate.json',
        ),
        (
            'hiring/agreement.json',
            'order_with_rebate_and_inner_vat_context.json',
            'hiring/expected_commission_and_vat_for_rebate_with_inner_vat'
            '.json',
        ),
        (
            'hiring/agreement.json',
            'order_with_driver_promocode_context.json',
            'hiring/expected_commission_and_vat_with_hiring.json',
        ),
        (
            'hiring/agreement.json',
            'order_with_driver_workshift_context.json',
            'hiring/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'acquiring/agreement.json',
            'card_order_context.json',
            'acquiring/expected_commission_and_vat_card_order.json',
        ),
        (
            'acquiring/agreement.json',
            'cash_order_context.json',
            'acquiring/expected_commission_and_vat_cash_order.json',
        ),
        (
            'acquiring/agreement.json',
            'order_with_driver_promocode_context.json',
            'acquiring/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'acquiring/agreement.json',
            'order_with_driver_workshift_context.json',
            'acquiring/expected_commission_and_vat_driver_workshift.json',
        ),
        (
            'taximeter/agreement.json',
            'order_context.json',
            'taximeter/expected_commission_and_vat.json',
        ),
        (
            'taximeter/zero_agreement.json',
            'order_context.json',
            'taximeter/expected_zero_commission_and_vat.json',
        ),
        (
            'taximeter/agreement.json',
            'order_with_driver_promocode_context.json',
            'taximeter/expected_commission_and_vat_driver_promocode.json',
        ),
        (
            'taximeter/agreement.json',
            'order_with_driver_workshift_context.json',
            'taximeter/expected_commission_and_vat_driver_workshift.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_commission_details(
        agreement_json,
        order_json,
        expected_commission_json,
        *,
        load_json,
        load_py_json,
):
    context = load_py_json(order_json)
    agreement = load_py_json(agreement_json)
    expected = load_py_json(expected_commission_json)

    actual = agreement.get_calculator().calculate(context)
    assert expected == actual
