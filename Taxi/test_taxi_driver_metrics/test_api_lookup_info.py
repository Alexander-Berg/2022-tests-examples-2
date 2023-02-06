import asyncio

import pytest


HANDLER_PATH = 'v2/lookup_info/'
DRIVER_UDID = '5b05621ee6c22ea2654849c9'
TST_ZONE = 'burgund'
TST_DESTINATION = 'moon'
TST_ORDER_ID = 'dlsjfslkfj'
TST_ALIAS_ID = 'tstalias'
WRONG_APP_VERSION = '10.0.0'

PARK_FAIL = {'activity_rule_info': {'rule_name': 'ParkFail'}}
COMPLETE = {'activity_rule_info': {'rule_name': 'ActivityTrip'}}
REJECT = {'activity_rule_info': {'rule_name': 'ActivityReject'}}
TIMEOUT = {'activity_rule_info': {'rule_name': 'ActivityOT'}}

RULE_INFO = {
    'order_auto_reorder': PARK_FAIL,
    'order_auto_reorder_long_waiting': PARK_FAIL,
    'order_complete': COMPLETE,
    'order_park_cancel': PARK_FAIL,
    'order_park_cancel_long_waiting': PARK_FAIL,
    'order_park_fail': PARK_FAIL,
    'order_park_fail_long_waiting': PARK_FAIL,
    'order_reject_auto_cancel': REJECT,
    'order_reject_auto_cancel_chained_order': REJECT,
    'order_reject_manual': REJECT,
    'order_reject_manual_chained_order': REJECT,
    'order_reject_missing_tariff': REJECT,
    'order_reject_missing_tariff_chained_order': REJECT,
    'order_offer_timeout_chained_order': TIMEOUT,
    'order_offer_timeout': TIMEOUT,
    'order_seen_timeout': TIMEOUT,
}


class Const:
    TARIFF_CLASS_EXPRESS = 'express'
    TARIFF_CLASS_ECONOM = 'econom'
    TARIFF_CLASS_BUSINESS = 'business'
    TARIFF_CLASS_COMFORTPLUS = 'comfortplus'
    TARIFF_CLASS_VIP = 'vip'
    TARIFF_CLASS_MINIVAN = 'minivan'
    TARIFF_CLASS_UNIVERSAL = 'universal'
    TARIFF_CLASS_POOL = 'pool'


async def find_prediction(collection, ident):
    prediction = None
    while not prediction:
        await asyncio.sleep(0.05)
        prediction = await collection.find_one({'dispatch_id': ident})
    return prediction


