import pytest

from billing_models.generated import models

from billing_functions.functions import check_order
from test_billing_functions import equatable


@pytest.mark.parametrize('test_data_json', ('order.json', 'old_order.json'))
@pytest.mark.json_obj_hook(
    # query
    Query=check_order.Query,
    ProcessingInfo=equatable.codegen(models.ProcessingInfo),
    Money=models.Money,
)
async def test_check_order(test_data_json, *, load_py_json, stq3_context):
    test_data = load_py_json(test_data_json)
    results = await check_order.execute(stq3_context, test_data['query'])
    assert results == test_data['expected_results']
