import pytest

from billing_models.generated import models

from billing_functions.functions import calculate_park_commission


@pytest.mark.json_obj_hook(
    Query=calculate_park_commission.Query,
    Subvention=calculate_park_commission.Query.Subvention,
    ParkCommissionRules=models.ParkCommissionRules,
    BaseParkCommissionRule=models.BaseParkCommissionRule,
)
@pytest.mark.parametrize(
    'test_data_json',
    ['rules_not_found.json', 'subvention.json', 'no_subvention.json'],
)
async def test_calculate_park_commission(test_data_json, load_py_json):
    test_data = load_py_json(test_data_json)
    result = calculate_park_commission.execute(test_data['query'])
    actual = result.serialize() if result else None
    assert actual == test_data['expected']
