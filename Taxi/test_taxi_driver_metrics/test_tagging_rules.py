import datetime
import typing as tp

import pytest

from metrics_processing.rules.common import RuleType
from metrics_processing.rules.common.rule import ActionsEntry
from metrics_processing.rules.common.rule import Event
from metrics_processing.rules.common.rule import Rule
from metrics_processing.tagging import utils as tags_utils

from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models.rules import rule_utils


TST_UDID = 'tst_udid'
TST_ZONE = 'tst_zone'
TST_DRIVER_ID = '8800_5553535'
TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)


def _tagging_rule_to_new_rule(old: tp.Dict) -> tp.Dict:
    new = dict()
    new['name'] = old.get('rule_name')
    new['events'] = [
        dict(
            name=event.get('name'),
            topic='order',
            tags=' OR '.join(
                ['\'event::' + tag + '\'' for tag in event.get('tags', [])],
            ),
        )
        for event in old.get('events', [])
    ]
    new['actions'] = [
        {'action': [dict(old['tagging'], type=RuleType.TAGGING.value)]},
    ]
    if old.get('tags'):
        new['tags'] = old['tags']
    if old.get('events_period_sec'):
        new['events_period_sec'] = old['events_period_sec']
    if old.get('events_to_trigger_cnt'):
        new['events_to_trigger_cnt'] = old['events_to_trigger_cnt']
    return new


# noinspection PyTypeChecker


@pytest.mark.parametrize(
    'rule, tags, events, expected',
    [
        (
            (
                [Events.OrderEventType.OFFER_TIMEOUT],
                [{'name': 'bad'}],
                'append',
                'udid',
                1,
                False,
                None,
            ),
            {'flying car', 'loves dogs'},
            [Events.OrderEventType.OFFER_TIMEOUT],
            ([{'name': 'bad'}], tags_utils.TagMergePolicy.APPEND.value),
        ),
        (
            (
                [
                    Events.OrderEventType.COMPLETE,
                    Events.OrderEventType.USER_CANCEL,
                ],
                [{'name': 'no seat belts'}, {'name': 'low_priority'}],
                'remove',
                'udid',
                2,
                False,
                None,
            ),
            {'flying car', 'no seat belts', 'loves cats'},
            [
                Events.OrderEventType.COMPLETE,
                Events.OrderEventType.USER_CANCEL,
                Events.OrderEventType.COMPLETE,
            ],
            (
                [{'name': 'no seat belts'}, {'name': 'low_priority'}],
                tags_utils.TagMergePolicy.REMOVE.value,
            ),
        ),
        pytest.param(
            (
                [Events.OrderEventType.COMPLETE],
                [{'name': 'no seat belts'}, {'name': 'low_priority'}],
                'remove',
                'udid',
                2,
                True,
                None,
            ),
            {'flying car', 'no seat belts', 'loves cats'},
            [
                Events.OrderEventType.COMPLETE,
                Events.OrderEventType.USER_CANCEL,
                Events.OrderEventType.COMPLETE,
            ],
            None,
            id='events_not_in_a_row_but_rule_is',
        ),
        pytest.param(
            (
                [Events.OrderEventType.COMPLETE],
                [{'name': 'no seat belts'}, {'name': 'low_priority'}],
                'remove',
                'udid',
                2,
                False,
                120,
            ),
            {'flying car', 'no seat belts', 'loves cats'},
            [
                Events.OrderEventType.COMPLETE,
                Events.OrderEventType.USER_CANCEL,
                Events.OrderEventType.COMPLETE,
            ],
            None,
            marks=pytest.mark.now(
                (TIMESTAMP + datetime.timedelta(seconds=121)).isoformat(),
            ),
            id='event_too_old_skip_rule',
        ),
        pytest.param(
            (
                [Events.OrderEventType.COMPLETE],
                [{'name': 'no seat belts'}, {'name': 'low_priority'}],
                'remove',
                'udid',
                2,
                False,
                120,
            ),
            {'flying car', 'no seat belts', 'loves cats'},
            [
                Events.OrderEventType.COMPLETE,
                Events.OrderEventType.USER_CANCEL,
                Events.OrderEventType.COMPLETE,
            ],
            (
                [{'name': 'no seat belts'}, {'name': 'low_priority'}],
                tags_utils.TagMergePolicy.REMOVE.value,
            ),
            marks=pytest.mark.now(
                (TIMESTAMP + datetime.timedelta(seconds=100)).isoformat(),
            ),
            id='event_new_enough_apply_rule',
        ),
    ],
)
def test_apply(web_context, rule, tags, events, expected, patch_rules):
    _new_rule = Rule(
        name='the_rule',
        revision_id='revision_id',
        zone=rule_utils.CONFIG_DEFAULT,
        additional_params={
            'events_to_trigger_cnt': rule[4],
            'events_period_sec': 3600,
            'are_events_in_a_row': rule[5],
            'tags': (
                '\'tags::loves cats\' OR NOT (\'tags::flying car\''
                ' AND \'tags::no seat belts\')'
            ),
        },
        events=[Event(topic='order', name=descr.value) for descr in rule[0]],
        disabled=False,
        actions=[
            ActionsEntry(
                action=[
                    {
                        'type': RuleType.TAGGING.value,
                        'tags': rule[1],
                        'entity_type': tags_utils.TagEntityType(rule[3]).value,
                        'merge_policy': tags_utils.TagMergePolicy(
                            rule[2],
                        ).value,
                    },
                ],
            ),
        ],
        deadline_seconds=rule[6],
    )

    driver = DriverInfo(udid=TST_UDID, tags=tags)

    for event_type in events:
        driver.update_event(
            Events.OrderEvent(
                descriptor=Events.EventTypeDescriptor(event_type.value),
                timestamp=TIMESTAMP,
                zone=rule_utils.CONFIG_DEFAULT,
                event_id='event_id',
                driver_id=TST_DRIVER_ID,
                entity_id=TST_UDID,
                order_id='393j3393j939j394',
                activity_value=10,
            ),
        )

    patch_rules([_new_rule])

    res_new = web_context.metrics_rules_config.apply(
        rule_type=None,
        entity=driver,
        now=TIMESTAMP,
        config_name=None,
        use_config_service=True,
    )

    assert len(res_new) == bool(expected)
    if not expected:
        return

    res_new = res_new[0]
    assert res_new == {
        'rule_name': 'the_rule',
        'type': 'tagging',
        'tags': expected[0],
        'rule_config_id': 'revision_id',
        'triggered_context': {'tags': []},
        'protected': False,
        'entity_type': 'udid',
        'merge_policy': expected[1],
    }


