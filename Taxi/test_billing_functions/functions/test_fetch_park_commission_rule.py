import pytest

from billing_models.generated import models

from billing_functions.functions import fetch_park_commission_rules
from test_billing_functions import equatable

TEST_DOC_ID = 18061991


@pytest.mark.parametrize(
    'dwm_responses_json, expected_results_json',
    [
        ('dwm_responses_200.json', 'function_result_response_200.json'),
        ('dwm_responses_404.json', 'function_result_response_404.json'),
    ],
)
@pytest.mark.json_obj_hook(
    Query=fetch_park_commission_rules.Query,
    QueryOrder=fetch_park_commission_rules.Query.Order,
    ParkCommissionRules=equatable.codegen(models.ParkCommissionRules),
    ParkCommissionRule=models.BaseParkCommissionRule,
    OrderParkCommissionRule=models.OrderParkCommissionRule,
)
async def test_fetch_park_commission_rule(
        dwm_responses_json,
        expected_results_json,
        load_py_json,
        stq3_context,
        mock_driver_work_modes,
):
    query = load_py_json('function_query.json')
    expected = load_py_json(expected_results_json)
    dwm_mocker = mock_driver_work_modes(dwm_responses_json)

    results = await fetch_park_commission_rules.execute(
        driver_work_modes_client=stq3_context.clients.driver_work_modes,
        query=query,
    )
    assert results == expected['function_results']
    assert dwm_mocker.requests == expected['dwm_requests']
