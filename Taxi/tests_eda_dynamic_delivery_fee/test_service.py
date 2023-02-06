# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eda_dynamic_delivery_fee_plugins.generated_tests import *

import pytest

from tests_eda_dynamic_delivery_fee.helpers import eda_dynamic_delivery_fee


@pytest.mark.pgsql(
    'eda_dynamic_delivery_fee',
    files=['eda_dynamic_delivery_fee/fill_cache.sql'],
)
async def test_not_found(taxi_eda_dynamic_delivery_fee):
    await eda_dynamic_delivery_fee.calculate(
        taxi_eda_dynamic_delivery_fee=taxi_eda_dynamic_delivery_fee,
        brand_id='123',
        region_id='123',
        device_id='123',
        zone_type='yandex_taxi',
        distance_to_customer=15,
        old_fees=None,
        expected_status=404,
        expected_response_json={
            'code': 'not-found',
            'message': 'Fees not found',
        },
    )
