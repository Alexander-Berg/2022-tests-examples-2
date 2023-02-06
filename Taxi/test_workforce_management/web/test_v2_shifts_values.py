import datetime
import typing as tp

import pytest

from taxi.util import dates

from . import data


def parse_and_make_step(provided_datetime: str, i: int):
    return dates.localize(
        dates.parse_timestring(provided_datetime)
        + datetime.timedelta(hours=i),
    ).isoformat()


def remove_extra_fields(records: tp.List[tp.Dict[str, tp.Any]]):
    for record in records:
        if not record:
            continue
        operator = record['operator']
        operator.pop('roles', None)
        record['operator'] = operator
        record['shift'].pop('yandex_uid', None)
    return records


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
        'mentor_login': 'mentor@unit.test',
        'telegram_login_pd_id': 'vasya_iz_derevni',
        'tags': ['naruto', 'driver'],
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
        'departments': ['2'],
        'employment_status': 'in_staff',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia'],
        'source': 'taxi',
        'yandex_uid': 'uid1',
        'employee_uid': '00000000-0000-0000-0000-000000000001',
        'login': 'abd-damir',
        'full_name': 'Abdullin Damir',
        'supervisor_login': 'aladin227',
        'supervisor': {
            'full_name': 'Abdullin Damir',
            'login': 'abd-damir',
            'yandex_uid': 'uid1',
            'state': 'ready',
        },
        'mentor_login': 'supervisor@unit.test',
        'phone_pd_id': '111',
        'tags': ['naruto'],
    },
]
URI = 'v2/shifts/values'
START = '2020-07-26T15:00:00+03:00'
HEADERS = {'X-WFM-Domain': 'taxi'}
SHIFT_RECORDS = [
    {
        'shift': {
            'shift_id': i + 1,
            'type': 'common',
            'description': 'empty',
            'start': parse_and_make_step(START, i),
            'duration_minutes': 60,
            'skill': 'pokemon',
        },
        'operator': data.FIRST_OPERATOR_SIMPLE,
    }
    for i in range(4)
]


def check_audit(expected_records, actual_records):
    for _expected, _actual in zip(expected_records, actual_records):
        expected_shift = _expected['shift']
        actual_shift = _actual['shift']

        audit = actual_shift['audit']
        assert audit['updated_at'] is not None
        if 'audit' not in expected_shift:
            del actual_shift['audit']


@pytest.mark.now('2020-07-10T00:00:00')
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
                'yandex_uids': ['uid1'],
                'limit': 1,
            },
            200,
            SHIFT_RECORDS[:1],
            4,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1'],
                'limit': 1,
                'offset': 2,
            },
            200,
            SHIFT_RECORDS[2:3],
            4,
        ),
        (
            {
                'datetime_from': '2020-07-01 14:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1'],
                'limit': 2,
                'offset': 1,
            },
            200,
            SHIFT_RECORDS[1:3],
            4,
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
                'skill': 'pokemon',
                'limit': 10,
            },
            200,
            [],
            0,
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'supervisors': ['aladin227'],
                'limit': 100,
            },
            200,
            SHIFT_RECORDS,
            4,
        ),
    ],
)
async def test_shift_values2(
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
    response = await res.json()
    assert response['full_count'] == expected_count
    check_audit(
        expected_records=expected_res, actual_records=response['records'],
    )
    assert remove_extra_fields(response['records']) == remove_extra_fields(
        expected_res,
    )


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'shifts_for_filtering.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'skill': 'hokage',
                'full_name': 'dullin',
                'multiskill': True,
                'limit': 10,
            },
            200,
            [data.FIRST_SHIFT],
            1,
            id='0',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {
                    'breaks_from': '2020-07-26 12:00:00.0 +0000',
                    'breaks_to': '2020-07-26 12:05:00.0 +0000',
                },
            },
            200,
            [data.FIRST_SHIFT],
            1,
            id='1',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {'shift_type': 'common'},
            },
            200,
            [
                data.FIRST_SHIFT,
                data.SECOND_SHIFT,
                data.THIRD_SHIFT,
                data.FIFTH_SHIFT,
                {**data.FOURTH_SHIFT, 'operator': data.SECOND_OPERATOR_EXTRA},
            ],
            5,
            id='2',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'tag_filter': {'tags': ['naruto']},
            },
            200,
            [
                data.FIRST_SHIFT,
                {**data.FOURTH_SHIFT, 'operator': data.SECOND_OPERATOR_EXTRA},
            ],
            2,
            id='3',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {
                    'shift_type': 'additional',
                    'shift_events': [1, 2],
                },
            },
            200,
            [data.SIXTH_SHIFT],
            1,
            id='4',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {'breaks_from': '2020-07-26 12:00:00.0 +0000'},
            },
            400,
            [],
            0,
            id='5',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2020-09-01 15:00:00.0 +0000',
                'skill': 'pokemon',
                'state': 'deleted',
                'limit': 10,
            },
            200,
            [],
            0,
            id='6',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-07-28T19:00:00+03:00',
                        'datetime_to': '2020-07-28T19:05:00+03:00',
                        'period_filter_type': 'starts',
                    },
                },
            },
            200,
            [data.SIXTH_SHIFT],
            1,
            id='7',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-08-03T18:30:00+03:00',
                        'datetime_to': '2020-08-03T19:05:00+03:00',
                        'period_filter_type': 'expires',
                    },
                },
            },
            200,
            [{**data.FOURTH_SHIFT, 'operator': data.SECOND_OPERATOR_EXTRA}],
            1,
            id='8',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'login': 'tatar',
            },
            200,
            [
                data.SECOND_SHIFT,
                data.THIRD_SHIFT,
                data.FIFTH_SHIFT,
                data.SIXTH_SHIFT,
            ],
            4,
            id='9',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'mentor_login': 'mentor',
            },
            200,
            [{**data.FOURTH_SHIFT, 'operator': data.SECOND_OPERATOR_EXTRA}],
            1,
            id='10',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-07-26T17:00:00+03:00',
                        'datetime_to': '2020-09-03T19:05:00+03:00',
                        'period_filter_type': 'intersects',
                    },
                },
            },
            200,
            [
                data.THIRD_SHIFT,
                data.FIFTH_SHIFT,
                data.SIXTH_SHIFT,
                {**data.FOURTH_SHIFT, 'operator': data.SECOND_OPERATOR_EXTRA},
            ],
            4,
            id='11',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'multiskill': True,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-07-25T17:00:00+03:00',
                        'datetime_to': '2020-08-03T19:05:00+03:00',
                        'period_filter_type': 'intersects',
                    },
                },
            },
            200,
            [data.FIRST_SHIFT, data.FOURTH_SHIFT],
            2,
            id='12',
        ),
    ],
)
async def test_filtering2(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
        mock_effrat_employees,
):
    mock_effrat_employees(operators_list=OPERATORS_LIST_CHANGES)
    await taxi_workforce_management_web.invalidate_caches(clean_update=False)
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    if expected_status > 200:
        return

    response = await res.json()
    assert response['full_count'] == expected_count
    check_audit(
        expected_records=expected_res, actual_records=response['records'],
    )
    assert remove_extra_fields(response['records']) == remove_extra_fields(
        expected_res,
    )


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_breaks.sql'],
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
            },
            200,
            [data.ZEROTH_SHIFT],
            1,
        ),
    ],
)
async def test_breaks2(
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
    response = await res.json()
    assert response['full_count'] == expected_count
    check_audit(
        expected_records=expected_res, actual_records=response['records'],
    )
    assert remove_extra_fields(response['records']) == remove_extra_fields(
        expected_res,
    )
