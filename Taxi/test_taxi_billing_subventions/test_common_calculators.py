import typing as tp

import pytest

from taxi_billing_subventions import config as config_module
from taxi_billing_subventions.common import calculators
from taxi_billing_subventions.common import db as db_module
from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'order_json, zone_by_name_json, '
    'config_json, order_completed_data_json, expected_cost_details_json',
    [
        (
            'order.json',
            'zone_by_name.json',
            'config.json',
            'order_completed_data.json',
            'cost_details.json',
        ),
        (
            'order_with_unknown_discount.json',
            'zone_by_name.json',
            'config.json',
            'order_completed_data.json',
            'zero_discount_cost_details.json',
        ),
        (
            'order.json',
            'zone_by_name.json',
            'config.json',
            'order_completed_data_with_cost_for_driver.json',
            'cost_details_with_cost_for_driver.json',
        ),
        (
            'cancelled_cash_order.json',
            'zone_by_name.json',
            'config.json',
            'order_completed_data_with_cost_for_driver.json',
            'cancelled_cost_details_with_cost_for_driver.json',
        ),
        (
            'applepay_order.json',
            'zone_by_name.json',
            'config.json',
            'order_completed_data_applepay.json',
            'applepay_cost_details.json',
        ),
        (
            'order_with_call_center_cost.json',
            'zone_by_name.json',
            'config.json',
            'order_completed_data.json',
            'cost_details_with_call_center_cost.json',
        ),
    ],
)
@pytest.mark.filldb(commission_contracts='for_test_get_cost_details')
async def test_get_cost_details(
        order_json,
        zone_by_name_json,
        config_json,
        order_completed_data_json,
        expected_cost_details_json,
        db,
        billing_subventions_app,
        load_py_json_dir,
):
    order: models.calculators.Order
    zone_by_name: tp.Dict[str, models.Zone]
    config: config_module.Config
    order_completed_data: models.doc.OrderCompletedData
    order, zone_by_name, config, expected_cost_details = load_py_json_dir(
        'test_get_cost_details',
        order_json,
        zone_by_name_json,
        config_json,
        expected_cost_details_json,
    )
    order_completed_data = load_py_json_dir(
        'test_get_cost_details', order_completed_data_json,
    )
    cost_context = await db_module.fetch_cost_context(
        database=billing_subventions_app.db,
        order=order,
        zone_by_name=zone_by_name,
        config=config,
        commissions_client=billing_subventions_app.billing_commissions_client,
        log_extra=None,
    )

    actual_cost_details = calculators.get_cost_details(
        cost_context.order,
        order_completed_data,
        cost_context.commission_agreements,
        log_extra=None,
        use_call_center_cost=order_json == 'order_with_call_center_cost.json',
    )
    assert expected_cost_details == actual_cost_details
