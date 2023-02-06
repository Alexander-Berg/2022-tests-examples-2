import pytest

from tests_cargo_corp import utils

BILLING_ID = 'billing_id'

LOCAL_CARD_ID_REGISTERED = 'LOCAL_CARD_ID_REGISTERED'
LOCAL_CLIENT_ID_REGISTERED = 'long_corp_client_id_length_32_02'
LOCAL_CLIENT_REGISTERED = {
    'id': LOCAL_CLIENT_ID_REGISTERED,
    'name': 'test_corp_client_name_registrated',
    'is_registration_finished': True,
}

LOCAL_CARD_ID_NOT_REGISTERED = 'LOCAL_CARD_ID_NOT_REGISTERED'
LOCAL_CLIENT_ID_NOT_REGISTERED = 'long_corp_client_id_length_32_03'
LOCAL_CLIENT_NOT_REGISTERED = {
    'id': LOCAL_CLIENT_ID_NOT_REGISTERED,
    'name': 'test_corp_client_name_not_registrated',
    'is_registration_finished': False,
}


async def prepare_client(prepare_multiple_clients, client_data):
    prepare_multiple_clients([client_data], card_id=client_data['id'])


async def prepare_billing_client(
        make_client_balance_upsert_request, billing_id, corp_client_id,
):
    request = {'billing_id': billing_id, 'contract': utils.PHOENIX_CONTRACT}
    response = await make_client_balance_upsert_request(
        corp_client_id, request,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    (
        'is_billing_client',
        'is_contract_active',
        'corp_client',
        'expected_code',
        'expected_response',
    ),
    (
        pytest.param(
            False,
            True,
            LOCAL_CLIENT_NOT_REGISTERED,
            500,
            {'code': '500', 'message': 'Internal Server Error'},
            id='card client',
        ),
        pytest.param(
            True,
            True,
            LOCAL_CLIENT_REGISTERED,
            200,
            {
                'is_client_registration_finished': True,
                'is_contract_active': True,
            },
            id='registered client',
        ),
        pytest.param(
            True,
            True,
            LOCAL_CLIENT_NOT_REGISTERED,
            200,
            {
                'is_client_registration_finished': False,
                'is_contract_active': True,
            },
            id='billing client, contract is active',
        ),
        pytest.param(
            True,
            False,
            LOCAL_CLIENT_NOT_REGISTERED,
            200,
            {
                'is_client_registration_finished': False,
                'is_contract_active': False,
            },
            id='billing client, contract is not active',
        ),
    ),
)
async def test_client_contract(
        taxi_cargo_corp,
        make_client_balance_upsert_request,
        prepare_multiple_clients,
        get_taxi_corp_contracts,
        is_billing_client,
        is_contract_active,
        corp_client,
        expected_code,
        expected_response,
):
    headers = {'X-B2B-Client-Id': corp_client['id']}

    get_taxi_corp_contracts.set_contracts(
        has_contracts=True,
        payment_type=utils.PHOENIX_CONTRACT['payment_type'],
        is_active=is_contract_active,
    )

    await prepare_client(prepare_multiple_clients, corp_client)

    if is_billing_client:
        await prepare_billing_client(
            make_client_balance_upsert_request, BILLING_ID, corp_client['id'],
        )

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/contract/get-active-status',
        headers=headers,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response
