# pylint: disable=protected-access
from replication.common.queue_mongo import confirm_util


_FROZEN_RULE_NAMES_LIST = (
    'test_errors_rule',
    'test_rule',
    'test_sharded_rule',
)
_FROZEN_RULE_NAMES_LIST_2 = (
    'test_rule',
    'test_sharded_pg',
    'test_sharded_rule',
)

BASE = {
    'yt-test_errors_rule_struct-arni': '1',
    'yt-test_errors_rule_struct-hahn': '2',
    'yt-test_errors_rule_struct_2-arni': '3',
    'yt-test_errors_rule_struct_2-hahn': '4',
    'yt-test_rule_bson-arni': '5',
    'yt-test_rule_bson-hahn': '6',
    'yt-test_rule_struct-arni': '7',
    'yt-test_rule_struct-hahn': '8',
    'yt-test_sharded_rule_no_partial-arni': '9',
    'yt-test_sharded_rule_no_partial-hahn': 'A',
    'yt-test_sharded_rule_sharded_struct-arni': 'B',
    'yt-test_sharded_rule_sharded_struct-hahn': 'C',
    'yt-test_sharded_rule_sharded_struct-seneca-man': 'D',
    'yt-test_sharded_rule_sharded_struct-seneca-vla': 'E',
}


async def test_ensure_ids(monkeypatch, replication_ctx):
    await replication_ctx.db.replication_settings.remove(
        confirm_util._CONFIRM_MAP_KEY,
    )
    confirm_map = replication_ctx.rule_keeper.confirm_map

    assert (await confirm_map.get_ids_map()).targets == {}
    assert _get_version(confirm_map) == 0

    old_getter = replication_ctx.rule_keeper.rules_storage.get_rules_list

    _patch(monkeypatch, replication_ctx, old_getter, _FROZEN_RULE_NAMES_LIST)
    await replication_ctx.rule_keeper.ensure_confirm_ids()

    confirm_map = replication_ctx.rule_keeper.confirm_map
    assert (await confirm_map.get_ids_map(force=False)).targets == BASE
    assert _get_version(confirm_map) == 1

    _patch(monkeypatch, replication_ctx, old_getter, _FROZEN_RULE_NAMES_LIST_2)
    await replication_ctx.rule_keeper.ensure_confirm_ids()
    confirm_map = replication_ctx.rule_keeper.confirm_map
    after = {
        'yt-test_sharded_pg_just_table-arni': 'F',
        'yt-test_sharded_pg_just_table-hahn': '10',
    }
    after.update(BASE)
    assert (await confirm_map.get_ids_map(force=False)).targets == after
    assert _get_version(confirm_map) == 2


def _get_version(confirm_map):
    return confirm_map._storage._version


def _patch(monkeypatch, replication_ctx, old_getter, frozen_rules_list):
    def frozen_get_rules_list(*args, **kwargs):
        return [
            rule
            for rule in old_getter(*args, **kwargs)
            if rule.name in frozen_rules_list
        ]

    monkeypatch.setattr(
        replication_ctx.rule_keeper.rules_storage,
        'get_rules_list',
        frozen_get_rules_list,
    )
