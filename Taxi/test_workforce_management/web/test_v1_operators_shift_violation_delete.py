import pytest

from taxi.util import dates

from workforce_management.storage.postgresql import (
    actual_shifts as actual_shifts_repo,
)


URI = 'v1/operators/shift-violations/delete'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_shift_violations.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, revision',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-26 11:59:00+00',
                'datetime_to': '2020-07-26 13:00:00+00',
                'yandex_uids': ['uid1'],
            },
            200,
            REVISION_ID,
            id='delete',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-26 11:59:00+00',
                'datetime_to': '2020-07-26 13:00:00+00',
                'yandex_uids': ['uid1'],
            },
            409,
            WRONG_REVISION_ID,
            id='wrong_operator_revision',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        revision,
):
    actual_shifts_db = actual_shifts_repo.ActualShiftsRepo(web_context)
    master_pool = await actual_shifts_db.master

    tst_request.update(
        dict(
            datetime_from=dates.parse_timestring_aware(
                tst_request['datetime_from'], 'UTC',
            ),
            datetime_to=dates.parse_timestring_aware(
                tst_request['datetime_to'], 'UTC',
            ),
        ),
    )

    async with master_pool.acquire() as conn:
        res = await actual_shifts_db.get_operators_shift_violations(
            conn, **tst_request,
        )

    shift_violations = [
        {'id': shift_violation['id'], 'revision_id': revision}
        for shift_violation in res
    ]

    res = await taxi_workforce_management_web.post(
        URI, json={'shift_violations': shift_violations}, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    async with master_pool.acquire() as conn:
        violation_ids = [record['id'] for record in shift_violations]
        res = await actual_shifts_db.get_deleted_operators_shift_violations(
            conn, violation_ids,
        )
        assert res and success or not (res or success)
