import pytest


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
RULES = [
    {
        'actions': [SOME_ACTION],
        'additional_params': {'event_cnt_threshold': 2},
        'events': [SOME_EVENT],
        'name': 'blocking_drivers_1',
        'type': 'activity',
        'service_name': 'driver-metrics',
        'query': 'SELECT * FROM $order_metrics',
        'zone': zone,
        'protected': False,
        'deleted': False,
        'tariff': '__default__',
    }
    for zone in ['spb', 'default', 'moscow']
]


@pytest.mark.parametrize(
    'rules, expected_old',
    [
        (RULES, []),
        (
            [
                {
                    'name': 'zbork tag F',
                    'revision_id': '5f8dc81d7b28510039da29f0',
                    'service_name': 'driver-metrics',
                    'type': 'tagging',
                    'zone': 'default',
                    'actions': [SOME_ACTION],
                    'additional_params': {
                        'events_period_sec': '3600',
                        'events_to_trigger_cnt': '1',
                    },
                    'disabled': False,
                    'events': [
                        {
                            'topic': 'dm_service_manual',
                            'name': 'set_activity_value',
                        },
                    ],
                    'protected': False,
                    'delayed': True,
                    'tariff': '__default__',
                },
            ],
            [
                {
                    'service_name': 'driver-metrics',
                    'name': 'zbork tag F',
                    'zone': 'default',
                    'type': 'tagging',
                    'events': [
                        {
                            'topic': 'dm_service_manual',
                            'name': 'set_activity_value',
                        },
                    ],
                    'actions': [
                        {
                            'action': [
                                {
                                    'type': 'tagging',
                                    'tags': [{'name': 'Pog', 'ttl': 300}],
                                },
                            ],
                            'expr': 'event.activity_change == 6',
                        },
                    ],
                    'revision_id': '5f8dc81d7b28510039da29f0',
                    'additional_params': {
                        'events_period_sec': '3600',
                        'events_to_trigger_cnt': '1',
                    },
                    'disabled': False,
                    'updated': '2020-10-19T17:08:45.330000Z',
                    'protected': False,
                    'delayed': True,
                    'deleted': False,
                    'tariff': '__default__',
                },
            ],
        ),
    ],
)
async def test_create_rule_drafts(
        taxi_driver_metrics,
        mockserver,
        tags_service_mock,
        web_context,
        create_rule,
        rules,
        expected_old,
):
    tags_service_mock(tag_info={'is_financial': False})
    result = await taxi_driver_metrics.post(
        'v1/config/bulk/draft/check',
        json={'new': rules},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    assert result.status == 200
    json = await result.json()

    assert json['data'] == {'new': rules}
    assert json['diff']['current']['data'] == expected_old

    res = await taxi_driver_metrics.post(
        'v1/config/bulk/draft/apply',
        json={'new': rules},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )
    assert res.status == 200
    json = await res.json()
    assert json['status'] == 'completed'
