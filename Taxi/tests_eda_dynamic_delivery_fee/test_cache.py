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
async def test_cache_regular_with_old_fees(taxi_eda_dynamic_delivery_fee):
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


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_dynamic_delivery_experiments.json',
)
async def test_cache_regular_no_old_fees(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='1',
        region_id='1',
        device_id='1',
        zone_type='pedestrian',
        distance_to_customer=2.20279026817141,
        old_fees=None,
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


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_no_brand_no_no_region_dynamic_delivery_experiments.json',
)
async def test_cache_regular_no_region(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='1',
        region_id='123',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '489.0000', 'order_price': '0.0000'},
                {'delivery_cost': '439.0000', 'order_price': '500.0000'},
                {'delivery_cost': '439.0000', 'order_price': '2000.0000'},
            ],
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
async def test_cache_regular_no_brand(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='123',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '379.0000', 'order_price': '0.0000'},
                {'delivery_cost': '329.0000', 'order_price': '500.0000'},
                {'delivery_cost': '0.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_no_brand_no_no_region_dynamic_delivery_experiments.json',
)
async def test_cache_regular_no_brand_no_region(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='123',
        region_id='123',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '489.0000', 'order_price': '0.0000'},
                {'delivery_cost': '439.0000', 'order_price': '500.0000'},
                {'delivery_cost': '439.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/exceptional_dynamic_delivery_experiments.json',
)
async def test_cache_exceptional(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='1',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '820.0000', 'order_price': '0.0000'},
                {'delivery_cost': '770.0000', 'order_price': '500.0000'},
                {'delivery_cost': '770.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/skip_threshold_dynamic_delivery_experiments.json',
)
async def test_cache_skip_threshold(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='1',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '479.0000', 'order_price': '0.0000'},
                {'delivery_cost': '429.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache_tiny_rpo_commission.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_dynamic_delivery_experiments.json',
)
async def test_cache_regular_tiny_rpo_commission(
        taxi_eda_dynamic_delivery_fee,
):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='2',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '409.0000', 'order_price': '0.0000'},
                {'delivery_cost': '359.0000', 'order_price': '500.0000'},
                {'delivery_cost': '0.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache_huge_rpo_commission.sql'],
)
@pytest.mark.experiments3(
    filename='eda_dynamic_delivery_fee/regular_dynamic_delivery_experiments.json',
)
async def test_cache_regular_huge_rpo_commission(
        taxi_eda_dynamic_delivery_fee,
):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='2',
        region_id='1',
        device_id='2',
        zone_type='pedestrian',
        distance_to_customer=15,
        old_fees=None,
        expected_status=200,
        expected_response_json={
            'fees': [
                {'delivery_cost': '299.0000', 'order_price': '0.0000'},
                {'delivery_cost': '249.0000', 'order_price': '500.0000'},
                {'delivery_cost': '0.0000', 'order_price': '2000.0000'},
            ],
            'is_fallback': False,
        },
    )
