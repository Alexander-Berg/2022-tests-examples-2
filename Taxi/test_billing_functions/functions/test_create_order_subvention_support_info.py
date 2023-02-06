import pytest

from billing_functions.functions import create_order_subvention_support_info
from test_billing_functions import mocks


@pytest.mark.json_obj_hook(Query=create_order_subvention_support_info.Query)
@pytest.mark.parametrize(
    'test_data_json', ['zero_values.json', 'non_zero_values.json'],
)
async def test_fetch_driver_mode(test_data_json, *, load_py_json):
    test_data = load_py_json(test_data_json)
    query = test_data['query']
    support_info_repo = mocks.SupportInfo()
    await create_order_subvention_support_info.execute(
        support_info_repo, query,
    )
    assert support_info_repo.queries == test_data['support_info']
