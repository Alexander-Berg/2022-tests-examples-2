import datetime

from replication.common.queue_mongo import collection


_DOC = {'foo': 'baz', 'updated': datetime.datetime(2021, 10, 23, 12, 30)}


async def test_lazy_connection_for_secondary_db(replication_ctx):
    rules_storage = replication_ctx.rule_keeper.rules_storage
    source = rules_storage.get_rules_list(
        rule_name='test_rule', target_types=['yt'],
    )[0].source
    queue_mongo_shard: collection.QueueShard = (
        source.meta.dependencies.queue_mongo_shard
    )
    _id = await queue_mongo_shard.primary.insert(_DOC)
    doc = await queue_mongo_shard.secondary.find_one(_id)
    assert doc == _DOC
