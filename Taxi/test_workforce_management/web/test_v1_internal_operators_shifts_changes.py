import pytest


URI = 'internal/v1/operators/shifts/changes'

SHIFT_1 = {
    'actual_shifts': [
        {
            'duration_minutes': 60.0,
            'events': [],
            'id': 1,
            'shift_id': 1,
            'start': '2020-07-26T15:00:00+03:00',
        },
    ],
    'audit': {'author_yandex_uid': 'uid1'},
    'breaks': [
        {
            'duration_minutes': 30,
            'id': 1,
            'start': '2020-07-26T15:00:00+03:00',
            'type': 'technical',
        },
        {
            'duration_minutes': 30,
            'id': 2,
            'start': '2020-07-26T15:30:00+03:00',
            'type': 'technical',
        },
    ],
    'description': 'empty',
    'duration_minutes': 60,
    'events': [
        {
            'description': 'technical',
            'duration_minutes': 30,
            'event_id': 1,
            'id': 1,
            'start': '2020-07-26T15:30:00+03:00',
        },
    ],
    'operators_schedule_types_id': 1,
    'shift_id': 1,
    'shift_violations': [
        {
            'duration_minutes': 60.0,
            'id': 1,
            'shift_id': 1,
            'start': '2020-07-26T15:00:00+03:00',
            'type': 'late',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'segments': [
        {
            'description': 'awesome description',
            'duration_minutes': 30,
            'id': 1,
            'skill': 'pokemon',
            'start': '2020-07-26T15:00:00+03:00',
        },
        {
            'duration_minutes': 30,
            'id': 2,
            'skill': 'pokemon',
            'start': '2020-07-26T15:30:00+03:00',
        },
    ],
    'start': '2020-07-26T15:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid1',
    'is_deleted': False,
}
SHIFT_2 = {
    'actual_shifts': [
        {
            'duration_minutes': 60.0,
            'events': [],
            'id': 2,
            'shift_id': 2,
            'start': '2020-07-26T16:00:00+03:00',
        },
    ],
    'audit': {'author_yandex_uid': 'uid1'},
    'description': 'empty',
    'duration_minutes': 60,
    'operators_schedule_types_id': 1,
    'shift_id': 2,
    'shift_violations': [
        {
            'duration_minutes': 60.0,
            'id': 2,
            'shift_id': 2,
            'start': '2020-07-26T16:00:00+03:00',
            'type': 'late',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'skill': 'pokemon',
    'start': '2020-07-26T16:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid1',
    'is_deleted': False,
}
DELETED_SHIFT_1 = {
    'audit': {'author_yandex_uid': 'uid1'},
    'breaks': [
        {
            'duration_minutes': 30,
            'id': 5,
            'start': '2020-07-26T15:00:00+03:00',
            'type': 'technical',
        },
        {
            'duration_minutes': 30,
            'id': 6,
            'start': '2020-07-26T15:30:00+03:00',
            'type': 'technical',
        },
    ],
    'description': 'empty',
    'duration_minutes': 60,
    'events': [
        {
            'description': 'technical',
            'duration_minutes': 30,
            'event_id': 1,
            'id': 5,
            'start': '2020-07-26T15:30:00+03:00',
        },
    ],
    'operators_schedule_types_id': 1,
    'shift_id': 8,
    'segments': [
        {
            'description': 'awesome description',
            'duration_minutes': 30,
            'id': 5,
            'skill': 'pokemon',
            'start': '2020-07-26T15:00:00+03:00',
        },
        {
            'duration_minutes': 30,
            'id': 6,
            'skill': 'pokemon',
            'start': '2020-07-26T15:30:00+03:00',
        },
    ],
    'start': '2020-07-26T15:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid1',
    'is_deleted': True,
}
DELETED_SHIFT_2 = {
    'audit': {'author_yandex_uid': 'uid1'},
    'description': 'empty',
    'duration_minutes': 60,
    'events': [
        {
            'description': 'technical',
            'duration_minutes': 15,
            'event_id': 2,
            'id': 6,
            'start': '2020-07-26T16:00:00+03:00',
        },
    ],
    'is_deleted': True,
    'operators_schedule_types_id': 1,
    'shift_id': 9,
    'skill': 'pokemon',
    'start': '2020-07-26T16:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid1',
}
SHIFT_3 = {
    'actual_shifts': [
        {
            'duration_minutes': 60.0,
            'events': [],
            'id': 3,
            'shift_id': 3,
            'start': '2020-07-26T17:00:00+03:00',
        },
    ],
    'audit': {'author_yandex_uid': 'uid1'},
    'description': 'empty',
    'duration_minutes': 60,
    'is_deleted': False,
    'operators_schedule_types_id': 1,
    'shift_id': 3,
    'shift_violations': [
        {
            'duration_minutes': 60.0,
            'id': 3,
            'shift_id': 3,
            'start': '2020-07-26T17:00:00+03:00',
            'type': 'late',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'skill': 'pokemon',
    'start': '2020-07-26T17:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid1',
}
SHIFT_4 = {
    'actual_shifts': [
        {
            'duration_minutes': 60.0,
            'events': [],
            'id': 4,
            'shift_id': 4,
            'start': '2020-07-26T18:00:00+03:00',
        },
    ],
    'audit': {'author_yandex_uid': 'uid1'},
    'description': 'empty',
    'duration_minutes': 60,
    'is_deleted': False,
    'operators_schedule_types_id': 1,
    'shift_id': 4,
    'shift_violations': [
        {
            'duration_minutes': 60.124,
            'id': 4,
            'shift_id': 4,
            'start': '2020-07-26T18:00:00+03:00',
            'type': 'late',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'skill': 'pokemon',
    'start': '2020-07-26T18:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid1',
}
SHIFT_5 = {
    'audit': {'author_yandex_uid': 'uid1'},
    'description': 'empty',
    'duration_minutes': 60,
    'events': [
        {
            'description': 'technical',
            'duration_minutes': 15,
            'event_id': 2,
            'id': 2,
            'start': '2020-07-26T19:00:00+03:00',
        },
    ],
    'is_deleted': False,
    'operators_schedule_types_id': 1,
    'shift_id': 5,
    'shift_violations': [
        {
            'duration_minutes': 480.0,
            'id': 6,
            'shift_id': 5,
            'start': '2020-07-26T19:00:00+03:00',
            'type': 'late',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'skill': 'pokemon',
    'start': '2020-07-26T19:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid2',
}
SHIFT_7 = {
    'audit': {},
    'description': 'empty',
    'duration_minutes': 120,
    'is_deleted': False,
    'operators_schedule_types_id': 1,
    'shift_id': 7,
    'shift_violations': [
        {
            'duration_minutes': 720.0,
            'id': 7,
            'shift_id': 7,
            'start': '2020-07-26T15:00:00+03:00',
            'type': 'absent',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'skill': 'pokemon',
    'start': '2020-07-26T15:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid3',
}
SHIFT_6 = {
    'actual_shifts': [
        {
            'duration_minutes': 60.0,
            'events': [
                {
                    'duration_minutes': 0.5020263166666666,
                    'start': '2020-07-26T18:40:00.608168+03:00',
                    'sub_type': 'work_with_rg',
                    'type': 'pause',
                },
                {
                    'duration_minutes': 1.2132323333333335,
                    'start': '2020-07-26T18:43:26.191939+03:00',
                    'sub_type': 'work_with_rg',
                    'type': 'pause',
                },
                {
                    'duration_minutes': 0.6532841,
                    'start': '2020-07-26T18:45:08.124016+03:00',
                    'type': 'pause',
                },
            ],
            'id': 6,
            'shift_id': 6,
            'start': '2020-07-26T18:00:00+03:00',
        },
    ],
    'audit': {'author_yandex_uid': 'uid1'},
    'description': 'empty',
    'duration_minutes': 60,
    'operators_schedule_types_id': 1,
    'shift_id': 6,
    'shift_violations': [
        {
            'duration_minutes': 240.0,
            'id': 5,
            'shift_id': 6,
            'start': '2020-07-26T15:00:00+03:00',
            'type': 'absent',
            'audit': {'updated_at': '2020-07-26T15:00:00+03:00'},
        },
    ],
    'skill': 'pokemon',
    'start': '2020-07-26T18:00:00+03:00',
    'type': 'common',
    'yandex_uid': 'uid2',
    'is_deleted': False,
}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_shift_violations.sql',
        'simple_actual_shifts.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {
                'updated_from': '2000-01-01T00:00:00Z',
                'updated_to': '2100-01-01T00:00:00Z',
                'limit': 10,
            },
            200,
            {
                'shifts': [
                    SHIFT_1,
                    SHIFT_7,
                    DELETED_SHIFT_1,
                    SHIFT_2,
                    DELETED_SHIFT_2,
                    SHIFT_3,
                    SHIFT_4,
                    SHIFT_5,
                    SHIFT_6,
                ],
                'last_id': '6',
            },
            id='get_all_updates',
        ),
        pytest.param(
            {
                'updated_from': '2000-01-01T00:00:00Z',
                'updated_to': '2100-01-01T00:00:00Z',
                'limit': 4,
            },
            200,
            {
                'shifts': [SHIFT_1, SHIFT_7, DELETED_SHIFT_1, SHIFT_2],
                'last_id': '2',
            },
            id='get_four_updates',
        ),
        pytest.param(
            {
                'updated_from': '2020-07-26T13:00:00Z',
                'updated_to': '2100-01-01T00:00:00Z',
                'limit': 4,
                'last_id': '2',
            },
            200,
            {
                'shifts': [DELETED_SHIFT_2, SHIFT_3, SHIFT_4, SHIFT_5],
                'last_id': '5',
            },
            id='get_four_updates_since_fourth_shift',
        ),
        pytest.param(
            {
                'updated_from': '2020-07-26T13:00:00Z',
                'updated_to': '2020-07-26T14:15:00Z',
                'limit': 4,
            },
            200,
            {'shifts': [SHIFT_2, DELETED_SHIFT_2, SHIFT_3], 'last_id': '3'},
            id='get_updates_between_dates',
        ),
    ],
)
async def test_simple(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        mock_effrat_employees,
):
    res = await taxi_workforce_management_web.post(URI, json=tst_request)
    assert res.status == expected_status

    if expected_status > 200:
        return
    body = await res.json()

    for shift in body['shifts']:
        shift['audit'].pop('updated_at', None)

    assert body == expected_res
