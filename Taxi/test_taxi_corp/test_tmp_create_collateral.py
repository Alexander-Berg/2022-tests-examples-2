# pylint: disable = redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)

CONTRACTS = {
    'client_id_1': [
        {
            'SERVICES': [650, 135],
            'EXTERNAL_ID': 'taxi_contract',
            'ID': 1,
            'IS_ACTIVE': 1,
        },
    ],
    'client_id_2': [
        {
            'SERVICES': [650],
            'EXTERNAL_ID': 'taxi_contract',
            'ID': 1,
            'IS_ACTIVE': 1,
        },
        {
            'SERVICES': [672],
            'EXTERNAL_ID': 'drive_contract',
            'ID': 2,
            'IS_ACTIVE': 1,
        },
    ],
}


@pytest.fixture
def mock_balance(patch):
    class MockBalance:
        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
        async def get_client_contracts(client_id: str, *args, **kwargs):
            return CONTRACTS[client_id]

        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.create_collateral')
        async def create_collateral(
                operator_id, contract_id, collateral_type, **kwargs,
        ):
            return {}

    return MockBalance()


@pytest.mark.now(NOW.isoformat())
async def test_create_collateral(
        taxi_corp_auth_client, db, mock_balance, mock_corp_clients,
):
    data = {'external_id': 'taxi_contract', 'services': ['drive']}

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client_id_1/tmp-create-collateral', json=data,
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    client = await db.corp_clients.find_one({'_id': 'client_id_1'})
    assert client['collateral_accept'] == {
        'accepted': True,
        'updated': NOW,
        'performer': 'login',
    }

    assert mock_balance.get_client_contracts.calls == [
        {
            'args': (),
            'client_id': 'client_id_1',
            'kwargs': {'contract_signed': False},
        },
    ]
    assert mock_balance.create_collateral.calls == [
        {
            'collateral_type': 1001,
            'contract_id': 1,
            'kwargs': {
                'print_form_type': 3,
                'services': [650, 135, 668, 672],
                'sign': 1,
                'memo': 'ДС о переходе на единый договор создан автоматически LEGALTAXI-4823',  # noqa: E501
                'num': 'Ф-б/н',
            },
            'operator_id': '0',
        },
    ]

    assert not mock_corp_clients.service_eats2.has_calls

    drive_call = mock_corp_clients.service_drive.next_call()
    assert drive_call['request'].json == {
        'is_active': True,
        'is_visible': True,
    }


@pytest.mark.parametrize(
    'data, expected_code, expected_response',
    [
        pytest.param(
            {},
            400,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': (
                                '\'external_id\' is a required property'
                            ),
                            'path': [],
                        },
                        {
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'message': '\'services\' is a required property',
                            'path': [],
                        },
                    ],
                },
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': '\'external_id\' is a required property',
                    },
                    {
                        'code': 'GENERAL',
                        'text': '\'services\' is a required property',
                    },
                ],
                'message': 'Invalid input',
            },
            id='schema',
        ),
        pytest.param(
            {'external_id': 'unknown', 'services': ['eats2', 'drive']},
            400,
            {
                'code': 'GENERAL',
                'errors': [{'code': 'GENERAL', 'text': 'Contract not found'}],
                'message': 'Contract not found',
            },
            id='contract_not_found',
        ),
        pytest.param(
            {'external_id': 'taxi_contract', 'services': ['drive']},
            400,
            {
                'code': 'GENERAL',
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'Not available, service exists',
                    },
                ],
                'message': 'Not available, service exists',
            },
            id='service_exists',
        ),
    ],
)
async def test_create_collateral_fail(
        taxi_corp_auth_client,
        mock_balance,
        data,
        expected_code,
        expected_response,
):
    response = await taxi_corp_auth_client.post(
        '/1.0/client/client_id_2/tmp-create-collateral', json=data,
    )
    response_json = await response.json()

    assert response.status == expected_code, response_json
    assert response_json == expected_response
