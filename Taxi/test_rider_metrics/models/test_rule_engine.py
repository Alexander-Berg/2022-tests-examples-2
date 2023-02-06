# pylint:disable=protected-access
import datetime

import pytest

from metrics_processing.rules import common as rules_common
from metrics_processing.utils.safe_eval import safe_eval

from rider_metrics.models import rider as rider_module
from rider_metrics.models import rider_event
from rider_metrics.models.actions import constants

EXPECTED_ACTIONS = [
    {
        'type': 'communications',
        'campaign_id': 'communication_69',
        'triggered_context': {
            'tags': ['event::long_waiting', 'rider::bad', 'rider::good'],
        },
    },
    {
        'tags': [{'id': 'misha', 'name': 'ManyOTsWarning', 'ttl': 86400}],
        'type': 'tagging',
        'triggered_context': {
            'tags': ['event::long_waiting', 'rider::bad', 'rider::good'],
        },
    },
]


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True)
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'tags': '\'rider::good\'',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_69',
                            },
                            {
                                'tags': [
                                    {'name': 'ManyOTsWarning', 'ttl': 86400},
                                ],
                                'type': 'tagging',
                            },
                        ],
                    },
                ],
                'events': [
                    {
                        'topic': 'order',
                        'tags': (
                            'NOT \'event::stop\' AND \'event::long_waiting\''
                        ),
                    },
                ],
                'name': 'unique',
                'additional_params': {
                    'tags': '\'event::long_waiting\' AND \'rider::bad\'',
                },
            },
        ],
    },
)
def test_rule_engine(stq3_context):
    rider = rider_module.Rider(entity_id='misha')
    rider.update_tags({'good', 'bad'})
    rider.update_event(
        rider_event.RiderEvent(
            name='32',
            event_id='333',
            event_type='order',
            timestamp=datetime.datetime.utcnow(),
            entity_id='user',
            tariff_zone='helsinki',
            tags_=['long_waiting'],
        ),
    )

    actions = stq3_context.metrics_rules_config.apply(
        rules_common.RuleType.DEFAULT,
        rider,
        datetime.datetime.utcnow(),
        config_name='RIDER_METRICS_RULES',
        use_config_service=True,
    )

    for action, expected_action in zip(actions, EXPECTED_ACTIONS):
        assert action.ACTION_TYPE.value == expected_action['type']
        action._triggered_context['tags'].sort()
        assert (
            action._triggered_context == expected_action['triggered_context']
        )
        if action.ACTION_TYPE == constants.ActionType.COMMUNICATION:
            assert action._campaign_id == expected_action['campaign_id']
        elif action.ACTION_TYPE == constants.ActionType.TAGGING:
            assert action.tags == expected_action['tags']
        else:
            assert False


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True)
@pytest.mark.config(RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'tags': '\'rider::good\'',
                        'expr': 'event.event_zone == \'heaven\'',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_69',
                            },
                        ],
                    },
                    {
                        'tags': '\'rider::good\'',
                        'expr': 'event.event_zone == \'helsinki\'',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_69',
                            },
                        ],
                    },
                ],
                'events': [
                    {
                        'topic': 'order',
                        'tags': (
                            'NOT \'event::stop\' AND \'event::long_waiting\''
                        ),
                    },
                ],
                'name': 'rule1',
                'expr': 'rider.tags and "good" in rider.tags',
            },
        ],
    },
)
def test_expr_in_rule(stq3_context):
    rider = rider_module.Rider(entity_id='misha')
    rider.update_tags({'good', 'bad'})
    rider.update_event(
        rider_event.RiderEvent(
            event_id='333',
            event_type='order',
            timestamp=datetime.datetime.utcnow(),
            entity_id='user',
            tariff_zone='helsinki',
            tags_=['long_waiting'],
        ),
    )

    actions = stq3_context.metrics_rules_config.apply(
        rules_common.RuleType.DEFAULT,
        rider,
        now=datetime.datetime.utcnow(),
        config_name='RIDER_METRICS_RULES',
        use_config_service=True,
    )

    assert actions


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True)
@pytest.mark.config(RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'tags': '\'rider::good\'',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_69',
                            },
                        ],
                    },
                ],
                'events': [
                    {
                        'topic': 'order',
                        'tags': (
                            'NOT \'event::stop\' AND \'event::long_waiting\''
                        ),
                    },
                ],
                'name': 'rule1',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'expr, res',
    [
        ('rider.tags and "ok" in rider.tags', True),
        ('rider.tags and "false" not in rider.tags', True),
        ('event.event_type != "order"', False),
        ('event.event_type == "order"', True),
    ],
)
def test_expr(stq3_context, expr, res):
    for rule_ in stq3_context.metrics_rules_config.cached_rules.DEFAULT[
            'default'
    ].values():
        rule_.additional_params['expr'] = expr
        rule_.additional_params['parsed_expr'] = safe_eval.parse_expr(expr)
    rider = rider_module.Rider(entity_id='misha')
    rider.update_tags({'ok', 'good'})
    event = rider_event.RiderEvent(
        event_id='333',
        event_type='order',
        timestamp=datetime.datetime.utcnow(),
        entity_id='user',
        tariff_zone='helsinki',
        tags_=['long_waiting'],
    )
    rider.update_event(event)

    actions = stq3_context.metrics_rules_config.apply(
        rules_common.RuleType.DEFAULT,
        rider,
        datetime.datetime.utcnow(),
        config_name='RIDER_METRICS_RULES',
        use_config_service=True,
    )

    assert bool(actions) == res


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True)
@pytest.mark.config(RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'tags': '\'rider::good\'',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_69',
                            },
                        ],
                    },
                ],
                'events': [
                    {
                        'topic': 'order',
                        'tags': (
                            'NOT \'event::stop\' AND \'event::long_waiting\''
                        ),
                    },
                ],
                'name': 'rule1',
                'expr': 'rider.tags and "good" not in rider.tags',
            },
        ],
    },
)
def test_wrong_expr_in_rule(stq3_context):
    rider = rider_module.Rider(entity_id='misha')
    rider.update_tags({'good', 'bad'})
    rider.update_event(
        rider_event.RiderEvent(
            event_id='333',
            event_type='order',
            timestamp=datetime.datetime.utcnow(),
            entity_id='user',
            tariff_zone='helsinki',
            tags_=['long_waiting'],
        ),
    )

    actions = stq3_context.metrics_rules_config.apply(
        rules_common.RuleType.DEFAULT,
        rider,
        datetime.datetime.utcnow(),
        config_name='RIDER_METRICS_RULES',
        use_config_service=False,
    )
    assert not actions


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True)
@pytest.mark.config(RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [
                    {
                        'expr': '\'rider::good\' in rider.tags',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_69',
                            },
                        ],
                    },
                    {
                        'expr': '\'rider::good\' not in rider.tags',
                        'action': [
                            {
                                'type': 'communications',
                                'campaign_id': 'communication_71',
                            },
                        ],
                    },
                ],
                'events': [
                    {
                        'topic': 'order',
                        'tags': (
                            'NOT \'event::stop\' AND \'event::long_waiting\''
                        ),
                    },
                ],
                'tags': '\'experiment::rrr\'',
                'name': 'rule1',
            },
        ],
    },
)
def test_expr_in_actions(stq3_context):
    rider = rider_module.Rider(entity_id='misha')
    rider.update_tags({'good', 'bad'})
    rider.update_event(
        rider_event.RiderEvent(
            event_id='333',
            event_type='order',
            timestamp=datetime.datetime.utcnow(),
            entity_id='user',
            tariff_zone='helsinki',
            tags_=['long_waiting'],
        ),
    )

    rider.update_experiment_tags({'rrr'})

    actions = stq3_context.metrics_rules_config.apply(
        rules_common.RuleType.DEFAULT,
        rider,
        now=datetime.datetime.utcnow(),
        config_name='RIDER_METRICS_RULES',
        use_config_service=True,
    )

    assert len(actions) == 1


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=True)
@pytest.mark.rules_config(
    DEFAULT={
        'default': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [],
                'events': [],
                'name': 'rule1',
            },
            {
                'id': '2',
                'zone': 'default',
                'actions': [],
                'events': [],
                'name': 'rule2',
            },
        ],
        'spb': [
            {
                'id': '3',
                'zone': 'spb',
                'actions': [],
                'events': [],
                'name': 'rule2',
            },
            {
                'id': '4',
                'zone': 'spb',
                'actions': [],
                'events': [],
                'name': 'rule4',
            },
        ],
    },
)
def test_fetching_rules_config_dm(stq3_context):
    rules = stq3_context.metrics_rules_config.rules_by_zone(
        zone='spb',
        rule_type=rules_common.RuleType.DEFAULT,
        config_name=None,
        use_config_service=True,
    )

    assert rules == [
        rules_common.Rule.from_json_config(
            dict(
                name='rule1',
                events=[],
                actions=[],
                disabled=False,
                rule_type='default',
                zone='default',
                events_period_sec=3600,
                tags=None,
                events_to_trigger_cnt=1,
                expr=None,
                tariff='__default__',
            ),
        ),
        rules_common.Rule.from_json_config(
            dict(
                name='rule2',
                events=[],
                actions=[],
                disabled=False,
                rule_type='default',
                zone='spb',
                events_period_sec=3600,
                tags=None,
                events_to_trigger_cnt=1,
                expr=None,
                tariff='__default__',
            ),
        ),
        rules_common.Rule.from_json_config(
            dict(
                name='rule4',
                events=[],
                actions=[],
                disabled=False,
                rule_type='default',
                zone='spb',
                events_period_sec=3600,
                tags=None,
                events_to_trigger_cnt=1,
                expr=None,
                tariff='__default__',
            ),
        ),
    ]


