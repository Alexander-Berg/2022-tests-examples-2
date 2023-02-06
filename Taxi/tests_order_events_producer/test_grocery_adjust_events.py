import json


async def test_grocery_ajdust_events_alive(
        testpoint,
        taxi_config,
        mockserver,
        taxi_order_events_producer,
        taxi_eventus_orchestrator_mock,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    pipelines_config = [
        {
            'description': '',
            'st_ticket': '',
            'source': {'name': 'grocery-adjust-events'},
            'root': {
                'output': {'sink_name': 'log_sink'},
                'operations': [
                    {
                        'name': 'add-seq-num',
                        'operation_variant': {
                            'arguments': {},
                            'operation_name': 'set_seq_num',
                            'type': 'mapper',
                        },
                    },
                ],
            },
            'name': 'test-grocery-adjust-events-alive',
        },
    ]

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_events_producer, pipelines_config,
    )
    await taxi_order_events_producer.run_task('invalidate-seq_num')

    event = {'key': 'value'}

    response = await taxi_order_events_producer.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'grocery-adjust-events',
                'data': json.dumps(event),
                'topic': 'smth',
                'cookie': 'cookie_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_0'
