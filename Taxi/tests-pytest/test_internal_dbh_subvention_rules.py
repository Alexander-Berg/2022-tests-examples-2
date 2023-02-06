from taxi.internal import dbh

import pytest


@pytest.mark.parametrize(
    'rule_id,expected_interval,expected_days,expected_any', [
        ('new_branding_rule_id', [[1]], 1, True),
        ('new_branding_with_tariff_rule_id', [[1]], 1, False),
        ('is_once_rule_id', [[10]], {}, {}),
        ('is_once_branding_rule_id', {}, {}, {}),
        ('old_branding_rule_id', [[15]], 1, False),
        ('empty_day_ride_count_rule_id', [], {}, {}),
        ('missing_day_ride_count_rule_id', {}, {}, {}),
])
@pytest.mark.filldb(
    subvention_rules='for_test_effective_day_ride_count',
)
@pytest.inline_callbacks
def test_effective_day_ride_count(
        rule_id, expected_interval, expected_days, expected_any
):
    rule = yield dbh.subvention_rules.Doc.find_one_by_id(rule_id)
    assert rule.effective_day_ride_count == expected_interval
    assert rule.effective_day_ride_count_days == expected_days
    actual_any = rule.effective_day_ride_count_is_for_any_category
    assert actual_any == expected_any


@pytest.mark.parametrize('rule_id,key,expected_value', [
    (
        'full_branding_total_dayridecount_rule_id',
        'full_branding_total_dayridecount',
        [[1]],
    ),
    (
        'sticker_total_dayridecount_rule_id',
        'sticker_total_dayridecount',
        [[1]],
    ),
    (
        'total_dayridecount_rule_id',
        'total_dayridecount',
        [[10]],
    ),
    (
        'full_branding_dayridecount_rule_id',
        'full_branding_dayridecount',
        [[1]],
    ),
    (
        'sticker_dayridecount_rule_id',
        'sticker_dayridecount',
        [[1]],
    ),
    (
        'dayridecount_rule_id',
        'dayridecount',
        [[10]],
    ),
])
@pytest.mark.filldb(
    subvention_rules='for_test_get_sub_rules',
)
@pytest.inline_callbacks
def test_get_sub_rules(rule_id, key, expected_value):
    rule = yield dbh.subvention_rules.Doc.find_one_by_id(rule_id)
    sub_rules = rule.get_sub_rules()
    _assert_same_day_ride_count_rules(
        sub_rules[key], _make_day_ride_count_rule(expected_value)
    )


def _make_day_ride_count_rule(intervals):
    assert len(intervals) == 1
    assert len(intervals[0]) == 1
    return dbh.subvention_rules.DayRideCountRule(
        num_days=1,
        rule=[xrange(intervals[0][0], 10000)],
        enable_declining=True,
    )


def _assert_same_day_ride_count_rules(left, right):
    assert left.num_days == right.num_days
    assert len(left.rule) == 1
    assert len(right.rule) == 1
    assert list(left.rule[0]) == list(right.rule[0])
    assert left.enable_declining == right.enable_declining
