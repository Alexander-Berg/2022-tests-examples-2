# pylint: disable=protected-access
import datetime

import pytest

from metrics_processing.rules.common import RuleType
from metrics_processing.rules.common.rule import ActionsEntry
from metrics_processing.rules.common.rule import Event
from metrics_processing.rules.common.rule import Rule

from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events


DRIVER_ID = 'uuid'
UDID = 'udid'
ZONE = 'msk'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)


# noinspection PyTypeChecker
@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'name': 'the_rule',
                'events': [
                    {
                        'topic': 'order',
                        'name': 'offer_timeout',
                        'tags': """ 'tags::wow' OR 'event::chain' """,
                    },
                ],
                'tags': """ 'tags::rock' AND NOT 'experiment::roll' """,
                'zone': ZONE,
                'actions': [
                    {
                        'tags': '\'selfemployed\'',
                        'action': [{'type': 'loyalty', 'value': 100}],
                    },
                    {
                        'action': [{'type': 'loyalty', 'value': -100}],
                        'action_name': 'qwerty',
                    },
                ],
                'expr': (
                    'driver.tags == event.tags and '
                    'event.event_zone != \'mahachkala\''
                ),
            },
        ],
        # a rule without events or actions is not possible
        # but we can still use it for the sake of tests
        ZONE: [{'zone': ZONE, 'name': 'a_rule', 'events': [], 'actions': []}],
    },
)
@pytest.mark.parametrize(
    'zone, expected',
    [
        (
            ZONE,  # rules have different names so they should both be created
            [
                Rule.from_json_config(
                    dict(
                        name='the_rule',
                        zone='default',
                        events_period_sec=3600,
                        events_to_trigger_cnt=1,
                        tags=""" 'tags::rock' AND NOT 'experiment::roll' """,
                        expr=(
                            'driver.tags == event.tags and '
                            'event.event_zone != \'mahachkala\''
                        ),
                        events=[
                            dict(
                                topic='order',
                                name='offer_timeout',
                                tags=""" 'tags::wow' OR 'event::chain' """,
                            ),
                        ],
                        actions=[
                            dict(
                                tags='\'selfemployed\'',
                                action=[{'type': 'loyalty', 'value': 100}],
                                action_name=None,
                            ),
                            dict(
                                action=[{'type': 'loyalty', 'value': -100}],
                                action_name='qwerty',
                            ),
                        ],
                        disabled=False,
                        rule_type=RuleType.LOYALTY.value,
                    ),
                ),
                Rule.from_json_config(
                    dict(
                        name='a_rule',
                        zone=ZONE,
                        events_period_sec=3600,
                        events_to_trigger_cnt=1,
                        tags=None,
                        expr=None,
                        events=[],
                        actions=[],
                        disabled=False,
                        rule_type=RuleType.LOYALTY.value,
                    ),
                ),
            ],
        ),
    ],
)
async def test_make_from_config(stq3_context, zone, expected):
    res = stq3_context.metrics_rules_config.rules_by_zone(
        rule_type=RuleType.LOYALTY, zone=zone, use_config_service=True,
    )
    assert [left == right for left, right in zip(res, expected)]


@pytest.mark.rules_config(
    LOYALTY={
        'default': [
            {
                'name': 'the_rule',
                'events': [
                    {
                        'topic': 'order',
                        'name': 'offer_timeout',
                        'tags': """ 'tags::wow' OR 'event::chain' """,
                    },
                ],
                'tags': """ 'tags::rock' AND NOT 'experiment::roll' """,
                'actions': [
                    {
                        'tags': '\'selfemployed\'',
                        'action': [{'type': 'loyalty', 'value': 100}],
                    },
                    {'action': [{'type': 'loyalty', 'value': -100}]},
                ],
                'expr': 'not not not None is True',
                'zonw': ZONE,
            },
        ],
        ZONE: [
            {
                'name': 'the_rule',
                'zone': ZONE,
                'events': [],
                'actions': [],
                'additional_params': {'are_events_in_a_row': True},
            },
        ],
    },
)
@pytest.mark.parametrize(
    'zone, expected',
    [
        (
            ZONE,  # rules have same names so zone rule should override
            [
                Rule(
                    name='the_rule',
                    zone=ZONE,
                    additional_params={
                        'events_period_sec': 3600,
                        'events_to_trigger_cnt': 1,
                        'tags': None,
                        'expr': None,
                        'are_events_in_a_row': True,
                    },
                    events=[],
                    actions=[],
                    disabled=False,
                    type=RuleType.LOYALTY.value,
                ),
            ],
        ),
    ],
)
async def test_make_from_config_override(stq3_context, zone, expected):
    res = stq3_context.metrics_rules_config.rules_by_zone(
        rule_type=RuleType.LOYALTY, zone=zone, use_config_service=True,
    )
    assert [left == right for left, right in zip(res, expected)]


