import datetime

import pytest

from taxi.util import dates


def parse_and_make_step(provided_datetime: str, i: int):
    return dates.localize(
        dates.parse_timestring(provided_datetime)
        + datetime.timedelta(hours=i),
    ).isoformat()


SCHEDULE_INFO = {
    'expires_at': '2020-08-01T03:00:00+03:00',
    'record_id': 1,
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': {'schedule_type_id': 1},
    'starts_at': '2020-07-01T03:00:00+03:00',
    'secondary_skills': ['tatarin'],
    'skills': ['hokage', 'tatarin'],
    'schedule_offset': 0,
}
URI = 'v2/operators/shifts/values'
HEADERS = {'X-WFM-Domain': 'taxi'}
START = '2020-07-26T15:00:00+03:00'
SHIFT_ID = 1
SHIFT_RECORDS = [
    {
        'description': 'empty',
        'duration_minutes': 60,
        'frozen': bool(i % 2),
        'shift_id': i + 1,
        'skill': 'pokemon',
        'start': parse_and_make_step(START, i),
        'type': 'common',
    }
    for i in range(4)
]


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2'],
                'limit': 1,
                'offset': 0,
            },
            200,
            [
                {
                    'operator': {
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'schedules': [SCHEDULE_INFO],
                        'skills': ['hokage', 'tatarin'],
                        'tags': ['naruto'],
                        'yandex_uid': 'uid1',
                        'full_name': 'Abdullin Damir',
                        'mentor_login': 'supervisor@unit.test',
                        'phone': '111',
                        'state': 'ready',
                    },
                    'shifts': SHIFT_RECORDS,
                },
            ],
            2,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2'],
                'limit': 1,
                'offset': 1,
            },
            200,
            [
                {
                    'operator': {
                        'revision_id': '2020-08-26T22:00:00.000000 +0000',
                        'schedules': [
                            {
                                'record_id': 2,
                                'revision_id': (
                                    '2020-06-25T21:00:00.000000 +0000'
                                ),
                                'schedule_type_info': {'schedule_type_id': 2},
                                'starts_at': '2020-08-01T03:00:00+03:00',
                                'secondary_skills': ['pokemon'],
                                'skills': ['pokemon', 'tatarin'],
                                'schedule_offset': 0,
                            },
                        ],
                        'tags': ['naruto', 'driver'],
                        'yandex_uid': 'uid2',
                        'full_name': 'Gilgenberg Valeria',
                        'mentor_login': 'mentor@unit.test',
                        'state': 'ready',
                    },
                    'shifts': [
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 6,
                            'skill': 'pokemon',
                            'start': '2020-07-26T18:00:00+03:00',
                            'type': 'common',
                        },
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 5,
                            'skill': 'pokemon',
                            'start': '2020-07-26T19:00:00+03:00',
                            'type': 'common',
                        },
                    ],
                },
            ],
            2,
        ),
        (
            {
                'datetime_from': '2020-07-01 14:00:00.0 +0000',
                'datetime_to': '2020-09-01 18:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2'],
                'limit': 2,
                'offset': 1,
                'state': 'ready',
            },
            200,
            [
                {
                    'operator': {
                        'revision_id': '2020-08-26T22:00:00.000000 +0000',
                        'schedules': [
                            {
                                'record_id': 2,
                                'revision_id': (
                                    '2020-06-25T21:00:00.000000 +0000'
                                ),
                                'schedule_type_info': {'schedule_type_id': 2},
                                'starts_at': '2020-08-01T03:00:00+03:00',
                                'secondary_skills': ['pokemon'],
                                'skills': ['pokemon', 'tatarin'],
                                'schedule_offset': 0,
                            },
                        ],
                        'tags': ['naruto', 'driver'],
                        'yandex_uid': 'uid2',
                        'full_name': 'Gilgenberg Valeria',
                        'mentor_login': 'mentor@unit.test',
                        'state': 'ready',
                    },
                    'shifts': [
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 6,
                            'skill': 'pokemon',
                            'start': '2020-07-26T18:00:00+03:00',
                            'type': 'common',
                        },
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 5,
                            'skill': 'pokemon',
                            'start': '2020-07-26T19:00:00+03:00',
                            'type': 'common',
                        },
                    ],
                },
            ],
            2,
        ),
        (
            {
                'datetime_from': '2020-07-26 13:00:00.0 +0000',
                'datetime_to': '2020-07-26 15:00:00.0 +0000',
                'skill': 'pokemon',
            },
            400,
            None,
            None,
        ),
        (
            {
                'datetime_from': '2020-09-26 13:00:00.0 +0000',
                'datetime_to': '2020-09-26 15:00:00.0 +0000',
                'skill': 'tatarin',
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {
                    'operator': {
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'schedules': [],
                        'skills': ['hokage', 'tatarin'],
                        'tags': ['naruto'],
                        'yandex_uid': 'uid1',
                        'full_name': 'Abdullin Damir',
                        'mentor_login': 'supervisor@unit.test',
                        'phone': '111',
                        'state': 'ready',
                    },
                    'shifts': [],
                },
            ],
            1,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 18:00:00.0 +0000',
                'supervisors': ['aladin227'],
                'limit': 100,
                'offset': 0,
            },
            200,
            [
                {
                    'operator': {
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'schedules': [SCHEDULE_INFO],
                        'skills': ['hokage', 'tatarin'],
                        'tags': ['naruto'],
                        'yandex_uid': 'uid1',
                        'full_name': 'Abdullin Damir',
                        'mentor_login': 'supervisor@unit.test',
                        'phone': '111',
                        'state': 'ready',
                    },
                    'shifts': SHIFT_RECORDS,
                },
            ],
            1,
        ),
    ],
)
async def test_operators_shifts_values(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert data['records'] == expected_res
    assert data['full_count'] == expected_count


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'shifts_for_filtering.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'skill': 'hokage',
                'full_name': 'dullin',
                'multiskill': True,
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {
                    'operator': {
                        'full_name': 'Abdullin Damir',
                        'mentor_login': 'supervisor@unit.test',
                        'phone': '111',
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'schedules': [
                            {
                                'expires_at': '2020-08-01T03:00:00+03:00',
                                'record_id': 1,
                                'revision_id': (
                                    '2020-06-25T21:' '00:00.000000 +0000'
                                ),
                                'schedule_type_info': {'schedule_type_id': 1},
                                'starts_at': '2020-07-01T03:00:00+03:00',
                                'secondary_skills': ['tatarin'],
                                'skills': ['hokage', 'tatarin'],
                                'schedule_offset': 0,
                            },
                        ],
                        'skills': ['hokage', 'tatarin'],
                        'tags': ['naruto'],
                        'yandex_uid': 'uid1',
                        'state': 'ready',
                    },
                    'shifts': [
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 1,
                            'skill': 'hokage',
                            'start': '2020-07-26T15:00:00+03:00',
                            'type': 'common',
                        },
                    ],
                },
            ],
            1,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'state': 'deleted',
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {
                    'operator': {
                        'full_name': 'Deleted Deleted',
                        'mentor_login': 'admin@unit.test',
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'schedules': [],
                        'yandex_uid': 'uid5',
                        'state': 'deleted',
                    },
                    'shifts': [],
                },
            ],
            1,
        ),
    ],
)
async def test_v2_shifts_filtering(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert data['records'] == expected_res
    assert data['full_count'] == expected_count


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_sorting.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-26T14:00:00+03:00',
                    'datetime_to': '2020-07-26T16:00:00+03:00',
                    'sequence': ['starts', 'expires'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            ['uid1', 'uid2', 'uid3'],
            3,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-26 19:50:00.0 +0300',
                    'datetime_to': '2020-07-26 20:10:00.0 +0300',
                    'sequence': ['expires', 'starts'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            ['uid2', 'uid1', 'uid3'],
            3,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'sort_by_interval': {
                    'datetime_from': '2020-07-26 19:50:00.0 +0300',
                    'datetime_to': '2023-09-26 20:10:00.0 +0300',
                    'sequence': ['intersects', 'expires', 'starts'],
                },
                'limit': 10,
                'offset': 0,
            },
            200,
            ['uid2', 'uid3', 'uid1'],
            3,
        ),
    ],
)
async def test_operators_shifts_values_sorting(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert [
        row['operator']['yandex_uid'] for row in data['records']
    ] == expected_res
    assert data['full_count'] == expected_count


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators_without_skills.sql', 'simple_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'full_name': 'dullin',
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {
                    'operator': {
                        'full_name': 'Abdullin Damir',
                        'mentor_login': 'supervisor@unit.test',
                        'phone': '111',
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'schedules': [],
                        'yandex_uid': 'uid1',
                        'tags': ['naruto'],
                        'state': 'ready',
                    },
                    'shifts': [
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 1,
                            'skill': 'pokemon',
                            'start': '2020-07-26T15:00:00+03:00',
                            'type': 'common',
                        },
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': True,
                            'shift_id': 2,
                            'skill': 'pokemon',
                            'start': '2020-07-26T16:00:00+03:00',
                            'type': 'common',
                        },
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': False,
                            'shift_id': 3,
                            'skill': 'pokemon',
                            'start': '2020-07-26T17:00:00+03:00',
                            'type': 'common',
                        },
                        {
                            'description': 'empty',
                            'duration_minutes': 60,
                            'frozen': True,
                            'shift_id': 4,
                            'skill': 'pokemon',
                            'start': '2020-07-26T18:00:00+03:00',
                            'type': 'common',
                        },
                    ],
                },
            ],
            1,
        ),
    ],
)
async def test_operators_shifts_values_without_skills(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert data['records'] == expected_res
    assert data['full_count'] == expected_count
