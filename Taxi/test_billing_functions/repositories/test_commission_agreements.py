import pytest

from billing_functions.repositories import commission_agreements


@pytest.mark.parametrize('test_data_json', ('happy_path.json',))
@pytest.mark.json_obj_hook(
    Query=commission_agreements.Query,
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
)
async def test_match(
        test_data_json,
        *,
        load_py_json,
        mock_billing_commissions,
        stq3_context,
):
    mock_billing_commissions(
        agreements=load_py_json('commissions_response.json'),
    )
    test_data = load_py_json(test_data_json)
    repo = stq3_context.commission_agreements
    agreements = await repo.match(test_data['query'])
    assert agreements == test_data['expected_agreements']


@pytest.mark.json_obj_hook(
    Query=commission_agreements.FineQuery,
    Agreement=commission_agreements.Agreement,
    RateAbsolute=commission_agreements.RateAbsolute,
    CancellationSettings=commission_agreements.CancellationSettings,
    CancellationInterval=commission_agreements.CancellationInterval,
    BrandingDiscount=commission_agreements.BrandingDiscount,
    CostInfoBoundaries=commission_agreements.CostInfoBoundaries,
    CostInfoAbsolute=commission_agreements.CostInfoAbsolute,
)
async def test_match_fines(
        load_py_json,
        mock_billing_commissions,
        stq3_context,
        *,
        test_data_json='test_data.json',
):
    test_data = load_py_json('test_data.json')
    billing_commissions = mock_billing_commissions(
        agreements=test_data['commissions_response'],
    )
    test_data = load_py_json(test_data_json)
    repo = stq3_context.commission_agreements
    agreements = await repo.match_fines(test_data['query'])
    assert billing_commissions.rules_match_requests == (
        test_data['expected_requests']
    )
    assert agreements == test_data['expected_agreements']
