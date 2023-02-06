import datetime

import psycopg2
import pytest


URI = 'v1/operator/shift/modify/check'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
REVISION_ID_UID2 = '2020-08-26T22:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-06-25T21:00:00.000000 +0000'
HEADERS = {
    'X-Yandex-UID': 'uid1',
    'X-WFM-Domain': 'taxi',
    'X-YaTaxi-Draft-Id': '1',
}


@pytest.mark.now('2009-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql', 'allowed_periods.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {
                'shift': {
                    'start': '2020-09-01T14:00:00+03:00',
                    'duration_minutes': 120,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': REVISION_ID,
                    },
                },
            },
            400,
            [],
            id='no_schedule',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2010-09-01T03:00:00+03:00',
                    'duration_minutes': 120,
                    'shift_id': 1,
                    'operator': {'shift_id': 1, 'yandex_uid': 'uid1'},
                },
            },
            400,
            [],
            id='outside_editing_period',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2020-08-26T15:00:00+03:00',
                    'duration_minutes': 30,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': REVISION_ID,
                    },
                },
            },
            200,
            [
                (
                    1,
                    1,
                    '1',
                    datetime.datetime(
                        2020,
                        8,
                        26,
                        15,
                        0,
                        tzinfo=psycopg2.tz.FixedOffsetTimezone(
                            offset=180, name=None,
                        ),
                    ),
                    30,
                    0,
                ),
            ],
            id='modify',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2020-07-26T16:00:00+03:00',
                    'duration_minutes': 30,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': REVISION_ID,
                    },
                },
            },
            400,
            [],
            id='wrong_start_intersects_with_another',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2020-09-01T03:00:00+03:00',
                    'duration_minutes': 120,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid5',
                        'revision_id': REVISION_ID,
                    },
                },
            },
            400,
            [],
            id='no_shifts_for_deleted_operator',
        ),
        pytest.param(
            {
                'shift': {
                    'start': '2020-09-01T03:00:00+03:00',
                    'duration_minutes': 120,
                    'shift_id': 1,
                    'operator': {
                        'yandex_uid': 'uid1',
                        'revision_id': WRONG_REVISION_ID,
                    },
                },
            },
            409,
            [],
            id='wrong_revision',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        mock_effrat_employees,
        pgsql,
):
    mock_effrat_employees()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status == 200:
        data = await res.json()
        if 'option' not in tst_request:
            tst_request['option'] = 'save_provided'
        assert data == {
            'data': tst_request,
            'change_doc_id': str(tst_request['shift']['shift_id']),
        }

    cursor = pgsql['workforce_management'].cursor()
    cursor.execute(
        """
        SELECT unique_operator_id, shift_id, draft_id, start,
            duration_minutes, status
        FROM callcenter_operators.operators_shifts_drafts""",
    )
    result = list(row for row in cursor)

    assert result == expected_res
