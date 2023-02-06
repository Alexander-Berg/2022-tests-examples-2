# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eda_candidates_plugins import *  # noqa: F403 F401
import pytest

import tests_eda_candidates.courier_positions


@pytest.fixture(name='courier_positions')
def _courier_positions(taxi_eda_candidates, redis_store, testpoint, now):
    async def _publish(positions):
        await tests_eda_candidates.courier_positions.publish(
            taxi_eda_candidates, positions, redis_store, testpoint, now,
        )

    return _publish


@pytest.fixture(autouse=True)
def supply_request(mockserver, load_json):
    @mockserver.json_handler('/eats-core/v1/supply/suppliers-data')
    def _mock_supply_handler(request):
        return load_json('suppliers_data.json')
