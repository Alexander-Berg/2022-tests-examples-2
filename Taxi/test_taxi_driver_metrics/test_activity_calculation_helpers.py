import typing as tp

import pytest

from taxi.util import dates

from taxi_driver_metrics.common.activity_calculation import dispatch_ranges
from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.utils import event_helpers
from taxi_driver_metrics.models import lookup_info


ZONE = 'stranglethorn vale'
DST = 'darkshire'
UDID = '5b05621ee6c22ea2654849c9'


class Const:
    TARIFF_CLASS_EXPRESS = 'express'
    TARIFF_CLASS_ECONOM = 'econom'
    TARIFF_CLASS_BUSINESS = 'business'
    TARIFF_CLASS_COMFORTPLUS = 'comfortplus'
    TARIFF_CLASS_VIP = 'vip'
    TARIFF_CLASS_MINIVAN = 'minivan'
    TARIFF_CLASS_UNIVERSAL = 'universal'
    TARIFF_CLASS_POOL = 'pool'


def _compare_activity_change_values(
        old: tp.Dict[str, int], new: tp.Dict[str, int],
) -> bool:
    """ Return True only if all values are equal (None is zero) """
    for code in new.keys() | old.keys():
        old_change = old.get(code) or 0
        new_change = new.get(code) or 0
        if old_change != new_change:
            return False
    return True


@pytest.mark.parametrize(
    'old, new, res',
    [
        ({'c': 6}, {'a': 4, 'c': '6'}, False),  # 'a' is 0 for old
        ({'f': 4}, {'f': '4'}, False),  # wrong type
        ({'b': 6, 'd': 2}, {'b': 6}, False),  # 'd' is 0 for new
        ({'b': 6}, {'b': 0}, False),
        ({'b': 1, 'q': 0}, {'a': 0, 'b': 1}, True),
    ],
)
def test_compare_activity_change_values(old, new, res):
    assert _compare_activity_change_values(old, new) == res


@pytest.mark.filldb()
@pytest.mark.parametrize('antisurge', [True, False])
@pytest.mark.parametrize('adverse_zone', [True, False])
@pytest.mark.parametrize('long_trip', [True, False])
@pytest.mark.parametrize('distance_to_a, expected', [(200, 3), (999999, 5)])
@pytest.mark.parametrize('tariff', ['econom', 'comfortplus', 'vip'])
@pytest.mark.parametrize('duration', [2, 7, 30])
@pytest.mark.config(
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={'__default__': ['activity']},
    DRIVER_METRICS_DISPATCH_LENGTH_RULES={
        '__default__': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'distance': [1000, 2000],
                                'time': [180, 360],
                                'type': 'dispatch_length_thresholds',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'CommonDispatchRule',
            },
        ],
    },
)
@pytest.mark.rules_config(
    ACTIVITY={
        'default': [
            {
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 8}],
                        'tags': '\'event::adverse_zone\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 7}],
                        'tags': '\'event::explicit_antisurge\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 6}],
                        'tags': '\'event::long_trip\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 5}],
                        'tags': '\'event::dispatch_long\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 4}],
                        'tags': '\'event::dispatch_medium\'',
                    },
                    {
                        'action': [{'type': 'activity', 'value': 3}],
                        'tags': '\'event::dispatch_short\'',
                    },
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'name': 'ActivityTrip',
            },
        ],
    },
)
async def test_new_activity_calculation(
        antisurge: bool,
        adverse_zone: bool,
        long_trip: bool,
        distance_to_a: int,
        expected: int,
        tariff: str,
        duration: int,
        stq3_context,
        patch,
        dms_mockserver,
):
    event_tags = []

    if long_trip:
        expected = 6
        event_tags.append('long_trip')

    if antisurge:
        expected = 7
        event_tags.append('explicit_antisurge')

    if adverse_zone:
        expected = 8
        event_tags.append('adverse_zone')

    driver = await DriverInfo.make(
        stq3_context,
        UDID,
        fetch_blocking_history=False,
        fetch_events_history=False,
        fetch_tags=False,
        fetch_blocking_info=False,
        dms_timeout=100,
    )
    distance_type = await dispatch_ranges.get_dispatch_type_new(
        context=stq3_context,
        driver=driver,
        event=event_helpers.make_fake_order_event(
            udid=UDID,
            order_id='order_id',
            zone=ZONE,
            tariff_class='vip',
            tags=event_tags,
            rider_tags=[],
            event_name='complete',
            timestamp=dates.utcnow(),
            time_to_a=duration,
            distance_to_a=distance_to_a,
        ),
    )
    event_tags.append('dispatch_' + str(distance_type))
    fake_events = lookup_info.make_fake_order_events(
        udid=UDID,
        order_id='order_id',
        zone=ZONE,
        tariff_class='vip',
        rider_tags=[],
        tags=event_tags,
    )

    res = await lookup_info.get_new_activity_prediction(
        stq3_context,
        driver=driver,
        events=fake_events,
        dispatch_id='dispatch_id',
    )
    assert _compare_activity_change_values({'c': expected}, res.activity)


