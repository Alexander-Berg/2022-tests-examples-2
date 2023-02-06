import pytest

from taxi.internal import dbh
from taxi.internal.subvention_kit import rule_helpers
from taxi.internal.subvention_kit import rule_processors


def _make_driver_points_decline_reason():
    reason = rule_processors.DeclineReason(
        key=rule_processors.DECLINE_KEY_DRIVER_POINTS,
        reason=rule_processors.DECLINE_REASON_TOO_LOW_VALUE
    )
    return reason.as_dict()


def _make_rule(driver_points=None, decline_reasons=[]):
    doc = dbh.subvention_reasons.Doc()
    doc.subvention_calc_rules = []
    rule = doc.subvention_calc_rules.new()
    rule.driver_points = driver_points
    rule.decline_reasons = decline_reasons
    return rule


@pytest.mark.parametrize(
    'subventions_calc_rules, expected_type, expected_driver_points', [
        (
            [_make_rule(driver_points=30)], rule_helpers.APPLIED, 30
        ),
        (
            [
                _make_rule(
                    driver_points=40,
                    decline_reasons=[_make_driver_points_decline_reason()]
                )
            ],
            rule_helpers.DECLINED, 40
        ),
        (
            [
                _make_rule(driver_points=60),
                _make_rule(
                    driver_points=80,
                    decline_reasons=[_make_driver_points_decline_reason()]
                )
            ],
            rule_helpers.APPLIED, 60
        ),
        (
            [
                _make_rule(),
                _make_rule()
            ],
            rule_helpers.NO_SUBVENTION, None
        )
    ]
)
def test_find_driver_points_subvention(
        subventions_calc_rules, expected_type, expected_driver_points
):
    subvention_type, rule = rule_helpers.find_driver_points_subvention(
        subventions_calc_rules
    )

    assert subvention_type == expected_type
    if rule:
        assert rule.get(rule_helpers.DRIVER_POINTS) == expected_driver_points
