import pytest

from replication.sources.postgres import core as postgres
from replication.sources.postgres.core import tables_util


@pytest.mark.parametrize(
    'rule_name, expected_tables',
    [
        (
            'prefix_source_postgres',
            [
                'sequence.table',
                'sequence.table_by_ts',
                'sequence.table_indexed',
            ],
        ),
    ],
)
async def test_all_tables_got_by_prefix(
        replication_ctx, rule_name, expected_tables,
):
    # pylint: disable=protected-access
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[postgres.SOURCE_TYPE_POSTGRES],
    )
    rule = rules[0]
    source = rule.source
    pool = await source._pool()
    tables = await tables_util.get_tables(source.meta.table_settings, pool)
    assert sorted(tables) == expected_tables
