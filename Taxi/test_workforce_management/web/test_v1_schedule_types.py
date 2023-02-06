import pytest

URI = 'v1/schedule/types'
HEADERS = {'X-WFM-Domain': 'taxi'}

FIRST_SCHEDULE = {
    'active': True,
    'duration_minutes': 720,
    'first_weekend': False,
    'schedule': [2, 2],
    'schedule_by_minutes': [720, 720, 720, 720, 2880],
    'revision_id': '2020-08-26T09:00:00.000000 +0000',
    'schedule_type_id': 1,
    'rotation_type': 'sequentially',
    'start': '12:00:00',
}
SECOND_SCHEDULE = {
    'active': True,
    'duration_minutes': 840,
    'first_weekend': False,
    'schedule': [5, 2],
    'schedule_by_minutes': [
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        2880,
    ],
    'schedule_alias': '5x2/10:00-00:00',
    'rotation_type': 'weekly',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedule_type_id': 2,
    'start': '10:00:00',
}
THIRD_SCHEDULE = {
    'active': True,
    'duration_minutes': 840,
    'first_weekend': False,
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedule': [5, 2],
    'schedule_by_minutes': [
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        2880,
    ],
    'schedule_alias': '5x2/10:00-00:00',
    'rotation_type': 'weekly',
    'schedule_type_id': 3,
    'start': '10:00:00',
}
FORTH_SCHEDULE = {
    'active': True,
    'duration_minutes': 840,
    'first_weekend': False,
    'revision_id': '2023-07-31T21:00:00.000000 +0000',
    'schedule': [5, 2],
    'schedule_by_minutes': [
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        2880,
    ],
    'schedule_alias': '5x2/10:00-00:00',
    'rotation_type': 'weekly',
    'schedule_type_id': 4,
    'start': '10:00:00',
}

FIFTH_SCHEDULE = {
    **FIRST_SCHEDULE,
    'schedule_type_id': 5,
    'properties': {'performance_standard': 480},
}

SIXTH_SCHEDULE = {
    **FIRST_SCHEDULE,
    'schedule_type_id': 6,
    'properties': {'performance_standard': 420},
    'offset_settings': [
        {'offset_alias': 'blablabla', 'oebs_alias': 'blabla', 'offset': 2},
    ],
}

ABNORMAL_FOR_OTHER_BUT_OK_HERE_SCHEDULE = {
    'active': True,
    'duration_minutes': 840,
    'first_weekend': False,
    'revision_id': '2023-07-31T21:00:00.000000 +0000',
    'rotation_type': 'weekly',
    'schedule': [5, 2],
    'schedule_alias': 'abnormal-schedule-in-response',
    'schedule_by_minutes': [
        0,
        660,
        600,
        840,
        600,
        840,
        600,
        840,
        600,
        840,
        3480,
        180,
    ],
    'schedule_type_id': 9999,
    'start': '21:00:00',
}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'extra_schedule_types.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        (
            {},
            200,
            {
                'schedule_types': [
                    SECOND_SCHEDULE,
                    THIRD_SCHEDULE,
                    FORTH_SCHEDULE,
                    ABNORMAL_FOR_OTHER_BUT_OK_HERE_SCHEDULE,
                    FIRST_SCHEDULE,
                    FIFTH_SCHEDULE,
                    SIXTH_SCHEDULE,
                ],
            },
        ),
        (
            {'durations_minutes': [720]},
            200,
            {
                'schedule_types': [
                    FIRST_SCHEDULE,
                    FIFTH_SCHEDULE,
                    SIXTH_SCHEDULE,
                ],
            },
        ),
        (
            {'schedule': [5, 2], 'starts': ['10:00:00']},
            200,
            {
                'schedule_types': [
                    SECOND_SCHEDULE,
                    THIRD_SCHEDULE,
                    FORTH_SCHEDULE,
                ],
            },
        ),
        (
            {'schedule': [5, 2], 'starts': ['09:00:00']},
            200,
            {'schedule_types': []},
        ),
        (
            {'schedule': [5, 2], 'starts': ['09:001']},
            400,
            {},
        ),  # wrong starts format
        (
            {
                'schedule': [5, 2],
                'starts': ['09:00:00'],
                'schedule_aliases': ['5x2/10:00-00:00'],
            },
            200,
            {'schedule_types': []},
        ),
        (
            {'schedule_aliases': ['5x2/10:00-00:00']},
            200,
            {
                'schedule_types': [
                    SECOND_SCHEDULE,
                    THIRD_SCHEDULE,
                    FORTH_SCHEDULE,
                ],
            },
        ),
        (
            {'schedule_aliases': ['5x2/10:00-00:00'], 'starts': ['10:00:00']},
            200,
            {
                'schedule_types': [
                    SECOND_SCHEDULE,
                    THIRD_SCHEDULE,
                    FORTH_SCHEDULE,
                ],
            },
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_res


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'extra_schedule_types.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {'id': 1}, 200, {'schedule_types': [FIRST_SCHEDULE]}, id='default',
        ),
        pytest.param(
            {'id': 100}, 200, {'schedule_types': []}, id='wrong_params',
        ),
        pytest.param({'id': 7}, 200, {'schedule_types': []}, id='broken_data'),
    ],
)
async def test_single(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_res,
):
    res = await taxi_workforce_management_web.get(
        URI, params=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_res
