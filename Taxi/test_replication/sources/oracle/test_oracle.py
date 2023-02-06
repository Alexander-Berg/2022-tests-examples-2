import datetime

import pytest

from replication.sources.oracle.core import queries
from replication.sources.oracle.core import source

NOW = datetime.datetime(2019, 11, 5, 12, 0)


@pytest.mark.now(NOW.isoformat())
async def test_oracle_snapshot(
        replication_ctx,
        mock_oracle_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_snapshot_test',
        source_types=[source.SOURCE_TYPE_ORACLE],
    )
    assert len(rules) == 1

    meta = rules[0].source.meta
    mock_oracle_source.apply(
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
        'oracle_snapshot_test', source_type=source.SOURCE_TYPE_ORACLE,
    )

    assert len(mock_oracle_source.queries_history) == 1

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
async def test_oracle_raw_select_snapshot(
        replication_ctx,
        mock_oracle_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_raw_select_snapshot_test',
        source_types=[source.SOURCE_TYPE_ORACLE],
    )

    assert len(rules) == 1

    meta = rules[0].source.meta
    mock_oracle_source.apply(
        [
            (
                'fetch',
                queries.SnapshotRawSelectQuery(
                    table=meta.table, raw_select_data=meta.raw_select.data,
                ).text(),
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
        'oracle_raw_select_snapshot_test',
        source_type=source.SOURCE_TYPE_ORACLE,
    )

    assert len(mock_oracle_source.queries_history) == 1

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
async def test_oracle_increment(
        replication_ctx,
        mock_oracle_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_test', source_types=[source.SOURCE_TYPE_ORACLE],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_oracle_source.apply(
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
                    primary_key=meta.primary_key,
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
                    primary_key=meta.primary_key,
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
                ],
            ),
            (
                'fetch',
                queries.IncrementQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    data_chunk_size=meta.data_chunk_size,
                    primary_key=meta.primary_key,
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
        'oracle_test', source_type=source.SOURCE_TYPE_ORACLE,
    )

    assert len(mock_oracle_source.queries_history) == 6

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
    ]


@pytest.mark.now(NOW.isoformat())
async def test_oracle_increment_empty_table(
        replication_ctx,
        mock_oracle_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_test', source_types=[source.SOURCE_TYPE_ORACLE],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_oracle_source.apply(
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
        'oracle_test', source_type=source.SOURCE_TYPE_ORACLE,
    )
    assert len(mock_oracle_source.queries_history) == 1
    assert targets_data.queue_data == []


