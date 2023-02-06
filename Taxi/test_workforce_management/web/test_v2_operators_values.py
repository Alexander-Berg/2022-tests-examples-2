#  pylint:disable=C0302
import typing as tp

import pytest

from . import data
#  pylint:disable=import-only-modules
from .util import remove_deprecated_fields

URI = 'v2/operators/values'
HEADERS = {'X-WFM-Domain': 'taxi'}
OPERATORS_LIST_CHANGES = [
    {
        'departments': ['2'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia'],
        'source': 'taxi',
        'yandex_uid': 'uid2',
        'employee_uid': '00000000-0000-0000-0000-000000000002',
        'login': 'chakchak',
        'full_name': 'Gilgenberg Valeria',
        'supervisor_login': 'abd-damir',
        'supervisor': {
            'full_name': 'Abdullin Damir',
            'login': 'abd-damir',
            'yandex_uid': 'uid1',
            'state': 'ready',
        },
        'mentor_login': 'mentor@unit.test',
        'telegram_login_pd_id': 'vasya_iz_derevni',
        'tags': ['naruto', 'driver'],
    },
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
    {
        'departments': ['666'],
        'employment_status': 'in_staff',
        'positions': ['super-role'],
        'employment_datetime': '2020-07-21',
        'source': 'taxi',
        'yandex_uid': 'not-existing',
        'employee_uid': 'deadbeef-0000-0000-0000-000000000000',
        'login': 'unknown',
        'full_name': 'Anonymous Anonymous',
        'supervisor_login': 'anonym222',
        'mentor_login': 'supervisor@unit.test',
    },
]


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, '
    'expected_result, expected_result_with_cache',
    [
        (
            {
                'tag_filter': {'tags': ['driver', 'naruto']},
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {
                'tag_filter': {
                    'tags': ['driver', 'naruto'],
                    'connection_policy': 'disjunction',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
            None,
        ),
        (
            {
                'tag_filter': {
                    'tags': ['driver', 'naruto'],
                    'ownership_policy': 'exclude',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
            {
                'operators': [
                    data.FOURTH_OPERATOR,
                    data.FIRST_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 3,
            },
        ),
        (
            {
                'tag_filter': {
                    'tags': ['driver', 'naruto'],
                    'ownership_policy': 'exclude',
                    'connection_policy': 'disjunction',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.THIRD_OPERATOR], 'full_count': 1},
            {
                'operators': [data.FOURTH_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
        ),
        (
            {
                'yandex_uids': ['uid1'],
                'skills': ['hokage'],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {'supervisors': ['aladin227'], 'limit': 1000, 'offset': 0},
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {
                'yandex_uids': ['uid1'],
                'supervisors': ['aladin227'],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {
                'yandex_uids': ['uid1', 'uid2'],
                'supervisors': ['aladin227'],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {
                'supervisors': ['123'],
                'callcenters': ['1'],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
            None,
        ),
        (
            {
                'supervisors': ['abd-damir'],
                'yandex_uids': ['125'],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
            None,
        ),
        (
            {
                'tag_filter': {'tags': ['driver', 'naruto']},
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {
                'tag_filter': {
                    'tags': ['driver', 'naruto'],
                    'connection_policy': 'disjunction',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
            None,
        ),
        (
            {
                'tag_filter': {
                    'tags': ['driver', 'naruto'],
                    'ownership_policy': 'exclude',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
            {
                'operators': [
                    data.FOURTH_OPERATOR,
                    data.FIRST_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 3,
            },
        ),
        (
            {
                'tag_filter': {
                    'tags': ['driver', 'naruto'],
                    'ownership_policy': 'exclude',
                    'connection_policy': 'disjunction',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.THIRD_OPERATOR], 'full_count': 1},
            {
                'operators': [data.FOURTH_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
        ),
        (
            {'roles': ['nokia'], 'limit': 1000, 'offset': 0},
            200,
            {'operators': [], 'full_count': 0},
            None,
        ),
        (
            {'limit': 1000, 'offset': 0},
            200,
            {
                'operators': [
                    data.FOURTH_OPERATOR,
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 4,
            },
            None,
        ),
        (
            {'limit': 1, 'offset': 0},
            200,
            {'operators': [data.FOURTH_OPERATOR], 'full_count': 4},
            None,
        ),
        (
            {'limit': 1, 'offset': 2},
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 4},
            None,
        ),
        (
            {'limit': 10, 'offset': 5},
            200,
            {'operators': [], 'full_count': 0},
            None,
        ),
        (
            {'limit': 1000, 'offset': 0},
            200,
            {
                'operators': [
                    data.FOURTH_OPERATOR,
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 4,
            },
            None,
        ),
        (
            {'multiskill': True, 'limit': 1000, 'offset': 0},
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {'mentor_login': 'mentor', 'limit': 1000, 'offset': 0},
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 1},
            None,
        ),
        (
            {
                'employment_date_filter': {
                    'datetime_from': '2020-01-01T00:00:00Z',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [
                    data.FOURTH_OPERATOR,
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 4,
            },
            None,
        ),
        (
            {
                'employment_date_filter': {
                    'datetime_from': '2021-01-01T00:00:00Z',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
            None,
        ),
        (
            {
                'employment_date_filter': {
                    'datetime_from': '2020-01-01T00:00:00Z',
                    'datetime_to': '2020-01-02T00:00:00Z',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
            None,
        ),
        (
            {
                'employment_date_filter': {
                    'datetime_to': '3000-01-02T00:00:00Z',
                },
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [
                    data.FOURTH_OPERATOR,
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 4,
            },
            None,
        ),
    ],
)
async def test_v2_values_base(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        expected_result_with_cache,
        mock_effrat_employees,
):
    mock_effrat_employees(operators_list=OPERATORS_LIST_CHANGES)

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    if expected_result_with_cache:
        expected_result = expected_result_with_cache

    expected_result['operators'] = [
        remove_deprecated_fields(operator, 'rate')
        for operator in expected_result['operators']
    ]

    assert await res.json() == expected_result


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {'schedule_types': [{'id': 1}], 'limit': 1000, 'offset': 0},
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'schedule_types': [{'id': 1}, {'id': 2}],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
        ),
        (
            {
                'schedule_types': [
                    {'id': 1, 'datetime_from': '2020-07-15 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'schedule_types': [
                    {'id': 1, 'datetime_to': '2020-07-15 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'schedule_types': [
                    {'id': 1, 'datetime_to': '2020-07-15 00:00:00.0Z'},
                    {'id': 2, 'datetime_from': '2020-07-15 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
        ),
        (
            {'schedule_types': [{'id': 1}], 'limit': 1000, 'offset': 0},
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
        ),
        (
            {'schedule_types': [{'id': 2}], 'limit': 1000, 'offset': 0},
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 1},
        ),
        (
            {
                'schedule_types': [
                    {'id': 1, 'datetime_to': '2020-07-01 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
        (
            {
                'full_name': 'asdasdasdasd',
                'schedule_types': [{'id': 1}],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
        ),
    ],
)
async def test_schedule_filters(
        taxi_workforce_management_web,
        mock_effrat_employees,
        tst_request,
        expected_status,
        expected_result,
):
    expected_result['operators'] = [
        remove_deprecated_fields(operator, 'rate')
        for operator in expected_result['operators']
    ]
    mock_effrat_employees(operators_list=OPERATORS_LIST_CHANGES)

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_result


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'additional_schedule.sql',
        'simple_roles.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {'schedule_types': [{'id': 1}], 'limit': 1000, 'offset': 0},
            200,
            {
                'full_count': 1,
                'operators': [
                    {
                        **remove_deprecated_fields(
                            data.FIRST_OPERATOR, 'rate',
                        ),
                        'schedules': [
                            {
                                'expires_at': '2020-08-01T03:00:00+03:00',
                                'record_id': 1,
                                'revision_id': (
                                    '2020-06-25T21:00:00.000000 +0000'
                                ),
                                'schedule_type_info': {
                                    'duration_minutes': 720,
                                    'first_weekend': False,
                                    'revision_id': (
                                        '2020-08-26T09:00:00.000000 +0000'
                                    ),
                                    'schedule': [2, 2],
                                    'schedule_type_id': 1,
                                    'start': '12:00:00',
                                },
                                'skills': ['hokage', 'tatarin'],
                                'secondary_skills': ['tatarin'],
                                'schedule_offset': 0,
                                'starts_at': '2020-07-01T03:00:00+03:00',
                                'audit': data.FIRST_AUDIT,
                            },
                            {
                                'expires_at': '2020-09-01T03:00:00+03:00',
                                'record_id': 4,
                                'skills': [],
                                'secondary_skills': [],
                                'schedule_offset': 0,
                                'revision_id': (
                                    '2020-06-25T21:00:00.000000 +0000'
                                ),
                                'schedule_type_info': {
                                    'duration_minutes': 720,
                                    'first_weekend': False,
                                    'revision_id': (
                                        '2020-08-26T09:00:00.000000 +0000'
                                    ),
                                    'schedule': [2, 2],
                                    'schedule_type_id': 1,
                                    'start': '12:00:00',
                                },
                                'starts_at': '2020-08-01T04:00:00+03:00',
                                'audit': data.FIRST_AUDIT,
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_schedule_filters_extra_schedule(
        taxi_workforce_management_web,
        mock_effrat_employees,
        tst_request,
        expected_status,
        expected_result,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_result


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            {
                'schedule_types': [
                    {'datetime_from': '2020-08-01 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.SECOND_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
            id='id_none_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'datetime_from': '2020-07-01 00:00:00.0Z',
                        'datetime_to': '2020-07-30 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='id_none_from_to',
        ),
        pytest.param(
            {
                'schedule_types': [{'datetime_to': '2020-08-02 00:00:00.0Z'}],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
            id='id_none_to',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {'datetime_to': '2020-07-15 00:00:00.0Z'},
                    {'datetime_from': '2020-07-15 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 3,
            },
            id='id_none_from_to_2',
        ),
        pytest.param(
            {
                'full_name': 'asdasdasdasd',
                'schedule_types': [
                    {'datetime_from': '2020-07-15 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
            id='id_none_from_2',
        ),
        pytest.param(
            {'schedule_types': [{}, {'id': 1}], 'limit': 1000, 'offset': 0},
            400,
            {},
            id='id_none_bad_request',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {'datetime_from': '2020-06-30 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 3,
            },
            id='ids_and_skills_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'skills': ['tatarin'],
                        'datetime_from': '2020-06-30 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
            id='skills_any_type_skill_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'primary_skills': ['tatarin'],
                        'datetime_from': '2020-06-30 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.SECOND_OPERATOR], 'full_count': 1},
            id='skills_primary_skill_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'secondary_skills': ['tatarin'],
                        'datetime_from': '2020-06-30 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='skills_secondary_skill_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'ids': [1],
                        'skills': ['tatarin'],
                        'datetime_from': '2020-06-30 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='ids_and_skills_id_skill_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'ids': [1],
                        'datetime_from': '2020-06-30 00:00:00.0Z',
                        'datetime_to': '2020-07-30 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='ids_and_skills_id_from_to',
        ),
        pytest.param(
            {'schedule_types': [{'ids': [1, 2]}], 'limit': 1000, 'offset': 0},
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.SECOND_OPERATOR],
                'full_count': 2,
            },
            id='ids_and_skills_ids',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {'ids': [1, 2], 'skills': ['hokage', 'skill12345']},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='ids_and_skills_ids_skills',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'ids': [1, 2, 4],
                        'skills': ['hokage'],
                        'datetime_from': '2020-07-15 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [data.FIRST_OPERATOR, data.THIRD_OPERATOR],
                'full_count': 2,
            },
            id='ids_and_skills_ids_skills_from',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'ids': [1, 4],
                        'skills': ['tatarin'],
                        'datetime_to': '2020-07-15 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='ids_and_skills_ids_skills_to',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'ids': [1, 4],
                        'skills': ['tatarin'],
                        'datetime_to': '2020-07-15 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.FIRST_OPERATOR], 'full_count': 1},
            id='ids_and_skills_ids_skills_to',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {'ids': [1, 2], 'datetime_to': '2020-07-15 00:00:00.0Z'},
                    {'ids': [2, 4], 'datetime_from': '2020-07-15 00:00:00.0Z'},
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [
                    data.FIRST_OPERATOR,
                    data.SECOND_OPERATOR,
                    data.THIRD_OPERATOR,
                ],
                'full_count': 3,
            },
            id='ids_and_skills_two_filters',
        ),
        pytest.param(
            {
                'schedule_types': [
                    {
                        'ids': [1, 2, 4],
                        'datetime_to': '2019-07-01 00:00:00.0Z',
                    },
                ],
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [], 'full_count': 0},
            id='ids_and_skills_no_operators',
        ),
    ],
)
async def test_schedule_filters2(
        taxi_workforce_management_web,
        mock_effrat_employees,
        tst_request,
        expected_status,
        expected_result,
):
    if expected_status == 200:
        expected_result['operators'] = [
            remove_deprecated_fields(operator, 'rate')
            for operator in expected_result['operators']
        ]
    mock_effrat_employees(operators_list=OPERATORS_LIST_CHANGES)

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_result


@pytest.mark.now('2020-08-02T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {
                'yandex_uids': ['uid1', 'uid2'],
                'multiskill': True,
                'limit': 1000,
                'offset': 0,
            },
            200,
            {'operators': [data.SECOND_OPERATOR_WITH_SKILLS], 'full_count': 1},
        ),
        (
            {
                'yandex_uids': ['uid1', 'uid2'],
                'multiskill': False,
                'limit': 1000,
                'offset': 0,
            },
            200,
            {
                'operators': [
                    {**data.FIRST_OPERATOR, 'skills': []},
                    data.SECOND_OPERATOR_WITH_SKILLS,
                ],
                'full_count': 2,
            },
        ),
        (
            {'yandex_uids': ['uid1', 'uid2'], 'limit': 1000, 'offset': 0},
            200,
            {
                'operators': [
                    {**data.FIRST_OPERATOR, 'skills': []},
                    data.SECOND_OPERATOR_WITH_SKILLS,
                ],
                'full_count': 2,
            },
        ),
    ],
)
async def test_values_multiskill(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    expected_result['operators'] = [
        remove_deprecated_fields(operator, 'rate')
        for operator in expected_result['operators']
    ]
    mock_effrat_employees(operators_list=OPERATORS_LIST_CHANGES)
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    assert await res.json() == expected_result


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'yandex_uids': ['uid1'],
                'skills': ['hokage'],
                'limit': 1000,
                'offset': 0,
            },
            200,
        ),
    ],
)
async def test_v2_values_without_role(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        mock_effrat_employees,
):
    mock_effrat_employees(
        operators_list=[
            {
                'yandex_uid': 'uid1',
                'employee_uid': '00000000-0000-0000-0000-000000000001',
                'login': 'abd-damir',
                'staff_login': 'abd-damir',
                'departments': ['1'],
                'full_name': 'Abdullin Damir',
                'employment_status': 'in_staff',
                'phone_pd_id': '111',
                'supervisor_login': 'aladin227',
                'mentor_login': 'supervisor@unit.test',
                'employment_datetime': '2020-07-21T00:00:00+03:00',
                'positions': [],
                'source': 'taxi',
            },
        ],
    )

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    res_data = await res.json()
    assert 'role_in_telephony' not in res_data['operators'][0]


NEW_THIRD_OPERATOR_DATA = {
    'callcenter_id': '999',
    'employment_date': '2020-07-21',
    'full_name': 'Minihanov Minihanov',
    'login': 'tatarstan',
    'mentor_login': 'supervisor@unit.test',
    'role_in_telephony': 'iphone',
    'schedules': [
        {
            'record_id': 3,
            'revision_id': '2020-06-25T21:00:00.000000 +0000',
            'schedule_type_info': {
                'duration_minutes': 840,
                'first_weekend': False,
                'revision_id': '2023-07-31T21:00:00.000000 +0000',
                'schedule': [5, 2],
                'schedule_alias': '5x2/10:00-00:00',
                'schedule_type_id': 4,
                'start': '10:00:00',
            },
            'skills': ['hokage'],
            'secondary_skills': [],
            'starts_at': '2023-08-01T03:00:00+03:00',
            'audit': data.FIRST_AUDIT,
            'schedule_offset': 0,
        },
    ],
    'skills': [],
    'state': 'ready',
    'supervisor_login': 'abd-damir',
    'telegram': 'morozhenka',
    'yandex_uid': 'uid3',
    'roles': [{'name': 'group1'}],
}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            {'domain': 'wfm', 'limit': 1000, 'offset': 0},
            200,
            [],
            id='no_operators_in_wfm_domain',
        ),
        pytest.param(
            {'domain': 'taxi', 'limit': 1000, 'offset': 0},
            200,
            [data.FIRST_OPERATOR],
            id='taxi_domain_operators',
        ),
        pytest.param(
            {'domain': 'eats', 'limit': 1000, 'offset': 0},
            200,
            [NEW_THIRD_OPERATOR_DATA],
            id='single_operator_for_eats_domain',
        ),
    ],
)
async def test_v2_values_domain_filter(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    expected_result = [
        remove_deprecated_fields(operator, 'rate')
        for operator in expected_result
    ]
    mock_effrat_employees(
        operators_list=[
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
                'source': 'eats',
                'yandex_uid': 'uid3',
                'employee_uid': '00000000-0000-0000-0000-000000000003',
                'login': 'tatarstan',
                'full_name': 'Minihanov Minihanov',
                'supervisor_login': 'abd-damir',
                'mentor_login': 'supervisor@unit.test',
                'telegram_login_pd_id': 'morozhenka',
            },
        ],
    )
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    domain = tst_request.pop('domain')
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers={'X-WFM-Domain': domain},
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    res_data = await res.json()

    for actual, expected in zip(res_data['operators'], expected_result):
        actual.pop('revision_id', None)
        expected.pop('revision_id', None)
    assert res_data['operators'] == expected_result


SECONDS_OPERATOR_EATS: tp.Dict = {
    **data.SECOND_OPERATOR,
    'schedules': [],  # no schedules in the new domain
}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management', files=['simple_operators.sql', 'simple_roles.sql'],
)
@pytest.mark.parametrize(
    'tst_request, tst_domain, expected_status, expected_result',
    [
        pytest.param(
            {'limit': 1000, 'offset': 0},
            'taxi',
            200,
            [],
            id='operator fired from domain',
        ),
        pytest.param(
            {'limit': 1000, 'offset': 0},
            'eats',
            200,
            [SECONDS_OPERATOR_EATS],
            id='operator returned to other domain',
        ),
    ],
)
async def test_v2_values_operator_with_several_domains(
        taxi_workforce_management_web,
        tst_request,
        tst_domain,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    expected_result = [
        remove_deprecated_fields(operator, 'rate')
        for operator in expected_result
    ]
    mock_effrat_employees(operators_list=[OPERATORS_LIST_CHANGES[0]])
    await taxi_workforce_management_web.invalidate_caches(clean_update=True)

    mock_effrat_employees(
        operators_list=[
            {
                **OPERATORS_LIST_CHANGES[0],
                'employment_status': 'fired',
                'employee_uid': '00000000-0000-0000-0000-000000000002',
            },
        ],
    )
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    mock_effrat_employees(
        operators_list=[
            {
                **OPERATORS_LIST_CHANGES[0],
                'source': 'eats',
                'employee_uid': '00000000-0000-0000-0001-000000000002',
            },
        ],
    )
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)

    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers={'X-WFM-Domain': tst_domain},
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    res_data = await res.json()

    for actual, expected in zip(res_data['operators'], expected_result):
        actual.pop('revision_id', None)
        expected.pop('revision_id', None)
        if tst_domain == 'eats':
            expected.pop('supervisor', None)
            actual.pop('supervisor', None)
    assert res_data['operators'] == expected_result
