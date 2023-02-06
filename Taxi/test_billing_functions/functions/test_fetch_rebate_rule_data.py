import pytest

from billing_models.generated import models

from billing_functions import consts
from billing_functions.functions import fetch_rebate_rule_data
from billing_functions.repositories import migration_mode
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=fetch_rebate_rule_data.Query,
    RebateMigrationMode=migration_mode.Mode,
    RebateRule=equatable.codegen(models.RebateRule),
    PaymentType=consts.PaymentType,
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        'query.json',
        'query_rebate.json',
        'query_mode_order.json',
        'query_mode_service.json',
        'query_mode_test.json',
    ],
)
async def test_fetch_rebate_rule(
        test_data_json,
        stq3_context,
        *,
        load_py_json,
        monkeypatch,
        mock_billing_commissions,
):
    test_data = load_py_json(test_data_json)
    mock_billing_commissions(
        rebate_agreement=test_data.get('rebate_agreement'),
    )
    results = await fetch_rebate_rule_data.execute(
        stq3_context.rebate_rates, test_data['query'],
    )
    assert results == test_data['expected_results']
