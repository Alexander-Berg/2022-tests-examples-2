import pytest

from replication.sources.postgres import core as postgres


PG_META_TEST_CASES = [
    (
        postgres.SOURCE_TYPE_POSTGRES,
        'pg_one_shard',
        {
            'table': 'table',
            'primary_key': ['id'],
            'connection': {'secret': 'example_pg'},
            'replicate_by': 'updated1',
        },
        ['pg_one_shard_shard0'],
        {
            'shard_num': [0],
            'connection_kwargs.database': ['replication_example_pg_0'],
            'common_connection_kwargs': [{'max_size': 2, 'min_size': 1}],
            'timezone': ['UTC'],
            'replicate_by': ['updated1'],
        },
        1,
    ),
    (
        postgres.SOURCE_TYPE_POSTGRES,
        'pg_shards',
        {
            'table': 'table',
            'primary_key': ['id'],
            'connection': {'secret': 'example_pg'},
            'timezone': 'UTC',
            'replicate_by': 'updated2',
        },
        ['pg_shards_shard0', 'pg_shards_shard1'],
        {
            'shard_num': [0, 1],
            'connection_kwargs.database': [
                'replication_example_pg_0',
                'replication_example_pg_1',
            ],
            'common_connection_kwargs': [
                {'max_size': 2, 'min_size': 1},
                {'max_size': 2, 'min_size': 1},
            ],
            'timezone': ['UTC', 'UTC'],
            'replicate_by': ['updated2', 'updated2'],
        },
        2,
    ),
]


@pytest.mark.parametrize(
    'source_type,source_name,raw_meta,'
    'expected_names,expected_meta_attrs,'
    'additional_source_secrets',
    PG_META_TEST_CASES,
    indirect=['additional_source_secrets'],
)
@pytest.mark.nofilldb()
async def test_pg_meta_construct(
        source_meta_checker,
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
):
    source_meta_checker(
        source_type,
        source_name,
        raw_meta,
        expected_names,
        expected_meta_attrs,
    )