@pytest.mark.parametrize(
    'tst_request, tst_response, tst_prediction, response_code',
    [
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                    'properties': 121,
                },
            },
            {},
            {},
            400,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': '5b05621ee6c22ea2654849c0',
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -2,
                        'c': 1,
                        'm': -2,
                        'n': -6,
                        'o': -6,
                        'r': -6,
                        's': -1,
                        't': -2,
                        'w': -1,
                    },
                    'blocking': {'duration_sec': 3600, 'threshold': 30},
                },
                'distance_type': 'short',
                'event_tags': ['dispatch_short'],
            },
            {
                'order_auto_reorder': {'activity': -2},
                'order_auto_reorder_long_waiting': {'activity': -1},
                'order_complete': {'activity': 1},
                'order_park_cancel': {'activity': -2},
                'order_park_cancel_long_waiting': {'activity': -1},
                'order_park_fail': {'activity': -2},
                'order_park_fail_long_waiting': {'activity': -1},
                'order_reject_auto_cancel': {'activity': -6},
                'order_reject_auto_cancel_chained_order': {'activity': 0},
                'order_reject_manual': {'activity': -6},
                'order_reject_manual_chained_order': {'activity': 0},
                'order_reject_missing_tariff': {'activity': -6},
                'order_reject_missing_tariff_chained_order': {'activity': 0},
                'order_offer_timeout_chained_order': {'activity': -1},
                'order_offer_timeout': {'activity': -2},
                'order_seen_timeout': {'activity': -2},
            },
            200,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                    'properties': [],
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -2,
                        'c': 1,
                        'n': -6,
                        'o': -6,
                        'r': -6,
                        'w': -1,
                        'm': -2,
                        's': -1,
                        't': -2,
                    },
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'short',
                'event_tags': ['dispatch_short'],
            },
            {
                'order_auto_reorder': {'activity': -2},
                'order_auto_reorder_long_waiting': {'activity': -1},
                'order_complete': {'activity': 1},
                'order_park_cancel': {'activity': -2},
                'order_park_cancel_long_waiting': {'activity': -1},
                'order_park_fail': {'activity': -2},
                'order_park_fail_long_waiting': {'activity': -1},
                'order_reject_auto_cancel': {'activity': -6},
                'order_reject_auto_cancel_chained_order': {'activity': 0},
                'order_reject_manual': {'activity': -6},
                'order_reject_manual_chained_order': {'activity': 0},
                'order_reject_missing_tariff': {'activity': -6},
                'order_reject_missing_tariff_chained_order': {'activity': 0},
                'order_offer_timeout_chained_order': {'activity': -1},
                'order_offer_timeout': {'activity': -2},
                'order_seen_timeout': {'activity': -2},
            },
            200,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222000,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'econom',
                    'properties': ['explicit_antisurge'],
                    'route_distance': 100,
                    'route_time': 100,
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {'c': 2, 'm': -2, 's': -1, 't': -2},
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'long',
                'event_tags': ['explicit_antisurge', 'dispatch_long'],
            },
            {
                'order_complete': {'activity': 2},
                'order_auto_reorder': {'activity': 0},
                'order_auto_reorder_long_waiting': {'activity': 0},
                'order_park_cancel': {'activity': 0},
                'order_park_cancel_long_waiting': {'activity': 0},
                'order_park_fail': {'activity': 0},
                'order_park_fail_long_waiting': {'activity': 0},
                'order_reject_auto_cancel': {'activity': 0},
                'order_reject_auto_cancel_chained_order': {'activity': 0},
                'order_reject_manual': {'activity': 0},
                'order_reject_manual_chained_order': {'activity': 0},
                'order_reject_missing_tariff': {'activity': 0},
                'order_reject_missing_tariff_chained_order': {'activity': 0},
                'order_offer_timeout_chained_order': {'activity': -1},
                'order_offer_timeout': {'activity': -2},
                'order_seen_timeout': {'activity': -2},
            },
            200,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                    'tags': ['boring_tag'],
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -2,
                        'w': -1,
                        'c': 1,
                        'n': -6,
                        'o': -6,
                        'r': -6,
                        'm': -2,
                        's': -1,
                        't': -2,
                    },
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'short',
                'event_tags': ['dispatch_short'],
            },
            {
                'order_auto_reorder': {'activity': -2},
                'order_auto_reorder_long_waiting': {'activity': -1},
                'order_complete': {'activity': 1},
                'order_park_cancel': {'activity': -2},
                'order_park_cancel_long_waiting': {'activity': -1},
                'order_park_fail': {'activity': -2},
                'order_park_fail_long_waiting': {'activity': -1},
                'order_reject_auto_cancel': {'activity': -6},
                'order_reject_auto_cancel_chained_order': {'activity': 0},
                'order_reject_manual': {'activity': -6},
                'order_reject_manual_chained_order': {'activity': 0},
                'order_reject_missing_tariff': {'activity': -6},
                'order_reject_missing_tariff_chained_order': {'activity': 0},
                'order_offer_timeout_chained_order': {'activity': -1},
                'order_offer_timeout': {'activity': -2},
                'order_seen_timeout': {'activity': -2},
            },
            200,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                    'adverse_destination': TST_DESTINATION,
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -2,
                        'w': -1,
                        'c': 1,
                        'n': -4,
                        'o': -4,
                        'r': -4,
                        'm': -2,
                        's': -1,
                        't': -2,
                    },
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'short',
                'event_tags': ['adverse_zone', 'dispatch_short'],
            },
            {
                'order_auto_reorder': {'activity': -2},
                'order_auto_reorder_long_waiting': {'activity': -1},
                'order_complete': {'activity': 1},
                'order_park_cancel': {'activity': -2},
                'order_park_cancel_long_waiting': {'activity': -1},
                'order_park_fail': {'activity': -2},
                'order_park_fail_long_waiting': {'activity': -1},
                'order_reject_auto_cancel': {'activity': -4},
                'order_reject_auto_cancel_chained_order': {'activity': 0},
                'order_reject_manual': {'activity': -4},
                'order_reject_manual_chained_order': {'activity': 0},
                'order_reject_missing_tariff': {'activity': -4},
                'order_reject_missing_tariff_chained_order': {'activity': 0},
                'order_offer_timeout_chained_order': {'activity': -1},
                'order_offer_timeout': {'activity': -2},
                'order_seen_timeout': {'activity': -2},
            },
            200,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                    'time_to_a': 500,
                    'tags': ['selfemployed', 'bad'],
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -2,
                        'c': 12,
                        'w': -1,
                        'm': -2,
                        's': -1,
                        't': -2,
                    },
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'long',
                'event_tags': ['dispatch_long'],
            },
            {
                'order_auto_reorder': {'activity': -2},
                'order_auto_reorder_long_waiting': {'activity': -1},
                'order_complete': {'activity': 12},
                'order_park_cancel': {'activity': -2},
                'order_park_cancel_long_waiting': {'activity': -1},
                'order_park_fail': {'activity': -2},
                'order_reject_auto_cancel_chained_order': {'activity': 0},
                'order_reject_auto_cancel': {'activity': 0},
                'order_reject_manual': {'activity': 0},
                'order_reject_manual_chained_order': {'activity': 0},
                'order_reject_missing_tariff': {'activity': 0},
                'order_reject_missing_tariff_chained_order': {'activity': 0},
                'order_park_fail_long_waiting': {'activity': -1},
                'order_offer_timeout_chained_order': {'activity': -1},
                'order_offer_timeout': {'activity': -2},
                'order_seen_timeout': {'activity': -2},
            },
            200,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 12}],
                        'tags': '\'tags::selfemployed\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 2}],
                        'tags': '\'event::dispatch_long\'',
                    },
                    {'action': [{'type': 'activity', 'value': 1}]},
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': (
                            '\'event::explicit_antisurge\' '
                            'OR \'event::chained_order\' '
                            'OR \'event::dispatch_long\''
                        ),
                    },
                    {
                        'action': [{'type': 'activity', 'value': -4}],
                        'tags': (
                            '\'event::dispatch_medium\' '
                            'OR \'event::adverse_zone\' '
                        ),
                    },
                    {
                        'action': [{'type': 'activity', 'value': -6}],
                        'tags': '\'event::dispatch_short\'',
                    },
                ],
                'events': [
                    {'name': 'reject_manual', 'topic': 'order'},
                    {'name': 'reject_auto_cancel', 'topic': 'order'},
                    {'name': 'reject_missing_tariff', 'topic': 'order'},
                ],
                'name': 'ActivityReject',
            },
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': '\'event::explicit_antisurge\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': -1}],
                        'tags': '\'event::long_waiting\'',
                    },
                    {'action': [{'type': 'activity', 'value': -2}]},
                ],
                'events': [
                    {'name': 'park_fail', 'topic': 'order'},
                    {'name': 'park_cancel', 'topic': 'order'},
                    {'name': 'auto_reorder', 'topic': 'order'},
                ],
                'name': 'ParkFail',
            },
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': -1}],
                        'tags': '\'event::chained_order\'',
                    },
                    {'action': [{'type': 'activity', 'value': -2}]},
                ],
                'events': [
                    {'name': 'offer_timeout', 'topic': 'order'},
                    {'name': 'seen_timeout', 'topic': 'order'},
                ],
                'name': 'ActivityOT',
            },
        ],
    },
    ADVERSE_ZONES={
        TST_ZONE: {
            TST_DESTINATION: {'show_destination': True, 'skip_fields': ''},
        },
    },
    DRIVER_METRICS_PREDICTION_SETTINGS={
        'fallback': {
            'events': {'order_complete': {'activity': 0}},
            'letter_events': {'c': {'activity': 0}},
        },
        'insert_chunk_size': 1000,
        'insert_timeout': 20,
        'tags': {
            'order': {
                'auto_reorder': ['long_waiting'],
                'offer_timeout': ['chained_order'],
                'reject_manual': ['chained_order'],
                'reject_auto_cancel': ['chained_order'],
                'reject_missing_tariff': ['chained_order'],
                'park_cancel': ['long_waiting'],
                'park_fail': ['long_waiting'],
            },
        },
    },
    DRIVER_METRICS_ACTIVITY_FROM_DMS_IN_LOOKUP={
        'enabled': True,
        'timeout_ms': 1000,
    },
)
@pytest.mark.filldb()
async def test_base(
        web_context,
        web_app_client,
        mockserver,
        tst_request,
        tst_response,
        tst_prediction,
        response_code,
        mongo,
        taxi_config,
):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    async def fetch_activity_value(*args, **kwargs):
        return {'items': [{'unique_driver_id': 'asd', 'value': 93}]}

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == response_code
    if response_code > 200:
        return

    content = await response.json()
    ident = content.pop('ident')
    assert content == tst_response

    assert fetch_activity_value.times_called

    prediction = await find_prediction(mongo.driver_metrics_predictions, ident)

    assert prediction

    for event_type in prediction['prediction']:
        #  update prediction with common rule info
        tst_prediction[event_type].update(RULE_INFO[event_type])
        #  get triggered context
        triggered_context = prediction['prediction'][event_type][
            'activity_rule_info'
        ].pop('triggered_context', None)
        #  check only for long_waiting, because it is the simplest
        #  no need to check correctness of triggered context
        if 'long_waiting' in event_type:
            assert triggered_context
        assert (
            prediction['prediction'][event_type] == tst_prediction[event_type]
        )
    assert prediction['order_id'] == TST_ORDER_ID
    assert prediction['udid'] == tst_request['candidate']['unique_driver_id']


