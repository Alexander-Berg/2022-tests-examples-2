import datetime as dt

import pytest

from taxi.util import dates

from workforce_management.storage.postgresql import (
    actual_shifts as actual_shifts_repo,
)

URI = 'v1/operators/shift-violations/modify'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_shift_violations.sql',
        'allowed_periods.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        pytest.param(
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T02:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'new',
                        'shift_id': 1,
                    },
                ],
            },
            200,
            id='new',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2010-09-26T02:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'new',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='outside_editing_period',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T02:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'new_late',
                        'shift_id': 1,
                    },
                    {
                        'yandex_uid': 'uid1',
                        'type': 'absent',
                        'duration_minutes': 250.0,
                        'start': '2020-07-26T03:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'new_absence',
                        'shift_id': 1,
                    },
                ],
            },
            200,
            id='new_bulk',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T12:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'intersects',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='intersects',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid1',
                        'type': 'abcdef',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T12:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'intersects',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='wrong_type',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T00:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'modify',
                        'shift_id': 1,
                    },
                ],
            },
            200,
            id='modify',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T00:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'modify1',
                        'shift_id': 1,
                    },
                    {
                        'id': 2,
                        'yandex_uid': 'uid1',
                        'type': 'absent',
                        'duration_minutes': 250.0,
                        'start': '2020-07-26T01:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'modify2',
                        'shift_id': 1,
                    },
                ],
            },
            200,
            id='modify_bulk',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T18:00:00.0 +0000',
                        'revision_id': WRONG_REVISION_ID,
                        'description': 'wrong_revision',
                        'shift_id': 1,
                    },
                ],
            },
            409,
            id='wrong_operator_revision',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': -1,
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T12:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'intersects',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='wrong_id',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'revision_id': REVISION_ID,
                        'description': 'modify',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='missing_allowed_periods',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid1',
                        'type': 'late',
                        'revision_id': REVISION_ID,
                        'description': 'modify',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='missing_fields_for_new',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'type': 'late',
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T00:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'description': 'modify',
                        'shift_id': 1,
                    },
                ],
            },
            400,
            id='revision_missing_yandex_uid',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'duration_minutes': 30.0,
                        'start': '2020-07-26T00:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'yandex_uid': 'uid1',
                    },
                ],
            },
            200,
            id='modify_required_fields',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'id': 1,
                        'description': 'test',
                        'start': '2020-07-26T00:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'yandex_uid': 'uid1',
                    },
                ],
            },
            200,
            id='optional_duration',
        ),
        pytest.param(
            {
                'shift_violations': [
                    {
                        'description': 'test',
                        'start': '2020-07-26T00:00:00.0 +0000',
                        'revision_id': REVISION_ID,
                        'yandex_uid': 'uid1',
                    },
                ],
            },
            400,
            id='required_duration',
        ),
    ],
)
async def test_shift_violations_modify(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = expected_status <= 200
    if success:
        await check_shift_violations(tst_request, web_context)


async def check_shift_violations(tst_request, web_context):
    actual_shifts_db = actual_shifts_repo.ActualShiftsRepo(web_context)
    master_pool = await actual_shifts_db.master
    async with master_pool.acquire() as conn:
        res = await actual_shifts_db.get_operators_shift_violations(
            conn,
            datetime_from=dt.datetime(
                2020, 7, 26, 0, 0, tzinfo=dt.timezone.utc,
            ),
            datetime_to=dt.datetime(
                2020, 7, 26, 21, 0, tzinfo=dt.timezone.utc,
            ),
        )
    for requested, saved in zip(tst_request['shift_violations'], res):
        requested.pop('revision_id', None)
        type_ = requested.pop('type', None)
        if type_:
            requested['state_type'] = type_
        requested['start'] = dates.parse_timestring_aware(requested['start'])
        for field in requested.keys():
            assert requested[field] == saved[field]
