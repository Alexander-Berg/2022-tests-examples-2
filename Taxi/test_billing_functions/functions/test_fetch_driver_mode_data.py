import pytest

from billing_models.generated import models

from billing_functions.functions import fetch_driver_mode_data
from billing_functions.repositories import driver_mode_subscriptions
from test_billing_functions import equatable
from test_billing_functions import mocks


@pytest.mark.json_obj_hook(
    Query=fetch_driver_mode_data.Query,
    DriverMode=equatable.codegen(models.DriverMode),
    DriverFixSubscription=equatable.codegen(models.DriverFixModeSubscription),
    OrdersSubscription=equatable.codegen(models.OrdersModeSubscription),
    SubsDoc=driver_mode_subscriptions.Doc,
    SubsDocData=driver_mode_subscriptions.Data,
    DriverFixModeSettings=models.DriverFixModeSettings,
)
@pytest.mark.parametrize(
    'test_data_json',
    ['default_mode_if_no_subs.json', 'driver_fix.json', 'orders_mode.json'],
)
async def test_fetch_driver_mode(test_data_json, *, load_py_json):
    test_data = load_py_json(test_data_json)
    query = load_py_json('query.json')
    support_info_repo = mocks.SupportInfo()
    results = await fetch_driver_mode_data.execute(
        mocks.DriverModeSettings(['tag']),
        mocks.Subscriptions(test_data['subscription_doc']),
        support_info_repo,
        query,
    )
    assert results == test_data['expected_results']
    assert support_info_repo.queries == test_data['support_info']
