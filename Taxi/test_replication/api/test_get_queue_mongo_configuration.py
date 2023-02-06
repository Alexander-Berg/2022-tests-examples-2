import operator

import pytest


@pytest.mark.parametrize(
    'rule_names,expected,status',
    [
        (
            ['test_rule', 'test_sharded_rule'],
            {
                'queue_mongo_collections': [
                    {
                        'collections': [
                            {
                                'collection': 'test_rule',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 0,
                            },
                        ],
                        'number_of_shards': 1,
                        'rule_name': 'test_rule',
                    },
                    {
                        'collections': [
                            {
                                'collection': 'test_sharded_rule_0_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 0,
                            },
                            {
                                'collection': 'test_sharded_rule_1_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 1,
                            },
                            {
                                'collection': 'test_sharded_rule_2_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 2,
                            },
                            {
                                'collection': 'test_sharded_rule_3_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 3,
                            },
                        ],
                        'number_of_shards': 4,
                        'rule_name': 'test_sharded_rule',
                    },
                ],
            },
            200,
        ),
        (
            ['test_sharded_rule', 'wrong_rule'],
            {
                'queue_mongo_collections': [
                    {
                        'collections': [
                            {
                                'collection': 'test_sharded_rule_0_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 0,
                            },
                            {
                                'collection': 'test_sharded_rule_1_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 1,
                            },
                            {
                                'collection': 'test_sharded_rule_2_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 2,
                            },
                            {
                                'collection': 'test_sharded_rule_3_4',
                                'connection': 'replication_queue_mdb_0',
                                'database': 'replication_queue_mdb_0',
                                'shard_num': 3,
                            },
                        ],
                        'number_of_shards': 4,
                        'rule_name': 'test_sharded_rule',
                    },
                ],
            },
            200,
        ),
        (['wrong_rule'], {'queue_mongo_collections': []}, 200),
    ],
)
async def test_handle(replication_client, rule_names, expected, status):
    response = await replication_client.post(
        '/configuration/queue_mongo',
        json={'replication_rule_names': rule_names},
    )
    assert response.status == status
    response_data = await response.json()
    result = response_data.copy()
    result['queue_mongo_collections'] = sorted(
        response_data['queue_mongo_collections'],
        key=operator.itemgetter('rule_name'),
    )
    assert result == expected
