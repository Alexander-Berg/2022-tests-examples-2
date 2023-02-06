import pytest

NOW = '2020-01-02T10:00:00+03:00'

CORP_CLIENTS_RESPONSE = {
    'clients': [
        {
            'id': 'client_id_1',
            'name': 'ООО Ромашка',
            'country': 'rus',
            'yandex_login': '',
            'is_trial': False,
            'billing_id': '',
            'features': [],
            'services': {},
            'updated_at': '1532470703.0',
            'without_vat_contract': False,
        },
        {
            'id': 'client_id_2',
            'name': 'ООО Рожки и Копытца',
            'country': 'rus',
            'yandex_login': '',
            'is_trial': False,
            'billing_id': '',
            'features': [],
            'services': {},
            'updated_at': '1532470703.0',
            'without_vat_contract': False,
        },
    ],
    'skip': 0,
    'limit': 0,
    'amount': 0,
    'sort_field': 'name',
    'sort_direction': -1,
}

CORP_INT_API_RESPONSE = {
    'statuses': [
        {
            'client_id': 'client_id_1',
            'can_order': True,
            'zone_available': True,
        },
    ],
}

CORP_INT_API_FAILED_RESPONSE = {
    'statuses': [
        {
            'client_id': 'client_id_1',
            'can_order': False,
            'zone_available': True,
        },
    ],
}


async def test_fetch_eats_non_existed_users(web_app_client):
    response = await web_app_client.post(
        '/v1/users-limits/eats/fetch', headers=_get_headers('per_1'),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'users': []}


@pytest.mark.now(NOW)
async def test_fetch_eats_failed_can_order(
        web_app_client,
        mock_corp_clients,
        mock_corp_int_api,
        mock_billing_reports,
        load_json,
):
    mock_corp_clients.data.get_client_accurate_response = CORP_CLIENTS_RESPONSE
    mock_corp_int_api.data.clients_can_order_eats = (
        CORP_INT_API_FAILED_RESPONSE
    )
    mock_billing_reports.data.balances_select = load_json(
        'billing_reports_get_balances.json',
    )

    response = await web_app_client.post(
        '/v1/users-limits/eats/fetch',
        headers=_get_headers('personal_phone_id_3'),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'users': []}


@pytest.mark.parametrize(
    ['personal_phone_id', 'expected_users'],
    [
        pytest.param(
            'personal_phone_id_2',
            [
                {
                    'client_id': 'client_id_1',
                    'client_name': 'ООО Ромашка',
                    'id': 'test_user_2',
                    'limits': [
                        {
                            'is_qr_enabled': False,
                            'limit_id': 'eats2_limit_id_1',
                            'limits': {},
                            'time_restrictions': [],
                        },
                    ],
                },
            ],
            id='unlimited_eats',
        ),
        pytest.param(
            'personal_phone_id_3',
            [
                {
                    'client_id': 'client_id_1',
                    'client_name': 'ООО Ромашка',
                    'id': 'test_user_3',
                    'limits': [
                        {
                            'is_qr_enabled': True,
                            'limit_id': 'eats2_limit_id_2',
                            'limits': {
                                'orders_cost': {
                                    'balance': '591.67',
                                    'currency': 'RUB',
                                    'currency_sign': '₽',
                                    'period': 'month',
                                    'value': '833.33',
                                },
                            },
                            'time_restrictions': [
                                {
                                    'days': ['mo', 'tu', 'we', 'th', 'fr'],
                                    'end_time': '18:40:00',
                                    'start_time': '10:30:00',
                                    'type': 'weekly_date',
                                },
                            ],
                        },
                    ],
                },
            ],
            id='common_eats_limit',
        ),
    ],
)
@pytest.mark.now(NOW)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'currency': 'RUB', 'currency_sign': '₽', 'vat': 0.2},
    },
)
async def test_fetch_eats_success(
        web_app_client,
        mock_corp_clients,
        mock_corp_int_api,
        mock_billing_reports,
        load_json,
        personal_phone_id,
        expected_users,
):
    mock_corp_clients.data.get_client_accurate_response = CORP_CLIENTS_RESPONSE
    mock_corp_int_api.data.clients_can_order_eats = CORP_INT_API_RESPONSE
    mock_billing_reports.data.balances_select = load_json(
        'billing_reports_get_balances.json',
    )

    response = await web_app_client.post(
        '/v1/users-limits/eats/fetch', headers=_get_headers(personal_phone_id),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'users': expected_users}


@pytest.mark.parametrize(
    ['corp_int_api_response', 'expected_users_len'],
    [
        pytest.param(
            {'statuses': CORP_INT_API_RESPONSE['statuses'] * 2},
            2,
            id='all_clients_can_order',
        ),
        pytest.param(
            {
                'statuses': (
                    CORP_INT_API_RESPONSE['statuses']
                    + CORP_INT_API_FAILED_RESPONSE['statuses']
                ),
            },
            1,
            id='one_client_cannot_order',
        ),
    ],
)
async def test_fetch_eats_multiple_users(
        web_app_client,
        mock_corp_clients,
        mock_corp_int_api,
        mock_billing_reports,
        load_json,
        corp_int_api_response,
        expected_users_len,
):
    mock_corp_clients.data.get_client_accurate_response = CORP_CLIENTS_RESPONSE
    mock_corp_int_api.data.clients_can_order_eats = corp_int_api_response
    mock_billing_reports.data.balances_select = load_json(
        'billing_reports_get_balances.json',
    )

    response = await web_app_client.post(
        '/v1/users-limits/eats/fetch',
        headers=_get_headers('personal_phone_id_1'),
    )

    assert response.status == 200
    content = await response.json()
    assert len(content['users']) == expected_users_len


def _get_headers(personal_phone_id: str) -> dict:
    return {
        'X-Yandex-UID': '4062824',
        'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}',
    }
