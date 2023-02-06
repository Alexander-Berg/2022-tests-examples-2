import datetime as dt

import pytest

from taxi.util import dates

URI = 'v1/operator/shift-violations/values'
HEADERS = {'X-WFM-Domain': 'taxi'}
WRONG_DOMAIN_HEADERS = {'X-WFM-Domain': 'uber'}


START = dates.localize(
    dt.datetime(2020, 7, 26, 12, 0, 0, 0, tzinfo=dt.timezone.utc),
)


def add_minutes(minutes: float):
    return START + dt.timedelta(minutes=minutes)


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_shift_violations.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, tst_headers, expected_status, expected_res',
    [
        pytest.param(
            {
                'yandex_uid': 'uid1',
                'datetime_from': add_minutes(0),
                'datetime_to': add_minutes(120),
            },
            HEADERS,
            200,
            {
                'shift_violations': [
                    {
                        'duration_minutes': 60,
                        'id': 1,
                        'shift_id': 1,
                        'start': add_minutes(0).isoformat(),
                        'type': 'late',
                        'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
                    },
                    {
                        'duration_minutes': 60,
                        'id': 2,
                        'shift_id': 2,
                        'start': add_minutes(60).isoformat(),
                        'type': 'late',
                        'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
                    },
                ],
            },
            id='default',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid0',
                'datetime_from': add_minutes(0),
                'datetime_to': add_minutes(120),
            },
            HEADERS,
            404,
            None,
            id='wrong_uid',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid1',
                'datetime_from': add_minutes(0),
                'datetime_to': add_minutes(120),
            },
            WRONG_DOMAIN_HEADERS,
            404,
            None,
            id='wrong_domain',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid3',
                'datetime_from': add_minutes(0),
                'datetime_to': add_minutes(120),
            },
            HEADERS,
            200,
            {
                'shift_violations': [
                    {
                        'duration_minutes': 720,
                        'id': 7,
                        'shift_id': 7,
                        'start': add_minutes(0).isoformat(),
                        'type': 'absent',
                        'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
                    },
                ],
            },
            id='current_violation',
        ),
    ],
)
async def test_operator_shift_violations_values(
        taxi_workforce_management_web,
        mock_effrat_employees,
        web_context,
        tst_request,
        tst_headers,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.get(
        URI, params=tst_request, headers=tst_headers,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    data = await res.json()

    assert data == expected_res
