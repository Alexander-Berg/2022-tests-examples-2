import pytest

TST_DOMAIN = 'taxi'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': TST_DOMAIN}

MODIFY_SHIFT_VIOLATIONS_URI = 'v1/operators/shift-violations/modify'


@pytest.mark.pgsql(
    'workforce_management',
    files=['allowed_periods.sql', 'simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid3',
                        'revision_id': '2020-06-26 00:00:00.0',
                        'type': 'test',
                        'start': '2010-10-21 12:00:00.0 +0000',
                        'duration_minutes': 60,
                        'description': 'test',
                        'shift_id': 9,
                    },
                ],
            },
            400,
        ),
        (
            {
                'shift_violations': [
                    {
                        'yandex_uid': 'uid3',
                        'revision_id': '2020-06-26 00:00:00.0',
                        'type': 'test',
                        'start': '2010-10-22 10:00:00.0 +0000',
                        'duration_minutes': 180,
                        'description': 'test',
                        'shift_id': 9,
                    },
                ],
            },
            400,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web, tst_request, expected_status,
):
    res = await taxi_workforce_management_web.post(
        MODIFY_SHIFT_VIOLATIONS_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
