import pytest

DEFAULT_CLIENT = {
    'id': 'client3',
    'name': 'Имя клиента',
    'country': 'rus',
    'yandex_login': '',
    'is_trial': False,
    'billing_id': '',
    'features': [],
    'services': {'drive': {'parent_id': 12345, 'is_active': True}},
    'updated_at': '1532470703.0',
    'without_vat_contract': False,
}
SECOND_CLIENT = {
    'id': 'client1',
    'name': 'Имя другого клиента',
    'country': 'rus',
    'yandex_login': '',
    'is_trial': False,
    'billing_id': '',
    'features': [],
    'services': {'drive': {'parent_id': 12345, 'is_active': True}},
    'updated_at': '1532470703.0',
    'without_vat_contract': False,
}

CORP_CLIENTS_RESPONSE = {
    'clients': [DEFAULT_CLIENT],
    'skip': 0,
    'limit': 0,
    'amount': 0,
    'sort_field': 'name',
    'sort_direction': -1,
}


@pytest.mark.parametrize(
    ['search', 'limit', 'offset', 'expected_response'],
    [
        pytest.param(
            '857ddf8d410446679b198f80324be32e',
            1,
            0,
            {
                'items': [
                    {
                        'client_id': 'client3',
                        'client_name': 'Имя клиента',
                        'cost_centers_id': 'cost_center_1',
                        'email': 'example@yandex-team.ru',
                        'fullname': 'user in root department',
                        'id': '857ddf8d410446679b198f80324be32e',
                        'is_active': True,
                        'is_deleted': False,
                        'limits': [
                            {
                                'limit_id': 'limit3_2_with_users',
                                'service': 'taxi',
                            },
                        ],
                        'phone': '+79654646542',
                    },
                ],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            id='common flow',
        ),
    ],
)
async def test_search_users_admin(
        web_app_client,
        mock_personal,
        mock_corp_clients,
        search,
        limit,
        offset,
        expected_response,
):
    mock_corp_clients.data.get_client_accurate_response = CORP_CLIENTS_RESPONSE

    response = await web_app_client.get(
        'admin/v2/users/search',
        params={'limit': limit, 'offset': offset, 'search': search},
    )
    response_data = await response.json()
    assert response_data == expected_response
