import pytest

from billing_models.generated import models

from billing_functions.functions import load_shift_orders
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=load_shift_orders.Query,
    Account=load_shift_orders.Query.Account,
    ShiftOrders=equatable.codegen(models.ShiftOrders),
)
@pytest.mark.parametrize('test_data_json', ['happy_path.json', 'limited.json'])
async def test_load_progress(
        test_data_json,
        *,
        stq3_context,
        load_py_json,
        do_mock_billing_reports,
        do_mock_billing_accounts,
):
    test_data = load_py_json(test_data_json)
    do_mock_billing_reports()
    do_mock_billing_accounts(existing_entries=test_data['entries'])
    actual_result = await load_shift_orders.execute(
        stq3_context.journal, test_data['query'],
    )
    assert actual_result == test_data['expected_result']
