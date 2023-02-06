#  pylint:disable=C0302
import datetime
import typing as tp

import pytest

from workforce_management.common import constants
from workforce_management.storage.postgresql import (
    actual_shifts as actual_shifts_repo,
)
from . import util

URI = 'v1/operators/shift/modify'
GET_URI = 'v2/shifts/values'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
REVISION_ID_UID2 = '2020-08-26T22:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len, expected_schedule_id',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 11:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
            id='no_schedule',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2010-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
            id='outside_editing_period',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 12:00:00.0 +0000',
                        'duration_minutes': 30,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': (
                                    constants.ShiftTypes.additional.value
                                ),
                                'description': 'some description',
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            4,
            id='modify',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 16:00:00.0 +0000',
                        'duration_minutes': 30,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 5,
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID_UID2,
                                'type': (
                                    constants.ShiftTypes.additional.value
                                ),
                                'description': 'some description',
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            2,
            id='modify_type_description',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 13:00:00.0 +0000',
                        'duration_minutes': 30,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                            },
                        ],
                    },
                ],
            },
            400,
            1,
            1,
            id='wrong_start',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'hokage',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid5',
                                'revision_id': REVISION_ID,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
            id='no_schedules_for_deleted_operator',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': WRONG_REVISION_ID,
                            },
                        ],
                    },
                ],
            },
            409,
            None,
            None,
            id='wrong_revision',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 13:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 2,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            1,
            id='intersection',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 13:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 2,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            1,
            id='frozen',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 12:00:00.0 +0000',
                        'duration_minutes': 30,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': (
                                    constants.ShiftTypes.additional.value
                                ),
                                'description': 'some description',
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            4,
            id='delete_violation',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['simple_shift_violations.sql'],
                ),
            ],
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res_len,
        expected_schedule_id,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False
    else:
        data = await res.json()
        assert len(data['new_shifts']) == expected_res_len
    await util.check_shifts(
        taxi_workforce_management_web=taxi_workforce_management_web,
        tst_request=tst_request,
        success=success,
        expected_schedule_id=expected_schedule_id,
    )


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_with_breaks.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len, expected_schedule_id',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'events': [
                                    {
                                        'event_id': 0,
                                        'start': '2020-07-26 12:00:00.0 +0000',
                                        'duration_minutes': 60,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            1,
            id='0',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'events': [],
                            },
                        ],
                    },
                ],
            },
            200,
            0,
            1,
            id='1',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'events': [
                                    {
                                        'event_id': 0,
                                        'start': '2020-09-02 23:00:00.0 +0000',
                                        'duration_minutes': 60,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
            id='event_outside_shift',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-09-01 00:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'events': [
                                    {
                                        'event_id': 0,
                                        'start': '2020-09-01 00:00:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                    {
                                        'event_id': 0,
                                        'start': '2020-09-01 00:05:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            None,
            id='intersects',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-10 00:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'droid',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'events': [
                                    {
                                        'event_id': 0,
                                        'start': '2020-07-10 00:00:00.0 +0000',
                                        'duration_minutes': 60,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            1,
            4,
            id='event_and_spread_breaks',
        ),
    ],
)
async def test_events(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res_len,
        expected_schedule_id,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    await util.check_shifts(
        taxi_workforce_management_web=taxi_workforce_management_web,
        tst_request=tst_request,
        success=success,
        check_events_on_success=lambda actual_events: len(actual_events)
        == expected_res_len,
        expected_schedule_id=expected_schedule_id,
        check_schedule_type_id=False,
    )


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_with_segments.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'segments': [
                                    {
                                        'start': '2020-07-26 12:00:00.0 +0000',
                                        'duration_minutes': 60,
                                        'skill': 'pokemon',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            id='replace_segments_with_provided',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'segments': [],
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                            },
                        ],
                    },
                ],
            },
            200,
            0,
            id='make_multiskill_shift_singleskill',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'operators': [
                            {
                                'shift_id': 0,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'segments': [
                                    {
                                        'id': 0,
                                        'start': '2020-07-26 12:00:00.0 +0000',
                                        'duration_minutes': 60,
                                        'skill': 'pokemon',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            id='change_segment_duration_and_remove_one',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID_UID2,
                                'segments': [
                                    {
                                        'start': '2020-08-26 12:00:00.0 +0000',
                                        'duration_minutes': 60,
                                        'skill': 'pokemon',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            id='make_singleskill_shift_multiskill',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID,
                                'segments': [
                                    {
                                        'start': '2020-08-26 12:00:00.0 +0000',
                                        'duration_minutes': 60,
                                        'skill': 'pokemon',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            id='shift_single_and_multi_at_the_same_time',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-15 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'operators': [
                            {
                                'shift_id': 0,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'segments': [
                                    {
                                        'id': 0,
                                        'start': '2020-07-15 12:00:00.0 +0000',
                                        'duration_minutes': 30,
                                        'skill': 'pokemon',
                                    },
                                    {
                                        'id': 1,
                                        'start': '2020-07-15 12:30:00.0 +0000',
                                        'duration_minutes': 30,
                                        'skill': 'pokemon',
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'option': 'spread_new',
            },
            200,
            2,
            id='change_segment_duration_and_remove_one_spread_breaks',
        ),
    ],
)
async def test_segments(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res_len,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    await util.check_shifts(
        taxi_workforce_management_web=taxi_workforce_management_web,
        tst_request=tst_request,
        success=success,
        check_segments_on_success=lambda actual_segments: len(actual_segments)
        == expected_res_len,
        check_schedule_type_id=False,
    )


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_breaks.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res_len',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-07-26 12:00:00.0 +0000',
                                        'duration_minutes': 60,
                                    },
                                    {
                                        'id': 1,
                                        'type': 'technical',
                                        'start': '2020-07-26 12:00:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            400,
            1,
            id='break intersects existing one',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-07-26 12:30:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            1,
            id='create_break',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-07-26 12:30:00.0 +0000',
                                        'duration_minutes': 40,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            400,
            1,
            id='break_outside_shift',
        ),
    ],
)
async def test_breaks(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res_len,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    await util.check_shifts(
        taxi_workforce_management_web=taxi_workforce_management_web,
        tst_request=tst_request,
        success=success,
        check_breaks_on_success=lambda actual_events: len(actual_events)
        == expected_res_len,
        check_schedule_type_id=False,
    )


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_with_many_breaks.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_breaks_count',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 120,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [
                                    {
                                        'id': 2,
                                        'type': 'technical',
                                        'start': '2020-07-26 12:30:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                    {
                                        'id': 3,
                                        'type': 'technical',
                                        'start': '2020-07-26 13:00:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                    {
                                        'id': 4,
                                        'type': 'technical',
                                        'start': '2020-07-26 13:30:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            3,
            id='modify_breaks',
        ),
    ],
)
async def test_breaks_deleting(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_breaks_count,
        mock_effrat_employees,
        pgsql,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    data = await res.json()
    assert data

    if expected_status > 200:
        return

    res = await taxi_workforce_management_web.post(
        GET_URI,
        json={
            'skill': tst_request['shifts'][0]['skill'],
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 10,
        },
        headers=HEADERS,
    )
    data = await res.json()
    breaks = data['records'][0]['shift']['breaks']
    assert len(breaks) == expected_breaks_count


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_with_breaks.sql',
        'simple_break_rules.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_breaks_count',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 30,
                        'skill': 'droid',
                        'operators': [
                            {
                                'shift_id': 0,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            400,
            None,
            id='too_short_no_break_rules',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 110,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            1,
            id='spread_breaks',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-29 12:00:00.0 +0000',
                        'duration_minutes': 180,
                        'skill': 'droid',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'events': [
                                    {
                                        'event_id': 1,
                                        'start': '2020-07-29 12:00:00.0 +0000',
                                        'duration_minutes': 120,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            3,
            id='event_with_breaks',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-28 12:00:00.0 +0000',
                        'duration_minutes': 180,
                        'skill': 'droid',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'events': [
                                    {
                                        'event_id': 1,
                                        'start': '2020-07-28 12:00:00.0 +0000',
                                        'duration_minutes': 120,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            3,
            id='event_with_breaks',
        ),
    ],
)
async def test_breaks_spreading(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_breaks_count,
        mock_effrat_employees,
        pgsql,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    data = await res.json()
    assert data

    if expected_status > 200:
        return

    res = await taxi_workforce_management_web.post(
        GET_URI,
        json={
            'skill': tst_request['shifts'][0]['skill'],
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 10,
        },
        headers=HEADERS,
    )
    data = await res.json()
    breaks = data['records'][0]['shift']['breaks']
    assert len(breaks) == expected_breaks_count


FIRST_BREAK = {
    'start': '2020-07-26T15:00:00+03:00',
    'duration_minutes': 30,
    'type': 'technical',
}
SECOND_BREAK = {
    'start': '2020-07-26T15:30:00+03:00',
    'duration_minutes': 30,
    'type': 'technical',
}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_breaks.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_breaks',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 45,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                            },
                        ],
                    },
                ],
            },
            400,
            [FIRST_BREAK, SECOND_BREAK],
            id='break outside shift',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID_UID2,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 1,
                                'breaks': [
                                    {
                                        'start': '2020-08-26T15:30:00+03:00',
                                        'duration_minutes': 30,
                                        'type': 'technical',
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            [
                {
                    'start': '2020-08-26T15:30:00+03:00',
                    'duration_minutes': 30,
                    'type': 'technical',
                },
            ],
            id='break outside shift',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 11:59:00.0 +0000',
                        'duration_minutes': 45,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                            },
                        ],
                    },
                ],
                'option': 'leave_as_is',
            },
            200,
            [FIRST_BREAK],
            id='last break removed',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [FIRST_BREAK],
                            },
                        ],
                    },
                ],
                'option': 'save_provided',
            },
            200,
            [FIRST_BREAK],
            id='save_provided',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 45,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [FIRST_BREAK],
                            },
                        ],
                    },
                ],
                'option': 'remove_all',
            },
            200,
            None,
            id='remove_all',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-28 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'shift_id': 0,
                                'breaks': [
                                    {
                                        'id': 1,
                                        'start': '2020-07-28T15:00:00+03:00',
                                        'duration_minutes': 30,
                                        'type': 'technical',
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'option': 'save_provided',
            },
            200,
            [
                {
                    'start': '2020-07-28T15:00:00+03:00',
                    'duration_minutes': 30,
                    'type': 'technical',
                },
            ],
            id='start_is_changed_and_breaks_are_saved',
        ),
    ],
)
async def test_options(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_breaks,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    res = await taxi_workforce_management_web.post(
        GET_URI,
        json={
            'skill': tst_request['shifts'][0]['skill'],
            'yandex_uids': [
                tst_request['shifts'][0]['operators'][0]['yandex_uid'],
            ],
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 10,
        },
        headers=HEADERS,
    )
    data = await res.json()
    breaks = data['records'][0]['shift'].get('breaks')
    assert pop_break_id(breaks) == expected_breaks


def pop_break_id(breaks: tp.List[tp.Dict]):
    for break_ in breaks or []:
        break_.pop('id')
    return breaks


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'extra_schedule.sql',
        'simple_break_rules.sql',
        'extra_shifts_with_breaks.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_notify',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 15:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 6,
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID_UID2,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
            },
            400,
            None,
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='shift_without_schedule',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-29 12:00:00.0 +0000',
                        'duration_minutes': 45,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'events': [
                                    {
                                        'event_id': 0,
                                        'start': '2020-07-29 12:00:00.0 +0000',
                                        'duration_minutes': 30,
                                        'description': (
                                            'test notification on events'
                                        ),
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            {'messages': {'uid1': [{'message_key': 'new_shifts'}]}},
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='modified_events',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-29 12:00:00.0 +0000',
                        'duration_minutes': 45,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
            },
            200,
            {'messages': {'uid1': [{'message_key': 'new_shifts'}]}},
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='modified_shift',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-29 12:00:00.0 +0000',
                        'duration_minutes': 90,
                        'skill': 'order',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'events': [
                                    {
                                        'event_id': 0,
                                        'start': '2020-07-29 12:00:00.0 +0000',
                                        'duration_minutes': 30,
                                        'description': (
                                            '1 shift = 1 notification'
                                        ),
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            200,
            {'messages': {'uid1': [{'message_key': 'new_shifts'}]}},
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='shift_and_events',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            {'messages': {'uid1': [{'message_key': 'new_breaks'}]}},
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='spread_breaks',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-07-26 12:30:00.0 +0000',
                                        'duration_minutes': 10,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'option': 'save_provided',
            },
            200,
            {'messages': {'uid1': [{'message_key': 'new_breaks'}]}},
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='one_new_break',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-26 11:45:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 1,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            {
                'messages': {
                    'uid1': [
                        {'message_key': 'new_shifts'},
                        {'message_key': 'new_breaks'},
                    ],
                },
            },
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='shift_and_break',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 10,
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID_UID2,
                                'type': constants.ShiftTypes.common.value,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-08-26 12:30:00.0 +0000',
                                        'duration_minutes': 15,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'option': 'leave_as_is',
            },
            200,
            {'messages': {'uid2': [{'message_key': 'new_shifts'}]}},
            marks=pytest.mark.now('2020-08-26T12:30:40'),
            id='1_old_break',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-27 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 11,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-07-27 12:30:00.0 +0000',
                                        'duration_minutes': 15,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            None,
            marks=pytest.mark.now('2020-07-26T12:30:40'),
            id='not_current_shift',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-08-26 11:30:00.0 +0000',
                        'duration_minutes': 60,
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 10,
                                'yandex_uid': 'uid2',
                                'revision_id': REVISION_ID_UID2,
                                'type': constants.ShiftTypes.common.value,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2020-08-26 12:00:00.0 +0000',
                                        'duration_minutes': 15,
                                    },
                                ],
                            },
                        ],
                    },
                ],
                'spread_breaks': True,
            },
            200,
            None,
            marks=pytest.mark.now('2020-09-26T12:30:40'),
            id='old_shift_is_modified',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        'start': '2020-07-28 04:00:00.0 +0000',
                        'duration_minutes': 480,  # from 600
                        'skill': 'pokemon',
                        'operators': [
                            {
                                'shift_id': 12,
                                'yandex_uid': 'uid1',
                                'revision_id': REVISION_ID,
                                'type': constants.ShiftTypes.common.value,
                                'breaks': [
                                    {
                                        'type': 'technical',
                                        'start': '2021-06-29T05:30:00.0 +0000',
                                        'duration_minutes': 15,
                                    },
                                    {
                                        'type': 'lunchtime',
                                        'start': '2021-06-29T07:30:00.0 +0000',
                                        'duration_minutes': 30,
                                    },
                                    {
                                        'type': 'technical',
                                        'start': '2021-06-29T09:45:00.0 +0000',
                                        'duration_minutes': 15,
                                    },
                                    {
                                        'type': 'technical',
                                        'start': '2021-06-29T11:15:00.0 +0000',
                                        'duration_minutes': 15,
                                    },
                                    {
                                        'type': 'technical',
                                        'start': '2021-06-29T13:30:00.0 +0000',
                                        'duration_minutes': 15,
                                    },  # shrunk break
                                ],
                            },
                        ],
                    },
                ],
                'option': 'leave_as_is',
            },
            200,
            {
                'messages': {'uid1': [{'message_key': 'new_shifts'}]},
            },  # no need for message about shrunk break
            marks=pytest.mark.now('2020-07-28T12:50:00'),
            id='shrink_current_shift',
        ),  # shift has shrunk and now it is not current
    ],
)
async def test_trigger_telegram_change_shift(
        taxi_workforce_management_web,
        web_context,
        mock_effrat_employees,
        stq,
        tst_request,
        expected_status,
        expected_notify,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    notify = {'messages': {}}

    def merge_messages(update):
        for uid, messages in update['messages'].items():
            if uid in notify['messages']:
                notify['messages'][uid].extend(messages)
            else:
                notify['messages'][uid] = messages

    if not expected_notify:
        assert not stq.workforce_management_bot_sending.times_called
    else:
        count = sum(
            len(messages)
            for uid, messages in expected_notify['messages'].items()
        )
        for _ in range(count):
            new_notify = stq.workforce_management_bot_sending.next_call()[
                'kwargs'
            ]
            merge_messages(new_notify)
        assert notify == expected_notify


OPERATOR_1: tp.Dict = {
    'shift_id': 1,
    'yandex_uid': 'uid1',
    'revision_id': REVISION_ID,
}
SHIFT_1: tp.Dict = {
    'start': '2020-07-26 12:00:00.0 +0000',
    'duration_minutes': 60,
    'skill': 'pokemon',
}


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_break_rules.sql',
        'simple_shift_violations.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {
                'shifts': [
                    {
                        **SHIFT_1,
                        'operators': [{**OPERATOR_1, 'description': 'test'}],
                    },
                ],
                'option': 'leave_as_is',
            },
            200,
            [1],
            id='update_description',
        ),
        pytest.param(
            {
                'shifts': [
                    {
                        **SHIFT_1,
                        'duration_minutes': 45,
                        'operators': [OPERATOR_1],
                    },
                ],
                'option': 'leave_as_is',
            },
            200,
            [],
            id='update_range',
        ),
        pytest.param(
            {
                'shifts': [{**SHIFT_1, 'operators': [OPERATOR_1]}],
                'option': 'spread_new',
            },
            200,
            [],
            id='update_breaks',
        ),
    ],
)
async def test_shift_violations(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        mock_effrat_employees,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    actual_shifts_db = actual_shifts_repo.ActualShiftsRepo(web_context)
    async with actual_shifts_db.master.acquire() as conn:
        res = await actual_shifts_db.get_operators_shift_violations(
            conn,
            datetime_from=datetime.datetime(2020, 1, 1),
            datetime_to=datetime.datetime(2023, 1, 1),
            yandex_uids=['uid1'],
        )
    assert [record['id'] for record in res] == expected_res
