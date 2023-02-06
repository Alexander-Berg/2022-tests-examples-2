from replication.foundation import rules_metadata
from replication.stuff import actualize_rules_metadata

_EXPECTED = {
    'test_sharded_pg': rules_metadata.SourceMetadataInfo(
        source_unit_names=['shard0', 'shard1'],
        source_extra_filters={'pg_table': 'just_table'},
    ),
}


async def test_rules_metadata_cls(replication_ctx, monkeypatch):
    metadata_coll = replication_ctx.db.replication_rules_metadata
    rules_metadata_cache = rules_metadata.RulesMetadataCollection(
        metadata_coll,
    )
    old_getter = replication_ctx.rule_keeper.rules_storage.get_rules_list
    source_definitions = replication_ctx.pluggy_deps.source_definitions

    def get_rules_list(*args, **kwargs):
        return old_getter(
            rule_name='test_sharded_pg',
            source_types=source_definitions.base_replication_types,
        )

    monkeypatch.setattr(
        replication_ctx.rule_keeper.rules_storage,
        'get_rules_list',
        get_rules_list,
    )
    await rules_metadata_cache.init_cache()
    assert rules_metadata_cache.get_source_metadata_info() == {}
    await actualize_rules_metadata.actualize_data(replication_ctx)
    await rules_metadata_cache.init_cache()
    assert rules_metadata_cache.get_source_metadata_info() == _EXPECTED
