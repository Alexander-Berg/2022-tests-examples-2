import datetime
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules

_NOW = '2020-08-03T19:51:00+00:00'
_FUTURE = '2021-08-03T19:51:00+00:00'
_PAST = '2019-08-03T19:51:00+00:00'
_REQUEST_HEADERS = {
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
    'X-Yandex-Login': 'loginef',
    'X-YaTaxi-Draft-Id': '42',
}


def _get_rule_close_times(pgsql):
    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT replace(rule_id::text, \'-\', \'\'), '
        ' stops_at at time zone \'UTC\' '
        'FROM config.mode_rules;',
    )
    return {row[0]: row[1] for row in cursor}


def _to_utc_datetime(time_str: str):
    return datetime.datetime.fromisoformat(time_str).replace(tzinfo=None)


_RULE_ID0 = '00000000000000000000000000000000'
_RULE_ID1 = '11111111111111111111111111111111'
_RULE_ID2 = '22222222222222222222222222222222'
_RULE_ID3 = '33333333333333333333333333333333'
_RULE_ID4 = '44444444444444444444444444444444'
_RULE_ID5 = '55555555555555555555555555555555'
_RULE_ID6 = '66666666666666666666666666666666'
_RULE_ID7 = '77777777777777777777777777777777'

_INITIAL_CLOSE_TIMES = {
    _RULE_ID1: None,
    _RULE_ID2: _to_utc_datetime('2020-08-03T10:00:00+00:00'),
    _RULE_ID3: _to_utc_datetime('2020-08-03T19:00:00+00:00'),
    _RULE_ID4: _to_utc_datetime('2020-08-03T20:00:00+00:00'),
    _RULE_ID5: _to_utc_datetime('2020-08-03T21:00:00+00:00'),
    _RULE_ID6: _to_utc_datetime('2020-08-04T10:00:00+00:00'),
    _RULE_ID7: None,
}


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.config()
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(rule_name='ordinary_rule', rule_id=_RULE_ID1),
                mode_rules.Patch(
                    rule_name='closed_rule',
                    rule_id=_RULE_ID2,
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-08-03T10:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='many_versioned_rule',
                    rule_id=_RULE_ID3,
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-08-03T19:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='many_versioned_rule',
                    rule_id=_RULE_ID4,
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-08-03T19:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-08-03T20:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='many_versioned_rule',
                    rule_id=_RULE_ID5,
                    starts_at=datetime.datetime.fromisoformat(
                        '2020-08-03T20:00:00+00:00',
                    ),
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-08-03T21:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='planned_to_be_closed_rule',
                    rule_id=_RULE_ID6,
                    stops_at=datetime.datetime.fromisoformat(
                        '2020-08-04T10:00:00+00:00',
                    ),
                ),
                mode_rules.Patch(
                    rule_name='canceled_rule',
                    rule_id=_RULE_ID7,
                    is_canceled=True,
                ),
            ],
            rules={},
        ),
    ],
)
@pytest.mark.parametrize('is_check', [False, True])
@pytest.mark.parametrize(
    'rule_id, stops_at, expected_code, expected_error, work_mode',
    [
        pytest.param(
            _RULE_ID1,
            _NOW,
            200,
            None,
            'ordinary_rule',
            id='close_active_rule_now',
        ),
        pytest.param(
            _RULE_ID1,
            _FUTURE,
            200,
            None,
            'ordinary_rule',
            id='close_active_rule_in_future',
        ),
        pytest.param(
            _RULE_ID1,
            _PAST,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID1}: stop time should not '
                    f'be in the past'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID1}: stop time should not '
                    f'be in the past'
                ),
            },
            None,
            id='close_active_rule_in_past',
        ),
        pytest.param(
            _RULE_ID2,
            _NOW,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID2}: '
                    f'new stop time should not be later than existing one'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID2}: '
                    f'new stop time should not be later than existing one'
                ),
            },
            None,
            id='close_closed_rule_now',
        ),
        pytest.param(
            _RULE_ID2,
            _FUTURE,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID2}: '
                    f'new stop time should not be later than existing one'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID2}: '
                    f'new stop time should not be later than existing one'
                ),
            },
            None,
            id='close_closed_rule_in_future',
        ),
        pytest.param(
            _RULE_ID2,
            _PAST,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID2}: stop time should not '
                    f'be in the past'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID2}: stop time should not '
                    f'be in the past'
                ),
            },
            None,
            id='close_closed_rule_in_past',
        ),
        pytest.param(
            _RULE_ID2,
            '2020-08-03T10:00:00+00:00',
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID2}: stop time should not '
                    f'be in the past'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID2}: stop time should not '
                    f'be in the past'
                ),
            },
            None,
            id='close_closed_rule_same_time',
        ),
        pytest.param(
            _RULE_ID6,
            '2020-08-04T10:00:00+00:00',
            200,
            None,
            'planned_to_be_closed_rule',
            id='close_planned_rule_same_time',
        ),
        pytest.param(
            _RULE_ID6,
            '2020-08-04T11:00:00+00:00',
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID6}: '
                    f'new stop time should not be later than existing one'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID6}: '
                    f'new stop time should not be later than existing one'
                ),
            },
            None,
            id='close_planned_rule_later',
        ),
        pytest.param(
            _RULE_ID6,
            '2020-08-04T09:00:00+00:00',
            200,
            None,
            'planned_to_be_closed_rule',
            id='close_planned_rule_earlier',
        ),
        pytest.param(
            _RULE_ID5,
            _NOW,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID5}: stop time should'
                    f' not be earlier than start time'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID5}: stop time should'
                    f' not be earlier than start time'
                ),
            },
            None,
            id='close_versioned_rule_last_before_start',
        ),
        pytest.param(
            _RULE_ID4,
            _NOW,
            200,
            None,
            'many_versioned_rule',
            id='close_versioned_rule_middle',
        ),
        pytest.param(
            _RULE_ID0,
            _NOW,
            400,
            {
                'code': 'RULE_NOT_FOUND',
                'message': 'Rule with given id not found',
                'details': 'Rule with given id not found',
            },
            None,
            id='missing_rule',
        ),
        pytest.param(
            _RULE_ID7,
            _NOW,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    f'Failed to close rule {_RULE_ID7}: rule is already '
                    f'canceled'
                ),
                'details': (
                    f'Failed to close rule {_RULE_ID7}: rule is already '
                    f'canceled'
                ),
            },
            None,
            id='missing_rule',
        ),
        pytest.param(
            _RULE_ID1,
            _NOW,
            400,
            {
                'code': 'INVALID_MODE_RULE',
                'message': (
                    'Editing of work mode ordinary_rule is prohibited in '
                    'DRIVER_MODE_RULES_VALIDATION_SETTINGS config'
                ),
                'details': (
                    'Editing of work mode ordinary_rule is prohibited in '
                    'DRIVER_MODE_RULES_VALIDATION_SETTINGS config'
                ),
            },
            None,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_VALIDATION_SETTINGS={
                        'read_only_modes': ['ordinary_rule'],
                    },
                ),
            ],
            id='read_only_rule',
        ),
    ],
)
async def test_rules_close(
        taxi_driver_mode_subscription,
        pgsql,
        rule_id: str,
        stops_at: str,
        expected_code: int,
        is_check: bool,
        expected_error: Optional[Dict[str, str]],
        work_mode: Optional[str],
):
    request_body = {'rule_id': rule_id, 'stops_at': stops_at}
    if is_check:
        response = await taxi_driver_mode_subscription.post(
            'v1/admin/mode_rules/check_close',
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
    else:
        response = await taxi_driver_mode_subscription.post(
            'v1/admin/mode_rules/close',
            json=request_body,
            headers=_REQUEST_HEADERS,
        )
        assert response.status_code == expected_code

        expected_close_times = {**_INITIAL_CLOSE_TIMES}
        if expected_code == 200:
            expected_close_times[rule_id] = _to_utc_datetime(stops_at)
        assert _get_rule_close_times(pgsql) == expected_close_times


@pytest.mark.parametrize(
    'rule_id, valid',
    [
        ('helloworldhelloworldhelloworldhe', False),
        ('444444', False),
        ('feffffff-fdfe-ffff-fffd-fefffffffdfe', False),
        ('000000000000400000000000000000001', False),
        ('000000000000000h0000000000000000', False),
        ('0123456789abcdefABCDEF0000000000', True),
        ('00000000000000000000000000000000', True),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_validate_rule_id(
        taxi_driver_mode_subscription, rule_id: str, valid: bool,
):
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/close',
        json={'rule_id': rule_id, 'stops_at': _NOW},
        headers=_REQUEST_HEADERS,
    )
    assert response.status_code == 400
    rule_missing = response.json().get('code', '') == 'RULE_NOT_FOUND'
    # service returns 400 if rule is valid but not found
    assert rule_missing == valid


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        mode_rules.patched_db(
            patches=[
                mode_rules.Patch(
                    rule_name='ordinary_rule',
                    rule_id=_RULE_ID1,
                    drafts=[mode_rules.Draft('1', 'create')],
                ),
            ],
            rules={},
        ),
    ],
)
async def test_draft(taxi_driver_mode_subscription, pgsql):
    request_body = {'rule_id': _RULE_ID1, 'stops_at': _NOW}
    response = await taxi_driver_mode_subscription.post(
        'v1/admin/mode_rules/close',
        json=request_body,
        headers=_REQUEST_HEADERS,
    )
    assert response.status_code == 200

    cursor = pgsql['driver_mode_subscription'].cursor()
    cursor.execute(
        'SELECT drafts FROM config.mode_rules '
        f'WHERE rule_id = \'{_RULE_ID1}\'::uuid;',
    )
    for row in cursor:
        assert row[0] == '{"(1,create)","(42,close)"}'
