import typing as tp

import pytest

from workforce_management.common import utils

FIRST_SCHEDULE_INFO = {
    'expires_at': '2020-08-01T03:00:00+03:00',
    'record_id': 1,
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': {'schedule_type_id': 1},
    'starts_at': '2020-07-01T03:00:00+03:00',
    'secondary_skills': ['tatarin'],
    'skills': ['hokage', 'tatarin'],
    'schedule_offset': 0,
}
SECOND_SCHEDULE_INFO = {
    'record_id': 2,
    'revision_id': '2020-06-25T21:00:00.000000 +0000',
    'schedule_type_info': {'schedule_type_id': 2},
    'starts_at': '2020-08-01T03:00:00+03:00',
    'secondary_skills': ['pokemon'],
    'skills': ['pokemon', 'tatarin'],
    'schedule_offset': 0,
}
FIRST_OPERATOR = {
    'full_name': 'Abdullin Damir',
    'phone': '111',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedules': [FIRST_SCHEDULE_INFO],
    'skills': ['hokage', 'tatarin'],
    'tags': ['naruto'],
    'yandex_uid': 'uid1',
}
SECOND_OPERATOR = {
    'full_name': 'Gilgenberg Valeria',
    'revision_id': '2020-08-26T22:00:00.000000 +0000',
    'schedules': [SECOND_SCHEDULE_INFO],
    'skills': [],
    'tags': ['naruto', 'driver'],
    'yandex_uid': 'uid2',
}
THIRD_OPERATOR = {
    'full_name': 'Minihanov Minihanov',
    'revision_id': '2020-08-25T21:00:00.000000 +0000',
    'schedules': [],
    'skills': [],
    'yandex_uid': 'uid3',
}
URI = 'v1/operators/absences/values'
SHIFTS_URI = 'v2/shifts/values'
MODIFY_URI = 'v1/operators/absences/modify'
DELETE_URI = 'v1/operators/absences/delete'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


def is_common_keys_equal(lhs_dict, rhs_dict):
    for key, value in lhs_dict.items():
        if key in rhs_dict:
            if value != rhs_dict[key]:
                return False
    return True


