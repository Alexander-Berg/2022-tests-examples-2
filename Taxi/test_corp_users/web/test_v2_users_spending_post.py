import pytest


NOW = '2020-01-02T10:00:00+03:00'

CORP_CLIENTS_RESPONSE = {
    'clients': [
        {
            'id': 'client3',
            'name': '',
            'country': 'rus',
            'yandex_login': '',
            'is_trial': False,
            'billing_id': '',
            'features': [],
            'services': {'drive': {'parent_id': 12345, 'is_active': True}},
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

DRIVE_RESPONSE = {
    'accounts': {
        'drive_user_id_1': [
            {'details': {'expenditure': 18200}, 'parent': {'id': 12345}},
        ],
    },
}


@pytest.mark.parametrize(
    ['user_ids', 'status_code'],
    [
        pytest.param(['test_user_1', 'test_user_3'], 200, id='common flow'),
        pytest.param(
            ['test_user_1', '857ddf8d410446679b198f80324be32e'],
            403,
            id='user from another dep',
        ),
        pytest.param(['client1_user1'], 403, id='user from another client'),
        pytest.param(
            ['test_user_1', 'not_existed_user'], 404, id='not existed user',
        ),
    ],
)
@pytest.mark.now(NOW)
@pytest.mark.config(CORP_BILLING_ACCOUNTS_CHUNK=20)
async def test_get_users_spending(
        web_app_client,
        load_json,
        mock_corp_clients,
        mock_billing_reports,
        mock_drive,
        user_ids,
        status_code,
):
    mock_corp_clients.data.get_client_accurate_response = CORP_CLIENTS_RESPONSE
    mock_billing_reports.data.balances_select = load_json(
        'billing_reports_get_balances.json',
    )
    mock_drive.data.drive_accounts_response = DRIVE_RESPONSE

    response = await web_app_client.post(
        '/v2/users-spending',
        json={
            'user_ids': user_ids,
            'client_id': 'client3',
            'performer_department_id': 'dep1',
        },
    )
    assert response.status == status_code
    if response.status == 200:
        response_data = await response.json()
        assert response_data == {
            'items': {
                'test_user_1': {
                    'limit3_2_eats2': {'spent': '320'},
                    'limit3_2_tanker': {'spent': '340'},
                    'limit3_2_with_users': {'spent': '290'},
                    'drive_limit': {'spent': '182'},
                },
                'test_user_3': {'limit3_2_with_users': {'spent': '0'}},
            },
        }