@pytest.mark.config(RIDER_METRICS_USE_RULES_CONFIG_SERVICE=False)
@pytest.mark.config(
    RIDER_METRICS_RULES={
        '__default__': [
            {
                'id': '2',
                'zone': 'default',
                'actions': [],
                'events': [],
                'name': 'rule1',
            },
            {
                'id': '3',
                'zone': 'default',
                'actions': [],
                'events': [],
                'name': 'rule2',
            },
        ],
        'spb': [
            {
                'id': '4',
                'zone': 'spb',
                'actions': [],
                'events': [],
                'name': 'rule2',
            },
            {
                'id': '5',
                'zone': 'spb',
                'actions': [],
                'events': [],
                'name': 'rule4',
            },
        ],
    },
)
def test_fetching_rules_config(stq3_context):
    rules = stq3_context.metrics_rules_config.rules_by_zone(
        zone='spb',
        rule_type=rules_common.RuleType.DEFAULT,
        config_name='RIDER_METRICS_RULES',
    )
    assert rules == [
        rules_common.Rule.from_json_config(
            dict(
                name='rule1',
                events=[],
                actions=[],
                disabled=False,
                rule_type='default',
                zone='default',
                events_period_sec=3600,
                tags=None,
                events_to_trigger_cnt=1,
                expr=None,
                tariff='__default__',
            ),
        ),
        rules_common.Rule.from_json_config(
            dict(
                name='rule2',
                events=[],
                actions=[],
                disabled=False,
                rule_type='default',
                zone='spb',
                events_period_sec=3600,
                tags=None,
                events_to_trigger_cnt=1,
                tariff='__default__',
            ),
        ),
        rules_common.Rule.from_json_config(
            dict(
                name='rule4',
                events=[],
                actions=[],
                disabled=False,
                rule_type='default',
                zone='spb',
                events_period_sec=3600,
                tags=None,
                events_to_trigger_cnt=1,
                tariff='__default__',
            ),
        ),
    ]


