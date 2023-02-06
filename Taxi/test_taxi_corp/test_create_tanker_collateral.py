# pylint: disable = redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)

CONTRACTS = {
    'client_id_1': [
        {
            'PERSON_ID': 1,
            'SERVICES': [650, 672, 668],
            'EXTERNAL_ID': 'taxi_contract',
            'ID': 1,
            'IS_ACTIVE': 1,
        },
    ],
    'client_id_2': [
        {
            'PERSON_ID': 1,
            'SERVICES': [650],
            'EXTERNAL_ID': 'taxi_contract',
            'ID': 1,
            'IS_ACTIVE': 1,
        },
    ],
    'client_id_3': [
        {
            'PERSON_ID': 1,
            'SERVICES': [650, 672, 668, 1171],
            'EXTERNAL_ID': 'taxi_contract',
            'ID': 1,
            'IS_ACTIVE': 1,
        },
        {
            'PERSON_ID': 1,
            'SERVICES': [636],
            'EXTERNAL_ID': 'tanker_contract',
            'ID': 2,
            'IS_ACTIVE': 1,
        },
    ],
    'client_id_4': [
        {
            'PERSON_ID': 1,
            'SERVICES': [650, 672, 668],
            'EXTERNAL_ID': 'taxi_contract',
            'ID': 1,
            'IS_ACTIVE': 1,
        },
        {
            'PERSON_ID': 1,
            'SERVICES': [636],
            'EXTERNAL_ID': 'tanker_contract',
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

        @staticmethod
        @patch('taxi.clients.billing_v2.BalanceClient.create_offer')
        async def create_offer(operator_id, **kwargs):
            return {'ID': 123456, 'EXTERNAL_ID': 'tanker_offer'}

    return MockBalance()


@pytest.mark.config(
    CORP_OFFER_BALANCE_MANAGER_UIDS={'rus': {'__default__': [9999]}},
)
@pytest.mark.now(NOW.isoformat())
async def test_create_tanker_collateral(
        taxi_corp_auth_client, db, mock_balance, mock_corp_clients,
):
    data = {'external_id': 'taxi_contract'}

    response = await taxi_corp_auth_client.post(
        '/1.0/client/client_id_1/create-tanker-collateral', json=data,
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {}

    client = await db.corp_clients.find_one({'_id': 'client_id_1'})
    assert client['tanker_collateral_accept'] == {
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
    assert mock_balance.create_offer.calls == [
        {
            'kwargs': {
                'client_id': 'client_id_1',
                'person_id': 1,
                'country': 225,
                'region': 225,
                'payment_type': 2,
                'currency': 'RUB',
                'firm_id': 124,
                'manager_uid': 9999,
                'services': [636],
            },
            'operator_id': '0',
        },
    ]
    assert mock_balance.create_collateral.calls == [
        {
            'collateral_type': 1101,
            'contract_id': 1,
            'kwargs': {
                'print_form_type': 3,
                'link_contract_id': 123456,
                'services': [650, 672, 668, 1171],
                'sign': 1,
                'memo': 'Д/с на привязку Заправок к ЕД LEGALTAXI-16062',
                'num': 'Ф-б/н',
            },
            'operator_id': '0',
        },
    ]

    tanker_call = mock_corp_clients.service_tanker.next_call()
    assert tanker_call['request'].json == {
        'is_active': True,
        'is_visible': True,
    }


@pytest.mark.parametrize(
    ['client_id', 'data', 'expected_code', 'expected_response'],
    [
        pytest.param(
            'client_id_2',
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
                    ],
                },
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': '\'external_id\' is a required property',
                    },
                ],
                'message': 'Invalid input',
            },
            id='schema',
        ),
        pytest.param(
            'client_id_2',
            {'external_id': 'unknown'},
            400,
            {
                'code': 'GENERAL',
                'errors': [{'code': 'GENERAL', 'text': 'Contract not found'}],
                'message': 'Contract not found',
            },
            id='contract_not_found',
        ),
        pytest.param(
            'client_id_2',
            {'external_id': 'taxi_contract'},
            400,
            {
                'code': 'GENERAL',
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'Not available, not a common contract',
                    },
                ],
                'message': 'Not available, not a common contract',
            },
            id='not_common_contract',
        ),
        pytest.param(
            'client_id_3',
            {'external_id': 'taxi_contract'},
            400,
            {
                'code': 'GENERAL',
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'Not available, 1171 service exists',
                    },
                ],
                'message': 'Not available, 1171 service exists',
            },
            id='service_exists_1171',
        ),
        pytest.param(
            'client_id_4',
            {'external_id': 'taxi_contract'},
            400,
            {
                'code': 'GENERAL',
                'errors': [
                    {
                        'code': 'GENERAL',
                        'text': 'Not available, 636 service exists',
                    },
                ],
                'message': 'Not available, 636 service exists',
            },
            id='service_exists_636',
        ),
    ],
)
async def test_create_collateral_fail(
        taxi_corp_auth_client,
        mock_balance,
        client_id,
        data,
        expected_code,
        expected_response,
):
    response = await taxi_corp_auth_client.post(
        f'/1.0/client/{client_id}/create-tanker-collateral', json=data,
    )
    response_json = await response.json()

    assert response.status == expected_code, response_json
    assert response_json == expected_response
