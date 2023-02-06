from replication.tools import drop_staging_collections

_DOC = {'foo': 'baz'}


async def test_drop_collections(replication_ctx):
    collection = replication_ctx.rule_keeper.staging_db.get_queue_mongo_shard(
        'test_rule',
    ).primary
    await collection.remove({})
    await collection.insert(_DOC)
    assert await collection.count() == 1
    await drop_staging_collections.drop_collections(
        shared_deps=replication_ctx.shared_deps,
        shards_num=1,
        db_cluster='replication_queue_mdb_0',
        rule_names=['test_rule'],
        dry_run=False,
    )
    assert await collection.count() == 0


async def test_drop_collections_multi(replication_ctx):
    staging_db = replication_ctx.rule_keeper.staging_db
    staging_collections = (
        staging_db.get_queue_mongo_shard('test_sharded_rule', 0).primary,
        staging_db.get_queue_mongo_shard('test_sharded_rule', 1).primary,
        staging_db.get_queue_mongo_shard('test_sharded_rule', 2).primary,
        staging_db.get_queue_mongo_shard('test_sharded_rule', 3).primary,
    )
    for collection in staging_collections:
        await collection.remove({})
        await collection.insert(_DOC)
        assert await collection.count() == 1

    await drop_staging_collections.drop_collections(
        shared_deps=replication_ctx.shared_deps,
        shards_num=4,
        db_cluster='replication_queue_mdb_0',
        rule_names=['test_sharded_rule'],
        dry_run=False,
    )

    for collection in staging_collections:
        assert await collection.count() == 0
