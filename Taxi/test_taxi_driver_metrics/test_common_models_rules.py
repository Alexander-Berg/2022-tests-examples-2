# pylint: disable-all
# type: ignore
import datetime
from operator import attrgetter

import pytest

from metrics_processing.rules import common as rules_common
from metrics_processing.rules.common import utils
from metrics_processing.rules_config import handler
from metrics_processing.utils import helpers

from taxi_driver_metrics.common.models import BlockingType
from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models.rules import rule_utils

TIMESTAMP = datetime.datetime.now()
BEGINNING_TIME = datetime.timedelta(days=2).total_seconds()
FROM_TIMESTAMP = TIMESTAMP - datetime.timedelta(seconds=BEGINNING_TIME)
VALID_TIMESTAMP = TIMESTAMP - datetime.timedelta(days=1)
BLOCKING_DURATION = datetime.timedelta(days=1).total_seconds()
BLOCK_UNTIL = TIMESTAMP + datetime.timedelta(seconds=BLOCKING_DURATION)
TST_ZONE = 'tst_zone'
DEFAULT_ACTIONS_RULE_NAME = 'none'
BLOCKING_PARAMS = {
    'zone': TST_ZONE,
    'rule_name': DEFAULT_ACTIONS_RULE_NAME,
    'reason': rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
    'type': BlockingType.BY_ACTIONS,
}
TST_RULE_NAME = 'tst_rule'
TST_UDID = 'tst_udid'
TST_EVENT_DESCR1 = Events.EventTypeDescriptor(
    Events.OrderEventType.OFFER_TIMEOUT.value,
)
TST_EVENT_DESCR2 = Events.EventTypeDescriptor(
    Events.OrderEventType.COMPLETE.value,
)
TST_EVENT_DESCR3 = Events.EventTypeDescriptor(
    Events.OrderEventType.USER_CANCEL.value,
)
TST_EVENT_DESCR4 = Events.EventTypeDescriptor(
    Events.OrderEventType.REJECT_MANUAL.value,
)
TST_EID = 'tst_event_Id'


def make_test_event(descr, timestamp, event_id):
    return Events.OrderEvent(
        timestamp=timestamp,
        event_id=event_id,
        descriptor=descr,
        entity_id=TST_UDID,
    )


@pytest.mark.translations(
    taximeter_messages={
        'drivercheck.DriverMetricsFallbackTempBlockTitle': {
            'ru': 'title-ru-' + rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
            'fr': 'title-fr-' + rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
            'en': 'title-en-' + rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
        },
        'drivercheck.DriverMetricsFallbackTempBlockMessage': {
            'ru': 'message-ru-' + rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
            'fr': 'message-fr-' + rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
            'en': 'message-en-' + rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
        },
        'drivercheck.DriverMetricsTempBlockTitle': {
            'ru': 'title-ru-DriverMetricsTempBlockTitle',
            'fr': 'title-fr-DriverMetricsTempBlockTitle',
            'en': 'title-en-DriverMetricsTempBlockTitle',
        },
        'drivercheck.DriverMetricsTempBlockMessage': {
            'ru': 'message-ru-DriverMetricsTempBlockTitle',
            'fr': 'message-fr-DriverMetricsTempBlockTitle',
            'en': 'message-en-DriverMetricsTempBlockTitle',
        },
    },
)
@pytest.mark.parametrize(
    'key,fixed_key',
    [
        ('QWERTY', rule_utils.DEFAULT_TANKER_KEY_TEMPLATE),
        ('DriverMetricsTempBlock', 'DriverMetricsTempBlock'),
        (
            rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
            rule_utils.DEFAULT_TANKER_KEY_TEMPLATE,
        ),
    ],
)
async def test_check_and_fix_tanker_key(
        key, fixed_key, web_context, fake_event_provider, patch,
):
    assert (
        helpers.check_and_fix_tanker_key(key, web_context.translations)
        == fixed_key
    )


ACTIVITY_TRIP = {'actions': [], 'events': [], 'name': 'ActivityTrip'}

ACTIVITY_TRIP_OBJ = rules_common.Rule(
    actions=[],
    events=[],
    name='ActivityTrip',
    type='activity',
    additional_params={
        'events_period_sec': 3600,
        'tags': None,
        'expr': None,
        'events_to_trigger_cnt': 1,
    },
)

ACTIVITY_TRIPPER = {'actions': [], 'events': [], 'name': 'ActivityTripper'}

