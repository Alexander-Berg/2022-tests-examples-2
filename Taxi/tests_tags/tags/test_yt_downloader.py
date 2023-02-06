# pylint: disable=C5521, W0621
import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools
from tests_tags.tags.yql_services_fixture import (  # noqa: F401
    local_yql_services,
)


_SNAPSHOT_PATH = 'home/snapshot'
_APPEND_PATH = 'home/append'
_REMOVE_PATH = 'home/remove'
_TAGS_YT_DOWNLOADER_CHUNK_SIZE = 3
_NOW = datetime.datetime.now()
_TEST_TTL = tags_tools.time_to_str(_NOW + datetime.timedelta(hours=1))
_INFINITY = datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)

_CORRECT_ENTITY: Dict[str, Optional[str]] = {
    'tag': 'topvipcars',
    'entity_type': 'dbid_uuid',
    'entity_value': 'entity',
}
_CORRECT_ENTITY_WITH_TTL: Dict[str, Any] = {
    'tag': 'topvipcars',
    'entity_type': 'dbid_uuid',
    'entity_value': 'entity',
    'ttl': _INFINITY,
}


@pytest.mark.pgsql(
    'tags',
    queries=[tags_tools.insert_providers([tags_tools.Provider.from_id(0)])],
)
@pytest.mark.config(
    TAGS_YT_DOWNLOADER_CHUNK_SIZE=_TAGS_YT_DOWNLOADER_CHUNK_SIZE,
)
@pytest.mark.parametrize('status', ['failed', 'description', 'finished'])
async def test_not_running_tasks(taxi_tags, status: str, pgsql):
    db = pgsql['tags']
    cursor = db.cursor()
    cursor.execute(
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    0, 's', 'a', None, 359, status, malformed_rows_count=0,
                ),
            ],
        ),
    )

    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    rows = tags_select.select_table_named(
        'service.yt_download_tasks', 'provider_id', db,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row['provider_id'] == 0
    assert row['status'] == status
    assert row['current_row'] == 359


def _insert_snapshot_with_syntax(db, query_syntax):
    with db.cursor() as cursor:
        cursor.execute(
            yql_tools.insert_snapshot(
                yql_tools.YtSnapshot(
                    0,
                    _SNAPSHOT_PATH,
                    _NOW,
                    'description',
                    query_syntax=query_syntax,
                ),
            ),
        )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    0,
                    _SNAPSHOT_PATH,
                    _APPEND_PATH,
                    (_REMOVE_PATH, 'dbid_uuid'),
                    status='in_progress',
                    malformed_rows_count=0,
                ),
            ],
        ),
        yql_tools.insert_operation(
            '0', 0, 'dbid_uuid', 'downloading', _NOW.isoformat(),
        ),
    ],
)
@pytest.mark.config(
    TAGS_YT_DOWNLOADER_CHUNK_SIZE=_TAGS_YT_DOWNLOADER_CHUNK_SIZE,
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YT_SKIP_MALFORMED_ROWS=True,
)
@pytest.mark.parametrize(
    'query_syntax, use_dynamic_entity_type',
    [('CLICKHOUSE', False), ('SQLv1', False), ('SQLv1', True)],
)
async def test_task_usual_update(
        taxi_tags,
        yt_client,
        local_yql_services,  # noqa: F811
        pgsql,
        query_syntax,
        use_dynamic_entity_type,
):
    chunk_size = 40
    if query_syntax == 'SQLv1':
        ttl_frequency = 5
        ttl = _TEST_TTL
    else:
        ttl_frequency = None
        ttl = None
    db = pgsql['tags']
    _insert_snapshot_with_syntax(db, query_syntax)

    data = yql_tools.generate_and_insert_tags(
        db,
        local_yql_services,
        tags_count=chunk_size * 3,
        tags_to_insert=chunk_size * 2,
        entity_type=None if use_dynamic_entity_type else 'dbid_uuid',
        query_syntax=query_syntax,
        ttl_frequency=ttl_frequency,
        ttl=ttl,
    )

    # In the beginning we have 80 tags [0:80], [80:120] are not inserted
    # After "yql execution" in append path we have [80:120] tags
    append_data = data[chunk_size * 2 : chunk_size * 3]
    # and remove table has [0:40] tags.
    remove_data = data[0:chunk_size]
    # so, after all we should have [40:120] tags

    yt_client.write_table('//' + _APPEND_PATH, append_data)
    yt_client.write_table('//' + _REMOVE_PATH, remove_data)

    for i in range(chunk_size // _TAGS_YT_DOWNLOADER_CHUNK_SIZE + 1):
        yql_tools.verify_yt_download_task(
            db,
            0,
            'in_progress',
            i * _TAGS_YT_DOWNLOADER_CHUNK_SIZE,
            _APPEND_PATH,
            _REMOVE_PATH,
            0,
        )
        await tags_tools.activate_task(taxi_tags, 'yt-downloader')
        yql_tools.verify_snapshot_status(db, 'partially_applied')
    yql_tools.verify_yt_download_task(
        db, 0, 'in_progress', 0, None, _REMOVE_PATH, 0,
    )

    for i in range(chunk_size // _TAGS_YT_DOWNLOADER_CHUNK_SIZE + 1):
        yql_tools.verify_yt_download_task(
            db,
            0,
            'in_progress',
            i * _TAGS_YT_DOWNLOADER_CHUNK_SIZE,
            None,
            _REMOVE_PATH,
            0,
        )
        yql_tools.verify_snapshot_status(db, 'partially_applied')
        await tags_tools.activate_task(taxi_tags, 'yt-downloader')

    yql_tools.verify_snapshot_status(db, 'fully_applied')
    yql_tools.verify_yt_download_task(db, 0, 'finished', 0, None, None, 0)

    await tags_tools.activate_task(taxi_tags, 'customs-officer')
    expected_tags = list(
        yql_tools.gen_tags(
            0,
            0,
            range(chunk_size, chunk_size * 3),
            entity_type=None if use_dynamic_entity_type else 'dbid_uuid',
            ttl_frequency=ttl_frequency,
            ttl=ttl,
        ),
    )
    tags_tools.verify_active_tags(db, expected_tags)


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    0,
                    snapshot_path=_SNAPSHOT_PATH,
                    append_path=_SNAPSHOT_PATH,
                    remove_info=None,
                    status='in_progress',
                    malformed_rows_count=0,
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(0, _SNAPSHOT_PATH, _NOW, 'description'),
        ),
        yql_tools.insert_operation(
            '0', 0, 'dbid_uuid', 'downloading', _NOW.isoformat(),
        ),
    ],
)
@pytest.mark.config(
    TAGS_YT_DOWNLOADER_CHUNK_SIZE=_TAGS_YT_DOWNLOADER_CHUNK_SIZE,
    UTAGS_YQL_WORKER_ENABLED=True,
)
@pytest.mark.parametrize('use_dynamic_entity_type', [(False, True)])
async def test_task_update_from_scratch(
        taxi_tags,
        yt_client,
        local_yql_services,  # noqa: F811
        pgsql,
        use_dynamic_entity_type,
):
    db = pgsql['tags']
    data = yql_tools.generate_and_insert_tags(
        db,
        local_yql_services,
        tags_count=60,
        tags_to_insert=0,
        entity_type=None if use_dynamic_entity_type else 'dbid_uuid',
    )

    yt_client.write_table('//' + _SNAPSHOT_PATH, data)

    for i in range(60 // _TAGS_YT_DOWNLOADER_CHUNK_SIZE):
        yql_tools.verify_yt_download_task(
            db,
            0,
            'in_progress',
            i * _TAGS_YT_DOWNLOADER_CHUNK_SIZE,
            _SNAPSHOT_PATH,
            None,
            0,
        )
        await tags_tools.activate_task(taxi_tags, 'yt-downloader')
        yql_tools.verify_snapshot_status(db, 'partially_applied')

    # need to execute it two more times
    # for yt-downloader to see, that there is no data in snapshot path
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    yql_tools.verify_snapshot_status(db, 'partially_applied')
    # for yt-downloader to see, that there are no paths left
    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    # assert snapshot was not deleted
    assert yt_client.exists('//' + _SNAPSHOT_PATH)

    yql_tools.verify_yt_download_task(db, 0, 'finished', 0, None, None, 0)
    yql_tools.verify_snapshot_status(db, 'fully_applied')
    await tags_tools.activate_task(taxi_tags, 'customs-officer')

    tags_tools.verify_active_tags(
        db,
        list(
            yql_tools.gen_tags(
                0,
                0,
                range(0, 60),
                entity_type=None if use_dynamic_entity_type else 'dbid_uuid',
            ),
        ),
    )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    0,
                    snapshot_path=_SNAPSHOT_PATH,
                    append_path=_SNAPSHOT_PATH,
                    remove_info=None,
                    status='in_progress',
                    malformed_rows_count=0,
                ),
            ],
        ),
        yql_tools.insert_operation(
            '0', 0, 'dbid_uuid', 'downloading', _NOW.isoformat(),
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(0, _SNAPSHOT_PATH, _NOW, 'description'),
        ),
    ],
)
@pytest.mark.parametrize(
    'table_exists, task_state',
    [
        # if table still exists, task should not be failed
        (True, 'in_progress'),
        # but if table is not there, nothing can be done
        (False, 'failed'),
    ],
)
@pytest.mark.config(UTAGS_YQL_WORKER_ENABLED=True)
async def test_task_yt_fail(
        taxi_tags, yt_client, pgsql, table_exists, task_state, yt_apply_force,
):
    if table_exists:
        yt_client.create_table(
            '//' + _SNAPSHOT_PATH,
            attributes={
                'schema': [
                    {'name': 'tag', 'type': 'string'},
                    {'name': 'dbid_uuid', 'type': 'string'},
                ],
                'dynamic': True,  # this makes read_table fail
            },
        )

    db = pgsql['tags']
    await tags_tools.activate_task(taxi_tags, 'yt-downloader', 500)
    yql_tools.verify_yt_download_task(
        db, 0, task_state, 0, _SNAPSHOT_PATH, None, 0,
    )


