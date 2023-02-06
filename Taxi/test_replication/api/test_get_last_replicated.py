import pytest


@pytest.mark.parametrize(
    'replication_rule_name, response_status, expected, v1_expected',
    [
        (
            'basic_source_postgres_sequence',
            200,
            {
                'replication_settings': {'field': 'id', 'type': 'int'},
                'queue_states': {'state': {'last_replicated': '1235'}},
                'target_state': {'last_replicated': '1235'},
            },
            {
                'queue_timestamp': None,
                'targets_timestamp': None,
                'replicate_by': 'id',
            },
        ),
        (
            'basic_source_postgres_strict_sequence',
            200,
            {
                'replication_settings': {'field': 'id', 'type': 'int'},
                'queue_states': {'state': {'last_replicated': '1239'}},
                'target_state': {'last_replicated': '1234'},
            },
            {
                'queue_timestamp': None,
                'targets_timestamp': None,
                'replicate_by': 'id',
            },
        ),
        (
            'test_sharded_mongo',
            200,
            {
                'replication_settings': {
                    'field': 'updated',
                    'type': 'datetime',
                },
                'queue_states': {
                    'state': {'last_replicated': '2019-03-10T11:00:00+0000'},
                    'source_units': [
                        {'name': 'shard0', 'state': {}},
                        {
                            'name': 'shard1',
                            'state': {
                                'last_replicated': '2019-03-10T11:00:00+0000',
                            },
                        },
                    ],
                },
                'target_state': {
                    'last_replicated': '2019-01-09T11:00:00+0000',
                },
            },
            {
                'queue_timestamp': '2019-03-10T11:00:00+0000',
                'targets_timestamp': '2019-01-09T11:00:00+0000',
                'replicate_by': 'updated',
            },
        ),
        (
            'basic_source_mongo_snapshot',
            400,
            None,
            {
                'queue_timestamp': None,
                'targets_timestamp': None,
                'replicate_by': None,
            },
        ),
        ('nonexistent_rule', 404, None, None),
        (
            'test_sharded_mongo_sharded_queue',
            200,
            {
                'replication_settings': {
                    'field': 'updated',
                    'type': 'datetime',
                },
                'queue_states': {
                    'state': {'last_replicated': '2019-03-10T11:01:00+0000'},
                    'source_units': [
                        {
                            'name': 'shard0',
                            'state': {
                                'last_replicated': '2019-03-10T11:01:00+0000',
                            },
                        },
                        {
                            'name': 'shard1',
                            'state': {
                                'last_replicated': '2019-03-10T11:01:30+0000',
                            },
                        },
                    ],
                },
                'target_state': {
                    'last_replicated': '2019-03-10T10:00:21+0000',
                },
            },
            {
                'queue_timestamp': '2019-03-10T11:01:00+0000',
                'targets_timestamp': '2019-03-10T10:00:21+0000',
                'replicate_by': 'updated',
            },
        ),
    ],
)
async def test_get_min_ts(
        replication_client,
        replication_rule_name,
        response_status,
        expected,
        v1_expected,
):
    response = await replication_client.get(
        f'/v2/state/get/{replication_rule_name}',
    )
    assert response.status == response_status
    if response_status == 200:
        response_data = await response.json()
        assert response_data == expected, str(response_data)

    v1_response = await replication_client.get(
        f'/state/min_ts/{replication_rule_name}',
    )
    if response_status == 404:
        assert v1_response.status == response_status
    else:
        assert v1_response.status == 200
        response_data = await v1_response.json()
        assert response_data == v1_expected, str(response_data)
