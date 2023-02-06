# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eda_dynamic_delivery_fee_plugins.generated_tests import *

import pytest

from tests_eda_dynamic_delivery_fee.helpers import eda_dynamic_delivery_fee


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
async def test_fallback(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='any-brand',
        region_id='1',
        device_id='any-device',
        zone_type='pedestrian',
        distance_to_customer=3,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'order_price': '0.0000', 'delivery_cost': '169.0000'},
                {'order_price': '500.0000', 'delivery_cost': '119.0000'},
            ],
            'is_fallback': True,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/missing_dynamic_delivery_experiments.json',
)
async def test_missing_experiment_result(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='2',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=3,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'order_price': '0.0000', 'delivery_cost': '169.0000'},
                {'order_price': '500.0000', 'delivery_cost': '119.0000'},
            ],
            'is_fallback': True,
        },
    )
