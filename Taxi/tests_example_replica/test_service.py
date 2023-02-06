import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from example_replica_plugins.generated_tests import *  # noqa


pytest.CONFIG = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
    },
}

# Every service must have this handler
@pytest.mark.servicetest
@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_ping(taxi_example_replica):
    response = await taxi_example_replica.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


# pylint: disable=undefined-variable
del test_incremental_cache_update  # type: ignore # noqa: F821
