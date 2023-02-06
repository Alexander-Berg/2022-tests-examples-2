import datetime

import pytest

from replication.common.queue_mongo import collection as collection_mod
from replication.foundation import consts
from replication.replication.core import replication

NOW = datetime.datetime(2018, 11, 26, 0)
RULE_NAME = 'test_sharded_rule'


# pylint: disable=too-many-locals
# pylint: disable=invalid-name
@pytest.mark.mongodb_collections('test_coll')
@pytest.mark.now(NOW.isoformat())
async def test_replicate_via_sharded_queue(
        replication_ctx, yt_clients_storage, replication_tasks_getter,
):
    tasks = await replication_tasks_getter(consts.SOURCE_TYPE_MONGO, RULE_NAME)
    assert len(tasks) == 1

    await replication.replicate_to_targets(replication_ctx, tasks)
    rules_storage = replication_ctx.rule_keeper.rules_storage
    rule = rules_storage.get_rules_list(
        rule_name=RULE_NAME, target_types=[consts.TARGET_TYPE_QUEUE_MONGO],
    )[0]
    queue_mongo_collection: collection_mod.QueueShardingCollection = (
        rule.targets[0].meta.dependencies.queue_mongo_collection
    )
    expected_docs_by_shards = {
        'staging_test_sharded_rule_{}_4'.format(x): {str(x)} for x in range(4)
    }
    for (
            staging_collection_name,
            collection,
    ) in queue_mongo_collection.get_collections().items():
        docs = await collection.find().to_list(None)
        assert (
            set(doc['_id'] for doc in docs)
            == expected_docs_by_shards[staging_collection_name]
        )
        for doc in docs:
            await collection.update(
                {'_id': doc['_id']},
                {'$set': {'updated': NOW - datetime.timedelta(hours=1)}},
            )
    with yt_clients_storage() as all_clients:
        tasks = await replication_tasks_getter(
            consts.SOURCE_TYPE_QUEUE_MONGO, RULE_NAME,
        )
        assert len(tasks) == 4
        for task in tasks:
            await replication.replicate_to_targets(replication_ctx, [task])

    data = {
        '0': {'id': '0', 'value_1': 0, 'value_2': 3},
        '2': {'id': '2', 'value_1': 1, 'value_2': 2},
        '3': {'id': '3', 'value_1': 5, 'value_2': 6},
        '1': {'id': '1', 'value_1': 11, 'value_2': 22},
    }
    expected = {
        'test/test_struct_sharded': data,
        'test/test_struct_sharded_no_partial': data,
    }
    assert all_clients['hahn'].rows_by_ids == expected
    assert all_clients['arni'].rows_by_ids == expected
