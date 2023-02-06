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
                    'service_id': 111,
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
                    'DT': '2019-03-15 15:46:59',
                },
            ],
        ),
        (
            [553918, 553920],
            200,
            [
                {
                    'ContractID': 553918,
                    'service_id': 111,
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
                    'DT': '2019-03-15 15:46:59',
                },
                {
                    'ContractID': 553920,
                    'service_id': 1161,
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
                    'DT': '2019-03-15 15:46:59',
                },
            ],
        ),
        # the contract has balances for 2 services
        (
            [553921],
            200,
            [
                {
                    'Balance': '0',
                    'BonusLeft': '0',
                    'ClientID': 105423433,
                    'CommissionToPay': None,
                    'ContractID': 553921,
                    'CurrMonthBonus': '0',
                    'CurrMonthCharge': '0',
                    'Currency': 'RUB',
                    'DT': '2019-02-20 23:32:37',
                    'NettingLastDt': None,
                    'OfferAccepted': 1,
                    'PersonalAccountExternalID': 'ЛСТ-1262870339-1',
                    'service_id': 111,
                },
                {
                    'Balance': '0',
                    'BonusLeft': '0',
                    'ClientID': 105423433,
                    'CommissionToPay': None,
                    'ContractID': 553921,
                    'CurrMonthBonus': '0',
                    'CurrMonthCharge': '0',
                    'Currency': 'RUB',
                    'DT': '2019-02-20 23:32:37',
                    'NettingLastDt': None,
                    'OfferAccepted': 1,
                    'PersonalAccountExternalID': 'ЛСТ-1262870339-1',
                    'service_id': 1161,
                },
            ],
        ),
        # get & merge balances from 2 tables
        (
            [553921, 553922],
            200,
            [
                {
                    'Balance': '0',
                    'BonusLeft': '0',
                    'ClientID': 105423433,
                    'CommissionToPay': None,
                    'ContractID': 553921,
                    'CurrMonthBonus': '0',
                    'CurrMonthCharge': '0',
                    'Currency': 'RUB',
                    'DT': '2019-02-20 23:32:37',
                    'NettingLastDt': None,
                    'OfferAccepted': 1,
                    'PersonalAccountExternalID': 'ЛСТ-1262870339-1',
                    'service_id': 111,
                },
                {
                    'Balance': '0',
                    'BonusLeft': '0',
                    'ClientID': 105423433,
                    'CommissionToPay': None,
                    'ContractID': 553921,
                    'CurrMonthBonus': '0',
                    'CurrMonthCharge': '0',
                    'Currency': 'RUB',
                    'DT': '2019-02-20 23:32:37',
                    'NettingLastDt': None,
                    'OfferAccepted': 1,
                    'PersonalAccountExternalID': 'ЛСТ-1262870339-1',
                    'service_id': 1161,
                },
                {
                    'Balance': '2000',
                    'BonusLeft': '0',
                    'ClientID': 103917439,
                    'CommissionToPay': None,
                    'ContractID': 553922,
                    'CurrMonthBonus': '0',
                    'CurrMonthCharge': '0',
                    'Currency': 'RUB',
                    'DT': '2019-03-15 15:46:59.315361',
                    'NettingLastDt': None,
                    'OfferAccepted': 1,
                    'PersonalAccountExternalID': 'ЛСТ-1259357521-1',
                    'service_id': 111,
                },
            ],
        ),
        ([1009624, 1009627], 200, []),
        ([553919], 200, []),
        ([], 400, None),
    ],
)
async def test_v2_balances_by_client_ids(
        taxi_billing_replication_client,
        contract_ids,
        expected_status,
        expected_response,
):
    response = await taxi_billing_replication_client.request(
        'POST',
        '/v2/balances/by_contract_ids/',
        json={'contract_ids': contract_ids},
    )

    assert response.status == expected_status
    if expected_status == 200:
        response_data = await response.json()
        assert (
            sorted(response_data['balances'], key=lambda x: x['ContractID'])
            == expected_response
        )


@pytest.mark.parametrize(
    'request_body, expected_contract_service_ids, expected_max_revision',
    [({'revision': 2, 'limit': 2}, [(1009624, 111), (1009627, 1161)], 4)],
)
async def test_v2_get_balances_by_revision(
        taxi_billing_replication_client,
        request_body,
        expected_contract_service_ids,
        expected_max_revision,
):
    response = await taxi_billing_replication_client.request(
        'POST', '/v2/balances/by_revision/', json=request_body,
    )
    assert response.status == 200
    response_data = await response.json()
    assert [
        (balance['ContractID'], balance['service_id'])
        for balance in response_data['balances']
    ] == expected_contract_service_ids
    assert expected_max_revision == response_data['max_revision']
