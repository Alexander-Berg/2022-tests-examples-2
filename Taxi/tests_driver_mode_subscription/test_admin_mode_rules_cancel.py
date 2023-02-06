import datetime
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

_NOW = '2020-08-03T19:51:00+00:00'
_REQUEST_HEADERS = {
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
    'X-Yandex-Login': 'loginef',
    'X-YaTaxi-Draft-Id': '42',
}


def _get_rules_canceled(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT replace(rule_id::text, \'-\', \'\'), canceled '
        'FROM config.mode_rules;',
    )
    return {row[0]: row[1] for row in cursor}


def _get_canceled_diff(pgsql, initial_state: Dict[str, bool]):
    new_state = _get_rules_canceled(pgsql)
    return {k: v for k, v in new_state.items() if initial_state[k] != v}


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='future_rule',
                    rule_id='11111111111111111111111111111111',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-08-03T20:51:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='closed_future_rule',
                    rule_id='22222222222222222222222222222222',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-08-03T20:51:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-08-03T21:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='canceled_rule',
                    rule_id='33333333333333333333333333333333',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-08-03T20:51:00+00:00',
                    ),
                    is_canceled=True,
                ),
                mode_rules.Patch(
                    rule_name='active_rule',
                    rule_id='44444444444444444444444444444444',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('is_check', [False, True])
@pytest.mark.parametrize(
    'rule_id, expected_code, expected_error, should_cancel, work_mode',
    [
        pytest.param(
            '11111111111111111111111111111111',
            200,
            None,
            True,
            'future_rule',
            id='future',
        ),
        pytest.param(
            '22222222222222222222222222222222',
            200,
            None,
            True,
            'closed_future_rule',
            id='closed_future',
        ),
        pytest.param(
            '33333333333333333333333333333333',
            200,
            None,
            False,
            'canceled_rule',
            id='canceled_future',
        ),
        pytest.param(
            '44444444444444444444444444444444',
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    'Rule 44444444444444444444444444444444 start time reached'
                ),
                'details': (
                    'Rule 44444444444444444444444444444444 start time reached'
                ),
            },
            False,
            'active_rule',
            id='active_rule',
        ),
        pytest.param(
            '55555555555555555555555555555555',
            404,
            {
                'code': 'RULE_NOT_FOUND',
                'message': (
                    'Rule with id 55555555555555555555555555555555 not found'
                ),
                'details': (
                    'Rule with id 55555555555555555555555555555555 not found'
                ),
            },
            False,
            None,
            id='missing_rule',
        ),
        pytest.param(
            '22222222222222222222222222222222',
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    'Rule 22222222222222222222222222222222 may be '
                    'canceled at least 61 minutes before start'
                ),
                'details': (
                    'Rule 22222222222222222222222222222222 may be '
                    'canceled at least 61 minutes before start'
                ),
            },
            False,
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
                        'rule_draft_cancel_min_threshold_m': 61,
                    },
                ),
            ],
            id='threshold_fail',
        ),
        pytest.param(
            '22222222222222222222222222222222',
            200,
            None,
            True,
            'closed_future_rule',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
                        'rule_draft_cancel_min_threshold_m': 59,
                    },
                ),
            ],
            id='threshold_ok',
        ),
        pytest.param(
            '22222222222222222222222222222222',
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    'Editing of work mode closed_future_rule is prohibited in '
                    'DRIVER_MODE_RULES_VALIDATION_SETTINGS config'
                ),
                'details': (
                    'Editing of work mode closed_future_rule is prohibited in '
                    'DRIVER_MODE_RULES_VALIDATION_SETTINGS config'
                ),
            },
            False,
            'closed_future_rule',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
                        'read_only_modes': ['closed_future_rule'],
                    },
                ),
            ],
            id='mode_read_only',
        ),
    ],
)
async def test_rules_cancel(
        taxi_driver_mode_subscription,
        pgsql,
        rule_id: str,
        expected_code: int,
        is_check: bool,
        should_cancel: bool,
        expected_error: Optional[Dict[str, str]],
        work_mode: Optional[str],
):
    request_body = {'rule_id': rule_id}
    initial_state = _get_rules_canceled(pgsql)
    if is_check:
        response = await taxi_driver_mode_subscription.post(
            'v1/admin/mode_rules/check_cancel',
            json=request_body,
            headers=_REQUEST_HEADERS,
        )
        assert response.status_code == expected_code
        if expected_code == 200:
            assert work_mode
            assert response.json() == {
                'data': request_body,
                'lock_ids': [
                    {
                        'custom': True,
                        'id': mode_rules.build_draft_lock_id(work_mode),
                    },
                ],
            }
        else:
            assert response.json() == expected_error
        assert not _get_canceled_diff(pgsql, initial_state)
    else:
        response = await taxi_driver_mode_subscription.post(
            'v1/admin/mode_rules/cancel',
            json=request_body,
            headers=_REQUEST_HEADERS,
        )
        assert response.status_code == expected_code
        canceled_rules = _get_canceled_diff(pgsql, initial_state)
        if expected_code == 200:
            if should_cancel:
                assert canceled_rules == {rule_id: True}
            else:
                assert not canceled_rules
        else:
            assert response.json() == expected_error
            assert canceled_rules == {}


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='future_rule',
                    rule_id='11111111111111111111111111111111',
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-08-03T20:51:00+00:00',
                    ),
                    drafts=[mode_rules.Draft('1', 'create')],
                ),
            ],
        ),
    ],
)
async def test_draft(taxi_driver_mode_subscription, pgsql):
    rule_id = '11111111111111111111111111111111'
    request_body = {'rule_id': rule_id}

    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/cancel',
        json=request_body,
        headers=_REQUEST_HEADERS,
    )
    assert response.status_code == 200

    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT drafts FROM config.mode_rules '
        f'WHERE rule_id = \'{rule_id}\'::uuid;',
    )
    for row in cursor:
        assert row[0] == '{"(1,create)","(42,cancel)"}'
