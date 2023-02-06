import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import mode_rules_create
from tests_driver_mode_subscription import offer_templates

_NOW = '2020-08-03T19:51:00+00:00'

_INTERSECT_RULE_ID1 = '11111111111111111111111111111111'
_INTERSECT_RULE_ID2 = '11111111111111111111111111111112'
_INTERSECT_RULE_ID3 = '11111111111111111111111111111113'
_INTERSECT_RULE_ID4 = '11111111111111111111111111111114'


def _make_rule_patch(
        starts_at: str,
        stops_at: Optional[str] = None,
        rule_id: Optional[str] = None,
        is_canceled: Optional[bool] = None,
):
    _stops_at = datetime.datetime.fromisoformat(stops_at) if stops_at else None

    return mode_rules.Patch(
        rule_id=rule_id,
        rule_name='test_rule',
        starts_at=datetime.datetime.fromisoformat(starts_at),
        stops_at=_stops_at,
        is_canceled=is_canceled,
    )


_RULE_ACTIVE = _make_rule_patch(
    '2020-08-03T19:00:00+00:00',
    '2020-08-03T21:00:00+00:00',
    rule_id=_INTERSECT_RULE_ID1,
)

_RULE_CONTAINED = _make_rule_patch(
    '2020-08-03T21:00:00+00:00',
    '2020-08-03T22:00:00+00:00',
    rule_id=_INTERSECT_RULE_ID2,
)

_RULE_INTERSECT_RIGHT = _make_rule_patch(
    '2020-08-03T22:00:00+00:00',
    '2020-08-03T23:00:00+00:00',
    rule_id=_INTERSECT_RULE_ID3,
)

_RULE_NO_INTERSECTION = _make_rule_patch(
    '2020-08-03T23:00:00+00:00',
    '2020-08-04T00:00:00+00:00',
    rule_id=_INTERSECT_RULE_ID4,
)


def _make_intersection_error_message(
        starts_at: str,
        stops_at: str = 'null',
        rule_id: str = _INTERSECT_RULE_ID1,
):
    return (
        f'intersect with rules: [{{id: {rule_id}, starts at: {starts_at}, '
        f'stops_at: {stops_at}}}]'
    )


def _normalize_datetime(datetime_with_timezone: Optional[datetime.datetime]):
    if not datetime_with_timezone:
        return datetime_with_timezone
    return datetime_with_timezone.replace(tzinfo=None)


def _make_close_canceled(close_time_str: Optional[str], canceled: bool):
    close_time = (
        datetime.datetime.fromisoformat(close_time_str)
        if close_time_str
        else None
    )
    return (_normalize_datetime(close_time), canceled)


def _get_rules_close_canceled(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        """
        SELECT
        rule_id, stops_at AT TIME ZONE 'UTC', canceled
        FROM config.mode_rules
        """,
    )
    rows = list(row for row in cursor)
    return {
        row[0].replace('-', ''): (_normalize_datetime(row[1]), row[2])
        for row in rows
    }


def _get_rules_close_canceled_diff(
        pgsql, initial_state: Dict[str, Tuple[datetime.datetime, bool]],
):
    new_state = _get_rules_close_canceled(pgsql)
    return {
        id: new_state[id]
        for id, values in initial_state.items()
        if new_state[id] != values
    }


