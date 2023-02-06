import pytest

URI = 'v1/operators/dashboards/violations/values'
STATS_URI = 'v1/operators/dashboards/violations/stats'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.now('2020-07-26 18:00:00.0 +0000')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'dashboard_operators.sql',
        'dashboard_shifts.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_stats',
    [
        pytest.param(
            {
                'datetime_from': '2020-01-01 00:00:00.0 +0000',
                'datetime_to': '2023-09-01 00:00:00.0 +0000',
                'skill': 'pokemon',
                'limit': 50,
                'offset': 0,
            },
            200,
            [
                {'absences': [0, 1], 'shifts': [1, 2], 'uid': 'uid1'},
                {'absences': [2], 'shifts': [3], 'uid': 'uid2'},
            ],
            {'not_working': 1, 'absent': 1, 'late': 1},
            id='usual',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-26 13:00:00.0 +0000',
                'datetime_to': '2020-07-28 13:00:00.0 +0000',
                'skill': 'pokemon',
                'limit': 50,
                'offset': 0,
            },
            200,
            [
                {'absences': [0, 1], 'shifts': [2], 'uid': 'uid1'},
                {'absences': [2], 'shifts': [3], 'uid': 'uid2'},
            ],
            {'not_working': 1, 'absent': 1, 'late': 1},
            id='same_start',
        ),
        pytest.param(
            {
                'datetime_from': '2020-01-01 00:00:00.0 +0000',
                'datetime_to': '2023-09-01 00:00:00.0 +0000',
                'skill': 'pokemon',
                'limit': 50,
                'offset': 0,
                'yandex_uids': ['uid1'],
            },
            200,
            [{'absences': [0, 1], 'shifts': [1, 2], 'uid': 'uid1'}],
            {'not_working': 1, 'late': 1},
            id='yandex_uid',
        ),
        pytest.param(
            {
                'datetime_from': '2020-01-01 00:00:00.0 +0000',
                'datetime_to': '2023-09-01 00:00:00.0 +0000',
                'skill': 'pokemon',
                'limit': 50,
                'offset': 0,
                'shift_violation_filter': {
                    'shift_violation_types': ['absent', 'late'],
                    'datetime_from': '2020-07-26 13:30:00.0 +0000',
                    'datetime_to': '2020-07-26 13:45:00.0 +0000',
                },
            },
            200,
            [{'absences': [2], 'shifts': [3], 'uid': 'uid2'}],
            {'absent': 1},
            id='violations_filter',
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_stats,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    dashboard_data = await res.json()

    assert prepare_response(dashboard_data) == expected_res

    res = await taxi_workforce_management_web.post(
        STATS_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    dashboard_stats = await res.json()
    stats = {row['name']: row['value'] for row in dashboard_stats['stats']}
    assert stats == expected_stats


def prepare_response(data):
    return [
        {
            'uid': row['operator']['yandex_uid'],
            'shifts': [shift['shift_id'] for shift in row['shifts']],
            'absences': [absence['id'] for absence in row['absences']],
        }
        for row in data['records']
    ]
