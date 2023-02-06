import pytest


@pytest.mark.parametrize(
    'contract_ids,expected_status,expected_response',
    [
        (
            [553918, 1040309],
            200,
            [
                {
                    'ContractID': 553918,
                    'Balance': '0',
                    'CurrMonthCharge': '0',
                    'CommissionToPay': None,
                    'CurrMonthBonus': '0',
                    'BonusLeft': '0',
                    'ClientID': 103917439,
                    'OfferAccepted': 1,
                    'Currency': 'RUB',
                    'NettingLastDt': None,
                    'PersonalAccountExternalID': 'ЛСТ-1259357521-1',
                    'DT': '2019-03-15 15:46:59.315361',
                },
            ],
        ),
        (
            [553918, 553920],
            200,
            [
                {
                    'ContractID': 553918,
                    'Balance': '0',
                    'CurrMonthCharge': '0',
                    'CommissionToPay': None,
                    'CurrMonthBonus': '0',
                    'BonusLeft': '0',
                    'ClientID': 103917439,
                    'OfferAccepted': 1,
                    'Currency': 'RUB',
                    'NettingLastDt': None,
                    'PersonalAccountExternalID': 'ЛСТ-1259357521-1',
                    'DT': '2019-03-15 15:46:59.315361',
                },
                {
                    'ContractID': 553920,
                    'Balance': '10000',
                    'CurrMonthCharge': '0',
                    'CommissionToPay': None,
                    'CurrMonthBonus': '0',
                    'BonusLeft': '0',
                    'ClientID': 104871401,
                    'OfferAccepted': None,
                    'Currency': 'RUB',
                    'NettingLastDt': None,
                    'PersonalAccountExternalID': 'ЛСТ-1261397230-1',
                    'DT': '2019-03-15 15:46:59.312176',
                },
            ],
        ),
        ([1009624, 1009627], 200, []),
        ([553919], 200, []),
        ([], 400, None),
    ],
)
async def test_get_client_balances(
        taxi_billing_replication_client,
        contract_ids,
        expected_status,
        expected_response,
):
    response = await taxi_billing_replication_client.request(
        'POST', '/balance/bulk_retrieve/', json={'contract_ids': contract_ids},
    )

    assert response.status == expected_status
    if expected_status == 200:
        response_data = await response.json()
        assert (
            sorted(response_data, key=lambda x: x['ContractID'])
            == expected_response
        )


@pytest.mark.parametrize(
    'params, expected_contract_ids,expected_max_revision',
    [({'revision': 2, 'limit': 2}, {1009624, 1009627}, 4)],
)
async def test_get_balances_by_revision(
        taxi_billing_replication_client,
        params,
        expected_contract_ids,
        expected_max_revision,
):
    response = await taxi_billing_replication_client.request(
        'GET', '/v1/balances/by_revision/', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert {
        balance['ContractID'] for balance in response_data['balances']
    } == expected_contract_ids
    assert expected_max_revision == response_data['max_revision']
