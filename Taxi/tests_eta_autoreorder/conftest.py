import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eta_autoreorder_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
async def _set_geobus_channel_timelefts(taxi_config):
    taxi_config.set(ETA_AUTOREORDER_GEOBUS_SETTINGS={'use_timelefts': True})
    yield


@pytest.fixture(autouse=True)
async def _clear_tracks_state(taxi_eta_autoreorder):
    yield
    # GeobusEta component is not recreated between consecutive
    # test runs. Clear its state after each test run, so it won't
    # affect next test.
    await taxi_eta_autoreorder.run_task('clear_driver_eta_cache')