@pytest.mark.config(
    DRIVER_METRICS_TAG_FOR_EXPERIMENT={
        'tst_tag': {'from': 0, 'to': 100, 'salt': '&%^^#@%'},
    },
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'name': 'rule_name',
                'events': [{'name': 'complete'}],
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 10}],
                        'tags': '\'experiment::tst_tag\'',
                    },
                    {'action': [{'type': 'activity', 'value': 0}]},
                ],
            },
            {
                'name': 'other_rule_name',
                'events': [{'name': 'reject_missing_tariff'}],
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 5}],
                        'tags': '\'tags::apple\'',
                    },
                    {'action': [{'type': 'activity', 'value': 0}]},
                ],
            },
        ],
    },
)
async def test_driver_tags(stq3_context, dms_mockserver):
    fake_events = lookup_info.make_fake_order_events(
        udid=UDID,
        order_id='order_id',
        zone=ZONE,
        tariff_class='vip',
        rider_tags=[],
        tags=[],
    )
    driver = await DriverInfo.make(
        stq3_context,
        UDID,
        fetch_blocking_history=False,
        fetch_events_history=False,
        fetch_tags=False,
        fetch_blocking_info=False,
        dms_timeout=100,
    )
    driver.tags.add('tags::apple')
    res = await lookup_info.get_new_activity_prediction(
        stq3_context,
        driver=driver,
        events=fake_events,
        dispatch_id='dispatch_id',
    )
    res = res.activity
    assert res['c'] == 10
    assert res['r'] == 5


@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'name': 'new_rule_name',
                'events': [{'name': 'complete'}],
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 7}],
                        'tags': '\'rider::orange\'',
                    },
                    {'action': [{'type': 'activity', 'value': 0}]},
                ],
            },
        ],
    },
)
async def test_rider_tags(stq3_context, dms_mockserver):
    fake_events = lookup_info.make_fake_order_events(
        udid=UDID,
        order_id='order_id',
        zone=ZONE,
        tariff_class='vip',
        rider_tags=['orange'],
        tags=[],
    )
    driver = await DriverInfo.make(
        stq3_context,
        UDID,
        fetch_blocking_history=False,
        fetch_events_history=False,
        fetch_tags=False,
        fetch_blocking_info=False,
        dms_timeout=100,
    )

    res = await lookup_info.get_new_activity_prediction(
        stq3_context,
        driver=driver,
        events=fake_events,
        dispatch_id='dispatch_id',
    )
    res = res.activity
    assert res['c'] == 7


