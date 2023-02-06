import datetime

from metrics_processing.rules.common import RuleType
from metrics_processing.utils import action_journal
from metrics_processing.utils.builder import make_action_object

from taxi_driver_metrics.common.models import action as action_module
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.models import Events


SIMPLE_RULE_NAME = 'simple_rule_name'
TIMESTAMP = datetime.datetime.now().replace(microsecond=0)
ACTIONS = [
    {
        'type': RuleType.TAGGING.value,
        'rule_name': 'tagging_name',
        'tags': [],
        'action_result': ['tag'],
        'rule_config_id': '123',
    },
    {
        'type': RuleType.ACTIVITY.value,
        'rule_name': 'activity_name',
        'action_result': 51,
        'rule_config_id': '123',
    },
    {
        'type': RuleType.BLOCKING.value,
        'rule_name': 'blocking_name',
        'tanker_key_template': 'asd',
        'blocking_duration_sec': 12,
        'action_result': True,
        'rule_config_id': '123',
    },
]

EXPECTED = {
    'entity_id': 'UDID_1',
    'entity_type': 'driver',
    'event_id': 'tst12',
    'event_name': 'offer_timeout',
    'event_type': 'order',
    'event_zone': 'bangladesh',
    'context': {
        'rider': {'tags': ['tag']},
        'driver': {
            'tags': [
                'good_driver',
                'lucky',
                'tags::good_driver',
                'tags::lucky',
            ],
            'activity': 93,
        },
        'event': {
            'extra_data': {
                'activity_value': 0,
                'descriptor': {'tags': None, 'type': 'offer_timeout'},
                'dispatch_id': None,
                'distance_to_a': 0,
                'driver_id': None,
                'dtags': None,
                'rtags': ['tag'],
                'sp': None,
                'sp_alpha': None,
                'tariff_class': None,
                'time_to_a': 0,
                'replace_activity_with_priority': False,
                'calculate_priority': False,
            },
            'tags': [],
        },
    },
    'extra_data': {},
    'trace_id': '',
    'link': '',
}

RULES = [
    {
        'action_result': ['tag'],
        'rule_name': 'tagging_name',
        'rule_type': 'tagging',
        'triggered_context': {},
        'rule_config_id': '123',
    },
    {
        'action_result': 51,
        'rule_name': 'activity_name',
        'rule_type': 'activity',
        'triggered_context': {},
        'rule_config_id': '123',
    },
    {
        'action_result': True,
        'rule_name': 'blocking_name',
        'rule_type': 'blocking',
        'triggered_context': {},
        'rule_config_id': '123',
    },
]


def test_build_log_data(web_context):
    journal = action_journal.ActionJournal()
    entity = DriverInfo(
        udid='UDID_1',
        activity=93,
        tags={'good_driver', 'tags::good_driver', 'lucky', 'tags::lucky'},
    )

    event = Events.OrderEvent(
        timestamp=TIMESTAMP,
        descriptor=Events.EventTypeDescriptor(
            Events.OrderEventType.OFFER_TIMEOUT.value,
        ),
        event_id='tst12',
        zone='bangladesh',
        entity_id='UDID_1',
        rider_tags=['tag'],
    )

    for action in ACTIONS:
        action_obj = make_action_object(
            app=web_context,
            event=event,
            entity=entity,
            action=action,
            actions=[
                action_module.TaggingAction,
                action_module.BaseBlockingAction,
                action_module.ActivityBlockingAction,
                action_module.ActivityChangeAction,
            ],
        )

        journal.update_action(
            action=action_obj, result=action['action_result'],
        )

    log_data = journal.fetch_log_data(entity=entity, event=event)

    assert log_data

    for i, log in enumerate(log_data):
        log.update({'trace_id': '', 'link': ''})
        log['context']['driver']['tags'].sort()
        EXPECTED['rules'] = RULES[i]
        assert log == EXPECTED