# noinspection PyTypeChecker
def test_correctness(web_context, patch_rules):
    driver = DriverInfo(udid=TST_UDID)
    rule = Rule(
        name='rule_name',
        zone=rule_utils.CONFIG_DEFAULT,
        protected=True,
        additional_params={
            'events_period_sec': 7200,
            'events_to_trigger_cnt': 1,
        },
        type='tagging',
        events=[Event(topic='order', name='complete')],
        actions=[
            ActionsEntry(
                action=[
                    {
                        'type': RuleType.TAGGING.value,
                        'merge_policy': tags_utils.TagMergePolicy.APPEND.value,
                        'entity_type': tags_utils.TagEntityType.UDID.value,
                        'tags': [{'name': 'tag_0'}],
                    },
                ],
            ),
        ],
    )
    complete_event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.COMPLETE.value,
        ),
        timestamp=TIMESTAMP,
        event_id='uid',
        entity_id=TST_UDID,
    )
    timeout_event = Events.OrderEvent(
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.OFFER_TIMEOUT.value,
        ),
        timestamp=TIMESTAMP,
        event_id='uid',
        entity_id=TST_UDID,
    )
    driver.update_event(timeout_event)

    # rule should not apply because of event type mismatch
    patch_rules([rule])

    res = web_context.metrics_rules_config.apply(
        rule_type=RuleType.TAGGING, entity=driver, now=TIMESTAMP,
    )
    assert not res

    driver.update_event(complete_event)
    # and now we can fix it
    res = web_context.metrics_rules_config.apply(
        rule_type=RuleType.TAGGING, entity=driver, now=TIMESTAMP,
    )
    assert res == [
        {
            'entity_type': 'udid',
            'merge_policy': 'append',
            'protected': True,
            'rule_name': 'rule_name',
            'triggered_context': {'tags': []},
            'rule_config_id': None,
            'tags': [{'name': 'tag_0'}],
            'type': 'tagging',
        },
    ]