@pytest.mark.parametrize(
    'tst_request, tst_response, response_code, comment_times_called',
    [
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                    'time_to_a': 500,
                    'tags': ['selfemployed', 'bad'],
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                    'comment': 'Some kind comment',
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -4,
                        'c': 2,
                        'n': -4,
                        'o': -4,
                        'p': -4,
                        'r': -4,
                        'w': -4,
                    },
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'long',
                'event_tags': ['has_order_comment', 'dispatch_long'],
            },
            200,
            1,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                    'time_to_a': 500,
                    'tags': ['selfemployed', 'bad'],
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'minivan',
                    'comment': 'Some offensive comment',
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {'c': 2},
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'long',
                'event_tags': [
                    'bad_order_comment',
                    'has_order_comment',
                    'dispatch_long',
                ],
            },
            200,
            1,
        ),
        (
            {
                'candidate': {
                    'unique_driver_id': DRIVER_UDID,
                    'distance_to_a': 222,
                    'application_version': WRONG_APP_VERSION,
                    'time_to_a': 500,
                    'tags': ['selfemployed', 'bad'],
                },
                'order': {
                    'zone': TST_ZONE,
                    'order_id': TST_ORDER_ID,
                    'tariff_class': 'vip',
                    'comment': 'Some offensive comment',
                },
            },
            {
                'prediction': {
                    'type': 'activity',
                    'value': 93,
                    'value_changes': {
                        'a': -4,
                        'c': 2,
                        'n': -4,
                        'o': -4,
                        'p': -4,
                        'r': -4,
                        'w': -4,
                    },
                    'blocking': {'duration_sec': 172800, 'threshold': 30},
                },
                'distance_type': 'long',
                'event_tags': ['has_order_comment', 'dispatch_long'],
            },
            200,
            0,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'test_comment': {'from': 0, 'to': 100, 'salt': 'asddsa'},
    },
    DRIVER_METRICS_COMMENT_ANALYZING_TIMEOUT_MS=100000,
    DRIVER_METRICS_STOP_WORDS_FOR_COMMENTS={
        'similarity_threshold': 0.7,
        'stop_words_list': [{'word': 'offensive'}],
    },
    DRIVER_METRICS_PROPERTIES_TO_EXTRACT=['bad_order_comment'],
    DRIVER_METRICS_COMMENTS_FILTER={
        'filters': {'tariff': {'filter_out': [Const.TARIFF_CLASS_VIP]}},
    },
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 2}],
                        'tags': '\'event::has_order_comment\'',
                    },
                    {'action': [{'type': 'activity', 'value': 1}]},
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 0}],
                        'tags': (
                            '\'event::explicit_antisurge\''
                            ' OR \'event::bad_order_comment\''
                        ),
                    },
                    {'action': [{'type': 'activity', 'value': -4}]},
                ],
                'events': [
                    {'name': 'reject_manual', 'topic': 'order'},
                    {'name': 'reject_auto_cancel', 'topic': 'order'},
                    {'name': 'reject_missing_tariff', 'topic': 'order'},
                    {'name': 'auto_reorder', 'topic': 'order'},
                ],
                'name': 'ActivityReject',
            },
        ],
    },
)
async def test_comment_analyzing(
        web_app_client,
        web_context,
        mockserver,
        tst_request,
        tst_response,
        response_code,
        comment_times_called,
):
    @mockserver.json_handler('/driver-metrics-storage/v1/comment/properties/')
    async def comment_properties_by_dms(*args, **kwargs):
        data = args[0].json
        comment = data['comment']
        # pylint: disable=protected-access
        res = ['bad_order_comment'] if 'offensive' in comment else []

        return {'comment_properties': res}

    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    async def _fetch_activity_value(*_a, **_kw):
        return {'items': [{'unique_driver_id': DRIVER_UDID, 'value': 93}]}

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == response_code
    if response_code > 200:
        return

    content = await response.json()
    assert content.pop('ident')
    assert content == tst_response
    assert comment_properties_by_dms.times_called == comment_times_called


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'distance_to_a, time_to_a, tags, expected_dispatch_type',
    [
        (0, 0, [], 'short'),
        (0, 120, [], 'short'),
        (0, 120, ['boring_tag'], 'long'),
        (11101, 9, ['boring_tag'], 'medium'),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 12}],
                        'tags': '\'event::dispatch_long\'',
                    },
                    {'action': [{'type': 'activity', 'value': 1}]},
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
        ],
    },
    DRIVER_METRICS_DISPATCH_LENGTH_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'type': 'dispatch_length_thresholds',
                                'time': [2, 10],
                            },
                        ],
                        'tags': '\'tags::boring_tag\'',
                    },
                    {
                        'action': [
                            {
                                'type': 'dispatch_length_thresholds',
                                'time': [20, 100],
                                'distance': [1000, 2000],
                                'aggregation_type': 'min',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'SimpleDispatch',
            },
        ],
    },
)
async def test_new_dispatch(
        web_app_client,
        mockserver,
        response_mock,
        time_to_a,
        distance_to_a,
        tags,
        expected_dispatch_type,
):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _fetch_activity_value(*args, **kwargs):
        return {'items': [{'unique_driver_id': DRIVER_UDID, 'value': 10}]}

    request = {
        'candidate': {
            'unique_driver_id': DRIVER_UDID,
            'distance_to_a': distance_to_a,
            'application_version': WRONG_APP_VERSION,
            'time_to_a': time_to_a,
            'tags': tags,
        },
        'order': {
            'zone': TST_ZONE,
            'order_id': TST_ORDER_ID,
            'tariff_class': Const.TARIFF_CLASS_MINIVAN,
        },
    }

    response = await web_app_client.post(HANDLER_PATH, json=request)

    assert response.status == 200

    content = await response.json()
    assert content.pop('ident')

    assert content == {
        'distance_type': expected_dispatch_type,
        'prediction': {
            'type': 'activity',
            'blocking': {'duration_sec': 172800, 'threshold': 30},
            'value_changes': {
                'c': 12 if expected_dispatch_type == 'long' else 1,
            },
            'value': 10,
        },
        'event_tags': [f'dispatch_{expected_dispatch_type}'],
    }


