# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eda_dynamic_delivery_fee_plugins.generated_tests import *

import pytest

from tests_eda_dynamic_delivery_fee.helpers import eda_dynamic_delivery_fee


async def test_insert_cache(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.update_cache(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='123',
        region_id='123',
        zone_type='pedestrian',
        commission='11',
        fixed_commission='12',
        mean_check='13',
        rpo_commission='14',
        expected_status=200,
    )


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
async def test_update_cache(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.update_cache(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='2',
        region_id='1',
        zone_type='pedestrian',
        commission='11',
        fixed_commission='12',
        mean_check='13',
        rpo_commission='14',
        expected_status=200,
    )
