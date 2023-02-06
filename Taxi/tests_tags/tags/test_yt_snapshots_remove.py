import datetime

import pytest

from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_NOW = datetime.datetime.now()
_MINUTE_AGO = _NOW - datetime.timedelta(minutes=1)
_OUTDATED_HISTORY_OPERATION = _NOW - datetime.timedelta(days=1, seconds=1)


def _verify_snapshots(snapshots, db):
    cursor = db.cursor()
    cursor.execute(
        'SELECT provider_id, snapshot_path, created, status FROM '
        'service.yt_snapshots ORDER BY created;',
    )
    rows = list(yql_tools.YtSnapshot(*row) for row in cursor)
    assert sorted(rows, key=lambda x: x.snapshot_path) == sorted(
        snapshots, key=lambda x: x.snapshot_path,
    )


_PATHS = [[f'path_{i}_{j}' for j in range(7)] for i in range(4)]


_YT_SNAPSHOTS = [
    # 2000 provider should have 1 snapshot by default
    # first snapshot in description should not be touched in any way
    yql_tools.YtSnapshot(2000, _PATHS[0][0], _NOW, 'description'),
    yql_tools.YtSnapshot(
        2000,
        _PATHS[0][1],
        _NOW - datetime.timedelta(minutes=1),
        'description',
    ),
    yql_tools.YtSnapshot(
        2000,
        _PATHS[0][2],
        _NOW - datetime.timedelta(minutes=2),
        'description',
    ),
    yql_tools.YtSnapshot(
        2000,
        _PATHS[0][3],
        _NOW - datetime.timedelta(minutes=10),
        'fully_applied',
    ),
    yql_tools.YtSnapshot(
        2000,
        _PATHS[0][4],
        _NOW - datetime.timedelta(minutes=11),
        'description',
    ),
    yql_tools.YtSnapshot(
        2000,
        _PATHS[0][5],
        _NOW - datetime.timedelta(minutes=12),
        'description',
    ),
    # old
    yql_tools.YtSnapshot(
        2000,
        _PATHS[0][6],
        _NOW - datetime.timedelta(hours=1),
        'fully_applied',
    ),
    # 2001 provider should have 3 snapshots by config
    yql_tools.YtSnapshot(2001, _PATHS[1][0], _NOW, 'fully_applied'),
    yql_tools.YtSnapshot(
        2001,
        _PATHS[1][1],
        _NOW - datetime.timedelta(hours=5),
        'partially_applied',
    ),
    yql_tools.YtSnapshot(
        2001, _PATHS[1][2], _NOW - datetime.timedelta(hours=6), 'description',
    ),
    yql_tools.YtSnapshot(
        2001,
        _PATHS[1][3],
        _NOW - datetime.timedelta(hours=10),
        'fully_applied',
    ),
    # old
    yql_tools.YtSnapshot(
        2001,
        _PATHS[1][4],
        _NOW - datetime.timedelta(hours=15),
        'fully_applied',
    ),
    # 2002 provider should have 1 snapshots by config
    # partially applied is considered as snapshot
    yql_tools.YtSnapshot(2002, _PATHS[2][0], _NOW, 'partially_applied'),
    # old
    yql_tools.YtSnapshot(
        2002,
        _PATHS[2][1],
        _NOW - datetime.timedelta(hours=10),
        'fully_applied',
    ),
    # 2003 provider should have 10 snapshots by config
    # Although 10 snapshots should be preserved, all snapshots after
    # 'outdated' should be deleted to optimize number of
    # tables used
    yql_tools.YtSnapshot(2003, _PATHS[3][0], _NOW, 'fully_applied'),
    yql_tools.YtSnapshot(
        2003, _PATHS[3][1], _NOW - datetime.timedelta(hours=10), 'outdated',
    ),
    yql_tools.YtSnapshot(
        2003,
        _PATHS[3][2],
        _NOW - datetime.timedelta(hours=11),
        'fully_applied',
    ),
    yql_tools.YtSnapshot(
        2003,
        _PATHS[3][3],
        _NOW - datetime.timedelta(hours=12),
        'fully_applied',
    ),
]