@pytest.mark.now(NOW.isoformat())
async def test_oracle_raw_select_increment(
        replication_ctx,
        mock_oracle_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_raw_select_test',
        source_types=[source.SOURCE_TYPE_ORACLE],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    raw_select_has_conditions = meta.raw_select.data_query_has_conditions
    mock_oracle_source.apply(
        [
            (
                'fetch_one',
                queries.MinStampRawSelectQuery(
                    table=meta.table,
                    min_replicate_by=meta.raw_select.min_replicate_by,
                ).text(),
                None,
                {'utc_updated_dttm': datetime.datetime(2019, 5, 1, 0, 0)},
            ),
            (
                'fetch',
                queries.UnindexedDocsRawSelectQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    raw_select_data=meta.raw_select.data,
                    raw_select_has_conditions=raw_select_has_conditions,
                ).text(),
                None,
                [{'ID': 1, 'value': 'a', 'utc_updated_dttm': None}],
            ),
            (
                'fetch_one',
                queries.MaxStampRawSelectQuery(
                    table=meta.table,
                    max_replicate_by=meta.raw_select.max_replicate_by,
                ).text(),
                None,
                {'utc_updated_dttm': datetime.datetime(2019, 8, 17, 1, 1)},
            ),
            (
                'fetch',
                queries.IncrementRawSelectQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    raw_select_data=meta.raw_select.data,
                    raw_select_has_conditions=raw_select_has_conditions,
                ).text(),
                {
                    'left': datetime.datetime(2019, 4, 30, 23, 59),
                    'right': datetime.datetime(2019, 5, 30, 23, 59),
                },
                [
                    {
                        'ID': 2,
                        'value': 'b',
                        'utc_updated_dttm': datetime.datetime(
                            2019, 5, 1, 0, 0,
                        ),
                    },
                ],
            ),
            (
                'fetch',
                queries.IncrementRawSelectQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    raw_select_data=meta.raw_select.data,
                    raw_select_has_conditions=raw_select_has_conditions,
                ).text(),
                {
                    'left': datetime.datetime(2019, 5, 30, 23, 59),
                    'right': datetime.datetime(2019, 6, 29, 23, 59),
                },
                [],
            ),
            (
                'fetch_one',
                queries.NextStampRawSelectQuery(
                    table=meta.table,
                    raw_select_has_conditions=raw_select_has_conditions,
                    min_replicate_by=meta.raw_select.min_replicate_by,
                    replicate_by=meta.replicate_by,
                ).text(),
                {'left': datetime.datetime(2019, 6, 29, 23, 59)},
                {'utc_updated_dttm': datetime.datetime(2019, 7, 2, 0, 0)},
            ),
            (
                'fetch',
                queries.IncrementRawSelectQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    raw_select_data=meta.raw_select.data,
                    raw_select_has_conditions=raw_select_has_conditions,
                ).text(),
                {
                    'left': datetime.datetime(2019, 6, 29, 23, 59),
                    'right': datetime.datetime(2019, 8, 1, 0, 0),
                },
                [
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
                queries.IncrementRawSelectQuery(
                    table=meta.table,
                    replicate_by=meta.replicate_by,
                    raw_select_data=meta.raw_select.data,
                    raw_select_has_conditions=raw_select_has_conditions,
                ).text(),
                {
                    'left': datetime.datetime(2019, 8, 1, 0, 0),
                    'right': datetime.datetime(2019, 8, 17, 1, 1),
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
                            2019, 8, 17, 1, 1,
                        ),
                    },
                ],
            ),
        ],
    )
    targets_data = await replication_runner.run(
        'oracle_raw_select_test', source_type=source.SOURCE_TYPE_ORACLE,
    )

    assert len(mock_oracle_source.queries_history) == 8

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
            'bs': datetime.datetime(2019, 8, 17, 1, 1),
            'created': datetime.datetime(2019, 11, 5, 12, 0),
            'data': {
                'ID': 5,
                'utc_updated_dttm': datetime.datetime(2019, 8, 17, 1, 1),
                'value': 'e',
            },
            'unit': 'shard0',
            'updated': datetime.datetime(2019, 11, 5, 12, 0),
            'v': 1,
            '__raw_json': (
                '{"ID": 5, "utc_updated_dttm": {"$a": {"raw_type": "datetime"}'
                ', "$v": "2019-08-17T01:01:00"}, "value": "e"}'
            ),
        },
    ]


@pytest.mark.now(NOW.isoformat())
async def test_oracle_raw_select_increment_empty_table(
        replication_ctx,
        mock_oracle_source,
        load_py_json,
        replication_runner,
        patch_queue_current_date,
):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='oracle_raw_select_test',
        source_types=[source.SOURCE_TYPE_ORACLE],
    )
    assert len(rules) == 1
    meta = rules[0].source.meta
    mock_oracle_source.apply(
        [
            (
                'fetch_one',
                queries.MinStampRawSelectQuery(
                    table=meta.table,
                    min_replicate_by=meta.raw_select.min_replicate_by,
                ).text(),
                None,
                {'utc_updated_dttm': None},
            ),
        ],
    )
    targets_data = await replication_runner.run(
        'oracle_raw_select_test', source_type=source.SOURCE_TYPE_ORACLE,
    )
    assert len(mock_oracle_source.queries_history) == 1
    assert targets_data.queue_data == []
