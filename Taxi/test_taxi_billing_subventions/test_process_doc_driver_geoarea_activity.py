import collections

import pytest

from taxi_billing_subventions.common.models.doc import DriverGeoareaActivity
from taxi_billing_subventions.common.models.rule import (
    SubventionType as SubvType,
)
from taxi_billing_subventions.process_doc import _driver_geoarea_activity

_RuleMock = collections.namedtuple('RuleMock', ['subvention_type', 'identity'])
_DockMock = collections.namedtuple('DockMock', ['rule_types'])
_RuleType = DriverGeoareaActivity.RuleType


@pytest.mark.parametrize(
    'rule_types, doc_rule_types, expected_rules',
    [
        ([SubvType.DRIVER_FIX], [_RuleType.DRIVER_FIX], [SubvType.DRIVER_FIX]),
        ([SubvType.BOOKING_GEO_ON_TOP], [_RuleType.DRIVER_FIX], []),
        (
            [SubvType.BOOKING_GEO_ON_TOP],
            [_RuleType.GEO_BOOKING],
            [SubvType.BOOKING_GEO_ON_TOP],
        ),
        (
            [SubvType.BOOKING_GEO_GUARANTEE],
            [_RuleType.GEO_BOOKING],
            [SubvType.BOOKING_GEO_GUARANTEE],
        ),
        ([SubvType.BOOKING_GEO_ON_TOP], [], [SubvType.BOOKING_GEO_ON_TOP]),
        (
            [SubvType.DRIVER_FIX, SubvType.BOOKING_GEO_ON_TOP],
            [_RuleType.DRIVER_FIX],
            [SubvType.DRIVER_FIX],
        ),
    ],
)
def test_select_rules_for_doc(rule_types, doc_rule_types, expected_rules):
    # pylint: disable=protected-access
    rules = [_RuleMock(rule_type, '#') for rule_type in rule_types]
    event = _DockMock(doc_rule_types)

    selected_rules = _driver_geoarea_activity._select_rules_for_doc(
        rules, event, None,
    )
    for expected_rule, actual_rule in zip(expected_rules, selected_rules):
        assert expected_rule == actual_rule.subvention_type