@pytest.mark.yt(
    schemas=[
        {
            'path': f'//{path}',
            'attributes': {'schema': [{'name': 'id', 'type': 'string'}]},
        }
        for provider_paths in _PATHS
        for path in provider_paths
    ],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers(
            [tags_tools.Provider.from_id(i, True) for i in range(2000, 2005)],
        ),
        yql_tools.insert_queries(
            [
                yql_tools.Query(
                    f'query{i}',
                    i,
                    [],
                    '2018-08-30T12:34:56.0',
                    '2018-08-30T12:34:56.0',
                    'text',
                    300,
                )
                for i in range(2000, 2005)
            ],
        ),
        yql_tools.insert_snapshots(_YT_SNAPSHOTS),
        tags_tools.insert_history_operations(
            [
                ['outdated_operation_id', 'path', _OUTDATED_HISTORY_OPERATION],
                ['actual_operation_id', 'path', _NOW],
            ],
        ),
    ],
)
@pytest.mark.config(
    TAGS_YT_SNAPSHOT_MAX_COUNT={
        '__default__': 1,
        'query2001': 3,
        'query2003': 10,
    },
    UTAGS_GARBAGE_CRON_SETTINGS={
        '__default__': {
            '__default__': {'enabled': True},
            'cleanup_yt_tables': {'enabled': False},
        },
    },
)
@pytest.mark.now(_NOW.isoformat())
async def test_snapshot_add_for_delete(taxi_tags, pgsql, yt_client):
    db = pgsql['tags']

    await tags_tools.activate_task(taxi_tags, 'garbage-collector')

    _verify_snapshots(
        [_YT_SNAPSHOTS[0]]
        + [_YT_SNAPSHOTS[3]]
        + _YT_SNAPSHOTS[7:9]
        + [_YT_SNAPSHOTS[10]]
        + [_YT_SNAPSHOTS[12]]
        + [_YT_SNAPSHOTS[14]],
        db,
    )

    snapshots_for_delete = [
        _PATHS[0][1],
        _PATHS[0][2],
        _PATHS[0][4],
        _PATHS[0][5],
        _PATHS[0][6],
        _PATHS[1][2],
        _PATHS[1][4],
        _PATHS[2][1],
        _PATHS[3][1],
        _PATHS[3][2],
        _PATHS[3][3],
    ]

    yt_tables = tags_select.select_table_named(
        'service.yt_tables_delete_queue', 'yt_table_path', db,
    )
    assert [item['yt_table_path'] for item in yt_tables] == sorted(
        snapshots_for_delete,
    )

    for provider_paths in _PATHS:
        for path in provider_paths:
            assert yt_client.exists('//' + path)

    tags_tools.verify_inserted_operations(
        [{'operation_id': 'actual_operation_id', 'created': _NOW}],
        pgsql['tags'],
    )


_YT_TABLE_PATHS = [f'yt_table_path_{j}' for j in range(9)]
_EXECUTION_COUNT = 1
_LIMIT = 3


@pytest.mark.yt(
    schemas=[
        {
            'path': f'//{yt_table_path}',
            'attributes': {'schema': [{'name': 'id', 'type': 'string'}]},
        }
        for yt_table_path in _YT_TABLE_PATHS
    ],
)
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_providers([tags_tools.Provider.from_id(0)]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(1)]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(2)]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(3)]),
        tags_tools.insert_providers([tags_tools.Provider.from_id(4)]),
        yql_tools.insert_operation(
            'op_running', 0, None, 'running', _MINUTE_AGO,
        ),
        yql_tools.insert_operation(
            'op_done', 1, None, 'completed', _MINUTE_AGO,
        ),
        yql_tools.insert_operation(
            'op_failed', 2, None, 'failed', _MINUTE_AGO,
        ),
        yql_tools.insert_operation(
            'op_aborted', 3, None, 'aborted', _MINUTE_AGO,
        ),
        yql_tools.insert_operation(
            'op_applying', 4, None, 'downloading', _MINUTE_AGO,
        ),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[0]),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[1], 'op_running'),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[2]),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[3], 'op_applying'),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[4], 'op_done'),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[5], 'op_done'),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[6], 'op_failed'),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[7], 'op_None'),
        yql_tools.insert_yt_table(_YT_TABLE_PATHS[8], 'op_aborted'),
    ],
)
@pytest.mark.config(
    UTAGS_GARBAGE_CRON_SETTINGS={
        '__default__': {
            '__default__': {'enabled': False},
            'cleanup_yt_tables': {
                'enabled': True,
                'execution_count': _EXECUTION_COUNT,
                'limit': _LIMIT,
            },
        },
    },
)
async def test_yt_tables_delete(taxi_tags, pgsql, yt_client):
    db = pgsql['tags']

    non_removed_tables = [_YT_TABLE_PATHS[1], _YT_TABLE_PATHS[3]]
    yt_tables_count = len(_YT_TABLE_PATHS)

    for index in range(1, 5):
        await tags_tools.activate_task(taxi_tags, 'garbage-collector')
        yt_tables = tags_select.select_table_named(
            'service.yt_tables_delete_queue', 'yt_table_path', db,
        )
        left_yt_tables = max(
            len(non_removed_tables),
            yt_tables_count - index * _EXECUTION_COUNT * _LIMIT,
        )
        assert len(yt_tables) == left_yt_tables

    yt_tables = tags_select.select_table_named(
        'service.yt_tables_delete_queue', 'yt_table_path', db,
    )
    left_yt_table_paths = [item['yt_table_path'] for item in yt_tables]

    assert left_yt_table_paths == non_removed_tables

    for yt_table_path in _YT_TABLE_PATHS:
        assert yt_client.exists('//' + yt_table_path) == (
            yt_table_path in left_yt_table_paths
        )
