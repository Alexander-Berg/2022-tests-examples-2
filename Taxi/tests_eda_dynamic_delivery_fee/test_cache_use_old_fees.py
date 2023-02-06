# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eda_dynamic_delivery_fee_plugins.generated_tests import *

import pytest

from tests_eda_dynamic_delivery_fee.helpers import eda_dynamic_delivery_fee


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_dynamic_delivery_experiments.json',
)
@pytest.mark.config(EDA_DYNAMIC_DELIVERY_FEE_USE_OLD_FEES_ENABLED=True)
async def test_cache_regular_old_fees_enabled(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='2',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=2.20279026817141,
        old_fees=[{'delivery_cost': '150.0000', 'order_price': '100.0000'}],
        expected_status=200,
        expected_response_json={
            'fees': [{'delivery_cost': '150.0000', 'order_price': '100.0000'}],
            'is_fallback': False,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_dynamic_delivery_experiments.json',
)
@pytest.mark.config(EDA_DYNAMIC_DELIVERY_FEE_USE_OLD_FEES_ENABLED=False)
async def test_cache_regular_old_fees_disabled(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='1',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=2.20279026817141,
        old_fees=[{'delivery_cost': '150.0000', 'order_price': '100.0000'}],
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '179.0000', 'order_price': '0.0000'},
                {'delivery_cost': '129.0000', 'order_price': '500.0000'},
                {'delivery_cost': '0.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )
