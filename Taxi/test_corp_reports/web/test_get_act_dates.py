import pytest

_CLIENT = 'some_client_id'
_GET_CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'contract_id': 123456,
            'external_id': 'some_contract_eid',
            'billing_client_id': '1',
            'billing_person_id': '1',
            'payment_type': 'prepaid',
            'is_offer': True,
            'currency': 'RUB',
            'services': [],
        },
        {
            'contract_id': 123450,
            'external_id': 'some_empty_contract_eid',
            'billing_client_id': '2',
            'billing_person_id': '2',
            'payment_type': 'prepaid',
            'is_offer': True,
            'currency': 'RUB',
            'services': [],
        },
    ],
}


@pytest.mark.parametrize(
    ['contract_id', 'expected_response'],
    [
        pytest.param(
            123456,
            {
                'detailed_dates': [
                    {'act_date': '2021-11', 'is_correct': False},
                    {'act_date': '2021-12', 'is_correct': True},
                ],
            },
            id='with detailed dates',
        ),
        pytest.param(
            123450,
            {'detailed_dates': []},
            id='with empty detailed dates (no corp_detailed_acts docs found)',
        ),
    ],
)
@pytest.mark.config(CORP_REPORTS_ACT_DATES=['2021-10', '2021-11', '2021-12'])
async def test_get_dates(
        web_app_client, mock_corp_clients, contract_id, expected_response,
):
    mock_corp_clients.data.get_contracts_response = _GET_CONTRACTS_RESPONSE
    response = await web_app_client.get(
        '/corp-reports/v1/reports/act-dates',
        params={'client_id': _CLIENT, 'contract_id': contract_id},
    )
    assert response.status == 200
    assert (await response.json()) == expected_response


@pytest.mark.config(CORP_REPORTS_ACT_DATES=['2021-10', '2021-11', '2021-12'])
async def test_404(web_app_client, mock_corp_clients):
    contract_id = 100500  # invalid contract
    mock_corp_clients.data.get_contracts_response = _GET_CONTRACTS_RESPONSE
    response = await web_app_client.get(
        '/corp-reports/v1/reports/act-dates',
        params={'client_id': _CLIENT, 'contract_id': contract_id},
    )
    assert response.status == 404
    assert (await response.json()) == {
        'code': '404',
        'message': 'Contract not found',
    }
