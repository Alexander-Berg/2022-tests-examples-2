import pytest


@pytest.mark.parametrize(
    'client_id,contract_type,expected',
    [
        (
            '1',
            'GENERAL',
            [
                {
                    'ID': 553918,
                    'EXTERNAL_ID': '205101/18',
                    'PERSON_ID': 8349867,
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'IS_SUSPENDED': 0,
                    'CURRENCY': 'RUR',
                    'NETTING': 1,
                    'NETTING_PCT': '100',
                    'LINK_CONTRACT_ID': None,
                    'SERVICES': [128, 124, 125, 605, 111],
                    'NDS_FOR_RECEIPT': 18,
                    'OFFER_ACCEPTED': 1,
                    'NDS': None,
                    'PAYMENT_TYPE': 2,
                    'PARTNER_COMMISSION_PCT': None,
                    'PARTNER_COMMISSION_PCT2': '5',
                    'IND_BEL_NDS_PERCENT': None,
                    'END_DT': None,
                    'FINISH_DT': None,
                    'DT': '2018-09-26 00:00:00',
                    'CONTRACT_TYPE': 9,
                    'IND_BEL_NDS': None,
                    'COUNTRY': None,
                    'IS_FAXED': 1,
                    'IS_DEACTIVATED': 0,
                    'IS_CANCELLED': 0,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2018-09-26 00:00:00', [128, 124, 125]],
                            ['2018-09-27 00:00:00', [128, 124, 125, 605, 111]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [
                            ['2018-09-26 00:00:00', '5'],
                        ],
                    },
                    'FIRM_ID': 13,
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': None,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
        (
            '1',
            'SPENDABLE',
            [
                {
                    'ID': 553919,
                    'EXTERNAL_ID': 'РАС-115692',
                    'PERSON_ID': 8349869,
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'IS_SUSPENDED': 0,
                    'CURRENCY': 'RUR',
                    'NETTING': None,
                    'NETTING_PCT': None,
                    'LINK_CONTRACT_ID': None,
                    'SERVICES': [135],
                    'NDS_FOR_RECEIPT': None,
                    'OFFER_ACCEPTED': None,
                    'NDS': 18,
                    'PAYMENT_TYPE': None,
                    'PARTNER_COMMISSION_PCT': None,
                    'PARTNER_COMMISSION_PCT2': None,
                    'IND_BEL_NDS_PERCENT': None,
                    'END_DT': None,
                    'FINISH_DT': '2019-03-05 10:56:24',
                    'DT': '2018-09-26 00:00:00',
                    'CONTRACT_TYPE': 10,
                    'IND_BEL_NDS': '80.19',
                    'COUNTRY': None,
                    'IS_FAXED': None,
                    'IS_DEACTIVATED': None,
                    'IS_CANCELLED': None,
                    'ATTRIBUTES_HISTORY': None,
                    'FIRM_ID': None,
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': None,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
                {
                    'ID': 553920,
                    'EXTERNAL_ID': 'spendta-205101/18',
                    'PERSON_ID': 8349869,
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'IS_SUSPENDED': 0,
                    'CURRENCY': 'RUR',
                    'NETTING': None,
                    'NETTING_PCT': None,
                    'LINK_CONTRACT_ID': 553918,
                    'SERVICES': [137],
                    'NDS_FOR_RECEIPT': None,
                    'OFFER_ACCEPTED': None,
                    'NDS': 18,
                    'PAYMENT_TYPE': None,
                    'PARTNER_COMMISSION_PCT': None,
                    'PARTNER_COMMISSION_PCT2': None,
                    'IND_BEL_NDS_PERCENT': None,
                    'END_DT': '2019-02-20 20:52:15',
                    'FINISH_DT': None,
                    'DT': '2018-09-26 00:00:00',
                    'CONTRACT_TYPE': None,
                    'IND_BEL_NDS': '23.44',
                    'COUNTRY': 225,
                    'IS_FAXED': None,
                    'IS_DEACTIVATED': None,
                    'IS_CANCELLED': None,
                    'ATTRIBUTES_HISTORY': None,
                    'FIRM_ID': None,
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': None,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
    ],
)
async def test_get_client_contracts(
        taxi_billing_replication_client,
        client_id,
        contract_type,
        expected,
        billing_replictaion_cron_app,
):
    params = {'client_id': client_id, 'type': contract_type}
    response = await taxi_billing_replication_client.request(
        'GET', '/contract/', params=params,
    )

    assert response.status == 200

    response_data = await response.json()
    assert sorted(response_data, key=lambda x: x['ID']) == expected


@pytest.mark.config(BILLING_REPLICATION_SERVICE_ID_PREV_ACTIVE_USAGE='enable')
@pytest.mark.parametrize(
    'params,expected_contract_ids,expected_currencies',
    [
        (
            # case 1
            {
                'client_id': '103917439',
                'actual_ts': '2020-01-21T09:05:00+0000',
                'active_ts': '2020-01-21T09:05:00+0000',
            },
            [1, 3, 5],
            {1: 'RUB'},
        ),
        (
            # case 2, like 1, but actual_ts is greater
            {
                'client_id': '103917439',
                'actual_ts': '2020-01-21T09:15:00+0000',
                'active_ts': '2020-01-21T09:15:00+0000',
            },
            [1, 3, 5],
            {1: 'USD'},
        ),
        (
            # case 3, like 1, but active_ts is less
            {
                'client_id': '103917439',
                'actual_ts': '2020-01-21T09:15:00+0000',
                'active_ts': '2020-01-20T00:00:00+0000',
            },
            [1, 2, 3, 4, 5],
            None,
        ),
        (
            # case 4, like 3, but with service_id filter
            [
                ('client_id', '103917439'),
                ('actual_ts', '2020-01-21T09:15:00+0000'),
                ('active_ts', '2020-01-20T00:00:00+0000'),
                ('service_id', '650'),
                ('service_id', '651'),
            ],
            [2, 5],
            None,
        ),
        (
            # case 4.1 service_id filter as str of ids
            {
                'client_id': '103917439',
                'actual_ts': '2020-01-21T09:15:00+0000',
                'active_ts': '2020-01-20T00:00:00+0000',
                'service_id': '650, 651',
            },
            [2, 5],
            None,
        ),
        (
            # case 5.1, like 3, but with service_id filter
            {
                'client_id': '103917439',
                'actual_ts': '2020-01-21T09:15:00+0000',
                'active_ts': '2020-01-20T00:00:00+0000',
                'service_id': 137,
            },
            [3, 4],
            None,
        ),
        (
            # case 5.2, like 3, but with service_id filter
            {
                'client_id': '105352633',
                'actual_ts': '2020-01-21T09:15:00+0000',
                'active_ts': '2020-01-20T00:00:00+0000',
                'service_id': 1164,
            },
            [18],
            None,
        ),
        (
            # case 6, like 3, but with active_ts is less
            {
                'client_id': '103917439',
                'actual_ts': '2020-01-21T09:15:00+0000',
                'active_ts': '2019-01-01T00:00:00+0000',
            },
            [2],
            None,
        ),
        (
            # case 7, check MSK timezone correction for DT
            #    '2020-05-20 22:45:00.000000', -- created
            #    '2020-05-21 00:00:00', -- DT
            #    '2020-08-21 00:00:00', -- FINISH_DT for general
            #    '2020-08-18 00:00:00', -- END_DT for spendable
            {
                'client_id': '103917440',
                'actual_ts': '2020-05-20T23:34:00.000000+00:00',
                'active_ts': '2020-05-20T23:34:00.000000+00:00',
            },
            [11, 12],
            None,
        ),
        (
            # case 8, check MSK timezone correction for FINISH_DT
            # no active contracts
            #    '2020-05-20 22:45:00.000000', -- created
            #    '2020-05-21 00:00:00', -- DT
            #    '2020-08-21 00:00:00', -- FINISH_DT for general
            #    '2020-08-18 00:00:00', -- END_DT for spendable
            {
                'client_id': '103917440',
                'actual_ts': '2020-08-20T23:34:00.000000+00:00',
                'active_ts': '2020-08-20T21:00:00.000000+00:00',
            },
            [],
            None,
        ),
        (
            # case 9, check MSK timezone correction for END_DT
            # no active SPENDABLE contracts
            #    '2020-05-20 22:45:00.000000', -- created
            #    '2020-05-21 00:00:00', -- DT
            #    '2020-08-21 00:00:00', -- FINISH_DT for general
            #    '2020-08-18 00:00:00', -- END_DT for spendable
            {
                'client_id': '103917440',
                'actual_ts': '2020-08-19T21:00:00.000000+00:00',
                'active_ts': '2020-08-19T21:00:00.000000+00:00',
            },
            [11],
            None,
        ),
        (
            # case 10, check MSK timezone correction for END_DT and
            # END_DT + 1 day
            #    '2020-05-20 22:45:00.000000', -- created
            #    '2020-05-21 00:00:00', -- DT
            #    '2020-08-21 00:00:00', -- FINISH_DT for general
            #    '2020-08-18 00:00:00', -- END_DT for spendable
            {
                'client_id': '103917440',
                'actual_ts': '2020-08-18T20:00:00.000000+00:00',
                'active_ts': '2020-08-18T20:00:00.000000+00:00',
            },
            [11, 12],
            None,
        ),
        (
            # case 11, get prev active
            [
                ('client_id', '111111111'),
                ('actual_ts', '2021-01-22T00:00:00+0000'),
                ('active_ts', '2021-01-22T00:00:00+0000'),
                ('service_id', '135'),
                ('service_id_prev_active', '135'),
            ],
            [13],
            None,
        ),
        (
            # case 12, get prev active suspended contract
            [
                ('client_id', '103917440'),
                ('actual_ts', '2021-01-22T00:00:00+0000'),
                ('active_ts', '2021-01-22T00:00:00+0000'),
                ('service_id', '128,111'),
                ('service_id_prev_active', '111,128'),
            ],
            [14],
            None,
        ),
        (
            # case 13, get prev active suspended contract, not newer 15
            [
                ('client_id', '103917440'),
                ('actual_ts', '2021-01-22T00:00:00+0000'),
                ('active_ts', '2021-01-22T00:00:00+0000'),
                ('service_id', '128,111'),
                ('service_id_prev_active', '111,128'),
            ],
            [14],
            None,
        ),
        (
            # case 14.1, try to get prev active 137 linked contract
            [
                ('client_id', '103917439'),
                ('actual_ts', '2021-01-22T00:00:00+0000'),
                ('active_ts', '2021-01-22T00:00:00+0000'),
                ('service_id', '137'),
                ('service_id_prev_active', '137'),
            ],
            [],
            None,
        ),
        (
            # case 14.2, try to get prev active 1164 linked contract
            [
                ('client_id', '105352633'),
                ('actual_ts', '2021-01-22T00:00:00+0000'),
                ('active_ts', '2021-01-22T00:00:00+0000'),
                ('service_id', '1164'),
                ('service_id_prev_active', '1164'),
            ],
            [],
            None,
        ),
        (
            # case 15, get services from attr history, no 605 active
            [
                ('client_id', '1'),
                ('actual_ts', '2021-02-05T00:00:00+0000'),
                ('active_ts', '2018-09-26T12:00:00+0000'),
                ('service_id', '605'),
            ],
            [],
            None,
        ),
        (
            # case 16, get services from attr history, has active 605
            [
                ('client_id', '1'),
                ('actual_ts', '2021-02-05T00:00:00+0000'),
                ('active_ts', '2018-09-28T00:00:00+0000'),
                ('service_id', '605'),
            ],
            [553918],
            None,
        ),
    ],
)
async def test_get_active_contracts(
        taxi_billing_replication_client,
        params,
        expected_contract_ids,
        expected_currencies,
        billing_replictaion_cron_app,
):
    """
    Currency value is used as a control field for different versions of the
    same contract
    """
    response = await taxi_billing_replication_client.request(
        'GET', '/v1/active-contracts/', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    contract_ids = [contract['ID'] for contract in response_data]
    assert contract_ids == expected_contract_ids
    if expected_currencies:
        currencies = {
            contract['ID']: contract['CURRENCY'] for contract in response_data
        }
        assert not set(expected_currencies.items()).difference(
            currencies.items(),
        )


@pytest.mark.pgsql(
    'billing_replication', files=['test_contracts_active_at.sql'],
)
@pytest.mark.parametrize(
    'params, expected_response',
    [
        (
            # no attributes history
            {
                'client_id': '000000000',
                'actual_ts': '2020-01-21T09:05:00+0000',
                'active_ts': '2020-01-21T09:05:00+0000',
            },
            [
                {
                    'ATTRIBUTES_HISTORY': None,
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
                    'PARTNER_COMMISSION_PCT2': '3',
                    'PAYMENT_TYPE': None,
                    'PERSON_ID': None,
                    'SERVICES': [111],
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': None,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
        (
            # services from history,
            # 124 was in services till 2020-03-01 00:00:00.000000
            # [111, 124] at active_ts
            {
                'client_id': '000000001',
                'actual_ts': '2020-01-21T09:05:00+0000',
                'active_ts': '2020-01-21T09:05:00+0000',
            },
            [
                {
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2020-01-01 00:00:00.000000', [111, 124]],
                            ['2020-03-01 00:00:00.000000', [111]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [],
                    },
                    'CONTRACT_TYPE': None,
                    'COUNTRY': None,
                    'CURRENCY': 'RUB',
                    'DT': '2020-01-01 00:00:00',
                    'END_DT': None,
                    'EXTERNAL_ID': None,
                    'FINISH_DT': '2020-12-31 00:00:00',
                    'FIRM_ID': None,
                    'ID': 2,
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
                    'PARTNER_COMMISSION_PCT2': '3',
                    'PAYMENT_TYPE': None,
                    'PERSON_ID': None,
                    'SERVICES': [111, 124],
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': None,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
        (
            # services from history,
            # 124 was in services till 2020-03-01 00:00:00.000000
            # [111] at active_ts
            {
                'client_id': '000000001',
                'actual_ts': '2020-01-21T09:05:00+0000',
                'active_ts': '2020-12-21T09:05:00+0000',
            },
            [
                {
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2020-01-01 00:00:00.000000', [111, 124]],
                            ['2020-03-01 00:00:00.000000', [111]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [],
                    },
                    'CONTRACT_TYPE': None,
                    'COUNTRY': None,
                    'CURRENCY': 'RUB',
                    'DT': '2020-01-01 00:00:00',
                    'END_DT': None,
                    'EXTERNAL_ID': None,
                    'FINISH_DT': '2020-12-31 00:00:00',
                    'FIRM_ID': None,
                    'ID': 2,
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
                    'PARTNER_COMMISSION_PCT2': '3',
                    'PAYMENT_TYPE': None,
                    'PERSON_ID': None,
                    'SERVICES': [111],
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': None,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
        (
            # partner_commission_pct2 from history
            # partner_commission_pct2 = 5 till 2020-04-01 00:00:00.000000,
            # 6 - after
            # 5 at active_ts
            {
                'client_id': '000000002',
                'actual_ts': '2020-01-21T09:05:00+0000',
                'active_ts': '2020-03-21T09:05:00+0000',
            },
            [
                {
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2020-01-01 00:00:00.000000', [111, 124]],
                            ['2020-03-01 00:00:00.000000', [111]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [
                            ['2020-01-01 00:00:00.000000', '5'],
                            ['2020-04-01 00:00:00.000000', '6'],
                        ],
                        'YANDEX_BANK_ENABLED': [
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
                    'ID': 3,
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
                    'PARTNER_COMMISSION_PCT2': '5',
                    'PAYMENT_TYPE': None,
                    'PERSON_ID': None,
                    'SERVICES': [111],
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': 0,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
        (
            # partner_commission_pct2 from history
            # partner_commission_pct2 = 5 till 2020-04-01 00:00:00.000000,
            # 6 - after
            # 5 at active_ts
            {
                'client_id': '000000002',
                'actual_ts': '2020-01-21T09:05:00+0000',
                'active_ts': '2020-12-21T09:05:00+0000',
            },
            [
                {
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            ['2020-01-01 00:00:00.000000', [111, 124]],
                            ['2020-03-01 00:00:00.000000', [111]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [
                            ['2020-01-01 00:00:00.000000', '5'],
                            ['2020-04-01 00:00:00.000000', '6'],
                        ],
                        'YANDEX_BANK_ENABLED': [
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
                    'ID': 3,
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
                    'PARTNER_COMMISSION_PCT2': '6',
                    'PAYMENT_TYPE': None,
                    'PERSON_ID': None,
                    'SERVICES': [111],
                    'YANDEX_BANK_ACCOUNT_ID': None,
                    'YANDEX_BANK_ENABLED': 0,
                    'YANDEX_BANK_WALLET_ID': None,
                    'YANDEX_BANK_WALLET_PAY': None,
                },
            ],
        ),
    ],
)
async def test_get_active_contracts_response_by_active_at(
        taxi_billing_replication_client, params, expected_response,
):
    response = await taxi_billing_replication_client.request(
        'GET', '/v1/active-contracts/', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    'data, expected_contracts',
    [
        pytest.param(
            {'client_ids': ['103917444']},
            {'103917444': {8, 9}},
            id='get client contracts without service filtration',
        ),
        pytest.param(
            {'client_ids': ['103917444', '105352445'], 'service_ids': [135]},
            {'103917444': {8}, '105352445': {10}},
            id='get clients contracts with services',
        ),
    ],
)
async def test_get_clients_contracts(
        taxi_billing_replication_client, data, expected_contracts,
):
    response = await taxi_billing_replication_client.request(
        'POST', '/v1/contracts/', json=data,
    )
    response_data = await response.json()
    assert response.status == 200, response_data
    assert len(response_data['contracts']) == len(expected_contracts)

    contracts_map = {
        contract_data['client_id']: contract_data['contracts']
        for contract_data in response_data['contracts']
    }
    for client_id, client_contracts in contracts_map.items():
        assert len(client_contracts) == len(expected_contracts[client_id])
        contracts_ids = {contract['ID'] for contract in client_contracts}
        assert contracts_ids == expected_contracts[client_id]


@pytest.mark.parametrize(
    'params, expected_contract_ids,expected_max_revision',
    [
        ({'revision': 2, 'limit': 3}, {2, 3, 4}, 5),
        ({'revision': 1, 'limit': 2}, {1, 2}, 3),
    ],
)
async def test_get_contracts_by_revision(
        taxi_billing_replication_client,
        params,
        expected_contract_ids,
        expected_max_revision,
):
    response = await taxi_billing_replication_client.request(
        'GET', '/v1/contracts/by_revision/', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert all('status' in contract for contract in response_data['contracts'])
    assert all(
        'client_id' in contract for contract in response_data['contracts']
    )
    assert all('type' in contract for contract in response_data['contracts'])
    assert {
        contract['ID'] for contract in response_data['contracts']
    } == expected_contract_ids
    assert expected_max_revision == response_data['max_revision']


@pytest.mark.parametrize(
    'params, expected_response_status, expected_response',
    [
        (
            # RUB in request
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': 'client_id',
                        'service_id': 128,
                        'currency': 'RUB',
                    },
                ],
            },
            400,
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': 'client_id',
                        'service_id': 128,
                        'currency': 'RUR',
                        'is_valid': False,
                    },
                ],
            },
        ),
        (
            # wrong client_id
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': 'client_id',
                        'service_id': 111,
                        'currency': 'RUR',
                    },
                ],
            },
            200,
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': 'client_id',
                        'service_id': 111,
                        'currency': 'RUR',
                        'is_valid': False,
                    },
                ],
            },
        ),
        (
            # contract has changed currency, both valid
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 111,
                        'currency': 'RUR',
                    },
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 111,
                        'currency': 'USD',
                    },
                ],
            },
            200,
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 111,
                        'currency': 'RUR',
                        'is_valid': True,
                    },
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 111,
                        'currency': 'USD',
                        'is_valid': True,
                    },
                ],
            },
        ),
        (
            # wrong currency
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 111,
                        'currency': 'AMD',
                    },
                ],
            },
            200,
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 111,
                        'currency': 'AMD',
                        'is_valid': False,
                    },
                ],
            },
        ),
        (
            # wrong service_id
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 137,
                        'currency': 'RUR',
                    },
                ],
            },
            200,
            {
                'contracts': [
                    {
                        'contract_id': 1,
                        'client_id': '103917439',
                        'service_id': 137,
                        'currency': 'RUR',
                        'is_valid': False,
                    },
                ],
            },
        ),
        (
            # services from attr history
            {
                'contracts': [
                    {
                        'contract_id': 2,
                        'client_id': '103917439',
                        'service_id': 672,
                        'currency': 'USD',
                    },
                ],
            },
            200,
            {
                'contracts': [
                    {
                        'contract_id': 2,
                        'client_id': '103917439',
                        'service_id': 672,
                        'currency': 'USD',
                        'is_valid': True,
                    },
                ],
            },
        ),
        (
            # no such contract
            {
                'contracts': [
                    {
                        'contract_id': 666666,
                        'client_id': '103917439',
                        'service_id': 672,
                        'currency': 'USD',
                    },
                ],
            },
            200,
            {
                'contracts': [
                    {
                        'contract_id': 666666,
                        'client_id': '103917439',
                        'service_id': 672,
                        'currency': 'USD',
                        'is_valid': False,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.pgsql('billing_replication', files=['test_check_contracts.sql'])
async def test_check_contracts(
        taxi_billing_replication_client,
        params,
        expected_response_status,
        expected_response,
):
    response = await taxi_billing_replication_client.request(
        'POST', '/v1/check_contracts/', json=params,
    )
    assert response.status == expected_response_status
    if response.status == 200:
        response_data = await response.json()
        assert response_data == expected_response
