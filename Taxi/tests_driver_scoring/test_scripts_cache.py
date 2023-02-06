import pytest


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_js_scripts_cache(taxi_driver_scoring):
    await taxi_driver_scoring.invalidate_caches()
