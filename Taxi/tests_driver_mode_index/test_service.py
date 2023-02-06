import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from driver_mode_index_plugins.generated_tests import *  # noqa


# Every service must have this handler
@pytest.mark.servicetest
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG={
        'enabled': False,
        'billing_sync_enabled': False,
        'billing_extended_api': False,
        'billing_sync_job': {'enabled': False, 'batch_size': 100},
        'cleanup_job': {
            'enabled': False,
            'delete_after': 3600,
            'batch_size': 1,
            'delete_limit': 4,
        },
        'metrics_job': {'enabled': False},
    },
)
async def test_ping(taxi_driver_mode_index):
    response = await taxi_driver_mode_index.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