@pytest.mark.parametrize(
    'time_to_a, distance_to_a, expected_activity',
    [(10, 210, 7), (60, 220, 0), (10, 200, 0)],
)
@pytest.mark.config(
    DRIVER_METRICS_NEW_ACTIVITY_RULES={
        '__default__': [
            {
                'name': 'new_rule_name',
                'events': [{'name': 'complete'}],
                'actions': [
                    {
                        'action': [{'type': 'activity', 'value': 7}],
                        'expr': (
                            'event.extra_data_json[\'distance_to_a\'] > 200 '
                            'and event.extra_data_json[\'time_to_a\'] < 60'
                        ),
                    },
                    {'action': [{'type': 'activity', 'value': 0}]},
                ],
            },
        ],
    },
)
async def test_expressions(
        stq3_context,
        time_to_a,
        distance_to_a,
        expected_activity,
        dms_mockserver,
):
    fake_events = lookup_info.make_fake_order_events(
        udid=UDID,
        order_id='order_id',
        zone=ZONE,
        tariff_class='vip',
        rider_tags=['orange'],
        tags=[],
        time_to_a=time_to_a,
        distance_to_a=distance_to_a,
    )
    driver = await DriverInfo.make(
        stq3_context,
        UDID,
        fetch_blocking_history=False,
        fetch_events_history=False,
        fetch_tags=False,
        fetch_blocking_info=False,
        dms_timeout=100,
    )

    res = await lookup_info.get_new_activity_prediction(
        stq3_context,
        driver=driver,
        events=fake_events,
        dispatch_id='dispatch_id',
    )
    res = res.activity
    assert res.get('c', 0) == expected_activity


@pytest.mark.parametrize(
    'distance, duration, zone, tariff, expected',
    [
        (2000, 2, 'bangladesh', 'econom', 'medium'),
        (1, 21, 'winterfell', 'comfortplus', 'short'),
        (800, 30, 'winterfell', 'vip', 'long'),
        (2001, 7, 'bangladesh', 'comfortplus', 'long'),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_CONFIG_SERVICE_USAGE_SETTINGS={
        '__default__': ['dispatch_length_thresholds'],
    },
)
@pytest.mark.rules_config(
    DISPATCH_LENGTH_THRESHOLDS={
        'default': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'distance': [600, 800],
                                'time': [1, 5],
                                'aggregation_type': 'max',
                                'type': 'dispatch_length_thresholds',
                            },
                        ],
                        'tags': '\'event::tariff_vip\'',
                    },
                    {
                        'action': [
                            {
                                'distance': [1000, 2000],
                                'time': [3, 6],
                                'type': 'dispatch_length_thresholds',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'CommonDispatchRule',
            },
        ],
        'winterfell': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'distance': [1, 1000],
                                'time': [20, 30],
                                'aggregation_type': 'min',
                                'type': 'dispatch_length_thresholds',
                            },
                        ],
                        'tags': '\'event::tariff_comfortplus\'',
                    },
                    {
                        'action': [
                            {
                                'distance': [1000, 2000],
                                'time': [3, 6],
                                'type': 'dispatch_length_thresholds',
                            },
                        ],
                    },
                ],
                'events': [{'topic': 'order'}],
                'name': 'CommonDispatchRule',
            },
        ],
    },
)
async def test_dispatch_type(
        distance,
        duration,
        zone,
        tariff,
        expected,
        stq3_context,
        dms_mockserver,
):
    driver = await DriverInfo.make(
        stq3_context,
        UDID,
        fetch_blocking_history=False,
        fetch_events_history=False,
        fetch_tags=False,
        fetch_blocking_info=False,
        dms_timeout=100,
    )
    distance_type = await dispatch_ranges.get_dispatch_type_new(
        context=stq3_context,
        driver=driver,
        event=event_helpers.make_fake_order_event(
            udid=UDID,
            order_id='order_id',
            zone=zone,
            tariff_class=tariff,
            rider_tags=[],
            tags=[],
            event_name='complete',
            timestamp=dates.utcnow(),
            time_to_a=duration,
            distance_to_a=distance,
        ),
    )
    assert distance_type == expected
