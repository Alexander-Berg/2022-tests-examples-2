import pytest


URI = 'v1/operators/shift'
HEADERS = {'X-WFM-Domain': 'taxi'}
WRONG_HEADERS = {'X-WFM-Domain': 'wrong'}

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
@pytest.mark.config(WORKFORCE_MANAGEMENT_DOMAIN_FILTER_ENABLED=True)
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        pytest.param(
            {'headers': HEADERS, 'id': 1}, 200, SHIFT_1, id='shift_1',
        ),
        pytest.param(
            {'headers': HEADERS, 'id': 2}, 200, SHIFT_2, id='shift_2',
        ),
        pytest.param(
            {'headers': WRONG_HEADERS, 'id': 1}, 404, None, id='wrong_headers',
        ),
        pytest.param({'headers': HEADERS, 'id': 10}, 404, None, id='wrong_id'),
        pytest.param(
            {'headers': HEADERS, 'id': 6},
            200,
            SHIFT_6,
            id='actual_shift_events',
        ),
    ],
)
async def test_shift_get(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
        expected_res,
        mock_effrat_employees,
):
    headers = tst_request.pop('headers')
    res = await taxi_workforce_management_web.get(
        URI, headers=headers, params=tst_request,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    body = await res.json()

    if 'audit' in body:
        body['audit'].pop('updated_at')

    assert body == expected_res
