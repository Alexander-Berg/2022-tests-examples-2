import json

import pytest

TEST_TEAM = {
    'description': (
        'Группа разработки инфраструктуры пользовательских продуктов'
    ),
    'staff_groups': [
        'yandex_distproducts_browserdev_mobile_taxi_9720_dep95813',
    ],
}
JUGGLER_RESPONSE = {
    'accepted_events': 1,
    'events': [{'code': 200}],
    'success': True,
}


@pytest.mark.disable_config_check
@pytest.mark.config(
    DEV_TEAMS={'test-team': TEST_TEAM, 'other-team': TEST_TEAM},
    FOO={'foo'},
    UPSTREAM_QOS_CONFIG={'__default__': {}},
)
@pytest.mark.parametrize(
    'dev_team, status, description, qos_config',
    [
        pytest.param(
            'test-team',
            'OK',
            'OK: all taxi-configs exist and qos ok',
            {'__default__': {'timeout-ms': 100, 'attempts': 2}},
            id='ok',
        ),
        pytest.param(
            'test-team',
            'WARN',
            'WARN: Invalid QoS configs: UPSTREAM_QOS_CONFIG',
            {
                '__default__': {'timeout-ms': 1, 'attempts': {'value': '42'}},
                'upstream-with-qos': {
                    'timeout-ms': 42,
                    'attempts': {'value': '1'},
                },
            },
            id='bad QoS schema',
        ),
        pytest.param(
            'test-team',
            'WARN',
            'WARN: Invalid QoS configs: UPSTREAM_QOS_CONFIG',
            {'timeout-ms': 100, 'attempts': 2},
            id='bad QoS operations schema',
        ),
    ],
)
async def test_invalid_qos_config_update(
        taxi_api_proxy,
        mockserver,
        endpoints,
        resources,
        taxi_config,
        load_yaml,
        qos_config,
        dev_team,
        status,
        description,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        for event in data['events']:
            if event['service'] == f'autogen_{dev_team}_handlers_configs':
                assert event['status'] == status
                assert event['description'] == description
                return JUGGLER_RESPONSE
        assert 0
        return {}

    await resources.safely_create_resource(
        resource_id='upstream-with-qos',
        url=mockserver.url('/upstream-with-qos'),
        method='post',
        qos_taxi_config='UPSTREAM_QOS_CONFIG',
    )

    await endpoints.safely_create_endpoint(
        path='/ep_with_upstream',
        endpoint_id='ep-with-upstream',
        post_handler=load_yaml('endpoint_with_upstream.yaml'),
        dev_team='test-team',
    )

    taxi_config.set(UPSTREAM_QOS_CONFIG=qos_config)
    await taxi_api_proxy.invalidate_caches()

    await taxi_api_proxy.run_periodic_task('handlers_configs-juggler-push')
    assert events_handler.times_called == 1
