import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest
import pytz

from tests_segments_provider import launch_tools
from tests_segments_provider import shipment_tools
from tests_segments_provider import tags_tools
from tests_segments_provider import yt_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')
_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 5))

_CURRENT_LAUNCH_ID = 'fd30171401ea49fb8c3651c8679369fc'
_SNAPSHOT_PATH = '//snapshot'

_SNAPSHOT_SCHEMA = {
    'path': _SNAPSHOT_PATH,
    'attributes': {
        'schema': [
            {'name': 'entity_value', 'type': 'string'},
            {'name': 'entity_type', 'type': 'string'},
            {'name': 'tag', 'type': 'string'},
            {'name': 'ttl', 'type': 'string'},
        ],
    },
}

_SNAPSHOT_DB_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_ID,
    alias='snapshot',
    path=_SNAPSHOT_PATH,
    lifespan='persistent',
    is_marked_for_deletion=False,
)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    SEGMENTS_PROVIDER_TAGS_UPLOADER_SETTINGS={
        '__default__': {
            'is_enabled': True,
            'upload_chunk_size': 3,
            'running_tasks_chunk_size': 10,
            'sleep_duration_ms': 10,
        },
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
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT 1;',
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
                uuid=_CURRENT_LAUNCH_ID,
                started_at=_NOW,
                is_failed=False,
                status='executing_consumer',
                errors=[],
                snapshot_status='prepared',
                record_counts=None,
            ),
        ),
        yt_tools.get_insert_yt_table_query(_SNAPSHOT_DB_TABLE),
    ],
)
@pytest.mark.yt(
    schemas=[_SNAPSHOT_SCHEMA],
    static_table_data=[
        {
            'path': _SNAPSHOT_PATH,
            'values': [
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
                {
                    'tag': 'tag2',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
                {
                    'tag': 'tag1',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'fd5b4e8d6aec42c18aa2942643163348',
                    'ttl': '2022-05-25T12:00:00+0300',
                },
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': '8fc41a003cf44c2199cd86ed8985e74b',
                    'ttl': 'infinity',
                },
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'discard_task, expected_discard_task, expected_tags_call',
    [
        pytest.param(
            tags_tools.DiscardTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                total_snapshot_records=4,
                processed_snapshot_records=0,
            ),
            tags_tools.DiscardTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                total_snapshot_records=4,
                processed_snapshot_records=3,
            ),
            {
                'remove': [
                    {
                        'entity_type': 'dbid_uuid',
                        'tags': [
                            {
                                'entity': 'fd5b4e8d6aec42c18aa2942643163348',
                                'name': 'tag1',
                            },
                        ],
                    },
                    {
                        'entity_type': 'udid',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag1',
                            },
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag2',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            id='chunk_1',
        ),
        pytest.param(
            tags_tools.DiscardTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                total_snapshot_records=4,
                processed_snapshot_records=3,
            ),
            tags_tools.DiscardTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                total_snapshot_records=4,
                processed_snapshot_records=4,
            ),
            {
                'remove': [
                    {
                        'entity_type': 'udid',
                        'tags': [
                            {
                                'entity': '8fc41a003cf44c2199cd86ed8985e74b',
                                'name': 'tag1',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            id='chunk_2',
        ),
        pytest.param(
            tags_tools.DiscardTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                total_snapshot_records=4,
                processed_snapshot_records=4,
            ),
            tags_tools.DiscardTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                total_snapshot_records=4,
                processed_snapshot_records=4,
            ),
            None,
            id='skip',
        ),
    ],
)
async def test_discard_task(
        taxi_segments_provider,
        testpoint,
        mockserver,
        pgsql,
        yt_client,
        yt_apply_force,
        discard_task: tags_tools.DiscardTask,
        expected_discard_task: tags_tools.DiscardTask,
        expected_tags_call: Optional[Dict[str, Any]],
):
    tags_tools.insert_discard_task(pgsql, discard_task)

    @testpoint('tags-uploader-finished')
    def tags_uploader_finished(data):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def upload_handler(request):
        return {'status': 'ok'}

    async with taxi_segments_provider.spawn_task('tags-uploader'):
        await tags_uploader_finished.wait_call()

    discard_task = tags_tools.find_discard_task(
        pgsql, launch_uuid=_CURRENT_LAUNCH_ID,
    )
    assert discard_task == expected_discard_task

    if expected_tags_call:
        assert upload_handler.has_calls
        tags_request = upload_handler.next_call()['request'].json
        assert tags_request == expected_tags_call
    else:
        assert not upload_handler.has_calls
