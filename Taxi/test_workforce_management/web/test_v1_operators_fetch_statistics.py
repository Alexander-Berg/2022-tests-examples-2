import pytest


URI = '/v1/operators/fetch-statistics'
HEADERS = {'X-WFM-Domain': 'taxi'}

FIRST_DATA = {
    'operator': {
        'full_name': 'Abdullin Damir',
        'login': 'abd-damir',
        'yandex_uid': 'uid1',
        'state': 'ready',
    },
    'stats': [
        {'name': 'shift_all_count', 'value': 4},
        {'name': 'shift_all_duration', 'value': 240},
        {'name': 'shift_common_count', 'value': 4},
        {'name': 'shift_common_duration', 'value': 240},
        {'name': 'absence_1_count', 'value': 2},
        {'name': 'absence_1_duration', 'value': 120},
        {'name': 'violation_late_count', 'value': 4},
        {'name': 'violation_late_duration', 'value': 240.12},
    ],
}

SECOND_DATA = {
    'operator': {
        'full_name': 'Gilgenberg Valeria',
        'login': 'chakchak',
        'yandex_uid': 'uid2',
        'state': 'ready',
    },
    'stats': [
        {'name': 'shift_all_count', 'value': 2},
        {'name': 'shift_all_duration', 'value': 120},
        {'name': 'shift_common_count', 'value': 2},
        {'name': 'shift_common_duration', 'value': 120},
        {'name': 'absence_1_count', 'value': 1},
        {'name': 'absence_1_duration', 'value': 60},
        {'name': 'violation_absent_count', 'value': 1},
        {'name': 'violation_absent_duration', 'value': 240.0},
        {'name': 'violation_late_count', 'value': 1},
        {'name': 'violation_late_duration', 'value': 5},
    ],
}

THIRD_DATA = {
    'operator': {
        'full_name': 'Minihanov Minihanov',
        'login': 'tatarstan',
        'yandex_uid': 'uid3',
        'state': 'ready',
    },
    'stats': [
        {'name': 'shift_all_count', 'value': 1},
        {'name': 'shift_all_duration', 'value': 60},
        {'name': 'shift_common_count', 'value': 1},
        {'name': 'shift_common_duration', 'value': 60},
        {'name': 'absence_2_count', 'value': 1},
        {'name': 'absence_2_duration', 'value': 6000},
        {'name': 'violation_absent_count', 'value': 1},
        {'name': 'violation_absent_duration', 'value': 55},
    ],
}


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_shift_violations.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, full_count',
    [
        (
            {
                'skill': 'hokage',
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [FIRST_DATA, SECOND_DATA, THIRD_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
                'operators_filters': {
                    'mentor_logins': ['supervisor@unit.test'],
                    'state': 'all',
                },
            },
            200,
            [FIRST_DATA, THIRD_DATA],
            2,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'shift',
                    'object_value': 'common',
                    'measure': 'count',
                },
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [THIRD_DATA, SECOND_DATA, FIRST_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'shift',
                    'object_value': 'common',
                    'measure': 'count',
                    'order': 'desc',
                },
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [FIRST_DATA, SECOND_DATA, THIRD_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'shift',
                    'object_value': 'common',
                    'measure': 'count',
                },
                'pagination': {
                    'limit': 20,
                    'offset': 2,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [FIRST_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'absence',
                    'object_value': '1',
                    'measure': 'count',
                    'order': 'desc',
                },
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [FIRST_DATA, SECOND_DATA, THIRD_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'violation',
                    'object_value': 'late',
                    'measure': 'count',
                    'order': 'desc',
                },
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [FIRST_DATA, SECOND_DATA, THIRD_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'violation',
                    'object_value': 'late',
                    'measure': 'count',
                    'order': 'asc',
                },
                'pagination': {
                    'limit': 20,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [THIRD_DATA, SECOND_DATA, FIRST_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'absence',
                    'object_value': '1',
                    'measure': 'count',
                    'order': 'desc',
                },
                'pagination': {
                    'limit': 2,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [FIRST_DATA, SECOND_DATA],
            3,
        ),
        (
            {
                'skill': 'hokage',
                'order_by': {
                    'object_type': 'absence',
                    'object_value': '1',
                    'measure': 'count',
                    'order': 'desc',
                },
                'pagination': {
                    'limit': 2,
                    'offset': 2,
                    'datetime_from': '2000-02-28T03:00:00+03:00',
                    'datetime_to': '2120-02-29T03:00:00+03:00',
                },
            },
            200,
            [THIRD_DATA],
            3,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        full_count,
):
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()
    assert data['operators_statistics'] == expected_res
    assert data['operators_full_count'] == full_count
