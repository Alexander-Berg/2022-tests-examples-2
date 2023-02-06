async def test_monitor_invalid_config(
        taxi_stq_agent, taxi_stq_agent_monitor, mongodb,
):
    response = await taxi_stq_agent_monitor.get('diagnostics')
    assert response.status_code == 200
    assert response.json() == {'invalid_config_queues': {'queues': []}}

    mongodb.stq_config.update(
        {'_id': 'foo'},
        {
            '$set': {
                'shards': [
                    {
                        'database': 'db',
                        'collection': 'foo_0',
                        'hosts': ['host1'],
                    },
                ],
            },
        },
    )
    await taxi_stq_agent.invalidate_caches()

    response = await taxi_stq_agent_monitor.get('diagnostics')
    assert response.status_code == 200
    assert response.json() == {'invalid_config_queues': {'queues': ['foo']}}
