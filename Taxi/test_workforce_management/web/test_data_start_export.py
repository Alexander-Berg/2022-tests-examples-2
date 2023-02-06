import pytest


JOB_SET_URI = 'v1/data/start-export'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.parametrize(
    'tst_request, expected_kwargs',
    [
        (
            {
                'data_to_export': 'quality_control_timetable',
                'filter': {
                    'timetable': {
                        'datetime_from': '2020-01-01T00:00:00Z',
                        'datetime_to': '2022-01-01T00:00:00Z',
                        'skill': 'order',
                        'limit': 5000,
                        'offset': 0,
                    },
                },
            },
            {
                'datetime_from': None,
                'datetime_to': None,
                'extra': {
                    'author_yandex_uid': 'uid1',
                    'datetime_from': '2020-01-01T03:00:00+03:00',
                    'datetime_to': '2022-01-01T03:00:00+03:00',
                    'domain': 'taxi',
                    'limit': 5000,
                    'load_entities': [
                        'shifts',
                        'shift_breaks',
                        'shift_events',
                        'absences',
                    ],
                    'offset': 0,
                    'skill': 'order',
                },
                'job_type': 'csv/timetable/quality_control_timetable',
                'ttl_time': None,
                'skill': None,
            },
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        tst_request,
        expected_kwargs,
        mock_effrat_employees,
        stq,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        JOB_SET_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()
    assert data

    task = stq.workforce_management_setup_jobs.next_call()
    assert task['kwargs'] == expected_kwargs
