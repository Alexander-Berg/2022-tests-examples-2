async def delete_config_request(client, body):
    result = await client.post('/v1/config/rule/remove/', json=body)
    json_response = await result.json()
    return result.status, json_response


async def test_deleting_rules(
        stq3_context, taxi_driver_metrics, patch, create_rule, test_rule,
):
    @patch(
        'metrics_processing.utils.helpers.' 'check_title_message_tanker_key',
    )
    def _(_):
        return True

    status, body = await create_rule(taxi_driver_metrics)
    assert status == 200

    status, body = await create_rule(taxi_driver_metrics, zone='izhevsk')
    assert status == 200

    status, _ = await create_rule(taxi_driver_metrics, zone='izhevsk')
    assert status == 409

    await stq3_context.metrics_rules_config.handler.refresh_cache_locally()
    assert (
        len(stq3_context.metrics_rules_config.cached_rules.STQ_CALLBACK) == 2
    )
    assert stq3_context.metrics_rules_config.cached_rules.STQ_CALLBACK[
        'izhevsk'
    ]

    status, _ = await delete_config_request(
        taxi_driver_metrics,
        {
            'service_name': test_rule['service_name'],
            'name': test_rule['name'],
            'type': test_rule['type'],
            'zone': 'izhevsk',
        },
    )
    assert status == 400

    status, body = await delete_config_request(
        taxi_driver_metrics,
        {
            'service_name': test_rule['service_name'],
            'name': test_rule['name'],
            'type': test_rule['type'],
            'zone': 'izhevsk',
            'revision_id': body['id'],
        },
    )
    assert status == 200

    await stq3_context.metrics_rules_config.handler.refresh_cache_locally()

    assert (
        len(stq3_context.metrics_rules_config.cached_rules.STQ_CALLBACK) == 2
    )
    assert (
        stq3_context.metrics_rules_config.cached_rules.STQ_CALLBACK['izhevsk']
        == {}
    )

    status, body = await create_rule(taxi_driver_metrics, zone='izhevsk')
    assert status == 200
