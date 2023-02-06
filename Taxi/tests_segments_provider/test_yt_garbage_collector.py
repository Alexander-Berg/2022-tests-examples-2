import datetime as dt

import pytest
import pytz

from tests_segments_provider import launch_tools
from tests_segments_provider import shipment_tools
from tests_segments_provider import yt_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_NOW = dt.datetime(2021, 12, 14, 15, 0, 5).astimezone(_TZ_MOSCOW)

_LAUNCH_UUID = 'fd30171401ea49fb8c3651c8679369fc'

_SERVICE_DIR = '//home/taxi/production/features/segments-provider'


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    SEGMENTS_PROVIDER_YT_GARBAGE_COLLECTOR_SETTINGS={
        'is_enabled': True,
        'sleep_duration_ms': 1000,
        'deletion_chunk_size': 5,
    },
)
@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['loginef'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    _NOW, shipment_tools.UnitOfTime.SECONDS, 60,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT 1 FROM [_LAST_RUN_RESULT_];',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    allowed_tag_names=['tag1'], entity_type='udid',
                ),
                created_at=_NOW,
                updated_at=_NOW,
                status=shipment_tools.Status.RUNNING,
            ),
        ),
        launch_tools.get_launch_insert_query(
            'tags',
            'shipment_name',
            launch_tools.Launch(
                uuid=_LAUNCH_UUID,
                started_at=_NOW,
                is_failed=False,
                status='finished',
                errors=[],
                snapshot_status='outdated',
                record_counts=None,
            ),
        ),
    ],
)
async def test_yt_garbage_collector(
        taxi_segments_provider,
        taxi_segments_provider_monitor,
        testpoint,
        pgsql,
        yt_client,
        yt_apply_force,
):
    ready_for_deletion_tables = [
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_append',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_remove',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_tag_names',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_entity_types',
        f'{_SERVICE_DIR}/tmp/tmp/00/01/02',
        f'{_SERVICE_DIR}/tmp/tmp/00/01/03',
    ]

    keeped_tables = [
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_snapshot',
        f'{_SERVICE_DIR}/snapshots/passenger-tags/shipment_2_snapshot',
    ]

    all_tables = keeped_tables + ready_for_deletion_tables

    for table in all_tables:
        yt_client.create_table(
            table,
            recursive=True,
            attributes={'schema': [{'name': 'id', 'type': 'string'}]},
        )

        yt_tools.insert_yt_table(
            pgsql,
            yt_tools.YtTable(
                launch_uuid=_LAUNCH_UUID,
                alias=table.split('/')[-1],
                path=table,
                lifespan='persistent',  # does not matter
                is_marked_for_deletion=table not in keeped_tables,
            ),
        )

    @testpoint('yt-garbage-collector-finished')
    def worker_finished(data):
        pass

    async with taxi_segments_provider.spawn_task('yt-garbage-collector'):
        await worker_finished.wait_call()

    yt_tables = yt_tools.find_yt_tables(pgsql, _LAUNCH_UUID)
    yt_tables = [table.path for table in yt_tables]

    expected_tables = [
        f'{_SERVICE_DIR}/tmp/tmp/00/01/03',
        f'{_SERVICE_DIR}/snapshots/tags/shipment_1_snapshot',
        f'{_SERVICE_DIR}/snapshots/passenger-tags/shipment_2_snapshot',
    ]

    assert yt_tables == expected_tables

    for table in all_tables:
        should_exist = table in expected_tables
        assert yt_client.exists(table) == should_exist

    metrics = await taxi_segments_provider_monitor.get_metric(
        'yt-garbage-collector',
    )
    assert metrics == {'deleted-nodes-count': 5}
