import pytest

_ANNIHILATION_ENABLED = pytest.mark.config(
    CASHBACK_START_ANNIHILATION_DATE={
        'enabled': True,
        'general_annihilation_date': '2020-01-01T00:00:00Z',
    },
)


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.servicetest
@pytest.mark.parametrize(
    'balance_request, balances_select_request, balances_select_response,'
    'expected_status, expected_response',
    [
        (
            {'wallet_id': 'non-existing', 'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'non-existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [],
            404,
            {'code': 'wallet_not_found', 'message': 'Wallet not found'},
        ),
        pytest.param(
            {'wallet_id': 'non-existing', 'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'non-existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [],
            404,
            {'code': 'wallet_not_found', 'message': 'Wallet not found'},
            marks=[_ANNIHILATION_ENABLED],
            id='No annihilation data',
        ),
        (
            {'wallet_id': 'existing', 'yandex_uid': 'uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'entity_external_id': 'wallet_id/uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/uid',
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            200,
            {'balance': '100.0000', 'currency': 'RUB'},
        ),
        pytest.param(
            {'wallet_id': 'existing', 'yandex_uid': 'annihilated-uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'entity_external_id': 'wallet_id/annihilated-uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/annihilated-uid',
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '100.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            200,
            {'balance': '0.0000', 'currency': 'RUB'},
            marks=[_ANNIHILATION_ENABLED],
            id='Fully annihilated',
        ),
        pytest.param(
            {'wallet_id': 'existing', 'yandex_uid': 'annihilated-uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'entity_external_id': 'wallet_id/annihilated-uid',
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': 'wallet_id/annihilated-uid',
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-02-10T00:00:00+00:00',
                            'balance': '1000.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            200,
            {'balance': '800.0000', 'currency': 'RUB'},
            marks=[_ANNIHILATION_ENABLED],
            id='Partially annihilated',
        ),
        pytest.param(
            {'wallet_id': 'existing', 'yandex_uid': 'future-annihilated-uid'},
            {
                'accounts': [
                    {
                        'agreement_id': 'existing',
                        'entity_external_id': (
                            'wallet_id/future-annihilated-uid'
                        ),
                        'sub_account': 'deposit',
                    },
                ],
                'accrued_at': ['2020-02-02T00:00:00+00:00'],
                'use_master': False,
            },
            [
                {
                    'account': {
                        'account_id': 5000000000,
                        'entity_external_id': (
                            'wallet_id/future-annihilated-uid'
                        ),
                        'agreement_id': 'existing',
                        'currency': 'RUB',
                        'sub_account': 'deposit',
                    },
                    'balances': [
                        {
                            'accrued_at': '2020-01-01T00:00:00+00:00',
                            'balance': '1000.0',
                            'last_entry_id': 6000000000,
                            'last_created': '2020-02-02T20:20:00+00:00',
                        },
                    ],
                },
            ],
            200,
            {'balance': '1000.0000', 'currency': 'RUB'},
            marks=[_ANNIHILATION_ENABLED],
            id='Too early for annihilation',
        ),
    ],
)
async def test_balance(
        taxi_billing_wallet,
        mockserver,
        balance_request,
        balances_select_request,
        balances_select_response,
        expected_status,
        expected_response,
):
    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _balances_select(request):
        assert request.json == balances_select_request
        return balances_select_response

    response = await taxi_billing_wallet.post('balance', json=balance_request)
    assert response.status_code == expected_status
    assert response.json() == expected_response
