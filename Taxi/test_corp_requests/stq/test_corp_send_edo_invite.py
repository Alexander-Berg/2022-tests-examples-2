import pytest

from corp_requests.stq import corp_send_edo_invite


CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'contract_id': 15384971,
            'external_id': '3553886/21',
            'billing_client_id': '1111',
            'billing_person_id': '5555',
            'payment_type': 'prepaid',
            'is_offer': True,
            'currency': 'RUB',
            'services': ['taxi', 'cargo'],
            'is_active': True,
        },
    ],
}

BASE_STQ_PARAMS = {
    'client_id': 'client_id_1',
    'organization': 'market',
    'operator': 'diadoc',
}

BASE_BILLING_RESPONSE = [{'INN': '123', 'KPP': '567', 'ID': '5555'}]

BASE_EXPECTED_INVITE_REQUEST = {
    'client_id': 'client_id_1',
    'company_name': 'ООО Маркет',
    'inn': '123',
    'operator': 'diadoc',
    'organization': 'market',
}


@pytest.mark.parametrize(
    [
        'stq_params',
        'balance_response',
        'client_has_kpp',
        'email',
        'is_email_valid',
        'expected_invite_request',
    ],
    [
        pytest.param(
            BASE_STQ_PARAMS,
            BASE_BILLING_RESPONSE,
            True,
            'example@yandex.ru',
            True,
            {
                'client_id': 'client_id_1',
                'company_name': 'ООО Маркет',
                'inn': '123',
                'operator': 'diadoc',
                'organization': 'market',
                'kpp': '567',
                'email': 'example@yandex.ru',
            },
            id='with_kpp',
        ),
        pytest.param(
            BASE_STQ_PARAMS,
            [{'INN': '123', 'ID': '5555'}],
            False,
            'example@yandex.ru',
            True,
            {
                'client_id': 'client_id_1',
                'company_name': 'ООО Маркет',
                'inn': '123',
                'operator': 'diadoc',
                'organization': 'market',
                'email': 'example@yandex.ru',
            },
            id='without_kpp',
        ),
        # такая почта считается невалидной в uzedo
        pytest.param(
            BASE_STQ_PARAMS,
            BASE_BILLING_RESPONSE,
            False,
            'example@яндекс.ру',
            False,
            {
                'client_id': 'client_id_1',
                'company_name': 'ООО Маркет',
                'inn': '123',
                'operator': 'diadoc',
                'organization': 'market',
                'kpp': '567',
            },
            id='invalid_email',
        ),
        pytest.param(
            BASE_STQ_PARAMS,
            BASE_BILLING_RESPONSE,
            True,
            'example@yandex.ru',
            True,
            {
                'client_id': 'client_id_1',
                'company_name': 'ООО Маркет',
                'operator': 'diadoc',
                'organization': 'market',
                'inn': '000',
                'kpp': '111',
                'email': 'example@yandex.ru',
            },
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'enabled': True,
                    'clients': {
                        'client_id_1': {
                            'diadoc': {'inn': '000', 'kpp': '111'},
                        },
                    },
                },
            ),
            id='map_inn_by_client_id',
        ),
        pytest.param(
            {**BASE_STQ_PARAMS, 'passport_login': 'market_login'},
            BASE_BILLING_RESPONSE,
            True,
            'example@yandex.ru',
            True,
            {
                'client_id': 'client_id_1',
                'company_name': 'ООО Маркет',
                'operator': 'diadoc',
                'organization': 'market',
                'inn': '555',
                'email': 'example@yandex.ru',
            },
            marks=pytest.mark.config(
                CORP_EDO_TESTING_CLIENTS_MAPPING={
                    'enabled': True,
                    'clients': {'market_login': {'diadoc': {'inn': '555'}}},
                },
            ),
            id='map_inn_by_passport_login',
        ),
    ],
)
async def test_send_edo_invite(
        patch,
        mockserver,
        db,
        stq3_context,
        stq,
        mock_corp_clients,
        stq_params,
        balance_response,
        client_has_kpp,
        email,
        is_email_valid,
        expected_invite_request,
):
    @mockserver.handler('/corp-edo/v1/invitations/create')
    async def _create_invite(request):
        return mockserver.make_response(json={})

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_persons')
    async def _get_client_persons(*args, **kwargs):
        return balance_response

    mock_corp_clients.data.get_client_response = {
        'id': 'client_id_1',
        'email': email,
        'country': 'rus',
        'billing_name': 'ООО Маркет',
    }
    mock_corp_clients.data.get_contracts_response = CONTRACTS_RESPONSE

    await corp_send_edo_invite.task(stq3_context, **stq_params)

    assert _create_invite.times_called == 1
    assert (
        _create_invite.next_call()['request'].json == expected_invite_request
    )
