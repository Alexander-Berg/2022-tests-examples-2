import pytest

OPERATORS_LIST_CHANGES = [
    {
        'departments': ['1'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia', 'nokia2'],
        'source': 'taxi',
        'yandex_uid': 'uid1',
        'employee_uid': '00000000-0000-0000-0000-000000000001',
        'login': 'abd-damir',
        'full_name': 'Abdullin Damir',
        'supervisor_login': 'aladin227',
        'mentor_login': 'supervisor@unit.test',
        'phone_pd_id': '111',
        'tags': ['naruto'],
    },
    {
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'departments': ['999'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['iphone', 'iphone2'],
        'source': 'taxi',
        'yandex_uid': 'uid3',
        'employee_uid': '00000000-0000-0000-0000-000000000003',
        'login': 'tatarstan',
        'full_name': 'Minihanov Minihanov',
        'supervisor_login': 'abd-damir',
        'mentor_login': 'supervisor@unit.test',
        'telegram_login_pd_id': 'morozhenka',
    },
]
URI = 'v2/operators/free/values'
FIRST_SCHEDULE_TYPE = {
    'duration_minutes': 720,
    'first_weekend': False,
    'revision_id': '2020-08-26T09:00:00.000000 +0000',
    'schedule': [2, 2],
    'schedule_type_id': 1,
    'start': '12:00:00',
}
SECOND_SCHEDULE_TYPE = {
    'duration_minutes': 840,
    'first_weekend': False,
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedule_alias': '5x2/10:00-00:00',
    'schedule': [5, 2],
    'schedule_type_id': 2,
    'start': '10:00:00',
}
FIRST_AUDIT = {'updated_at': '2020-06-26T00:00:00+03:00'}
FIRST_OPERATOR = {
    'yandex_uid': 'uid1',
    'callcenter_id': '1',
    'full_name': 'Abdullin Damir',
    'phone': '111',
    'mentor_login': 'supervisor@unit.test',
    'employment_date': '2020-07-21',
    'state': 'ready',
    'login': 'abd-damir',
    'roles': [],
    'role_in_telephony': 'nokia',
    'supervisor_login': 'aladin227',
    'schedules': [
        {
            'expires_at': '2020-08-01T03:00:00+03:00',
            'record_id': 1,
            'revision_id': '2020-06-25T21:00:00.000000 +0000',
            'schedule_type_info': FIRST_SCHEDULE_TYPE,
            'starts_at': '2020-07-01T03:00:00+03:00',
            'skills': ['droid', 'pokemon', 'tatarin'],
            'secondary_skills': ['pokemon'],
            'audit': FIRST_AUDIT,
            'schedule_offset': 0,
        },
    ],
    'skills': ['droid', 'pokemon', 'tatarin'],
    'tags': ['naruto'],
    'rate': 0.5,
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
}
THIRD_OPERATOR = {
    'callcenter_id': '999',
    'mentor_login': 'supervisor@unit.test',
    'employment_date': '2020-07-21',
    'full_name': 'Minihanov Minihanov',
    'state': 'ready',
    'login': 'tatarstan',
    'roles': [],
    'role_in_telephony': 'iphone',
    'yandex_uid': 'uid3',
    'supervisor_login': 'abd-damir',
    'telegram': 'morozhenka',
    'schedules': [
        {
            'record_id': 2,
            'revision_id': '2020-06-25T21:00:00.000000 +0000',
            'schedule_type_info': SECOND_SCHEDULE_TYPE,
            'starts_at': '2020-07-10T03:00:00+03:00',
            'skills': ['pokemon', 'tatarin'],
            'secondary_skills': [],
            'audit': FIRST_AUDIT,
            'schedule_offset': 0,
        },
    ],
    'supervisor': {
        'full_name': 'Abdullin Damir',
        'login': 'abd-damir',
        'yandex_uid': 'uid1',
        'state': 'ready',
    },
    'rate': 1.0,
    'skills': ['pokemon', 'tatarin'],
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
}
HEADERS = {'X-WFM-Domain': 'taxi'}


@pytest.mark.now('2020-07-25T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_free_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {
                'skill': 'droid',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'login': 'bd-',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'login': 'tatarsta',
                'tag_filter': {'tags': ['naruto']},
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR, THIRD_OPERATOR], 'full_count': 2},
        ),
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'limit': 1,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR], 'full_count': 2},
        ),
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'limit': 1,
                'offset': 1,
            },
            200,
            {'operators': [THIRD_OPERATOR], 'full_count': 2},
        ),
        (
            {
                'skill': 'pokemon',
                'state': 'deleted',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
        (
            {
                'skill': 'droid',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '2020-08-01T01:00:00.0Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2020-07-21 00:00:00Z',
                'datetime_to': '2020-07-31 00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR, THIRD_OPERATOR], 'full_count': 2},
        ),
        (
            {
                'skill': 'pokemon',
                'supervisors': ['aladin227'],
                'datetime_from': '2020-07-21 00:00:00Z',
                'datetime_to': '2020-07-31 00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'skill': 'pokemon',
                'supervisors': ['not_existing'],
                'datetime_from': '2020-07-21 00:00:00Z',
                'datetime_to': '2020-07-31 00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
        (
            {
                'skill': 'tatarin',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '2000-06-30T23:00:00.0Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
        (
            {
                'skill': 'pokemon',
                'state': 'deleted',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '2000-06-30T23:00:00.0Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
    ],
)
async def test_v2_free_base(
        web_context,
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees(operators_list=OPERATORS_LIST_CHANGES)
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert data == expected_result


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql('workforce_management', files=['simple_free_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {
                'skill': 'tatarin',
                'datetime_from': '2100.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'full_count': 1,
                'operators': [
                    {
                        'callcenter_id': '999',
                        'employment_date': '2020-07-21',
                        'full_name': 'Minihanov Minihanov',
                        'login': 'tatarstan',
                        'mentor_login': 'supervisor@unit.test',
                        'rate': 1.0,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                        'roles': [],
                        'role_in_telephony': 'iphone',
                        'schedules': [
                            {
                                'record_id': 2,
                                'revision_id': (
                                    '2020-06-25T21:00:00.000000 +0000'
                                ),
                                'schedule_type_info': {
                                    'duration_minutes': 840,
                                    'first_weekend': False,
                                    'revision_id': (
                                        '2020-08-25T21:00:00.000000 +0000'
                                    ),
                                    'schedule': [5, 2],
                                    'schedule_alias': '5x2/10:00-00:00',
                                    'schedule_type_id': 2,
                                    'start': '10:00:00',
                                },
                                'starts_at': '2020-07-10T03:00:00+03:00',
                                'skills': ['pokemon', 'tatarin'],
                                'secondary_skills': [],
                                'audit': FIRST_AUDIT,
                                'schedule_offset': 0,
                            },
                        ],
                        'skills': ['pokemon', 'tatarin'],
                        'state': 'ready',
                        'supervisor_login': 'abd-damir',
                        'supervisor': {
                            'full_name': 'Abdullin Damir',
                            'login': 'abd-damir',
                            'yandex_uid': 'uid1',
                            'state': 'ready',
                        },
                        'telegram': 'morozhenka',
                        'yandex_uid': 'uid3',
                    },
                ],
            },
        ),
    ],
)
async def test_v2_free_base_schedule_skills(
        web_context,
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert data == expected_result


@pytest.mark.now('2020-07-25T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_free_operators.sql', 'simple_free_shifts.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '3000.01.01T00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [THIRD_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'skill': 'droid',
                'datetime_from': '2000.01.01T00:00:00Z',
                'datetime_to': '2020-07-25T01:00:00.0Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'skill': 'kent',
                'datetime_from': '2020-07-21 00:00:00Z',
                'datetime_to': '2020-07-31 00:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
        (
            {
                'skill': 'pokemon',
                'datetime_from': '2020-07-21 00:00:00Z',
                'datetime_to': '2020-07-26 12:00:00Z',
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [FIRST_OPERATOR, THIRD_OPERATOR], 'full_count': 2},
        ),
    ],
)
async def test_with_shifts(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()
    assert data == expected_result
