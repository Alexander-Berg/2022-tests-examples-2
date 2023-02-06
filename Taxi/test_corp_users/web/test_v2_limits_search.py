import pytest


ACTIVE_SERVICES = {
    'taxi': {'is_active': True, 'is_visible': True},
    'eats2': {'is_active': True, 'is_visible': True},
    'drive': {'is_active': True, 'is_visible': True},
    'tanker': {'is_active': True, 'is_visible': True},
}


@pytest.mark.parametrize(
    ['query_params'],
    [pytest.param({'limit': 2, 'offset': 3}, id='with limit search param')],
)
async def test_search_limits(web_app_client, mock_corp_clients, query_params):
    mock_corp_clients.data.get_services_response = ACTIVE_SERVICES

    response = await web_app_client.get(
        '/v2/limits/search',
        params=dict(
            query_params, client_id='client3', performer_department_id='dep1',
        ),
    )

    response_data = await response.json()
    assert response_data == {
        'limits': [
            {
                'can_edit': True,
                'client_id': 'client3',
                'counters': {'users': 1},
                'department_id': 'dep1',
                'id': 'drive_limit',
                'is_default': False,
                'limits': {
                    'orders_cost': {'period': 'month', 'value': '1000'},
                },
                'service': 'drive',
                'title': 'drive limit',
            },
            {
                'can_edit': False,
                'client_id': 'client3',
                'counters': {'users': 0},
                'geo_restrictions': [],
                'id': 'eats2_limit_id_3',
                'is_default': False,
                'is_qr_enabled': False,
                'limits': {'orders_cost': {'period': 'day', 'value': '1000'}},
                'service': 'eats2',
                'time_restrictions': [],
                'title': 'eats2 limit with qr false',
            },
        ],
        'limit': 2,
        'offset': 3,
        'total_amount': 11,
    }


@pytest.mark.parametrize(
    [
        'query_params',
        'corp_clients_response',
        'found_limits_amount',
        'with_default_limit',
    ],
    [
        pytest.param(
            {}, ACTIVE_SERVICES, 11, True, id='without search params',
        ),
        pytest.param(
            {},
            {
                'taxi': {'is_active': True, 'is_visible': True},
                'drive': {'is_active': True, 'is_visible': True},
                'tanker': {'is_active': True, 'is_visible': True},
            },
            7,
            True,
            id='without search params (inactive eats2)',
        ),
        pytest.param(
            {'department_id': 'dep1'}, ACTIVE_SERVICES, 6, True, id='our dep',
        ),
        pytest.param(
            {'department_id': 'dep2'},
            ACTIVE_SERVICES,
            1,
            False,
            id='another dep',
        ),
        pytest.param(
            {'limit': 1},
            ACTIVE_SERVICES,
            1,
            True,
            id='with limit search param',
        ),
        pytest.param(
            {'offset': 1},
            ACTIVE_SERVICES,
            10,
            False,
            id='with offset search param',
        ),
        pytest.param(
            {'service': 'taxi'}, ACTIVE_SERVICES, 5, True, id='taxi limits',
        ),
        pytest.param(
            {'service': 'eats2'}, ACTIVE_SERVICES, 4, True, id='eats2 limits',
        ),
        pytest.param(
            {'service': 'tanker'},
            ACTIVE_SERVICES,
            1,
            True,
            id='tanker limits',
        ),
        pytest.param(
            {'search': 'limit3.2'},
            ACTIVE_SERVICES,
            5,
            True,
            id='search by name',
        ),
    ],
)
async def test_search_limits_count(
        web_app_client,
        mock_corp_clients,
        query_params,
        corp_clients_response,
        found_limits_amount,
        with_default_limit,
):
    mock_corp_clients.data.get_services_response = corp_clients_response

    response = await web_app_client.get(
        '/v2/limits/search', params=dict(query_params, client_id='client3'),
    )
    response_data = await response.json()
    assert len(response_data['limits']) == found_limits_amount, response_data
    if with_default_limit:
        assert response_data['limits'][0].get('is_default')
