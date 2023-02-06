# pylint: disable=C0302

import datetime as dt
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest
import pytz

from tests_segments_provider import common_tools
from tests_segments_provider import launch_tools
from tests_segments_provider import quota_tools
from tests_segments_provider import shipment_tools
from tests_segments_provider import tags_tools
from tests_segments_provider import yt_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_NOW = _TZ_MOSCOW.localize(dt.datetime(2021, 12, 14, 15, 0, 5))

_CURRENT_LAUNCH_ID = 'fd30171401ea49fb8c3651c8679369fc'


_APPEND_PATH = '//append'
_ENTITY_TYPES_PATH = '//entity_types'
_REMOVE_PATH = '//remove'
_TAG_NAMES_PATH = '//tag_names'
_SNAPSHOT_PATH = '//snapshot'

_APPEND_SCHEMA = {
    'path': _APPEND_PATH,
    'attributes': {
        'schema': [
            {'name': 'entity_value', 'type': 'string'},
            {'name': 'entity_type', 'type': 'string'},
            {'name': 'tag', 'type': 'string'},
            {'name': 'ttl', 'type': 'string'},
        ],
    },
}

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

_REMOVE_SCHEMA = {
    'path': _REMOVE_PATH,
    'attributes': {
        'schema': [
            {'name': 'entity_value', 'type': 'string'},
            {'name': 'entity_type', 'type': 'string'},
            {'name': 'tag', 'type': 'string'},
        ],
    },
}

_TAG_NAMES_SCHEMA = {
    'path': _TAG_NAMES_PATH,
    'attributes': {'schema': [{'name': 'tag', 'type': 'string'}]},
}

_ENTITY_TYPES_SCHEMA = {
    'path': _ENTITY_TYPES_PATH,
    'attributes': {'schema': [{'name': 'entity_type', 'type': 'string'}]},
}

_APPEND_DB_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_ID,
    alias='append',
    path=_APPEND_PATH,
    lifespan='till_end_of_launch',
    is_marked_for_deletion=False,
)

_REMOVE_DB_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_ID,
    alias='remove',
    path=_REMOVE_PATH,
    lifespan='till_end_of_launch',
    is_marked_for_deletion=False,
)

_ENTITY_TYPES_DB_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_ID,
    alias='entity_types',
    path=_ENTITY_TYPES_PATH,
    lifespan='till_end_of_launch',
    is_marked_for_deletion=False,
)

