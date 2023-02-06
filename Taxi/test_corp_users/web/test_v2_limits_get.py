import pytest


@pytest.mark.parametrize(
    [
        'limit_id',
        'performer_department_id',
        'status_code',
        'expected_response',
    ],
    [
        # client role can view and edit all limits
        pytest.param(
            'limit1',
            None,
            200,
            {
                'can_edit': True,
                'categories': ['econom'],
                'client_id': 'client1',
                'geo_restrictions': [
                    {
                        'destination': 'destination_restriction_id',
                        'source': 'source_restriction_1',
                    },
                ],
                'id': 'limit1',
                'is_default': False,
                'limits': {
                    'orders_amount': {'period': 'day', 'value': 12},
                    'orders_cost': {'period': 'month', 'value': '1000'},
                },
                'service': 'taxi',
                'time_restrictions': [
                    {
                        'days': ['mo', 'tu', 'we', 'th', 'fr'],
                        'end_time': '18:40:00',
                        'start_time': '10:30:00',
                        'type': 'weekly_date',
                    },
                ],
                'title': 'limit',
                'counters': {'users': 0},
            },
            id='client role, edit True',
        ),
        # dep role can view but can't edit limit from higher dep
        pytest.param(
            'limit3_1',
            'dep1',
            200,
            {
                'can_edit': False,
                'categories': [],
                'client_id': 'client3',
                'geo_restrictions': [],
                'id': 'limit3_1',
                'service': 'taxi',
                'time_restrictions': [],
                'title': 'limit3.1',
                'is_default': False,
                'limits': {},
                'counters': {'users': 0},
            },
            id='dep role, edit False',
        ),
        # dep role can view and edit limit from same dep
        pytest.param(
            'limit3_2',
            'dep1',
            200,
            {
                'can_edit': True,
                'categories': [],
                'client_id': 'client3',
                'counters': {'users': 0},
                'department_id': 'dep1',
                'geo_restrictions': [],
                'id': 'limit3_2',
                'service': 'taxi',
                'time_restrictions': [],
                'title': 'limit3.2',
                'is_default': False,
                'limits': {},
            },
            id='dep role, edit True',
        ),
        # dep role can view from another dep
        pytest.param(
            'limit3_3',
            'dep1',
            200,
            {
                'can_edit': False,
                'categories': [],
                'client_id': 'client3',
                'department_id': 'dep2',
                'geo_restrictions': [],
                'id': 'limit3_3',
                'service': 'taxi',
                'time_restrictions': [],
                'title': 'limit3.3',
                'is_default': False,
                'limits': {},
                'counters': {'users': 0},
            },
            id='permission denied',
        ),
    ],
)
async def test_get_limit_success(
        web_app_client,
        limit_id,
        performer_department_id,
        status_code,
        expected_response,
):
    params = {'limit_id': limit_id}
    if performer_department_id:
        params['performer_department_id'] = performer_department_id
    response = await web_app_client.get('/v2/limits', params=params)
    assert response.status == status_code
    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    ['limit_id', 'status_code'],
    [pytest.param('not_existed_limit', 404, id='not found')],
)
async def test_get_limit_fail(web_app_client, limit_id, status_code):
    response = await web_app_client.get(
        '/v2/limits', params={'limit_id': limit_id},
    )

    assert response.status == status_code
    response_data = await response.json()
    assert response_data == {
        'code': 'NOT_FOUND',
        'message': 'Not found',
        'reason': 'Limit not_existed_limit not found',
    }