async def check_absences(
        taxi_workforce_management_web,
        tst_request: tp.Dict,
        success: bool = True,
        check_shifts: bool = False,
        shift_ids: tp.Optional[tp.List[int]] = None,
):
    res = await taxi_workforce_management_web.post(
        URI,
        json={
            'yandex_uids': ['uid1', 'uid2'],
            'datetime_from': '2000-01-01T00:00:00Z',
            'datetime_to': '2100-01-01T00:00:00Z',
            'limit': 100,
        },
        headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()

    for operator in data['operators']:
        found = False
        modified = False
        for modified_absence in tst_request['absences']:
            #  sorted by uid by default

            if (
                    'yandex_uid' in modified_absence
                    and modified_absence['yandex_uid']
                    != operator['operator']['yandex_uid']
            ):
                continue

            for absence in operator['absences']:
                if utils.is_timestrings_equal(
                        absence['start'], modified_absence.get('start'),
                ) or absence['id'] == modified_absence.get('id'):
                    found = True
                    modified = is_common_keys_equal(absence, modified_absence)
                    assert modified or not success
                    break
        if not success:
            assert not (modified and found)

    if check_shifts:
        res = await taxi_workforce_management_web.post(
            SHIFTS_URI,
            json={
                'yandex_uids': ['uid1', 'uid2'],
                'datetime_from': '2000-01-01T00:00:00Z',
                'datetime_to': '2100-01-01T00:00:00Z',
                'limit': 100,
            },
            headers=HEADERS,
        )
        assert res.status == 200
        data = await res.json()
        assert sorted(shift_ids or []) == sorted(
            [row['shift']['shift_id'] for row in data['records']],
        )


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'limit': 5,
            },
            200,
            {
                'operators': [
                    {
                        'absences': [],
                        'operator': {
                            'full_name': 'Anonymous Anonymous',
                            'revision_id': '2021-06-02T14:11:55.012908 +0000',
                            'schedules': [],
                            'skills': [],
                            'yandex_uid': 'not-existing',
                        },
                    },
                    {
                        'operator': FIRST_OPERATOR,
                        'absences': [
                            {
                                'duration_minutes': 60,
                                'id': 1,
                                'start': '2020-07-28T00:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'updated_at': '2020-07-28T00:00:00+03:00',
                                },
                            },
                            {
                                'duration_minutes': 60,
                                'id': 0,
                                'start': '2020-07-27T21:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'author_yandex_uid': 'uid1',
                                    'updated_at': '2020-07-27T21:00:00+03:00',
                                },
                            },
                        ],
                    },
                    {
                        'operator': SECOND_OPERATOR,
                        'absences': [
                            {
                                'duration_minutes': 60,
                                'id': 2,
                                'start': '2020-07-27T15:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'updated_at': '2020-07-27T15:00:00+03:00',
                                },
                            },
                        ],
                    },
                    {'operator': THIRD_OPERATOR, 'absences': []},
                ],
            },
            4,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'limit': 2,
            },
            200,
            {
                'operators': [
                    {
                        'absences': [],
                        'operator': {
                            'full_name': 'Anonymous Anonymous',
                            'revision_id': '2021-06-02T14:11:55.012908 +0000',
                            'schedules': [],
                            'skills': [],
                            'yandex_uid': 'not-existing',
                        },
                    },
                    {
                        'operator': FIRST_OPERATOR,
                        'absences': [
                            {
                                'duration_minutes': 60,
                                'id': 1,
                                'start': '2020-07-28T00:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'updated_at': '2020-07-28T00:00:00+03:00',
                                },
                            },
                            {
                                'duration_minutes': 60,
                                'id': 0,
                                'start': '2020-07-27T21:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'author_yandex_uid': 'uid1',
                                    'updated_at': '2020-07-27T21:00:00+03:00',
                                },
                            },
                        ],
                    },
                ],
            },
            4,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'limit': 2,
                'offset': 3,
            },
            200,
            {'operators': [{'operator': THIRD_OPERATOR, 'absences': []}]},
            4,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'skill': 'hokage',
                'limit': 5,
            },
            200,
            {
                'operators': [
                    {
                        'operator': FIRST_OPERATOR,
                        'absences': [
                            {
                                'duration_minutes': 60,
                                'id': 1,
                                'start': '2020-07-28T00:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'updated_at': '2020-07-28T00:00:00+03:00',
                                },
                            },
                            {
                                'duration_minutes': 60,
                                'id': 0,
                                'start': '2020-07-27T21:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'author_yandex_uid': 'uid1',
                                    'updated_at': '2020-07-27T21:00:00+03:00',
                                },
                            },
                        ],
                    },
                ],
            },
            1,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-07-27 20:00:00.0 +0000',
                'skill': 'hokage',
                'limit': 5,
            },
            200,
            {
                'operators': [
                    {
                        'operator': FIRST_OPERATOR,
                        'absences': [
                            {
                                'duration_minutes': 60,
                                'id': 0,
                                'start': '2020-07-27T21:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'author_yandex_uid': 'uid1',
                                    'updated_at': '2020-07-27T21:00:00+03:00',
                                },
                            },
                        ],
                    },
                ],
            },
            1,
        ),
    ],
)
async def test_absence_values(
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

    def skip_revision(dicts):
        for dict_ in dicts:
            dict_['operator'] = {
                key: value
                for key, value in dict_['operator'].items()
                if key != 'revision_id'
            }
        return dicts

    assert skip_revision(data['operators']) == skip_revision(
        expected_res['operators'],
    )
    assert data['full_count'] == expected_count


@pytest.mark.now('2020-07-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-07-27 20:00:00.0 +0000',
                'skill': 'order',
                'limit': 5,
            },
            200,
            {'operators': []},
            0,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-07-27 20:00:00.0 +0000',
                'skill': 'hokage',
                'limit': 5,
            },
            200,
            {
                'operators': [
                    {
                        'operator': {
                            'full_name': 'Abdullin Damir',
                            'phone': '111',
                            'revision_id': '2020-08-25T21:00:00.000000 +0000',
                            'schedules': [
                                {
                                    'expires_at': '2020-08-01T03:00:00+03:00',
                                    'record_id': 1,
                                    'revision_id': (
                                        '2020-06-25T21:00:00.000000 +0000'
                                    ),
                                    'schedule_type_info': {
                                        'schedule_type_id': 1,
                                    },
                                    'starts_at': '2020-07-01T03:00:00+03:00',
                                    'secondary_skills': ['tatarin'],
                                    'skills': ['hokage', 'tatarin'],
                                    'schedule_offset': 0,
                                },
                            ],
                            'skills': ['hokage', 'tatarin'],
                            'tags': ['naruto'],
                            'yandex_uid': 'uid1',
                        },
                        'absences': [
                            {
                                'duration_minutes': 60,
                                'id': 0,
                                'start': '2020-07-27T21:00:00+03:00',
                                'type': 1,
                                'audit': {
                                    'author_yandex_uid': 'uid1',
                                    'updated_at': '2020-07-27T21:00:00+03:00',
                                },
                            },
                        ],
                    },
                ],
            },
            1,
        ),
    ],
)
async def test_absence_values_schedule_skills(
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
    assert data['operators'] == expected_res['operators']
    assert data['full_count'] == expected_count


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
        'allowed_periods.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, shift_ids',
    [
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'duration_minutes': 160,
                        'id': 0,
                        'start': '2020-08-26T21:00:00+03:00',
                        'type': 1,
                        'description': 'asd',
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
            },
            200,
            [1, 2, 3, 4, 5, 6],
        ),
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'duration_minutes': 160,
                        'id': 0,
                        'start': '2020-08-26T21:00:00+03:00',
                        'type': 1,
                        'revision_id': '2020-08-26T21:00:00.000000 +0000',
                    },
                ],
            },
            409,
            [1, 2, 3, 4, 5, 6],
        ),
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'duration_minutes': 160,
                        'start': '2020-09-26T21:00:00+03:00',
                        'type': 1,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
            },
            200,
            [1, 2, 3, 4, 5, 6],
        ),
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'duration_minutes': 180,
                        'start': '2020-07-27T21:00:00+03:00',
                        'type': 1,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
            },
            400,
            [1, 2, 3, 4, 5, 6],
            id='intersection_with_absence',
        ),
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'duration_minutes': 120,
                        'start': '2020-07-26T15:00:00+03:00',
                        'type': 1,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
            },
            400,
            [1, 2, 3, 4, 5, 6],
            id='intersection_with_shift',
        ),
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'duration_minutes': 120,
                        'start': '2020-07-26T15:00:00+03:00',
                        'type': 1,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
                'force_shift_delete': True,
            },
            200,
            [3, 4, 5, 6],
            id='delete_intersecting_shift',
        ),
        pytest.param(
            {
                'absences': [
                    {
                        'yandex_uid': 'uid1',
                        'start': '2020-08-26T21:00:00+03:00',
                        'duration_minutes': 15,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
            },
            400,
            [1, 2, 3, 4, 5, 6],
            id='absence_type_required',
        ),
    ],
)
async def test_absences_modify(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        mock_effrat_employees,
        shift_ids,
):
    res = await taxi_workforce_management_web.post(
        MODIFY_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = expected_status <= 200

    await check_absences(
        taxi_workforce_management_web,
        tst_request,
        success,
        check_shifts=True,
        shift_ids=shift_ids,
    )


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
        'allowed_periods.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status',
    [
        (
            {
                'absences': [
                    {
                        'id': 0,
                        'revision_id': '2020-08-25T21:00:00.000000 +0000',
                    },
                ],
            },
            200,
        ),
        (
            {
                'absences': [
                    {
                        'id': 0,
                        'revision_id': '2020-08-26T21:00:00.000000 +0000',
                    },
                ],
            },
            409,
        ),
    ],
)
async def test_absences_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(
        DELETE_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    #  not success means that we have to find object if request failed
    #  otherwise it should be deleted
    await check_absences(
        taxi_workforce_management_web, tst_request, not success,
    )
