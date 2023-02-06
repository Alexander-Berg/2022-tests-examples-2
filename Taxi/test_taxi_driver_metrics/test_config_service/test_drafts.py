import bson


SOME_ACTION = {
    'action': [
        {
            'tags': [{'name': 'RepositionOfferFailed', 'ttl': 86401}],
            'type': 'tagging',
        },
    ],
    'action_name': 'qwerty',
}
SOME_EVENT = {'name': 'complete', 'topic': 'order'}


async def test_remove_rule_drafts(
        taxi_driver_metrics, mockserver, web_context, create_rule,
):
    rule_body = {
        'actions': [SOME_ACTION],
        'additional_params': {'event_cnt_trashold': 2},
        'events': [SOME_EVENT],
        'name': f'blocking_drivers_1',
        'type': 'activity',
        'service_name': 'driver-metrics',
        'query': 'SELECT * FROM $order_metrics',
        'zone': 'spb',
        'protected': True,
        'deleted': False,
    }

    async def create_draft_rule(rule_body):
        return await create_rule(
            taxi_driver_metrics,
            body=rule_body,
            headers={'X-Ya-Service-Ticket': 'ticket'},
        )

    status, result = await create_draft_rule(rule_body)
    assert status == 200
    rule_id = result['id']

    result = await taxi_driver_metrics.post(
        'v1/config/rule/remove/check',
        json={
            'name': 'blocking_drivers_1',
            'type': 'activity',
            'service_name': 'driver-metrics',
            'zone': 'spb',
            'revision_id': rule_id,
        },
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    assert result.status == 200
    json = await result.json()

    change_doc_id = json.pop('change_doc_id')

    assert change_doc_id.startswith('spb:')

    assert json == {
        'data': {
            'name': 'blocking_drivers_1',
            'type': 'activity',
            'service_name': 'driver-metrics',
            'zone': 'spb',
            'revision_id': rule_id,
            'tariff': '__default__',
        },
    }

    await web_context.metrics_rules_config.handler.refresh_cache_locally()

    assert web_context.metrics_rules_config.cached_rules.ACTIVITY['spb']

    await taxi_driver_metrics.post(
        'v1/config/rule/remove',
        json={
            'name': 'blocking_drivers_1',
            'type': 'activity',
            'service_name': 'driver-metrics',
            'zone': 'spb',
            'revision_id': rule_id,
        },
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    await web_context.metrics_rules_config.handler.refresh_cache_locally()

    assert not web_context.metrics_rules_config.cached_rules.ACTIVITY['spb']

    status, result = await create_draft_rule(rule_body)
    assert status == 200
    rule_id = result['id']
    await web_context.metrics_rules_config.handler.refresh_cache_locally()
    assert web_context.metrics_rules_config.cached_rules.ACTIVITY['spb']

    await web_context.mongo.driver_metrics_rules_configs.update_one(
        {'revision_id': bson.ObjectId(rule_id)}, {'$set': {'protected': True}},
    )

    result = await taxi_driver_metrics.post(
        'v1/config/rule/remove/check',
        json={
            'name': 'blocking_drivers_1',
            'type': 'activity',
            'service_name': 'driver-metrics',
            'zone': 'spb',
            'revision_id': rule_id,
        },
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    # rule protected
    assert result.status == 400

    result = await taxi_driver_metrics.post(
        'v1/config/rule/protected/remove/check',
        json={
            'name': 'blocking_drivers_1',
            'type': 'activity',
            'service_name': 'driver-metrics',
            'zone': 'spb',
            'revision_id': rule_id,
        },
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    # rule protected
    assert result.status == 200
