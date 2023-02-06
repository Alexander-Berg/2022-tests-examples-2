import pytest

from billing_models.generated import models

from billing_functions.functions import calculate_park_commission_value
from test_billing_functions import equatable


@pytest.mark.json_obj_hook(
    Query=calculate_park_commission_value.Query,
    ParkCommissionValue=equatable.codegen(models.ParkCommissionValue),
    ParkCommissionRules=models.ParkCommissionRules,
    BaseParkCommissionRule=models.BaseParkCommissionRule,
)
@pytest.mark.parametrize(
    'function_query_json, function_result_json',
    [
        ('function_query.json', 'function_result.json'),
        (
            'function_query_rules_not_found.json',
            'function_result_rules_not_found.json',
        ),
    ],
)
async def test_calculate_park_commission_value(
        load_py_json, function_query_json, function_result_json,
):
    query = load_py_json(function_query_json)
    expected = load_py_json(function_result_json)
    results = calculate_park_commission_value.execute(query=query)
    assert results == expected['function_results']