@pytest.mark.filldb()
@pytest.mark.config(
    DRIVER_METRICS_ACTIVITY_FROM_DMS_IN_LOOKUP={
        'enabled': True,
        'timeout_ms': 1000,
    },
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 12}],
                        'tags': '\'tags::boring_tag\'',
                    },
                    {'action': [{'type': 'activity', 'value': 1}]},
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
        ],
    },
)
async def test_tags_in_lookup_info(web_app_client, mockserver, response_mock):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _fetch_activity_value(*args, **kwargs):
        return {'items': [{'unique_driver_id': DRIVER_UDID, 'value': 10}]}

    request = {
        'candidate': {
            'unique_driver_id': DRIVER_UDID,
            'distance_to_a': 222,
            'application_version': WRONG_APP_VERSION,
            'tags': ['boring_tag'],
        },
        'order': {
            'zone': TST_ZONE,
            'order_id': TST_ORDER_ID,
            'tariff_class': Const.TARIFF_CLASS_MINIVAN,
        },
    }

    response = await web_app_client.post(HANDLER_PATH, json=request)

    assert response.status == 200

    content = await response.json()
    assert content.pop('ident')

    assert content == {
        'distance_type': 'short',
        'prediction': {
            'type': 'activity',
            'blocking': {'duration_sec': 172800, 'threshold': 30},
            'value_changes': {'c': 12},
            'value': 10,
        },
        'event_tags': ['dispatch_short'],
    }


