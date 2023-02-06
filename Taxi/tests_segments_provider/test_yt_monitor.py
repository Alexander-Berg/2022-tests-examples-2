import datetime as dt

import pytest
import pytz

from tests_segments_provider import common_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 5))

_SERVICE_DIR = '//home/taxi/production/features/segments-provider'


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    SEGMENTS_PROVIDER_YT_MONITOR_SETTINGS={
        'is_enabled': True,
        'sleep_duration_ms': 10000,
    },
)
async def test_yt_monitor(
        taxi_segments_provider,
        taxi_segments_provider_monitor,
        testpoint,
        yt_client,
        yt_apply_force,
):
    tables = [
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_append',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_remove',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_snapshot',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_tag_names',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_entity_types',
        f'{_SERVICE_DIR}/snapshots/passenger-tags/shipment_1_snapshot',
        f'{_SERVICE_DIR}/tmp/tmp/00/01/02',
        f'{_SERVICE_DIR}/tmp/tmp/00/01/03',
    ]

    for table in tables:
        yt_client.create_table(
            table,
            recursive=True,
            attributes={'schema': [{'name': 'id', 'type': 'string'}]},
        )

    testpoint_handler = common_tools.WorkerTestpointWithMetrics(
        testpoint, taxi_segments_provider_monitor, 'yt-monitor',
    )

    async with taxi_segments_provider.spawn_task('yt-monitor'):
        await testpoint_handler.worker_finished.wait_call()

    expected_nodes_count = len(
        [
            f'{_SERVICE_DIR}',
            f'{_SERVICE_DIR}/snapshots',
            f'{_SERVICE_DIR}/snapshots/tags',
            f'{_SERVICE_DIR}/snapshots/tags/shipment_1_append',
            f'{_SERVICE_DIR}/snapshots/tags/shipment_1_remove',
            f'{_SERVICE_DIR}/snapshots/tags/shipment_1_snapshot',
            f'{_SERVICE_DIR}/snapshots/tags/shipment_1_tag_names',
            f'{_SERVICE_DIR}/snapshots/tags/shipment_1_entity_types',
            f'{_SERVICE_DIR}/snapshots/passenger-tags',
            f'{_SERVICE_DIR}/snapshots/passenger-tags/shipment_1_snapshot',
            f'{_SERVICE_DIR}/tmp/',
            f'{_SERVICE_DIR}/tmp/tmp',
            f'{_SERVICE_DIR}/tmp/tmp/00',
            f'{_SERVICE_DIR}/tmp/tmp/00/01',
            f'{_SERVICE_DIR}/tmp/tmp/00/01/02',
            f'{_SERVICE_DIR}/tmp/tmp/00/01/03',
        ],
    )

    assert testpoint_handler.metrics == {
        'yt-nodes-count': expected_nodes_count,
    }
