import typing as tp

import pytest

from workforce_management.common import constants

URI_V2_OPERATORS_VALUES = 'v1/full-count/v2_operators_values'
HEADERS = {'X-WFM-Domain': 'taxi'}

V2_OPERATORS_VALUES = constants.FullCountHandlerNames.v2_operators_values


def build_tst_request(handler_name: str, params: tp.Dict[str, tp.Any]):
    return {'filter': {handler_name: {**params, 'limit': 1000, 'offset': 0}}}


@pytest.mark.now('2020-07-27T00:00:00')
@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_result',
    [
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {'yandex_uids': ['uid1'], 'skills': ['hokage']},
            ),
            200,
            1,
            id='0',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value, {'supervisors': ['aladin227']},
            ),
            200,
            1,
            id='1',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {'yandex_uids': ['uid1'], 'supervisors': ['aladin227']},
            ),
            200,
            1,
            id='2',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'yandex_uids': ['uid1', 'uid2'],
                    'supervisors': ['aladin227'],
                },
            ),
            200,
            1,
            id='3',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {'supervisors': ['123'], 'callcenters': ['1']},
            ),
            200,
            0,
            id='4',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {'supervisors': ['abd-damir'], 'yandex_uids': ['125']},
            ),
            200,
            0,
            id='5',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {'tag_filter': {'tags': ['driver', 'naruto']}, 'limit': 1000},
            ),
            200,
            1,
            id='7',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'tag_filter': {
                        'tags': ['driver', 'naruto'],
                        'connection_policy': 'disjunction',
                    },
                },
            ),
            200,
            2,
            id='8',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'tag_filter': {
                        'tags': ['driver', 'naruto'],
                        'ownership_policy': 'exclude',
                    },
                },
            ),
            200,
            3,
            id='9',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'tag_filter': {
                        'tags': ['driver', 'naruto'],
                        'ownership_policy': 'exclude',
                        'connection_policy': 'disjunction',
                    },
                },
            ),
            200,
            2,
            id='10',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {'rates': [1.0], 'roles': ['nokia']},
            ),
            200,
            0,
            id='11',
        ),
        pytest.param(
            build_tst_request(V2_OPERATORS_VALUES.value, {}), 200, 4, id='12',
        ),
        pytest.param(
            build_tst_request(V2_OPERATORS_VALUES.value, {'multiskill': True}),
            200,
            1,
            id='13',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value, {'mentor_login': 'mentor'},
            ),
            200,
            1,
            id='14',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'employment_date_filter': {
                        'datetime_from': '2020-01-01T00:00:00Z',
                    },
                },
            ),
            200,
            4,
            id='15',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'employment_date_filter': {
                        'datetime_from': '2021-01-01T00:00:00Z',
                    },
                },
            ),
            200,
            0,
            id='16',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'employment_date_filter': {
                        'datetime_from': '2020-01-01T00:00:00Z',
                        'datetime_to': '2020-01-02T00:00:00Z',
                    },
                },
            ),
            200,
            0,
            id='17',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'employment_date_filter': {
                        'datetime_to': '3000-01-02T00:00:00Z',
                    },
                },
            ),
            200,
            4,
            id='18',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {'datetime_from': '2020-08-01 00:00:00.0Z'},
                    ],
                },
            ),
            200,
            2,
            id='19',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {
                            'datetime_from': '2020-07-01 00:00:00.0Z',
                            'datetime_to': '2020-07-30 00:00:00.0Z',
                        },
                    ],
                },
            ),
            200,
            1,
            id='20',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {'datetime_to': '2020-07-15 00:00:00.0Z'},
                        {'datetime_from': '2020-07-15 00:00:00.0Z'},
                    ],
                },
            ),
            200,
            3,
            id='21',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'full_name': 'asdasdasdasd',
                    'schedule_types': [
                        {'datetime_from': '2020-07-15 00:00:00.0Z'},
                    ],
                },
            ),
            200,
            0,
            id='22',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value, {'schedule_types': [{}, {'id': 1}]},
            ),
            400,
            0,
            id='23',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {
                            'ids': [1],
                            'skills': ['tatarin'],
                            'secondary_skills': ['tatarin'],
                            'datetime_from': '2020-06-30 00:00:00.0Z',
                        },
                    ],
                },
            ),
            200,
            1,
            id='24',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {'ids': [1, 2], 'skills': ['hokage', 'skill12345']},
                    ],
                },
            ),
            200,
            1,
            id='25',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {
                            'ids': [1, 2, 4],
                            'skills': ['hokage'],
                            'datetime_from': '2020-07-15 00:00:00.0Z',
                        },
                    ],
                },
            ),
            200,
            2,
            id='26',
        ),
        pytest.param(
            build_tst_request(
                V2_OPERATORS_VALUES.value,
                {
                    'schedule_types': [
                        {
                            'ids': [1, 2],
                            'datetime_to': '2020-07-15 00:00:00.0Z',
                        },
                        {
                            'ids': [2, 4],
                            'datetime_from': '2020-07-15 00:00:00.0Z',
                        },
                    ],
                },
            ),
            200,
            3,
            id='27',
        ),
    ],
)
async def test_v2_operators_values_full_count(
        taxi_workforce_management_web,
        tst_request,
        expected_status,
        expected_result,
        mock_effrat_employees,
):
    mock_effrat_employees()

    res = await taxi_workforce_management_web.post(
        URI_V2_OPERATORS_VALUES, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    res_operators = await taxi_workforce_management_web.post(
        '/v2/operators/values',
        json=tst_request['filter']['v2_operators_values'],
        headers=HEADERS,
    )
    parsed_res_operators = await res_operators.json()
    parsed_full_count = await res.json()
    assert parsed_full_count == {'full_count': expected_result}
    assert parsed_full_count == {
        'full_count': parsed_res_operators['full_count'],
    }