@pytest.mark.filldb()
@pytest.mark.config(
    DRIVER_METRICS_ACTIVITY_FROM_DMS_IN_LOOKUP={
        'enabled': True,
        'timeout_ms': 1000,
    },
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 12}],
                        'tags': '\'tags::boring_tag\'',
                    },
                    {'action': [{'type': 'activity', 'value': 1}]},
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
        ],
    },
)
async def test_activity_fallback(web_app_client, mockserver, response_mock):
    @mockserver.json_handler('/driver-metrics-storage/v2/activity_values/list')
    def _fetch_activity_value(*args, **kwargs):
        return mockserver.make_response(status=500)

    request = {
        'candidate': {
            'unique_driver_id': DRIVER_UDID,
            'distance_to_a': 222,
            'application_version': WRONG_APP_VERSION,
            'tags': ['boring_tag'],
        },
        'order': {
            'zone': TST_ZONE,
            'order_id': TST_ORDER_ID,
            'tariff_class': Const.TARIFF_CLASS_MINIVAN,
        },
    }

    response = await web_app_client.post(HANDLER_PATH, json=request)

    assert response.status == 200

    content = await response.json()
    assert content.pop('ident')

    assert content == {
        'distance_type': 'short',
        'prediction': {
            'type': 'activity',
            'blocking': {'duration_sec': 172800, 'threshold': 30},
            'value_changes': {'c': 12},
            'value': 100,
        },
        'event_tags': ['dispatch_short'],
    }