@pytest.mark.config(
    RIDER_METRICS_USE_RULES_CONFIG_SERVICE=False,
    RIDER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True},
    RIDER_METRICS_RULES={
        '__default__': [
            {
                'id': '1',
                'zone': 'default',
                'actions': [],
                'events': [
                    {'topic': 'order', 'expr': 'event.extra_data["i"] > 1.0'},
                ],
                'name': 'rule1',
                'events_to_trigger_cnt': 2,
            },
        ],
    },
)
def test_expr_in_events(stq3_context):
    rules = stq3_context.metrics_rules_config.rules_by_zone(
        'default',
        rules_common.RuleType.DEFAULT,
        config_name='RIDER_METRICS_RULES',
    )
    assert [
        left == right
        for left, right in zip(
            rules,
            [
                rules_common.Rule.from_json_config(
                    dict(
                        name='rule1',
                        events=[
                            dict(
                                topic='order',
                                expr='event.extra_data["i"] > 1.0',
                            ),
                        ],
                        rule_type='default',
                        actions=[],
                        disabled=False,
                        zone='default',
                        events_period_sec=3600,
                        tags=None,
                        events_to_trigger_cnt=2,
                    ),
                ),
            ],
        )
    ]

    fetched_rule = rules[0]

    events = [
        rider_event.RiderEvent(
            '',
            datetime.datetime.utcnow(),
            event_type='order',
            extra_data={'i': i},
        )
        for i in (1, 2, 3)
    ]
    rider = rider_module.Rider('')
    rider._entity_history = events

    modifier = rules_common.EventsCountModifier(
        event=events[-1],
        entity=rider,
        rule=fetched_rule,
        now=datetime.datetime.utcnow(),
        triggered_context={},
    )

    assert modifier.satisfy_rule()
