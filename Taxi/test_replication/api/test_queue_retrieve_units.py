import pytest


@pytest.mark.parametrize(
    'rule_name, status, expected',
    [
        ('test_sharded_pg', 200, {}),
        (
            'test_sharded_mongo_sharded_queue',
            200,
            {'queue_partitions': ['0_4', '1_4', '2_4', '3_4']},
        ),
        (
            'not_found',
            404,
            {'code': 'read-data-error', 'message': 'Rule not_found not found'},
        ),
    ],
)
async def test_retrieve_units(replication_client, rule_name, status, expected):
    response = await replication_client.post(
        f'/v1/queue/retrieve_partitions/{rule_name}',
    )
    assert response.status == status, await response.text()
    assert await response.json() == expected