@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        yql_tools.insert_yt_download_tasks(
            [
                yql_tools.YtDownloadTask(
                    0,
                    snapshot_path=_SNAPSHOT_PATH,
                    append_path=_SNAPSHOT_PATH,
                    remove_info=None,
                    status='in_progress',
                    malformed_rows_count=0,
                ),
            ],
        ),
        yql_tools.insert_snapshot(
            yql_tools.YtSnapshot(0, _SNAPSHOT_PATH, _NOW, 'description'),
        ),
        yql_tools.insert_operation(
            '0', 0, 'dbid_uuid', 'downloading', _NOW.isoformat(),
        ),
    ],
)
@pytest.mark.config(
    TAGS_YT_DOWNLOADER_CHUNK_SIZE=_TAGS_YT_DOWNLOADER_CHUNK_SIZE,
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_YT_SKIP_MALFORMED_ROWS=True,
)
@pytest.mark.parametrize(
    'yt_data, expected_tags, skip_nulls, expected_codes, nulls_count',
    [
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': f'entity{i%2}',
                    'ttl': 'infinity',
                }
                for i in range(3)  # entity0 present twice
            ],
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': f'entity{i}',
                    'ttl': _INFINITY,
                }
                for i in range(2)
            ],
            True,
            [200, 200, 200],
            0,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': None,
                    'ttl': 'infinity',
                }
                for i in range(3)
            ]
            + [_CORRECT_ENTITY],
            [_CORRECT_ENTITY_WITH_TTL],
            True,
            [200, 200, 200],
            3,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': None,
                    'ttl': 'infinity',
                }
                for i in range(3)
            ]
            + [_CORRECT_ENTITY],
            [],
            False,
            [500],
            3,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': 'not timestamp',
                }
                for i in range(3)
            ],
            [],
            False,
            [500],
            3,
        ),
        (
            [
                {
                    'tag': None,
                    'entity_type': 'dbid_uuid',
                    'entity_value': f'entity{i}',
                    'ttl': 'infinity',
                }
                for i in range(3)
            ]
            + [_CORRECT_ENTITY],
            [_CORRECT_ENTITY_WITH_TTL],
            True,
            [200, 200, 200],
            3,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': tags_tools.time_to_str(
                        _NOW + datetime.timedelta(hours=i),
                    ),
                }
                for i in range(3)
            ],
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': _NOW + datetime.timedelta(hours=2),
                },
            ],
            False,
            [200, 200, 200],
            0,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': tags_tools.time_to_str(
                        _NOW + datetime.timedelta(hours=i),
                    ),
                }
                for i in range(3, 0, -1)
            ],
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': _NOW + datetime.timedelta(hours=3),
                },
            ],
            False,
            [200, 200, 200],
            0,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': ttl,
                }
                for ttl in [tags_tools.time_to_str(_NOW), 'infinity']
            ],
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': _INFINITY,
                },
            ],
            False,
            [200, 200, 200],
            0,
        ),
        (
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': tags_tools.time_to_str(_NOW),
                },
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                },
            ],
            [
                {
                    'tag': 'topvipcars',
                    'entity_type': 'dbid_uuid',
                    'entity_value': 'entity',
                    'ttl': _INFINITY,
                },
            ],
            False,
            [200, 200, 200],
            0,
        ),
    ],
)
async def test_malformed_result(
        taxi_tags,
        yt_client,
        pgsql,  # noqa: F811
        yt_apply_force,
        yt_data,
        expected_tags,
        skip_nulls,
        expected_codes,
        nulls_count,
        taxi_config,
):
    db = pgsql['tags']
    taxi_config.set_values(dict(TAGS_YT_SKIP_MALFORMED_ROWS=skip_nulls))
    yt_client.write_table('//' + _SNAPSHOT_PATH, yt_data)

    for expected_code in expected_codes:
        await tags_tools.activate_task(
            taxi_tags, 'yt-downloader', expected_code,
        )
        if expected_code == 500:
            return

    yql_tools.verify_yt_download_task(
        db, 0, 'finished', 0, None, None, nulls_count,
    )
    yql_tools.verify_snapshot_status(db, 'fully_applied')

    await tags_tools.activate_task(taxi_tags, 'customs-officer')

    rows = tags_select.select_named(
        'SELECT name as tag, value as entity_value, entity_type, ttl '
        'FROM state.tags JOIN state.entities ON entity_id = entities.id '
        'JOIN meta.tag_names on tag_name_id = tag_names.id WHERE'
        ' ttl > updated ORDER BY 1,2',
        db,
    )
    assert rows == expected_tags


@pytest.mark.config(
    UTAGS_YQL_WORKER_ENABLED=True,
    TAGS_PG_THROTTLING_SETTINGS={
        'yt-downloader': {'pg_critical': {'is_disabled': True}},
    },
)
async def test_throttling(taxi_tags, statistics, testpoint):
    # init fallbacks
    statistics.fallbacks = ['tags.pg_critical']
    await taxi_tags.invalidate_caches()

    @testpoint('throttled')
    def _throttled_testpoint(data):
        pass

    await tags_tools.activate_task(taxi_tags, 'yt-downloader')
    assert _throttled_testpoint.has_calls
