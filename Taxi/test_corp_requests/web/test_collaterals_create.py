import pytest

from corp_requests import consts


CONTRACT = {
    'contract_id': 345678,
    'external_id': '3456789/22',
    'billing_client_id': 'billing_id_3',
    'billing_person_id': 'billing_person_id',
    'payment_type': 'prepaid',
    'is_offer': True,
    'currency': 'RUB',
    'services': ['taxi'],
    'is_active': True,
}


@pytest.mark.parametrize(
    ['client_id', 'billing_id', 'contract_id', 'collateral_type'],
    [
        pytest.param(
            'client_id_1',
            'billing_id_1',
            123456,
            'common',
            id='no_collaterals',
        ),
        pytest.param(
            'client_id_2',
            'billing_id_2',
            234567,
            'tanker',
            id='another_collateral',
        ),
    ],
)
async def test_collaterals_create(
        web_app_client,
        db,
        stq,
        client_id,
        contract_id,
        billing_id,
        collateral_type,
        mock_corp_clients,
):
    mock_corp_clients.data.get_client_response = {
        'id': client_id,
        'billing_id': billing_id,
    }
    mock_corp_clients.data.get_contracts_response = {
        'contracts': [{**CONTRACT, 'contract_id': contract_id}],
    }

    response = await web_app_client.post(
        '/v1/collaterals/create',
        json={
            'client_id': client_id,
            'contract_id': contract_id,
            'collateral_type': collateral_type,
            'performer_login_id': 'performer_login_id',
        },
    )

    assert response.status == 200

    collateral = await db.corp_collaterals.find_one(
        {
            'client_id': client_id,
            'contract_id': contract_id,
            'collateral_type': collateral_type,
        },
    )
    assert collateral is not None

    assert stq.corp_create_collateral.times_called == 1

    call_kwargs = stq.corp_create_collateral.next_call()['kwargs'][
        'collateral'
    ]
    for field in ('_id', 'created', 'updated'):
        call_kwargs.pop(field)

    assert call_kwargs == {
        'client_id': client_id,
        'contract_id': contract_id,
        'billing_id': billing_id,
        'collateral_type': collateral_type,
        'performer_login_id': 'performer_login_id',
        'status': consts.CollateralStatus.ACCEPTING,
    }


@pytest.mark.parametrize(
    [
        'client_id',
        'contract_id',
        'collateral_type',
        'get_client_response',
        'get_contracts_response',
        'expected_response',
    ],
    [
        pytest.param(
            'client_id_3',
            345678,
            'common_tanker',
            {'id': 'client_id_3', 'billing_id': 'billing_id_3'},
            {'contracts': [CONTRACT]},
            {
                'code': 'collateral-duplicate-request',
                'message': 'such collateral already exists',
                'details': {},
            },
            id='same_collateral',
        ),
        pytest.param(
            'client_id_unknown',
            345678,
            'common',
            None,
            {'contracts': [CONTRACT]},
            {
                'code': 'client-not-found',
                'details': {},
                'message': 'such client doesnt exist',
            },
            id='client_not_found',
        ),
        pytest.param(
            'client_id_3',
            345678,
            'tanker',
            {'id': 'client_id_3', 'billing_id': 'billing_id_3'},
            {'contracts': []},
            {
                'code': 'contract-not-found',
                'details': {},
                'message': 'such contract doesnt exist',
            },
            id='contract_not_found',
        ),
    ],
)
async def test_collaterals_create_fail(
        web_app_client,
        client_id,
        contract_id,
        collateral_type,
        get_client_response,
        get_contracts_response,
        expected_response,
        mock_corp_clients,
):
    mock_corp_clients.data.get_client_response = get_client_response
    mock_corp_clients.data.get_contracts_response = get_contracts_response

    response = await web_app_client.post(
        '/v1/collaterals/create',
        json={
            'client_id': client_id,
            'contract_id': contract_id,
            'collateral_type': collateral_type,
            'performer_login_id': 'performer_login_id',
        },
    )

    assert response.status == 400
    response_json = await response.json()
    assert response_json == expected_response