@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[mode_rules.init_admin_schema_version()],
)
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_DRIVER_MODE_SETTINGS=(
        mode_rules_create.DEFAULT_BILLING_DRIVER_MODE_SETTINGS
    ),
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {'test_rule': 'orders_template'},
    },
)
@pytest.mark.parametrize(
    'rule_data, rules_to_override, expected_error_msg, expected_error_code, '
    'expected_mode_rules_diff',
    [
        pytest.param(
            mode_rules_create.RuleData(starts_at='2020-08-03T20:51:00+00:00'),
            [_INTERSECT_RULE_ID1],
            None,
            None,
            {
                _INTERSECT_RULE_ID1: _make_close_canceled(
                    '2020-08-03T20:51:00+00:00', False,
                ),
            },
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[mode_rules.patched_db(patches=[_RULE_ACTIVE])],
                ),
            ],
            id='active_rule',
        ),
        pytest.param(
            mode_rules_create.RuleData(starts_at='2020-08-03T20:51:00+00:00'),
            [_INTERSECT_RULE_ID1],
            f'Failed to close rule {_INTERSECT_RULE_ID1}: new stop time should'
            f' not be later than existing one',
            'INVALID_MODE_RULE',
            {},
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-01T20:51:00+00:00',
                                    '2020-08-03T19:00:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID1,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
            id='closed_rule_in_past',
        ),
        pytest.param(
            mode_rules_create.RuleData(starts_at='2020-08-03T20:51:00+00:00'),
            [_INTERSECT_RULE_ID1, _INTERSECT_RULE_ID2],
            f'Failed to close rule {_INTERSECT_RULE_ID2}: new stop time should'
            f' not be later than existing one',
            'INVALID_MODE_RULE',
            {},
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                _make_rule_patch(
                                    '2020-08-01T20:51:00+00:00',
                                    '2020-08-02T20:50:00+00:00',
                                    rule_id=_INTERSECT_RULE_ID2,
                                ),
                                _RULE_ACTIVE,
                            ],
                        ),
                    ],
                ),
            ],
            id='several_rules_in_past',
        ),
        pytest.param(
            mode_rules_create.RuleData(starts_at='2020-08-03T20:51:00+00:00'),
            [_INTERSECT_RULE_ID1, _INTERSECT_RULE_ID2],
            f'Rule with id {_INTERSECT_RULE_ID2} not found',
            'RULE_NOT_FOUND',
            {},
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[mode_rules.patched_db(patches=[_RULE_ACTIVE])],
                ),
            ],
            id='missing_rule_id',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00',
                stops_at='2020-08-03T22:30:00+00:00',
            ),
            [
                _INTERSECT_RULE_ID1,
                _INTERSECT_RULE_ID2,
                _INTERSECT_RULE_ID3,
                _INTERSECT_RULE_ID4,
            ],
            None,
            None,
            {
                _INTERSECT_RULE_ID1: _make_close_canceled(
                    '2020-08-03T20:51:00+00:00', False,
                ),
                _INTERSECT_RULE_ID2: _make_close_canceled(
                    '2020-08-03T22:00:00+00:00', True,
                ),
                _INTERSECT_RULE_ID3: _make_close_canceled(
                    '2020-08-03T23:00:00+00:00', True,
                ),
                _INTERSECT_RULE_ID4: _make_close_canceled(
                    '2020-08-04T00:00:00+00:00', True,
                ),
            },
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[
                                # past: still active
                                _RULE_ACTIVE,
                                # future: contained in new rule
                                _RULE_CONTAINED,
                                # future: intersects with new rule
                                _RULE_INTERSECT_RIGHT,
                                # future: no intersection
                                _RULE_NO_INTERSECTION,
                            ],
                        ),
                    ],
                ),
            ],
            id='one_active_and_several_future_rules',
        ),
        pytest.param(
            mode_rules_create.RuleData(starts_at='2020-08-03T20:51:00+00:00'),
            [_INTERSECT_RULE_ID1],
            _make_intersection_error_message(
                '2020-08-03T21:00:00+0000',
                '2020-08-03T22:00:00+0000',
                _INTERSECT_RULE_ID2,
            ),
            'INVALID_MODE_RULE',
            {},
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        mode_rules.patched_db(
                            patches=[_RULE_ACTIVE, _RULE_CONTAINED],
                        ),
                    ],
                ),
            ],
            id='override_one_of_intersecting_rules',
        ),
        pytest.param(
            mode_rules_create.RuleData(
                starts_at='2020-08-03T20:51:00+00:00', stops_at='',
            ),
            [_INTERSECT_RULE_ID2],
            f'Rule {_INTERSECT_RULE_ID2} may be canceled at least 70'
            ' minutes before start',
            'INVALID_MODE_RULE',
            {},
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[mode_rules.patched_db(patches=[_RULE_CONTAINED])],
                ),
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
                        'rule_draft_cancel_min_threshold_m': 70,
                    },
                ),
            ],
            id='check_cancelation_threshold',
        ),
    ],
)
async def test_admin_mode_rules_create_overwrite(
        taxi_driver_mode_subscription,
        pgsql,
        rule_data: mode_rules_create.RuleData,
        rules_to_override: List[str],
        expected_error_msg: Optional[str],
        expected_error_code: Optional[str],
        expected_mode_rules_diff: Dict[str, Tuple[datetime.datetime, bool]],
):
    initial_state = _get_rules_close_canceled(pgsql)

    await mode_rules_create.check_test_create_body_base(
        taxi_driver_mode_subscription,
        rule_data.as_request(rules_to_override),
        expected_error_msg,
        expected_error_msg,
        expected_error_code,
    )

    mode_rules_diff = _get_rules_close_canceled_diff(pgsql, initial_state)
    assert mode_rules_diff == expected_mode_rules_diff
