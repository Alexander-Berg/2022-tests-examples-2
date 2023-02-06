# pylint: disable=invalid-name
import typing as tp

import pytest

URI = 'v1/operators/timetable/values'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.now('2020-07-26 18:00:00.0 +0000')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_sorting.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
        'simple_actual_shifts.sql',
        'simple_shift_violations.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-26T14:00:00+03:00',
                    'datetime_to': '2020-07-26T16:00:00+03:00',
                    'sequence': ['shift_starts', 'shift_expires'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
                {'absences': [4, 3], 'shifts': [7, 8, 9], 'uid': 'uid3'},
                {'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'},
            ],
            3,
            id='0',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [4, 3], 'shifts': [7, 8, 9], 'uid': 'uid3'},
                {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
                {'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'},
            ],
            3,
            id='1',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-27T11:00:00+00:00',
                    'datetime_to': '2020-07-27T13:00:00+00:00',
                    'sequence': ['absence_starts'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'},
                {'absences': [4, 3], 'shifts': [7, 8, 9], 'uid': 'uid3'},
                {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
            ],
            3,
            id='2',
        ),
        pytest.param(
            {
                'datetime_from': '2020-06-26 13:00:00.0 +0000',
                'datetime_to': '2023-06-28 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-27T11:00:00+00:00',
                    'datetime_to': '2020-07-27T13:00:00+00:00',
                    'sequence': [
                        'absence_starts',
                        'shift_starts',
                        'absence_intersects',
                    ],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'},
                {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
            ],
            2,
            id='3',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-26 13:00:00.0 +0000',
                'datetime_to': '2020-07-28 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-27T18:30:00+00:00',
                    'datetime_to': '2020-07-27T19:10:00+00:00',
                    'sequence': ['absence_expires'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [{'absences': [0, 1], 'shifts': [2, 3, 4], 'uid': 'uid1'}],
            1,
            id='4',
        ),
        pytest.param(
            {
                'datetime_from': '2023-06-26 13:00:00.0 +0000',
                'datetime_to': '2023-09-28 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-27T18:30:00+00:00',
                    'datetime_to': '2020-07-27T19:10:00+00:00',
                    'sequence': ['absence_starts'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 1,
            },
            200,
            [{'absences': [], 'shifts': [], 'uid': 'uid2'}],
            2,
            id='5_offset',
        ),
        pytest.param(
            {
                'datetime_from': '2023-06-26 13:00:00.0 +0000',
                'datetime_to': '2023-09-28 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-27T18:30:00+00:00',
                    'datetime_to': '2020-07-27T19:10:00+00:00',
                    'sequence': [
                        'absence_starts',
                        'absence_starts',
                        'absence_starts',
                    ],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            400,
            [],
            3,
            id='6',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-26 13:00:00.0 +0000',
                'datetime_to': '2020-07-28 15:00:00.0 +0000',
                'skill': 'droid',
                'limit': 10,
                'offset': 0,
            },
            200,
            [],
            0,
            id='7',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'shift_filter': {
                    'breaks_from': '2020-07-26 12:00:00.0 +0000',
                    'breaks_to': '2020-07-26 12:05:00.0 +0000',
                },
            },
            200,
            [{'absences': [], 'shifts': [1], 'uid': 'uid1'}],
            1,
            id='8',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'shift_filter': {'shift_type': 'common'},
            },
            200,
            [
                {'absences': [], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
                {'absences': [], 'shifts': [6, 5], 'uid': 'uid2'},
            ],
            2,
            id='9',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'shift_filter': {'shift_events': [1, 2]},
            },
            200,
            [
                {'absences': [], 'shifts': [1], 'uid': 'uid1'},
                {'absences': [], 'shifts': [5], 'uid': 'uid2'},
            ],
            2,
            id='10',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-07-26 12:00:00.0 +0000',
                        'datetime_to': '2020-07-26 13:15:00.0 +0000',
                        'period_filter_type': 'starts',
                    },
                },
            },
            200,
            [{'absences': [], 'shifts': [1, 2], 'uid': 'uid1'}],
            1,
            id='11',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-07-26 12:00:00.0 +0000',
                        'datetime_to': '2020-07-26 13:15:00.0 +0000',
                        'period_filter_type': 'expires',
                    },
                },
            },
            200,
            [{'absences': [], 'shifts': [1], 'uid': 'uid1'}],
            1,
            id='12',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'shift_filter': {
                    'period_filter': {
                        'datetime_from': '2020-07-26 12:00:00.0 +0000',
                        'datetime_to': '2020-07-26 13:15:00.0 +0000',
                        'period_filter_type': 'intersects',
                    },
                },
            },
            200,
            [{'absences': [], 'shifts': [1, 2], 'uid': 'uid1'}],
            1,
            id='13',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'absence_type_ids': [1],
            },
            200,
            [
                {'absences': [2], 'shifts': [], 'uid': 'uid2'},
                {'absences': [0, 1], 'shifts': [], 'uid': 'uid1'},
            ],
            2,
            id='14',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-08-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'absence_type_ids': [1],
                'login': 'tatar',
            },
            200,
            [{'absences': [4, 3], 'shifts': [], 'uid': 'uid3'}],
            1,
            id='15_login',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'mentor_login': 'mentor',
            },
            200,
            [{'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'}],
            1,
            id='16',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'absence_type_ids': [1, 2, 3],
                'multiskill': True,
            },
            200,
            [
                {'absences': [2], 'shifts': [], 'uid': 'uid2'},
                {'absences': [0, 1], 'shifts': [], 'uid': 'uid1'},
            ],
            2,
            id='17',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'tag_filter': {'tags': ['naruto']},
            },
            200,
            [
                {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
                {'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'},
            ],
            2,
            id='18',
        ),
        pytest.param(
            {
                'load_entities': ['actual_shifts'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {
                    'absences': [],
                    'actual_shifts': [1, 2, 3, 4, 5],
                    'shifts': [],
                    'uid': 'uid1',
                },
                {
                    'absences': [],
                    'actual_shifts': [6],
                    'shifts': [],
                    'uid': 'uid2',
                },
                {
                    'absences': [],
                    'actual_shifts': [],
                    'shifts': [],
                    'uid': 'uid3',
                },
            ],
            3,
            id='19_actual_shifts',
        ),
        pytest.param(
            {
                'load_entities': ['shifts', 'absences', 'actual_shifts'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-26T14:00:00+03:00',
                    'datetime_to': '2020-07-26T16:00:00+03:00',
                    'sequence': ['shift_starts', 'shift_expires'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {
                    'absences': [0, 1],
                    'actual_shifts': [1, 2, 3, 4, 5],
                    'shifts': [1, 2, 3, 4],
                    'uid': 'uid1',
                },
                {
                    'absences': [4, 3],
                    'actual_shifts': [],
                    'shifts': [7, 8, 9],
                    'uid': 'uid3',
                },
                {
                    'absences': [2],
                    'actual_shifts': [6],
                    'shifts': [6, 5],
                    'uid': 'uid2',
                },
            ],
            3,
            id='20_case_1_and_actual_shifts',
        ),
        pytest.param(
            {
                'load_entities': ['shift_violations'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [], 'shifts': [7, 8, 9], 'uid': 'uid3'},
                {'absences': [], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
                {'absences': [], 'shifts': [6, 5], 'uid': 'uid2'},
            ],
            3,
            id='21_shift_violations',
        ),
        pytest.param(
            {
                'load_entities': ['shifts', 'absences', 'shift_violations'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-26T14:00:00+03:00',
                    'datetime_to': '2020-07-26T16:00:00+03:00',
                    'sequence': ['shift_starts', 'shift_expires'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
                {'absences': [4, 3], 'shifts': [7, 8, 9], 'uid': 'uid3'},
                {'absences': [2], 'shifts': [6, 5], 'uid': 'uid2'},
            ],
            3,
            id='22_case_1_and_shift_violations',
        ),
        pytest.param(
            {
                'skill': 'hokage',
                'limit': 50,
                'offset': 0,
                'state': 'ready',
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'absence_type_ids': [1],
                'sort_by_interval': {
                    'sequence': ['shift_starts'],
                    'datetime_from': '2020-07-01 13:00:00.0 +0000',
                    'datetime_to': '2020-07-02 15:00:00.0 +0000',
                },
            },
            200,
            [
                {'absences': [4, 3], 'shifts': [], 'uid': 'uid3'},
                {'absences': [0, 1], 'shifts': [], 'uid': 'uid1'},
            ],
            2,
            id='23_absence_types',
        ),
        pytest.param(
            {
                'load_entities': ['shift_violations', 'shifts'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
                'shift_violation_filter': {
                    'shift_violation_types': ['absent'],
                },
            },
            200,
            [
                {'absences': [], 'shifts': [7], 'uid': 'uid3'},
                {'absences': [], 'shifts': [6], 'uid': 'uid2'},
            ],
            2,
            id='24_shift_violation_types',
        ),
        pytest.param(
            {
                'load_entities': ['shifts', 'absences', 'shift_drafts'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'sort_by_interval': {
                    'datetime_from': '2020-07-26T14:00:00+03:00',
                    'datetime_to': '2020-07-26T16:00:00+03:00',
                    'sequence': ['shift_starts', 'shift_expires'],
                },
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
                'skill': 'tatarin',
            },
            200,
            [
                {
                    'absences': [2],
                    'shift_drafts': [2, 3],
                    'shifts': [],
                    'uid': 'uid2',
                },
                {
                    'absences': [0, 1],
                    'shift_drafts': [],
                    'shifts': [],
                    'uid': 'uid1',
                },
            ],
            2,
            id='25_shift_drafts',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['additional_shifts_jobs.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'load_entities': ['shift_drafts'],
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
                'skill': 'tatarin',
            },
            200,
            [
                {
                    'absences': [],
                    'shift_drafts': [2, 3],
                    'shifts': [],
                    'uid': 'uid2',
                },
            ],
            1,
            id='26_shift_drafts_only',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management',
                    files=['additional_shifts_jobs.sql'],
                ),
            ],
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
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

    assert prepare_response(data, tst_request) == expected_res
    assert data['full_count'] == expected_count


@pytest.mark.config(WORKFORCE_MANAGEMENT_DOMAIN_FILTER_ENABLED=True)
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, headers, expected_status, expected_count',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            {'X-WFM-Domain': 'taxi'},
            200,
            3,
            id='valid_domain',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            {'X-WFM-Domain': None},
            200,
            0,
            id='missing_domain',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'limit': 10,
                'offset': 0,
            },
            {'X-WFM-Domain': 'eda'},
            200,
            0,
            id='wrong_domain',
        ),
    ],
)
async def test_headers(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        headers,
        expected_status,
        expected_count,
        mock_effrat_employees,
):
    mock_effrat_employees()

    headers = {**HEADERS, **headers}
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=headers,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()

    assert data['full_count'] == expected_count


@pytest.mark.now('2020-08-02T11:30:40')
@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_sorting.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res, expected_count',
    [
        pytest.param(
            {
                'datetime_from': '2020-07-26 14:00:00.0 +0000',
                'datetime_to': '2020-07-28 15:00:00.0 +0000',
                'skill': 'droid',
                'limit': 10,
                'offset': 0,
            },
            200,
            [],
            0,
            id='0',
        ),
        pytest.param(
            {
                'datetime_from': '2020-09-01 14:00:00.0 +0000',
                'datetime_to': '2020-09-02 15:00:00.0 +0000',
                'skill': 'hokage',
                'limit': 10,
                'offset': 0,
            },
            200,
            [],
            0,
            id='1',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-30 14:00:00.0 +0000',
                'datetime_to': '2020-08-01 15:00:00.0 +0000',
                'skill': 'hokage',
                'limit': 10,
                'offset': 0,
            },
            200,
            [{'absences': [], 'shifts': [], 'uid': 'uid1'}],
            1,
            id='2',
        ),
        pytest.param(
            {
                'datetime_from': '2020-05-26 13:00:00.0 +0000',
                'datetime_to': '2023-07-28 15:00:00.0 +0000',
                'limit': 10,
                'offset': 0,
                'absence_type_ids': [1],
                'multiskill': True,
            },
            200,
            [
                {'absences': [2], 'shifts': [], 'uid': 'uid2'},
                {'absences': [0, 1], 'shifts': [], 'uid': 'uid1'},
            ],
            2,
            id='3',
        ),
        pytest.param(
            {
                'datetime_from': '2020-07-26 14:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'skill': 'hokage',
                'limit': 10,
                'offset': 0,
            },
            200,
            [
                {'absences': [], 'shifts': [9], 'uid': 'uid3'},
                {'absences': [0, 1], 'shifts': [], 'uid': 'uid1'},
            ],
            2,
            id='4',
        ),
    ],
)
async def test_base_schedule_skills(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        expected_count,
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

    assert prepare_response(data, tst_request) == expected_res
    assert data['full_count'] == expected_count


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts_sorting.sql',
        'simple_absence_types.sql',
        'simple_absences.sql',
    ],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uid': 'uid1',
            },
            200,
            {'absences': [0, 1], 'shifts': [1, 2, 3, 4], 'uid': 'uid1'},
        ),
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uid': 'uid123',
            },
            404,
            None,
        ),
        (
            {
                'datetime_from': '2019-07-01 13:00:00.0 +0000',
                'datetime_to': '2019-07-01 15:00:00.0 +0000',
                'yandex_uid': 'uid1',
            },
            404,
            None,
        ),
    ],
)
async def test_single_handler(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.get(
        URI, params=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()

    load_entities = tst_request.get('load_entities', [])
    assert parse_single_object(data, load_entities) == expected_res


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts_with_job_id.sql'],
)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        (
            {
                'datetime_from': '2020-07-01 13:00:00.0 +0000',
                'datetime_to': '2023-09-01 15:00:00.0 +0000',
                'yandex_uid': 'uid1',
            },
            200,
            1,
        ),
    ],
)
async def test_job_id_field(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.get(
        URI, params=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()

    for shift in data['shifts']:
        assert shift['job_id'] == expected_result


def prepare_response(data, tst_request: tp.Dict):
    load_entities = tst_request.get('load_entities', [])
    return [parse_single_object(row, load_entities) for row in data['records']]


def parse_single_object(operator_data, load_entities: tp.List[str]):
    single = {
        'uid': operator_data['operator']['yandex_uid'],
        'shifts': [shift['shift_id'] for shift in operator_data['shifts']],
        'absences': [absence['id'] for absence in operator_data['absences']],
    }
    if 'actual_shifts' in load_entities:
        single['actual_shifts'] = [
            actual_shift['id']
            for actual_shift in operator_data['actual_shifts']
        ]
    if 'shift_drafts' in load_entities:
        single['shift_drafts'] = [
            shift_draft['job_id']
            for shift_draft in operator_data['shift_drafts']
        ]
    return single
