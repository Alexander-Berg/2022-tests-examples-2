import operator

from replication.stuff import actualize_rules_metadata

_EXPECTED = [
    {
        '_id': 'test_sharded_mongo',
        'source_unit_names': ['shard0', 'shard1'],
        'source_extra_filters': {},
        'v': 1,
    },
    {
        '_id': 'test_sharded_mongo_sharded_queue',
        'source_extra_filters': {},
        'source_unit_names': ['shard0', 'shard1'],
        'v': 1,
    },
    {
        '_id': 'basic_source_mongo',
        'source_unit_names': [None],
        'source_extra_filters': {},
        'v': 1,
    },
    {
        '_id': 'basic_source_postgres',
        'source_unit_names': ['shard0'],
        'source_extra_filters': {'pg_table': 'table'},
        'v': 1,
    },
    {
        '_id': 'basic_source_zendesk',
        'source_unit_names': [None],
        'source_extra_filters': {},
        'v': 1,
    },
]

_FROZEN_RULES_LIST = [
    'basic_source_postgres',
    'basic_source_mongo',
    'test_sharded_mongo',
    'test_sharded_mongo_sharded_queue',
    'basic_source_zendesk',
]


async def test_actualize_rules_metadata(loop, monkeypatch, replication_ctx):
    old_getter = replication_ctx.rule_keeper.rules_storage.get_rules_list

    def frozen_get_rules_list(*args, **kwargs):
        return [
            rule
            for rule in old_getter(*args, **kwargs)
            if rule.name in _FROZEN_RULES_LIST
        ]

    monkeypatch.setattr(
        replication_ctx.rule_keeper.rules_storage,
        'get_rules_list',
        frozen_get_rules_list,
    )

    all_docs = (
        await replication_ctx.db.replication_rules_metadata.find().to_list(
            None,
        )
    )
    assert all_docs == []
    await actualize_rules_metadata.actualize_data(replication_ctx)
    all_docs = (
        await replication_ctx.db.replication_rules_metadata.find().to_list(
            None,
        )
    )
    assert sorted(all_docs, key=operator.itemgetter('_id')) == sorted(
        _EXPECTED, key=operator.itemgetter('_id'),
    )