# noinspection PyTypeChecker
@pytest.mark.config(DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
def test_apply(web_context, patch_rules):
    rule = Rule.from_json_config(
        json=dict(
            name='the_rule',
            revision_id='revision_id',
            zone=ZONE,
            events_to_trigger_cnt=1,
            events_period_sec=3600,
            tags=""" 'tags::rock' AND NOT 'experiment::roll' """,
            expr=f'event.event_zone == \'{ZONE}\'',
            events=[
                dict(
                    topic='order',
                    name='offer_timeout',
                    tags=""" 'tags::wow' OR 'event::chain' """,
                ),
            ],
            actions=[
                dict(
                    tags='\'tags::selfemployed\'',
                    action=[{'type': 'loyalty', 'value': 100}],
                ),
                dict(action=[{'type': 'loyalty', 'value': -100}]),
            ],
            disabled=False,
            rule_type='loyalty',
        ),
    )

    patch_rules([rule])

    driver = DriverInfo(udid=UDID, tags=set())
    event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            event_name='offer_timeout', tags=['chain'],
        ),
        timestamp=TIMESTAMP,
        zone=ZONE,
        event_id='event_id',
        driver_id=DRIVER_ID,
        entity_id=UDID,
        order_id='393j3393j939j394',
        activity_value=10,
    )
    driver.update_event(event)
    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert not res  # driver tags don't satisfy rule

    driver.tags.add('tags::rock')
    event.tags.append('rock')
    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert len(res) == 1
    res = res[0]
    assert res == {
        'rule_name': 'the_rule',
        'type': 'loyalty',
        'value': -100,
        'triggered_context': {'tags': ['event::chain', 'tags::rock']},
        'rule_config_id': 'revision_id',
        'protected': False,
    }

    driver.tags.add('tags::selfemployed')
    event.tags.append('tags::selfemployed')
    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert len(res) == 1
    res = res[0]
    assert res == {
        'rule_name': 'the_rule',
        'type': 'loyalty',
        'value': 100,
        'triggered_context': {
            'tags': ['event::chain', 'tags::rock', 'tags::selfemployed'],
        },
        'rule_config_id': 'revision_id',
        'protected': False,
    }

    rule.actions = [
        ActionsEntry.from_json_config(
            dict(
                tags='\'tags::selfemployed\'',
                action=[
                    {'type': 'loyalty', 'value': 100},
                    {'type': 'unknown_type', 'random_key': 'random_value'},
                ],
            ),
        ),
    ]
    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert len(res) == 2
    assert res == [
        {
            'rule_name': 'the_rule',
            'type': 'loyalty',
            'value': 100,
            'triggered_context': {
                'tags': ['event::chain', 'tags::rock', 'tags::selfemployed'],
            },
            'rule_config_id': 'revision_id',
            'protected': False,
        },
        {
            'rule_name': 'the_rule',
            'type': 'unknown_type',
            'rule_config_id': 'revision_id',
            'triggered_context': {
                'tags': ['event::chain', 'tags::rock', 'tags::selfemployed'],
            },
            'random_key': 'random_value',
            'protected': False,
        },
    ]

    event_without_tags = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            event_name='offer_timeout', tags=[],
        ),
        timestamp=TIMESTAMP,
        zone=ZONE,
        event_id='event_id',
        driver_id=DRIVER_ID,
        entity_id=UDID,
        order_id='393j3393j939j394',
        activity_value=10,
    )

    driver._event = event_without_tags

    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert not res

    driver._event = event

    rule.disabled = True
    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert not res

    rule.disabled = False

    # next conditions are currently unreachable
    rule.actions = []
    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert not res

    rule.actions = [
        ActionsEntry.from_json_config(
            dict(tags='\'tags::selfemployed\'', action=[{'value': 100}]),
        ),
    ]

    driver._event = event_without_tags

    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )
    assert not res


