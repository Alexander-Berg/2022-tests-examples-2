import pytest


@pytest.mark.parametrize(
    'params, expected_response_status, expected_response',
    [
        (
            # Full contract projection at now
            {'ID': 1},
            200,
            {
                'client_id': '000000000',
                'ATTRIBUTES_HISTORY': {
                    'SERVICES': [
                        ['2020-01-01 00:00:00.000000', [111, 124]],
                        ['2020-03-01 00:00:00.000000', [111]],
                    ],
                    'YANDEX_BANK_ACCOUNT_ID': [
                        ['2020-03-01 00:00:00.000000', 'acc/098'],
                    ],
                    'YANDEX_BANK_ENABLED': [['2020-03-01 00:00:00.000000', 1]],
                    'YANDEX_BANK_WALLET_ID': [
                        ['2020-03-01 00:00:00.000000', 'w/123'],
                    ],
                    'YANDEX_BANK_WALLET_PAY': [
                        ['2020-03-01 00:00:00.000000', 0],
                    ],
                },
                'CONTRACT_TYPE': None,
                'COUNTRY': None,
                'CURRENCY': 'RUB',
                'DT': '2020-01-01 00:00:00',
                'END_DT': None,
                'EXTERNAL_ID': None,
                'FINISH_DT': '2020-12-31 00:00:00',
                'FIRM_ID': None,
                'ID': 1,
                'IND_BEL_NDS': None,
                'IND_BEL_NDS_PERCENT': None,
                'IS_ACTIVE': None,
                'IS_CANCELLED': 0,
                'IS_DEACTIVATED': 0,
                'IS_FAXED': 1,
                'IS_SIGNED': 1,
                'IS_SUSPENDED': 0,
                'LINK_CONTRACT_ID': None,
                'NDS': None,
                'NDS_FOR_RECEIPT': None,
                'NETTING': None,
                'NETTING_PCT': None,
                'OFFER_ACCEPTED': None,
                'PARTNER_COMMISSION_PCT': None,
                'PARTNER_COMMISSION_PCT2': None,
                'PAYMENT_TYPE': None,
                'PERSON_ID': None,
                'SERVICES': [111],
                'type': 'GENERAL',
                'YANDEX_BANK_ENABLED': 1,
                'YANDEX_BANK_WALLET_PAY': 0,
                'YANDEX_BANK_WALLET_ID': 'w/123',
                'YANDEX_BANK_ACCOUNT_ID': 'acc/098',
            },
        ),
        (
            # Some projection
            {
                'ID': 1,
                'projection': [
                    'ID',
                    'client_id',
                    'CURRENCY',
                    'FIRM_ID',
                    'SERVICES',
                    'NETTING',
                    'LINK_CONTRACT_ID',
                    'YANDEX_BANK_ENABLED',
                ],
            },
            200,
            {
                'CURRENCY': 'RUB',
                'FIRM_ID': None,
                'ID': 1,
                'LINK_CONTRACT_ID': None,
                'NETTING': None,
                'SERVICES': [111],
                'YANDEX_BANK_ENABLED': 1,
                'client_id': '000000000',
            },
        ),
        (
            # Add required fields in projection
            {'ID': 1, 'projection': ['SERVICES']},
            200,
            {'ID': 1, 'SERVICES': [111], 'client_id': '000000000'},
        ),
        (
            # Services at the date from request
            {
                'ID': 1,
                'projection': ['ID', 'client_id', 'SERVICES'],
                'at': '2020-01-01T20:00:00.000000+00:00',
            },
            200,
            {'ID': 1, 'SERVICES': [111, 124], 'client_id': '000000000'},
        ),
        (
            # Not found
            {
                'ID': 2,
                'projection': ['ID', 'client_id', 'SERVICES'],
                'at': '2020-01-01T20:00:00.000000+00:00',
            },
            404,
            None,
        ),
    ],
)
@pytest.mark.pgsql('billing_replication', files=['test_v2_contract_by_id.sql'])
async def test_v2_contract_y_id(
        taxi_billing_replication_client,
        params,
        expected_response_status,
        expected_response,
):
    response = await taxi_billing_replication_client.request(
        'POST', '/v2/contract/by_id/', json=params,
    )
    assert response.status == expected_response_status
    if response.status == 200:
        response_data = await response.json()
        assert response_data == expected_response
