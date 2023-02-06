import datetime

import pytest

from replication.targets.yt import auto_alter_table

FULL_SCHEMA = [
    {'sort_order': 'ascending', 'type': 'int64', 'name': 'created'},
    {'type': 'string', 'name': 'normal_column'},
    {'type': 'int64', 'name': 'extra_column_int'},
    {'type': 'string', 'name': 'extra_column_string'},
]
WRONG_SCHEMA = [
    {'sort_order': 'ascending', 'type': 'int64', 'name': 'created'},
    {'type': 'string', 'name': 'normal_column'},
    {'type': 'int64', 'name': 'wrong_column'},
]
WARNINGS = """These columns should be added to tables on YT
--------------------------------------------------
Columns: extra_column_int extra_column_string

Cluster: hahn
    Tables: //home/taxi/unittests/auto_alter_table/partitioning/2022-05

--------------------------------------------------
These columns should be removed from YT
--------------------------------------------------
Columns: wrong_column

Cluster: hahn
    Tables: //home/taxi/unittests/auto_alter_table/partitioning/2022-05

--------------------------------------------------"""


@pytest.mark.parametrize(
    'replication_id, table_path, expected_warning, expected_schema',
    (
        (
            'queue_mongo-staging_auto_alter_table-yt-auto_alter_table-hahn',
            'auto_alter_table/partitioning/2022-03',
            None,
            FULL_SCHEMA,
        ),
        (
            'queue_mongo-staging_auto_alter_table-yt-auto_alter_table-hahn',
            'auto_alter_table/partitioning/2022-04',
            'Nothing to alter',
            FULL_SCHEMA,
        ),
        (
            'queue_mongo-staging_auto_alter_table-yt-auto_alter_table-hahn',
            'auto_alter_table/partitioning/2022-05',
            WARNINGS,
            WRONG_SCHEMA,
        ),
        (
            'queue_mongo-staging_auto_alter_table-yt-auto_alter_table_single'
            '-hahn',
            'auto_alter_table/single',
            None,
            FULL_SCHEMA,
        ),
    ),
)
@pytest.mark.now(datetime.datetime(2022, 5, 2, 3).isoformat())
@pytest.mark.use_yt_local
async def test_auto_alter_table(
        yt_client,
        yt_apply,
        replication_ctx,
        replication_id,
        table_path,
        expected_warning,
        expected_schema,
):
    target = replication_ctx.rule_keeper.rules_storage.get_target(
        replication_id=replication_id,
    )
    warning = await auto_alter_table.AutoAlterTable(target).auto_add_columns(
        table_path,
    )
    yt_schema = _clean_yt_schema(
        yt_client.get(f'{target.meta.prefix + table_path}/@schema'),
    )
    assert yt_schema == expected_schema
    assert warning == expected_warning


def _clean_yt_schema(schema):
    result = []
    for col in schema:
        cleaned = {'type': str(col['type']), 'name': col['name']}
        if 'sort_order' in col:
            cleaned['sort_order'] = col['sort_order']
        result.append(cleaned)
    return result