@pytest.mark.config(DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
def test_expr_in_action(web_context, patch_rules):
    rule = Rule.from_json_config(
        dict(
            name='the_rule',
            zone=ZONE,
            events=[
                dict(
                    topic='order',
                    name='offer_timeout',
                    tags=""" 'tags::wow' OR 'event::chain' """,
                ),
            ],
            events_period_sec=3600,
            events_to_trigger_cnt=1,
            tags=""" 'tags::rock' AND NOT 'experiment::roll' """,
            actions=[
                dict(
                    action=[{'type': 'loyalty', 'value': 100}],
                    expr='"chain" in event.tags',
                ),
                dict(
                    action=[{'type': 'loyalty', 'value': -100}],
                    expr='driver.activity > 80',
                ),
            ],
            disabled=False,
            rule_type='loyalty',
        ),
    )
    driver = DriverInfo(udid=UDID, activity=70, tags={'tags::rock'})
    event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            event_name='offer_timeout', tags=['chain'],
        ),
        timestamp=TIMESTAMP,
        zone=ZONE,
        event_id='event_id',
        driver_id=DRIVER_ID,
        entity_id=UDID,
        order_id='393j3393j939j394',
        activity_value=10,
    )
    driver.update_event(event)
    patch_rules([rule])

    res = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )

    assert len(res) == 1
    assert res[0] == {
        'rule_name': 'the_rule',
        'rule_config_id': None,
        'triggered_context': {'tags': ['event::chain', 'tags::rock']},
        'type': 'loyalty',
        'value': 100,
        'protected': False,
    }


@pytest.mark.config(DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
def test_expr_in_action2(web_context, patch_rules):
    rule1 = Rule(
        name='the_rule',
        zone='default',
        events=[Event(topic='order')],
        additional_params={'expr': 'driver.activity > 80'},
        actions=[
            ActionsEntry(
                action=[{'type': 'tagging', 'tags': [{'tag': 'test1'}]}],
            ),
        ],
        disabled=False,
        type='tagging',
    )
    rule2 = Rule(
        name='the_rule2',
        zone='default',
        events=[Event(topic='order')],
        additional_params={'expr': 'driver.activity <=80'},
        actions=[
            ActionsEntry(
                action=[{'type': 'tagging', 'tags': [{'tag': 'test2'}]}],
            ),
        ],
        disabled=False,
        type='tagging',
    )
    driver = DriverInfo(udid=UDID, activity=100)
    event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(event_name='complete', tags=[]),
        timestamp=TIMESTAMP,
        zone=ZONE,
        event_id='event_id',
        driver_id=DRIVER_ID,
        entity_id=UDID,
        order_id='393j3393j939j394',
        activity_value=10,
    )
    driver.update_event(event)
    patch_rules([rule1, rule2])

    res = web_context.metrics_rules_config.apply(
        RuleType.TAGGING, driver, TIMESTAMP,
    )

    assert res


# noinspection PyTypeChecker
@pytest.mark.config(DRIVER_METRICS_EXPRESSIONS_SETTINGS={'enabled': True})
@pytest.mark.parametrize(
    'expr, res',
    [
        ('driver.activity < 11', False),
        ('driver.activity >= 80 or "q" not in event.tags', True),
        ('event.event_type != "order" or event.name != "complete"', False),
        ('driver.tags and "a" in driver.tags', True),
        ('driver.activity == 70', True),
        ('driver.activity > 80 and "q3" in event.tags', False),
        ('event.event_type == "order" and event.name == "complete"', True),
        ('not driver.tags or not event.tags or not driver.activity', False),
        ('"b" in (None or driver.tags)', True),
        # expressions with mistakes always result in False
        ('event.timestamp >= driver.created', False),
        ('Anime', False),
    ],
)
def test_rule_satisfies_expr(web_context, expr, res, patch_rules):
    rule = Rule.from_json_config(
        dict(
            name='name',
            zone='bangladesh',
            events=[dict(topic='order')],
            events_period_sec=3600,
            events_to_trigger_cnt=1,
            tags='',
            expr=expr,
            actions=[dict(action=[{'type': 'loyalty', 'value': -100}])],
            disabled=False,
            rule_type='loyalty',
        ),
    )
    event = Events.OrderEvent(
        event_id='eid',
        timestamp=TIMESTAMP,
        entity_id='udid',
        zone='bangladesh',
        order_id='oid',
        descriptor=Events.EventTypeDescriptor(
            event_name='complete', tags=['very', 'busy'],
        ),
    )
    driver = DriverInfo(
        udid='udid', activity=70, tags={'a', 'b'}, events=[event],
    )

    driver.update_event(event)

    patch_rules([rule])

    actions = web_context.metrics_rules_config.apply(
        RuleType.LOYALTY, driver, TIMESTAMP,
    )

    assert bool(actions) == res
