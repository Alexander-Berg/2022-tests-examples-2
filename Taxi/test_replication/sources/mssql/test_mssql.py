import datetime

import pytest

from replication.sources.mssql.core import queries
from replication.sources.mssql.core import source

NOW = datetime.datetime(2019, 11, 5, 12, 0)


@pytest.mark.now(NOW.isoformat())
async def test_mssql_snapshot(
        replication_ctx,
        mock_mssql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='mssql_snapshot_test',
        source_types=[source.SOURCE_TYPE_MSSQL],
    )
    assert len(rules) == 1

    meta = rules[0].source.meta
    mock_mssql_source.apply(
        [
            (
                'fetch',
                queries.SnapshotQuery(table=meta.table).text(),
                None,
                [
                    {'ID': 1, 'value': 'a'},
                    {'ID': 2, 'value': 'b'},
                    {'ID': 3, 'value': 'c'},
                    {'ID': 4, 'value': 'd'},
                ],
            ),
        ],
    )

    targets_data = await replication_runner.run(
        'mssql_snapshot_test', source_type=source.SOURCE_TYPE_MSSQL,
    )

    assert len(mock_mssql_source.queries_history) == 1

    assert targets_data.queue_data == [
        {
            '_id': '1',
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {'ID': 1, 'value': 'a'},
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': '{"ID": 1, "value": "a"}',
        },
        {
            '_id': '2',
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {'ID': 2, 'value': 'b'},
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': '{"ID": 2, "value": "b"}',
        },
        {
            '_id': '3',
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {'ID': 3, 'value': 'c'},
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': '{"ID": 3, "value": "c"}',
        },
        {
            '_id': '4',
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {'ID': 4, 'value': 'd'},
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': '{"ID": 4, "value": "d"}',
        },
    ]