_TAG_NAMES_DB_TABLE = yt_tools.YtTable(
    launch_uuid=_CURRENT_LAUNCH_ID,
    alias='tag_names',
    path=_TAG_NAMES_PATH,
    lifespan='till_end_of_launch',
    is_marked_for_deletion=False,
)

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
            'upload_chunk_size': 500,
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
    ],
)
@pytest.mark.yt(
    schemas=[
        _APPEND_SCHEMA,
        _REMOVE_SCHEMA,
        _TAG_NAMES_SCHEMA,
        _ENTITY_TYPES_SCHEMA,
        _SNAPSHOT_SCHEMA,
    ],
    static_table_data=[
        {
            'path': _APPEND_PATH,
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
                    'entity_type': 'udid',
                    'entity_value': 'fd5b4e8d6aec42c18aa2942643163348',
                    'ttl': '2022-05-25T12:00:00+0300',
                },
            ],
        },
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
                    'entity_type': 'udid',
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
        {
            'path': _REMOVE_PATH,
            'values': [
                {
                    'tag': 'tag3',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                },
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                },
            ],
        },
        {
            'path': _TAG_NAMES_PATH,
            'values': [{'tag': 'tag1'}, {'tag': 'tag2'}],
        },
        {'path': _ENTITY_TYPES_PATH, 'values': [{'entity_type': 'udid'}]},
    ],
)
@pytest.mark.parametrize(
    'yt_tables_in_db, expected_upload_task',
    [
        pytest.param(
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
                _SNAPSHOT_DB_TABLE,
            ],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='checking',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=4,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            id='ok',
        ),
        pytest.param(
            [_ENTITY_TYPES_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=[
                    'Required yt tables missing in DB: '
                    'tag_names, snapshot, append',
                ],
                started_at=_NOW,
                upload_state=None,
            ),
            id='missing_table',
        ),
    ],
)
async def test_upload_task_new(
        taxi_segments_provider,
        testpoint,
        mockserver,
        pgsql,
        yt_client,
        yt_tables_in_db: List[yt_tools.YtTable],
        expected_upload_task: tags_tools.UploadTask,
):
    tags_tools.insert_upload_task(
        pgsql,
        tags_tools.UploadTask(
            launch_uuid=_CURRENT_LAUNCH_ID,
            status='new',
            is_failed=False,
            error_messages=[],
            started_at=_NOW,
            upload_state=None,
        ),
    )

    for table in yt_tables_in_db:
        yt_tools.insert_yt_table(pgsql, table)

    @testpoint('tags-uploader-finished')
    def tags_uploader_finished(data):
        pass

    async with taxi_segments_provider.spawn_task('tags-uploader'):
        await tags_uploader_finished.wait_call()

    upload_task = tags_tools.find_upload_task(
        pgsql, launch_uuid=_CURRENT_LAUNCH_ID,
    )
    assert upload_task == expected_upload_task


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    SEGMENTS_PROVIDER_TAGS_UPLOADER_SETTINGS={
        '__default__': {
            'is_enabled': True,
            'upload_chunk_size': 500,
            'running_tasks_chunk_size': 10,
            'sleep_duration_ms': 10,
        },
    },
)
@pytest.mark.yt(
    schemas=[
        _APPEND_SCHEMA,
        _REMOVE_SCHEMA,
        _TAG_NAMES_SCHEMA,
        _ENTITY_TYPES_SCHEMA,
    ],
)
@pytest.mark.parametrize(
    'allowed_tag_names, entity_type, yt_tables_in_db, '
    'entity_types_table_content, tag_names_table_content, '
    'expected_upload_task, quota_assignments',
    [
        pytest.param(
            ['tag1', 'tag2'],
            'udid',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [{'entity_type': 'udid'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='ok',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'udid',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
                _SNAPSHOT_DB_TABLE,
            ],
            [{'entity_type': 'udid'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            {
                'efficiency': [
                    quota_tools.Assignment(
                        name=quota_tools.TAGS_COUNT, value=1000,
                    ),
                ],
            },
            id='ok_with_quota_assignment',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'udid',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [{'entity_type': 'udid'}],
            [{'tag': 'tag1'}, {'tag': 'tag3'}, {'tag': 'tag4'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=[
                    'Following tag names were not listed in shipment '
                    'settings: tag3,tag4',
                ],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='unlisted_tag_names',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'udid',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [
                {'entity_type': 'udid'},
                {'entity_type': 'dbid_uuid'},
                {'entity_type': 'park'},
            ],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=[
                    'Following entity types were not listed in shipment '
                    'settings: dbid_uuid,park',
                ],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='unlisted_entity_types',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'fasdfasgafa',  # unparsable entity type
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [{'entity_type': 'fasdfasgafa'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=['Invalid entity types: fasdfasgafa'],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='unparsable_entity_type',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'store_item_id',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [{'entity_type': 'store_item_id'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=['Invalid entity types: store_item_id'],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='different_consumer_entity_type',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            None,
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [
                {'entity_type': 'dbid_uuid'},
                {'entity_type': 'udid'},
                {'entity_type': 'park'},
            ],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='no_entity_type_restriction',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            None,
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [{'entity_type': 'udid'}],
            [{'tag': None}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=[
                    'Failed to parse tag name: got nullptr_t instead of '
                    'string. All tag names must be strings',
                ],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='null_tag_name',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            None,
            [_APPEND_DB_TABLE, _ENTITY_TYPES_DB_TABLE, _REMOVE_DB_TABLE],
            [{'entity_type': 'udid'}],
            [{'tag': None}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=['Missing tag_names table'],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='missing_tag_names_table',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            None,
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE, _TAG_NAMES_DB_TABLE],
            [{'entity_type': 'udid'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=['Missing entity_types table'],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            None,
            id='missing_entity_types_table',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'udid',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
            ],
            [{'entity_type': 'udid'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=['Missing snapshot_table table'],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            {
                'efficiency': [
                    quota_tools.Assignment(
                        name=quota_tools.TAGS_COUNT, value=1000,
                    ),
                ],
            },
            id='bad_missing_snaphost_table_for_tags_count_assignment',
        ),
        pytest.param(
            ['tag1', 'tag2'],
            'udid',
            [
                _APPEND_DB_TABLE,
                _ENTITY_TYPES_DB_TABLE,
                _REMOVE_DB_TABLE,
                _TAG_NAMES_DB_TABLE,
                _SNAPSHOT_DB_TABLE,
            ],
            [{'entity_type': 'udid'}],
            [{'tag': 'tag1'}, {'tag': 'tag2'}],
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=True,
                error_messages=[
                    'Snapshot\'s tags_count exceeded assignment limits',
                ],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=3,
                    total_remove_table_rows=2,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            {
                'efficiency': [
                    quota_tools.Assignment(
                        name=quota_tools.TAGS_COUNT, value=1,
                    ),
                ],
            },
            id='bad_tags_count_exceed_limits',
        ),
    ],
)
async def test_upload_task_checking(
        taxi_segments_provider,
        testpoint,
        mockserver,
        pgsql,
        yt_client,
        allowed_tag_names: List[str],
        entity_type: Optional[str],
        yt_tables_in_db: List[yt_tools.YtTable],
        entity_types_table_content: List[Dict[str, Any]],
        tag_names_table_content: List[Dict[str, Any]],
        expected_upload_task: tags_tools.UploadTask,
        quota_assignments,
):
    shipment_tools.insert_shipment(
        pgsql,
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
                allowed_tag_names=allowed_tag_names, entity_type=entity_type,
            ),
            created_at=_NOW,
            updated_at=_NOW,
            status=shipment_tools.Status.RUNNING,
        ),
    )

    launch_tools.insert_launch(
        pgsql,
        consumer_name='tags',
        shipment_name='shipment_name',
        launch=launch_tools.Launch(
            uuid=_CURRENT_LAUNCH_ID,
            started_at=_NOW,
            is_failed=False,
            status='executing_consumer',
            errors=[],
            snapshot_status='prepared',
            record_counts=None,
        ),
    )

    tags_tools.insert_upload_task(
        pgsql,
        tags_tools.UploadTask(
            launch_uuid=_CURRENT_LAUNCH_ID,
            status='checking',
            is_failed=False,
            error_messages=[],
            started_at=_NOW,
            upload_state=tags_tools.UploadState(
                total_append_table_rows=3,
                total_remove_table_rows=2,
                total_snapshot_table_rows=20,
                processed_append_table_rows=0,
                processed_remove_table_rows=0,
                appended_tags=0,
                removed_tags=0,
                malformed_rows=0,
            ),
        ),
    )

    quota_tools.insert_quotas(
        pgsql, {'efficiency': {quota_tools.TAGS_COUNT: 9999}},
    )

    if quota_assignments:
        for owner, assignments in quota_assignments.items():
            quota_tools.insert_assignments(
                pgsql, 'shipment_name', 'tags', owner, assignments,
            )

    @testpoint('tags-uploader-finished')
    def tags_uploader_finished(data):
        pass

    for table in yt_tables_in_db:
        yt_tools.insert_yt_table(pgsql, table)

    yt_client.write_table(
        _ENTITY_TYPES_PATH, entity_types_table_content, force_create=False,
    )

    yt_client.write_table(
        _TAG_NAMES_PATH, tag_names_table_content, force_create=False,
    )

    async with taxi_segments_provider.spawn_task('tags-uploader'):
        await tags_uploader_finished.wait_call()

    upload_task = tags_tools.find_upload_task(
        pgsql, launch_uuid=_CURRENT_LAUNCH_ID,
    )
    assert upload_task == expected_upload_task


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.yt(
    schemas=[
        _APPEND_SCHEMA,
        _REMOVE_SCHEMA,
        {
            'path': '//append_passenger_tags',
            'attributes': _APPEND_SCHEMA['attributes'],
        },
        {
            'path': '//append_eats_tags',
            'attributes': _APPEND_SCHEMA['attributes'],
        },
        {
            'path': '//append_grocery_tags',
            'attributes': _APPEND_SCHEMA['attributes'],
        },
        _TAG_NAMES_SCHEMA,
        _ENTITY_TYPES_SCHEMA,
    ],
    static_table_data=[
        {
            'path': _APPEND_PATH,
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
                    'entity_type': 'udid',
                    'entity_value': 'fd5b4e8d6aec42c18aa2942643163348',
                    'ttl': '2022-05-25T12:00:00+0300',
                },
                {
                    'tag': 'tag1',
                    'entity_type': 'udid',
                    'entity_value': None,
                    'ttl': 'infinity',
                },
            ],
        },
        {
            'path': '//append_passenger_tags',
            'values': [
                {
                    'tag': 'tag1',
                    'entity_type': 'user_id',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
            ],
        },
        {
            'path': '//append_eats_tags',
            'values': [
                {
                    'tag': 'tag1',
                    'entity_type': 'place_id',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
            ],
        },
        {
            'path': '//append_grocery_tags',
            'values': [
                {
                    'tag': 'tag1',
                    'entity_type': 'store_id',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                    'ttl': 'infinity',
                },
            ],
        },
        {
            'path': _REMOVE_PATH,
            'values': [
                {
                    'tag': 'tag3',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                },
                {'tag': 'tag1', 'entity_type': 'udid', 'entity_value': None},
                {
                    'tag': 'tag4',
                    'entity_type': 'park',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                },
                {
                    'tag': 'tag5',
                    'entity_type': 'udid',
                    'entity_value': '097ccaddcb06413e8537ee6f228a7b7b',
                },
                {
                    'tag': 'tag4',
                    'entity_type': 'park',
                    'entity_value': 'fd5b4e8d6aec42c18aa2942643163348',
                },
                {
                    'tag': 'tag5',
                    'entity_type': 'udid',
                    'entity_value': 'fd5b4e8d6aec42c18aa2942643163348',
                },
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'worker_name, consumer_name, yt_tables_in_db, current_upload_state, '
    'chunk_size, fail_tags_request, expected_tags_request, '
    'expected_appended_tags, expected_removed_tags, expected_tasks_no_error, '
    'expected_tasks_with_error, expected_upload_task',
    [
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=0,
                processed_remove_table_rows=0,
                appended_tags=0,
                removed_tags=0,
                malformed_rows=0,
            ),
            2,  # chunk size
            False,  # do not fail upload request
            {
                'append': [
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
            2,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=2,
                    processed_remove_table_rows=0,
                    appended_tags=2,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            id='append_first_chunk',
        ),
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=2,
                processed_remove_table_rows=0,
                appended_tags=2,
                removed_tags=0,
                malformed_rows=0,
            ),
            2,  # chunk size
            False,  # do not fail upload request
            {
                'append': [
                    {
                        'entity_type': 'udid',
                        'tags': [
                            {
                                'entity': 'fd5b4e8d6aec42c18aa2942643163348',
                                'name': 'tag1',
                                'until': '2022-05-25T09:00:00+0000',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            1,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=4,
                    processed_remove_table_rows=0,
                    appended_tags=3,
                    removed_tags=0,
                    malformed_rows=1,
                ),
            ),
            id='append_second_chunk',
        ),
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=4,
                processed_remove_table_rows=0,
                appended_tags=3,
                removed_tags=0,
                malformed_rows=1,
            ),
            2,  # chunk size
            False,  # do not fail upload request
            {
                'remove': [
                    {
                        'entity_type': 'udid',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag3',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            0,  # expected_appended_tags
            1,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=4,
                    processed_remove_table_rows=2,
                    appended_tags=3,
                    removed_tags=1,
                    malformed_rows=2,
                ),
            ),
            id='remove_first_chunk',
        ),
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=4,
                processed_remove_table_rows=2,
                appended_tags=3,
                removed_tags=1,
                malformed_rows=2,
            ),
            50,  # chunk size
            False,  # do not fail upload request
            {
                'remove': [
                    {
                        'entity_type': 'udid',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag5',
                            },
                            {
                                'entity': 'fd5b4e8d6aec42c18aa2942643163348',
                                'name': 'tag5',
                            },
                        ],
                    },
                    {
                        'entity_type': 'park',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag4',
                            },
                            {
                                'entity': 'fd5b4e8d6aec42c18aa2942643163348',
                                'name': 'tag4',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            0,  # expected_appended_tags
            4,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=4,
                    processed_remove_table_rows=6,
                    appended_tags=3,
                    removed_tags=5,
                    malformed_rows=2,
                ),
            ),
            id='remove_second_chunk',
        ),
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=4,
                processed_remove_table_rows=6,
                appended_tags=3,
                removed_tags=5,
                malformed_rows=2,
            ),
            2,  # chunk size
            False,  # do not fail upload request
            None,  # No tags request
            0,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='finished',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=4,
                    processed_remove_table_rows=6,
                    appended_tags=3,
                    removed_tags=5,
                    malformed_rows=2,
                ),
            ),
            id='finish_upload',
        ),
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=4,
                processed_remove_table_rows=1,
                appended_tags=3,
                removed_tags=0,
                malformed_rows=1,
            ),
            1,  # chunk size
            False,  # do not fail upload request
            None,  # do not upload tags
            0,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=4,
                    processed_remove_table_rows=2,
                    appended_tags=3,
                    removed_tags=0,
                    malformed_rows=2,
                ),
            ),
            id='malformed_chunk_no_upload',
        ),
        pytest.param(
            'tags-uploader',
            'tags',
            [_APPEND_DB_TABLE, _REMOVE_DB_TABLE],
            tags_tools.UploadState(
                total_append_table_rows=4,
                total_remove_table_rows=6,
                total_snapshot_table_rows=20,
                processed_append_table_rows=4,
                processed_remove_table_rows=1,
                appended_tags=3,
                removed_tags=0,
                malformed_rows=1,
            ),
            2,  # chunk size
            True,  # fail upload request
            {
                'remove': [
                    {
                        'entity_type': 'park',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag4',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            0,  # expected_appended_tags
            0,  # expected_removed_tags
            0,  # expected_tasks_no_error
            1,  # expected_tasks_with_error
            # no changes, will retry
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=4,
                    total_remove_table_rows=6,
                    total_snapshot_table_rows=20,
                    processed_append_table_rows=4,
                    processed_remove_table_rows=1,
                    appended_tags=3,
                    removed_tags=0,
                    malformed_rows=1,
                ),
            ),
            id='upload_fail',
        ),
        pytest.param(
            'passenger-tags-uploader',
            'passenger-tags',
            [
                yt_tools.YtTable(
                    launch_uuid=_CURRENT_LAUNCH_ID,
                    alias='append',
                    path='//append_passenger_tags',
                    lifespan='till_end_of_launch',
                    is_marked_for_deletion=False,
                ),
                _REMOVE_DB_TABLE,
            ],
            tags_tools.UploadState(
                total_append_table_rows=1,
                total_remove_table_rows=0,
                total_snapshot_table_rows=1,
                processed_append_table_rows=0,
                processed_remove_table_rows=0,
                appended_tags=0,
                removed_tags=0,
                malformed_rows=0,
            ),
            1,  # chunk size
            False,  # do not fail upload request
            {
                'append': [
                    {
                        'entity_type': 'user_id',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag1',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            1,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=1,
                    total_remove_table_rows=0,
                    total_snapshot_table_rows=1,
                    processed_append_table_rows=1,
                    processed_remove_table_rows=0,
                    appended_tags=1,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            id='append_passenger_tags',
        ),
        pytest.param(
            'eats-tags-uploader',
            'eats-tags',
            [
                yt_tools.YtTable(
                    launch_uuid=_CURRENT_LAUNCH_ID,
                    alias='append',
                    path='//append_eats_tags',
                    lifespan='till_end_of_launch',
                    is_marked_for_deletion=False,
                ),
                _REMOVE_DB_TABLE,
            ],
            tags_tools.UploadState(
                total_append_table_rows=1,
                total_remove_table_rows=0,
                total_snapshot_table_rows=1,
                processed_append_table_rows=0,
                processed_remove_table_rows=0,
                appended_tags=0,
                removed_tags=0,
                malformed_rows=0,
            ),
            1,  # chunk size
            False,  # do not fail upload request
            {
                'append': [
                    {
                        'entity_type': 'place_id',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag1',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            1,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=1,
                    total_remove_table_rows=0,
                    total_snapshot_table_rows=1,
                    processed_append_table_rows=1,
                    processed_remove_table_rows=0,
                    appended_tags=1,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            id='append_eats_tags',
        ),
        pytest.param(
            'grocery-tags-uploader',
            'grocery-tags',
            [
                yt_tools.YtTable(
                    launch_uuid=_CURRENT_LAUNCH_ID,
                    alias='append',
                    path='//append_grocery_tags',
                    lifespan='till_end_of_launch',
                    is_marked_for_deletion=False,
                ),
                _REMOVE_DB_TABLE,
            ],
            tags_tools.UploadState(
                total_append_table_rows=1,
                total_remove_table_rows=0,
                total_snapshot_table_rows=1,
                processed_append_table_rows=0,
                processed_remove_table_rows=0,
                appended_tags=0,
                removed_tags=0,
                malformed_rows=0,
            ),
            1,  # chunk size
            False,  # do not fail upload request
            {
                'append': [
                    {
                        'entity_type': 'store_id',
                        'tags': [
                            {
                                'entity': '097ccaddcb06413e8537ee6f228a7b7b',
                                'name': 'tag1',
                            },
                        ],
                    },
                ],
                'provider_id': 'seagull_shipment_name',
            },
            1,  # expected_appended_tags
            0,  # expected_removed_tags
            1,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=1,
                    total_remove_table_rows=0,
                    total_snapshot_table_rows=1,
                    processed_append_table_rows=1,
                    processed_remove_table_rows=0,
                    appended_tags=1,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            id='append_grocery_tags',
        ),
        pytest.param(
            'tags-uploader',
            'grocery-tags',
            [
                yt_tools.YtTable(
                    launch_uuid=_CURRENT_LAUNCH_ID,
                    alias='append',
                    path='//append_grocery_tags',
                    lifespan='till_end_of_launch',
                    is_marked_for_deletion=False,
                ),
                _REMOVE_DB_TABLE,
            ],
            tags_tools.UploadState(
                total_append_table_rows=1,
                total_remove_table_rows=0,
                total_snapshot_table_rows=1,
                processed_append_table_rows=0,
                processed_remove_table_rows=0,
                appended_tags=0,
                removed_tags=0,
                malformed_rows=0,
            ),
            1,  # chunk size
            False,  # do not fail upload request
            None,
            0,  # expected_appended_tags
            0,  # expected_removed_tags
            0,  # expected_tasks_no_error
            0,  # expected_tasks_with_error
            tags_tools.UploadTask(
                launch_uuid=_CURRENT_LAUNCH_ID,
                status='uploading',
                is_failed=False,
                error_messages=[],
                started_at=_NOW,
                upload_state=tags_tools.UploadState(
                    total_append_table_rows=1,
                    total_remove_table_rows=0,
                    total_snapshot_table_rows=1,
                    processed_append_table_rows=0,
                    processed_remove_table_rows=0,
                    appended_tags=0,
                    removed_tags=0,
                    malformed_rows=0,
                ),
            ),
            id='append_grocery_tags_wrong_worker',
        ),
    ],
)
async def test_upload_task_uploading(
        taxi_segments_provider,
        taxi_segments_provider_monitor,
        testpoint,
        mockserver,
        pgsql,
        yt_client,
        taxi_config,
        worker_name: str,
        consumer_name: str,
        yt_tables_in_db: List[yt_tools.YtTable],
        current_upload_state: tags_tools.UploadState,
        chunk_size: int,
        fail_tags_request: bool,
        expected_tags_request: Dict[str, Any],
        expected_appended_tags: int,
        expected_removed_tags: int,
        expected_tasks_no_error: int,
        expected_tasks_with_error: int,
        expected_upload_task: tags_tools.UploadTask,
):
    shipment_tools.insert_shipment(
        pgsql,
        consumer_name,
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
                allowed_tag_names=['tag1', 'tag2'], entity_type=None,
            ),
            created_at=_NOW,
            updated_at=_NOW,
            status=shipment_tools.Status.RUNNING,
        ),
    )

    launch_tools.insert_launch(
        pgsql,
        consumer_name=consumer_name,
        shipment_name='shipment_name',
        launch=launch_tools.Launch(
            uuid=_CURRENT_LAUNCH_ID,
            started_at=_NOW,
            is_failed=False,
            status='executing_consumer',
            errors=[],
            snapshot_status='partially_applied',
            record_counts=None,
        ),
    )

    tags_tools.insert_upload_task(
        pgsql,
        tags_tools.UploadTask(
            launch_uuid=_CURRENT_LAUNCH_ID,
            status='uploading',
            is_failed=False,
            error_messages=[],
            started_at=_NOW,
            upload_state=current_upload_state,
        ),
    )

    for table in yt_tables_in_db:
        yt_tools.insert_yt_table(pgsql, table)

    taxi_config.set_values(
        dict(
            SEGMENTS_PROVIDER_TAGS_UPLOADER_SETTINGS={
                '__default__': {
                    'is_enabled': True,
                    'upload_chunk_size': chunk_size,
                    'running_tasks_chunk_size': 10,
                    'sleep_duration_ms': 10,
                },
            },
        ),
    )

    testpoint_handler = common_tools.WorkerTestpointWithMetrics(
        testpoint, taxi_segments_provider_monitor, worker_name,
    )

    @mockserver.json_handler(f'{consumer_name}/v2/upload')
    def upload_handler(request):
        if fail_tags_request:
            raise mockserver.TimeoutError()
        return {'status': 'ok'}

    async with taxi_segments_provider.spawn_task(worker_name):
        await testpoint_handler.worker_finished.wait_call()

    if expected_tags_request:
        assert upload_handler.has_calls
        tags_request = upload_handler.next_call()['request'].json
        assert tags_request == expected_tags_request
    else:
        assert not upload_handler.has_calls

    upload_task = tags_tools.find_upload_task(
        pgsql, launch_uuid=_CURRENT_LAUNCH_ID,
    )
    assert upload_task == expected_upload_task

    assert testpoint_handler.metrics == {
        'processed-tasks': {
            'no-error': expected_tasks_no_error,
            'with-error': expected_tasks_with_error,
        },
        'uploaded-tags': {
            'appended': expected_appended_tags,
            'removed': expected_removed_tags,
        },
    }
