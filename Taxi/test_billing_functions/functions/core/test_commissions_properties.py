import pytest

from billing_functions.functions.core.commissions import acquiring
from billing_functions.functions.core.commissions import base
from billing_functions.functions.core.commissions import call_center
from billing_functions.functions.core.commissions import hiring
from billing_functions.functions.core.commissions import taximeter
from billing_functions.repositories import commission_agreements


@pytest.mark.json_obj_hook(
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
)
@pytest.mark.parametrize(
    'agreement_json, expected_status',
    [
        ('agreement_absolute_value.json', False),
        ('agreement_asymptotic.json', False),
        ('agreement_fixed.json', False),
        ('agreement_fixed_cancel.json', False),
        ('agreement_fixed_cancel_non_zero.json', True),
    ],
)
@pytest.mark.nofilldb()
def test_use_minimal_tariff_cost_enabled(
        agreement_json, expected_status, *, load_json, load_py_json,
):
    agreement: base.Agreement = load_py_json(agreement_json)

    assert expected_status == agreement.use_minimal_tariff_cost
