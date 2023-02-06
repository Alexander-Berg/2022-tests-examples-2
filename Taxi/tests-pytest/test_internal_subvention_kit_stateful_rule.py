# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import pytest

import taxi.internal.subvention_kit.stateful_rule as sr
import taxi.internal.dbh.unique_driver_zone_stats as udzs


def achieve_dayridecount(interval_list, ride_count, result):
    return sr.DayRideCountCheck(interval_list)(ride_count) == result


@pytest.mark.parametrize(
    ('ride_count', 'result'), [
    (0, False),
    (1, True),
    (2, True),
    (100500, True),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_day_ride_count_check_single_interval(ride_count, result):
    assert achieve_dayridecount([[1]], ride_count, result)


@pytest.mark.parametrize(
    ('ride_count', 'result'), [
    (0, False),
    (1, True),
    (2, True),
    (3, True),
    (4, False),
    (100500, False),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_day_ride_count_check_double_interval(ride_count, result):
    assert achieve_dayridecount([[1, 3]], ride_count, result)


@pytest.mark.parametrize(
    ('ride_count', 'result'), [
    (5, False),
    (6, True),
    (7, True),
    (8, False),
    (9, True),
    (10, True),
    (100500, True),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_day_ride_count_check_interval_list(ride_count, result):
    assert achieve_dayridecount([[6, 7], [9]], ride_count, result)


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_day_ride_count_check_raises():
    with pytest.raises(sr.InvalidDayRideCountIntervalError):
        sr.DayRideCountCheck([[1, 2, 3]])(0)


class MockStatsItem(object):
    def __init__(self, num_days, shallow_order_list):
        self.shallow_order_stats = {num_days: shallow_order_list}


def default_stateful_rule_args(**kwargs):
    result = {
        'rule_id': 'stateful_test_id',
        'day_number': 7,
        'interval_list': [[1]],
        'is_once': True,
        'hour': [],
        'day_ride_count_is_for_any_category': True,
        'branding_type': None,
        'tariff_class': 'econom',
    }
    result.update(kwargs)
    return result


def _new_shallow_order(tariff_class, localized_due, branding_abbr=''):
    soo = udzs._unique_driver_stats.ShallowOrderObject()
    soo.obj['tariff_class'] = tariff_class
    soo.obj['localized_due'] = localized_due
    result = {
        'tariff_class': tariff_class,
        'localized_due': localized_due,
    }
    if 'l' in branding_abbr:
        soo.obj.has_lightbox = True
        result['has_lightbox'] = True
    if 's' in branding_abbr:
        soo.obj.has_sticker = True
        result['has_sticker'] = True
    return soo.obj


@pytest.mark.parametrize(
    ('hour', 'threshold', 'result'), [
    ([10], 1, True),
    ([10], 2, False),
    ([10, 11], 2, True),
    ([10, 11], 3, True),
    ([10, 11], 4, False),
    ([10, 12], 3, True),
    ([10, 12], 4, True),
    ([10, 12], 5, False),
    ([], 6, True),
]
)
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_stateful_rule_hour(hour, threshold, result):
    stateful_rule = sr.StatefulRule(**default_stateful_rule_args(
        hour=hour,
        interval_list=[[threshold]],
    ))
    stats_item = MockStatsItem(7, [
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 10)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 11)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 11)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12)),
    ])
    assert stateful_rule.is_matches(stats_item) == result


@pytest.mark.parametrize(
    ('anycat', 'tariff_class', 'threshold', 'result'), [
    (True, [], 7, True),
    (True, [], 8, False),
    (False, [], 7, True),
    (False, [], 8, False),
    (False, ['unknown_tariff'], 1, False),
    (False, ['vip'], 3, True),
    (False, ['vip'], 4, False),
    (False, ['econom'], 4, True),
    (False, ['econom'], 5, False),
    (False, ['econom', 'vip'], 7, True),
    (False, ['econom', 'vip'], 8, False),
]
)
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_stateful_rule_tariff(anycat, tariff_class, threshold, result):
    stateful_rule = sr.StatefulRule(**default_stateful_rule_args(
        hour=range(24),
        day_ride_count_is_for_any_category=anycat,
        tariff_class=tariff_class,
        interval_list=[[threshold]],
    ))
    stats_item = MockStatsItem(7, [
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 10)),
        _new_shallow_order('vip', datetime.datetime(2017, 10, 10, 11)),
        _new_shallow_order('vip', datetime.datetime(2017, 10, 10, 11)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12)),
        _new_shallow_order('vip', datetime.datetime(2017, 10, 10, 12)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12)),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 13)),
    ])
    assert stateful_rule.is_matches(stats_item) == result


@pytest.mark.parametrize(
    ('branding_type', 'threshold', 'result'), [
    ('full_branding', 1, True),
    ('full_branding', 2, False),
    ('sticker', 4, True),
    ('sticker', 5, False),
    ('lightbox', 3, True),
    ('lightbox', 4, False),
    (None, 7, True),
    (None, 8, False),
]
)
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_stateful_rule_branding(branding_type, threshold, result):
    stateful_rule = sr.StatefulRule(**default_stateful_rule_args(
        hour=range(24),
        branding_type=branding_type,
        interval_list=[[threshold]],
    ))
    stats_item = MockStatsItem(7, [
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 10), 'l'),
        _new_shallow_order('vip', datetime.datetime(2017, 10, 10, 11), 'l'),
        _new_shallow_order('vip', datetime.datetime(2017, 10, 10, 11), 'ls'),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12), 's'),
        _new_shallow_order('vip', datetime.datetime(2017, 10, 10, 12), 's'),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 12), 's'),
        _new_shallow_order('econom', datetime.datetime(2017, 10, 10, 13)),
    ])
    assert stateful_rule.is_matches(stats_item) == result


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_stateful_rule_repr():
    stateful_rule = sr.StatefulRule(**default_stateful_rule_args())
    assert stateful_rule.__repr__() == ('StatefulRule('
    'rule_id=u\'stateful_test_id\',day_number=7,interval_list=[[1]],'
    'is_once=True,hour=[],any_tariff_class=True,branding_type=None,'
    'tariff_class=u\'econom\')')


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_stateful_rule_log():
    stateful_rule = sr.StatefulRule(**default_stateful_rule_args(
        interval_list=[[1, 2, 3]]
    ))
    assert not stateful_rule.is_matches(MockStatsItem(7, []))
