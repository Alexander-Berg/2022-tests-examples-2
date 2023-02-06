import pytest

from replication.sources.ydb.core import source


@pytest.mark.parametrize(
    'source_type,source_name,raw_meta,expected_names,expected_meta_attrs',
    [
        (
            source.SOURCE_TYPE_YDB,
            'ydb_test_source',
            {
                'table': 'example_table',
                'primary_key': ['id'],
                'replicate_by': 'updated',
                'replicate_by_index_view': 'updated_idx',
                'connection': {'secret': 'testing-ydb'},
            },
            ['ydb_test_source'],
            {
                'table': ['example_table'],
                'replicate_by': ['updated'],
                'replicate_by_index_view': ['updated_idx'],
                'timezone': ['UTC'],
                'unit_name': [None],
            },
        ),
    ],
)
@pytest.mark.nofilldb
async def test_ydb_meta_construct(
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
