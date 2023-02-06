import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from order_events_producer_plugins.generated_tests import *  # noqa


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(
        taxi_order_events_producer, taxi_eventus_orchestrator_mock,
):
    response = await taxi_order_events_producer.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_incremental_cache_update(
        taxi_order_events_producer, taxi_eventus_orchestrator_mock,
):
    await taxi_order_events_producer.invalidate_caches(clean_update=False)
