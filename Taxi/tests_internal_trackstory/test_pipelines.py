# pylint: disable=import-error
import asyncio  # noqa: F401 C5521

from geobus_tools import geobus  # noqa: F401 C5521


async def test_geobus_subscription(
        taxi_internal_trackstory_adv, redis_store, now, testpoint,
):
    expected = 1

    @testpoint('pipeline_configs_end')
    def pipeline_configs_end(data):
        assert data == expected

    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config.json',
    )

    assert pipeline_configs_end.times_called == 1

    expected = 2

    await taxi_internal_trackstory_adv.update_service_config(
        'pipeline_config_2_pipelines.json',
    )

    assert pipeline_configs_end.times_called == 2