@pytest.mark.now(NOW.isoformat())
async def test_mssql_increment(
        replication_ctx,
        mock_mssql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='mssql_test', source_types=[source.SOURCE_TYPE_MSSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mssql_source.apply(
        [
            (
                'fetch_one',
                queries.MinStampQuery(
                    table=meta.table, replicate_by=meta.replicate_by,
                ).text(),
                None,
                {'utc_updated_dttm': datetime.datetime(2019, 5, 1, 0, 0)},
            ),
            (
                'fetch',
                queries.UnindexedDocsQuery(
                    table=meta.table, replicate_by=meta.replicate_by,
                ).text(),
                None,
                [{'ID': 1, 'value': 'a', 'utc_updated_dttm': None}],
            ),
            (
                'fetch_one',
                queries.MaxStampQuery(
                    table=meta.table, replicate_by=meta.replicate_by,
                ).text(),
                None,
                {'utc_updated_dttm': datetime.datetime(2019, 11, 1, 1, 1)},
            ),
            (
                'fetch',
                queries.IncrementQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    data_chunk_size=meta.data_chunk_size,
                ).text(),
                {
                    'left': datetime.datetime(2019, 4, 30, 23, 59),
                    'right': datetime.datetime(2019, 11, 1, 1, 1),
                },
                [
                    {
                        'ID': 2,
                        'value': 'b',
                        'utc_updated_dttm': datetime.datetime(
                            2019, 5, 1, 0, 0,
                        ),
                    },
                    {
                        'ID': 3,
                        'value': 'c',
                        'utc_updated_dttm': datetime.datetime(
                            2019, 7, 2, 0, 0,
                        ),
                    },
                ],
            ),
            (
                'fetch',
                queries.IncrementQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    data_chunk_size=meta.data_chunk_size,
                ).text(),
                {
                    'left': datetime.datetime(2019, 7, 2, 0, 0),
                    'right': datetime.datetime(2019, 11, 1, 1, 1),
                },
                [
                    {
                        'ID': 4,
                        'value': 'd',
                        'utc_updated_dttm': datetime.datetime(
                            2019, 8, 3, 0, 0,
                        ),
                    },
                    {
                        'ID': 5,
                        'value': 'e',
                        'utc_updated_dttm': datetime.datetime(
                            2019, 11, 1, 1, 1,
                        ),
                    },
                    {
                        'ID': 6,
                        'value': 'f',
                        'utc_updated_dttm': datetime.datetime(
                            2019, 11, 1, 1, 1,
                        ),
                    },
                ],
            ),
            (
                'fetch',
                queries.IncrementQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    data_chunk_size=meta.data_chunk_size,
                ).text(),
                {
                    'left': datetime.datetime(2019, 11, 1, 1, 1),
                    'right': datetime.datetime(2019, 11, 1, 1, 1),
                },
                [],
            ),
        ],
    )
    targets_data = await replication_runner.run(
        'mssql_test', source_type=source.SOURCE_TYPE_MSSQL,
    )

    assert len(mock_mssql_source.queries_history) == 6

    assert targets_data.queue_data == [
        {
            '_id': '1',
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {'ID': 1, 'utc_updated_dttm': None, 'value': 'a'},
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': '{"ID": 1, "utc_updated_dttm": null, "value": "a"}',
        },
        {
            '_id': '2',
            'bs': datetime.datetime(2019, 5, 1, 0, 0),
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {
                'ID': 2,
                'utc_updated_dttm': datetime.datetime(2019, 5, 1, 0, 0),
                'value': 'b',
            },
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': (
                '{"ID": 2, "utc_updated_dttm": {"$a": {"raw_type": "datetime"}'
                ', "$v": "2019-05-01T00:00:00"}, "value": "b"}'
            ),
        },
        {
            '_id': '3',
            'bs': datetime.datetime(2019, 7, 2, 0, 0),
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {
                'ID': 3,
                'utc_updated_dttm': datetime.datetime(2019, 7, 2, 0, 0),
                'value': 'c',
            },
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': (
                '{"ID": 3, "utc_updated_dttm": {"$a": {"raw_type": "datetime"}'
                ', "$v": "2019-07-02T00:00:00"}, "value": "c"}'
            ),
        },
        {
            '_id': '4',
            'bs': datetime.datetime(2019, 8, 3, 0, 0),
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {
                'ID': 4,
                'utc_updated_dttm': datetime.datetime(2019, 8, 3, 0, 0),
                'value': 'd',
            },
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': (
                '{"ID": 4, "utc_updated_dttm": {"$a": {"raw_type": "datetime"}'
                ', "$v": "2019-08-03T00:00:00"}, "value": "d"}'
            ),
        },
        {
            '_id': '5',
            'bs': datetime.datetime(2019, 11, 1, 1, 1),
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {
                'ID': 5,
                'utc_updated_dttm': datetime.datetime(2019, 11, 1, 1, 1),
                'value': 'e',
            },
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': (
                '{"ID": 5, "utc_updated_dttm": {"$a": {"raw_type": "datetime"}'
                ', "$v": "2019-11-01T01:01:00"}, "value": "e"}'
            ),
        },
        {
            '_id': '6',
            'bs': datetime.datetime(2019, 11, 1, 1, 1),
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {
                'ID': 6,
                'utc_updated_dttm': datetime.datetime(2019, 11, 1, 1, 1),
                'value': 'f',
            },
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': (
                '{"ID": 6, "utc_updated_dttm": {"$a": {"raw_type": "datetime"}'
                ', "$v": "2019-11-01T01:01:00"}, "value": "f"}'
            ),
        },
    ]


@pytest.mark.now(NOW.isoformat())
async def test_mssql_increment_empty_table(
        replication_ctx,
        mock_mssql_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='mssql_test', source_types=[source.SOURCE_TYPE_MSSQL],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_mssql_source.apply(
        [
            (
                'fetch_one',
                queries.MinStampQuery(
                    table=meta.table, replicate_by=meta.replicate_by,
                ).text(),
                None,
                {'utc_updated_dttm': None},
            ),
        ],
    )
    targets_data = await replication_runner.run(
        'mssql_test', source_type=source.SOURCE_TYPE_MSSQL,
    )
    assert len(mock_mssql_source.queries_history) == 1
    assert targets_data.queue_data == []
