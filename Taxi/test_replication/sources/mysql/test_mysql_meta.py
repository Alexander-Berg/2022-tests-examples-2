import pytest

from replication.sources.mysql.core import meta
from replication.sources.mysql.core import source


@pytest.mark.parametrize(
    'source_type,source_name,raw_meta,expected_names,expected_meta_attrs',
    [
        (
            source.SOURCE_TYPE_MYSQL,
            'mysql_test_source',
            {
                'table': 'example_table',
                'primary_key': ['id'],
                'replicate_by': 'updated_at',
                'connection': {'secret': 'testing-mysql-one-shard'},
            },
            ['mysql_test_source_shard0'],
            {
                'table': ['example_table'],
                'replicate_by': ['updated_at'],
                'timezone': ['UTC'],
                'unit_name': ['shard0'],
            },
        ),
        (
            source.SOURCE_TYPE_MYSQL,
            'mysql_raw_test_source',
            {
                'table': 'example_table',
                'raw_select': {
                    'data': 'select updated_at from example_table',
                    'min_replicate_by': (
                        'select min(updated_at) as updated_at '
                        'from example_table'
                    ),
                    'max_replicate_by': (
                        'select max(updated_at) as updated_at '
                        'from example_table'
                    ),
                },
                'primary_key': ['id'],
                'replicate_by': 'updated_at',
                'connection': {'secret': 'testing-mysql-one-shard'},
            },
            ['mysql_raw_test_source_shard0'],
            {
                'raw_select': [
                    meta.MysqlRawSelect(
                        data='select updated_at from example_table',
                        min_replicate_by=(
                            'select min(updated_at) as updated_at '
                            'from example_table'
                        ),
                        max_replicate_by=(
                            'select max(updated_at) as updated_at '
                            'from example_table'
                        ),
                    ),
                ],
                'table': ['example_table'],
                'replicate_by': ['updated_at'],
                'timezone': ['UTC'],
                'unit_name': ['shard0'],
            },
        ),
    ],
)
@pytest.mark.nofilldb
async def test_mysql_meta_construct(
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
