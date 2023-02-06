import pytest

URI = 'v1/break-rules/values'
DELETE_URI = 'v1/break-rules/delete'
MODIFY_URI = 'v1/break-rules/modify'
HEADERS = {'X-Yandex-UID': 'uid1'}


def pop_not_modified_fields(provided_data, result):
    return {
        key: value for key, value in result.items() if key in provided_data
    }


@pytest.mark.pgsql('workforce_management', files=['simple_break_rules.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        (
            {
                'alias': 'new_rule',
                'shift_description': {
                    'skill': 'order',
                    'shift_duration_minutes_from': 120,
                    'shift_duration_minutes_to': 180,
                },
                'breaks': [
                    {
                        'type': 'technical',
                        'min_time_without_break_minutes': 60,
                        'max_time_without_break_minutes': 90,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': 0,
                'shift_description': {
                    'skill': 'order',
                    'shift_duration_minutes_from': 20,
                    'shift_duration_minutes_to': 40,
                },
                'breaks': [
                    {
                        'type': 'technical',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                ],
            },
            409,
        ),
        (
            {
                'id': 0,
                'revision_id': '2020-10-22T12:00:00.000000 +0000',
                'shift_description': {
                    'skill': 'order',
                    'shift_duration_minutes_from': 20,
                    'shift_duration_minutes_to': 40,
                },
                'breaks': [
                    {
                        'type': 'technical',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'min_time_from_start_minutes': 25,
                        'max_time_from_start_minutes': 35,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': 0,
                'revision_id': '2020-10-22T12:00:00.000000 +0000',
                'shift_description': {
                    'skill': 'order',
                    'shift_duration_minutes_from': 20,
                    'shift_duration_minutes_to': 40,
                },
                'breaks': [
                    {
                        'type': 'technical',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'min_time_from_start_minutes': 30,
                        'max_time_from_start_minutes': 35,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                ],
            },
            200,
        ),
        (
            {
                'id': 0,
                'revision_id': '2020-10-22T12:00:00.000000 +0000',
                'shift_description': {
                    'skill': 'order',
                    'shift_duration_minutes_from': 20,
                    'shift_duration_minutes_to': 40,
                },
                'breaks': [
                    {
                        'type': 'technical',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                    {
                        'type': 'dinner',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'min_time_from_start_minutes': 20,
                        'max_time_from_start_minutes': 40,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                ],
            },
            400,
        ),
        (
            {
                'id': 0,
                'revision_id': '2020-10-22T12:00:00.000000 +0000',
                'shift_description': {
                    'skill': 'order',
                    'shift_duration_minutes_from': 20,
                    'shift_duration_minutes_to': 40,
                },
                'breaks': [
                    {
                        'type': 'technical',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'count': 1,
                        'duration_minutes': 2,
                    },
                    {
                        'type': 'dinner',
                        'min_time_without_break_minutes': 10,
                        'max_time_without_break_minutes': 20,
                        'allowed_breaks_count_before': [],
                        'count': 1,
                        'duration_minutes': 2,
                    },
                ],
            },
            400,
        ),
    ],
)
async def test_modify(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        MODIFY_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return

    data = await res.json()
    for field_to_pop in ('revision_id', 'id'):
        data.pop(field_to_pop)
        tst_request.pop(field_to_pop, None)
    data = pop_not_modified_fields(tst_request, data)
    assert data == tst_request


@pytest.mark.pgsql('workforce_management', files=['simple_break_rules.sql'])
@pytest.mark.parametrize(
    'tst_request, expected_status,',
    [
        ({'id': 0}, 400),
        ({'id': 0, 'revision_id': '2020-10-22T13:00:00.000000 +0000'}, 409),
        ({'id': 0, 'revision_id': '2020-10-22T12:00:00.000000 +0000'}, 200),
    ],
)
async def test_delete(
        taxi_workforce_management_web,
        web_context,
        tst_request,
        expected_status,
):
    res = await taxi_workforce_management_web.post(
        DELETE_URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status
    success = True
    if expected_status > 200:
        success = False

    res = await taxi_workforce_management_web.get(URI, json=tst_request)
    assert res.status == 200

    data = await res.json()

    found = any([rule['id'] == tst_request['id'] for rule in data['rules']])

    assert not found or not success
