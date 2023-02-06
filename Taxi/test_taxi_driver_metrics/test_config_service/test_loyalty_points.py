import pytest

HANDLER_PATH = '/v1/config/rule/loyalty/points'


@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'name': 'test_rule',
                'events': [{'topic': 'order', 'name': 'complete'}],
                'actions': [
                    {
                        'tags': """ 'event::a' """,
                        'action': [{'type': 'loyalty', 'value': 100}],
                        'action_name': 'event_a',
                    },
                    {
                        'tags': """ 'event::tariff_vip' """,
                        'action': [{'type': 'loyalty', 'value': -100}],
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': 0}],
                        'action_name': 'default',
                    },
                ],
            },
        ],
        'moscow': [
            {
                'name': 'test_rule',
                'events': [{'topic': 'order', 'name': 'complete'}],
                'actions': [
                    {
                        'tags': """ 'event::a' """,
                        'action': [{'type': 'loyalty', 'value': 10}],
                        'action_name': 'event_a',
                    },
                    {
                        'tags': """ 'event::tariff_vip' """,
                        'action': [{'type': 'loyalty', 'value': -10}],
                    },
                ],
            },
            {
                'name': 'test_rule_moscow',
                'events': [{'topic': 'order', 'name': 'offer_timeout'}],
                'actions': [
                    {
                        'expr': 'not event.surge',
                        'action': [{'type': 'loyalty', 'value': -1}],
                        'action_name': 'not surge',
                    },
                    {
                        'tags': """ 'event::surge' """,
                        'action': [{'type': 'loyalty', 'value': 1}],
                        'action_name': 'surge!<><>__ _',
                    },
                ],
            },
        ],
        'spb': [
            {
                'name': 'test_rule_spb',
                'events': [{'topic': 'order', 'name': 'user_cancel'}],
                'actions': [
                    {
                        'expr': '\'omg\' in event.tags',
                        'action': [{'type': 'loyalty', 'value': 99}],
                        'action_name': 'omg',
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': -100}],
                        'action_name': 'minus_sto_prosto_tak',
                    },
                ],
            },
            {
                'name': 'test_rule_spb_complete',
                'events': [{'topic': 'order'}],
                'actions': [
                    {
                        'action': [{'type': 'loyalty', 'value': 45}],
                        'action_name': '321Ooo_ye',
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': -1}],
                        'action_name': 1,
                    },
                ],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'zone, expected_status, expected_response',
    (
        (
            None,
            400,
            {
                'code': 'incorrect_zone',
                'details': {'zone': None},
                'message': 'Zone is empty',
            },
        ),
        (
            'spb',
            200,
            {
                'items': [
                    {
                        'action_name': 'event_a',
                        'rule_name': 'test_rule',
                        'value': 100,
                    },
                    {
                        'action_name': 'omg',
                        'rule_name': 'test_rule_spb',
                        'value': 99,
                    },
                    {
                        'action_name': 'minus_sto_prosto_tak',
                        'rule_name': 'test_rule_spb',
                        'value': -100,
                    },
                    {
                        'action_name': '321Ooo_ye',
                        'rule_name': 'test_rule_spb_complete',
                        'value': 45,
                    },
                    {
                        'action_name': 1,
                        'rule_name': 'test_rule_spb_complete',
                        'value': -1,
                    },
                ],
            },
        ),
        (
            'ashenvale',
            200,
            {
                'items': [
                    {
                        'action_name': 'event_a',
                        'rule_name': 'test_rule',
                        'value': 100,
                    },
                ],
            },
        ),
        (
            'moscow',
            200,
            {
                'items': [
                    {
                        'action_name': 'event_a',
                        'rule_name': 'test_rule',
                        'value': 10,
                    },
                    {
                        'action_name': 'not surge',
                        'rule_name': 'test_rule_moscow',
                        'value': -1,
                    },
                    {
                        'action_name': 'surge!<><>__ _',
                        'rule_name': 'test_rule_moscow',
                        'value': 1,
                    },
                ],
            },
        ),
    ),
)
async def test_loyalty_point(
        taxi_driver_metrics, zone, expected_status, expected_response,
):

    params = {'zone': zone} if zone else {}

    response = await taxi_driver_metrics.get(HANDLER_PATH, params=params)

    assert response.status == expected_status

    json = await response.json()

    assert json == expected_response
