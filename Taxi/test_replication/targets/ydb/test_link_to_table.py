import pytest


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'target_name, table_link',
    [('test_ydb', 'unittests'), ('test_ydb_daily', 'test_ydb_daily/url')],
)
async def test_current_table(replication_ctx, target_name, table_link):
    target = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        target_names=[target_name],
    )[0].targets[0]
    assert target.meta.link == table_link