ACTIVITY_TRIPPER_OBJ = rules_common.Rule(
    actions=[],
    events=[],
    name='ActivityTripper',
    type='activity',
    additional_params={
        'events_period_sec': 3600,
        'tags': None,
        'expr': None,
        'events_to_trigger_cnt': 1,
    },
)

ACTIVITY_TRIP_MOSCOW = {
    'actions': [],
    'events': [],
    'name': 'ActivityTripMoscow',
}

ACTIVITY_TRIP_MOSCOW_OBJ = rules_common.Rule(
    actions=[],
    events=[],
    name='ActivityTripMoscow',
    type='activity',
    additional_params={
        'events_period_sec': 3600,
        'tags': None,
        'expr': None,
        'events_to_trigger_cnt': 1,
    },
    zone='moscow',
)

ACTIVITY_TRIP_MOSCOW_OTHER = {
    'actions': [],
    'events': [],
    'name': 'ActivityTrip',
}

ACTIVITY_TRIP_MOSCOW_OTHER_OBJ = rules_common.Rule(
    actions=[],
    events=[],
    name='ActivityTrip',
    type='activity',
    additional_params={
        'events_period_sec': 3600,
        'tags': None,
        'expr': None,
        'events_to_trigger_cnt': 1,
    },
    zone='moscow',
)

ACTIVITY_TRIP_SPB = {'actions': [], 'events': [], 'name': 'ActivityTripSpb'}

ACTIVITY_TRIP_SPB_OBJ = rules_common.Rule(
    actions=[],
    events=[],
    name='ActivityTripSpb',
    type='activity',
    additional_params={
        'events_period_sec': 3600,
        'tags': None,
        'expr': None,
        'events_to_trigger_cnt': 1,
    },
    zone='spb',
)

ACTIVITY_TRIP_SUB_MOSCOW = {
    'actions': [],
    'events': [],
    'name': 'ActivityTripSubMoscow',
}

ACTIVITY_TRIP_SUB_MOSCOW_OBJ = rules_common.Rule(
    actions=[],
    events=[],
    name='ActivityTripSubMoscow',
    type='activity',
    additional_params={
        'events_period_sec': 3600,
        'tags': None,
        'expr': None,
        'events_to_trigger_cnt': 1,
    },
    zone='sub_moscow',
)


@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [ACTIVITY_TRIP],
        'node:root': [ACTIVITY_TRIPPER],
        'node:moscow': [ACTIVITY_TRIP_MOSCOW, ACTIVITY_TRIP_MOSCOW_OTHER],
        'spb': [ACTIVITY_TRIP_SPB],
        'sub_moscow': [ACTIVITY_TRIP_SUB_MOSCOW],
    },
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'parent_name': 'root',
            'node_type': 'node',
            'tariff_zones': ['sub_moscow'],
        },
    ],
)
@pytest.mark.parametrize(
    'request_zone, result',
    [
        ('spb', [ACTIVITY_TRIP_OBJ, ACTIVITY_TRIP_SPB_OBJ]),
        ('ashenvale', [ACTIVITY_TRIP_OBJ]),
        (
            'sub_moscow',
            [
                ACTIVITY_TRIP_MOSCOW_OTHER_OBJ,
                ACTIVITY_TRIPPER_OBJ,
                ACTIVITY_TRIP_MOSCOW_OBJ,
                ACTIVITY_TRIP_SUB_MOSCOW_OBJ,
            ],
        ),
        ('moscow', [ACTIVITY_TRIP_OBJ, ACTIVITY_TRIPPER_OBJ]),
    ],
)
async def test_get_zone_chain_config(web_context, request_zone, result):
    zone_chain = list(utils.get_zone_chain(web_context, request_zone))

    for rule in result:
        rule.zone = request_zone

    rules = web_context.metrics_rules_config.rules_by_zone(
        request_zone,
        rule_type=rules_common.RuleType.ACTIVITY,
        config_name='DRIVER_METRICS_NEW_ACTIVITY_RULES',
        zone_chain=zone_chain,
    )

    def get_names(rls):
        return list(map(attrgetter('name'), rls))

    assert get_names(rules) == get_names(result)


@pytest.mark.filldb()
async def test_fail_while_parsing_rules(stq3_context, patch):
    @patch('metrics_processing.rules_config.fetch.format_rules')
    def format_rules(*args, **kwags):
        raise KeyError

    client = handler._RulesConfigLocalClient(stq3_context, 'driver-metrics')
    with pytest.raises(KeyError):
        res = await client.get_ids()
        assert res
