import collections

import pytest

import testsuite


@pytest.mark.pgsql('personal_wallet', files=['stq_test.sql'])
@pytest.mark.experiments3(filename='exp3_billing_wallet_enabled.json')
@pytest.mark.config(PLUS_WALLET_UPDATE_WALLETS_ON_MISMATCH=True)
@pytest.mark.config(PLUS_WALLET_WALLET_CURRENCIES=['RUB', 'EUR', 'KZT', 'UAH'])
@pytest.mark.parametrize(
    'yandex_uid,billing_wallet_response,plus_wallet_response',
    [
        [
            'user_id1',
            {
                'status': 200,
                'balances': [
                    {
                        'amount': '100',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                ],
            },
            {
                'balances': [
                    {
                        'balance': '100.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'EUR',
                        'wallet_id': 'ze60a1f1c3fd3a28704840c8a4872228',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'KZT',
                        'wallet_id': 'z29d4c353a9d2c666ec4885a2e99062b',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'UAH',
                        'wallet_id': 'ze03a1e49a4b0a10310accbaf7d1dd5e',
                    },
                ],
            },
        ],
        [
            'user_id1',
            {
                'status': 200,
                'balances': [
                    {
                        'amount': '100',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                    {
                        'amount': '200.01',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id2',
                    },
                    {
                        'amount': '300.02',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id3',
                    },
                    {
                        'amount': '400.03',
                        'currency': 'UAH',
                        'wallet_id': 'wallet_id4',
                    },
                ],
            },
            {
                'balances': [
                    {
                        'balance': '100.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                    {
                        'balance': '200.0000',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id2',
                    },
                    {
                        'balance': '300.0000',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id3',
                    },
                    {
                        'balance': '400.0000',
                        'currency': 'UAH',
                        'wallet_id': 'wallet_id4',
                    },
                ],
            },
        ],
    ],
)
async def test_stq_not_called(
        taxi_plus_wallet,
        load_json,
        mockserver,
        stq,
        yandex_uid,
        billing_wallet_response,
        plus_wallet_response,
):
    @mockserver.json_handler('/billing-wallet/balances')
    def _mock_order_core(request):
        return billing_wallet_response

    response = await taxi_plus_wallet.get(
        f'v1/balances?yandex_uid={yandex_uid}',
    )
    assert response.status_code == 200
    assert response.json() == plus_wallet_response
    assert stq.personal_wallet_update_balance.times_called == 0
    with pytest.raises(testsuite.utils.callinfo.CallQueueEmptyError):
        stq.personal_wallet_update_balance.next_call()


@pytest.mark.pgsql('personal_wallet', files=['stq_test.sql'])
@pytest.mark.experiments3(filename='exp3_billing_wallet_enabled.json')
@pytest.mark.config(PLUS_WALLET_UPDATE_WALLETS_ON_MISMATCH=True)
@pytest.mark.config(PLUS_WALLET_WALLET_CURRENCIES=['RUB', 'EUR', 'KZT', 'UAH'])
@pytest.mark.parametrize(
    'yandex_uid,billing_wallet_response,plus_wallet_response,'
    'stq_times_called,stq_calls',
    [
        [
            'user_id1',
            {
                'status': 200,
                'balances': [
                    {
                        'amount': '101',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                ],
            },
            {
                'balances': [
                    {
                        'balance': '101.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'EUR',
                        'wallet_id': 'ze60a1f1c3fd3a28704840c8a4872228',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'KZT',
                        'wallet_id': 'z29d4c353a9d2c666ec4885a2e99062b',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'UAH',
                        'wallet_id': 'ze03a1e49a4b0a10310accbaf7d1dd5e',
                    },
                ],
            },
            1,
            ['wallet_id1'],
        ],
        [
            'user_id1',
            {
                'status': 200,
                'balances': [
                    {
                        'amount': '101.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                    {
                        'amount': '200.9999',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id2',
                    },
                    {
                        'amount': '300.1234',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id3',
                    },
                    {
                        'amount': '399.0000',
                        'currency': 'UAH',
                        'wallet_id': 'wallet_id4',
                    },
                ],
            },
            {
                'balances': [
                    {
                        'balance': '101.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id1',
                    },
                    {
                        'balance': '200.0000',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id2',
                    },
                    {
                        'balance': '300.0000',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id3',
                    },
                    {
                        'balance': '399.0000',
                        'currency': 'UAH',
                        'wallet_id': 'wallet_id4',
                    },
                ],
            },
            2,
            ['wallet_id1', 'wallet_id4'],
        ],
        [
            'user_id2',
            {
                'status': 200,
                'balances': [
                    {
                        'amount': '500.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id5',
                    },
                    {
                        'amount': '200.9999',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id6',
                    },
                    {
                        'amount': '300.1234',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id7',
                    },
                ],
            },
            {
                'balances': [
                    {
                        'balance': '500.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id5',
                    },
                    {
                        'balance': '200.0000',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id6',
                    },
                    {
                        'balance': '300.0000',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id7',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'UAH',
                        'wallet_id': 'zcb611046e28c6dada9738706bbdaf49',
                    },
                ],
            },
            2,
            ['wallet_id6', 'wallet_id7'],
        ],
    ],
)
async def test_stq_called(
        taxi_plus_wallet,
        load_json,
        mockserver,
        stq,
        yandex_uid,
        billing_wallet_response,
        plus_wallet_response,
        stq_times_called,
        stq_calls,
):
    @mockserver.json_handler('/billing-wallet/balances')
    def _mock_order_core(request):
        return billing_wallet_response

    response = await taxi_plus_wallet.get(
        f'v1/balances?yandex_uid={yandex_uid}',
    )
    assert response.status_code == 200
    assert response.json() == plus_wallet_response

    assert stq.personal_wallet_update_balance.times_called == stq_times_called
    actual_calls = []
    for _ in stq_calls:
        actual_call = stq.personal_wallet_update_balance.next_call()
        assert actual_call['queue'] == 'personal_wallet_update_balance'
        assert actual_call['id'] == actual_call['kwargs']['wallet_id']
        actual_calls.append(actual_call['kwargs']['wallet_id'])
        assert actual_call['args'] == []
        assert actual_call['kwargs']['yandex_uid'] == yandex_uid

    assert collections.Counter(stq_calls) == collections.Counter(actual_calls)
    assert len(actual_calls) == len(set(actual_calls))

    with pytest.raises(testsuite.utils.callinfo.CallQueueEmptyError):
        stq.personal_wallet_update_balance.next_call()


@pytest.mark.pgsql('personal_wallet', files=['stq_test.sql'])
@pytest.mark.experiments3(filename='exp3_billing_wallet_enabled.json')
@pytest.mark.config(PLUS_WALLET_UPDATE_WALLETS_ON_MISMATCH=False)
@pytest.mark.config(PLUS_WALLET_WALLET_CURRENCIES=['RUB', 'EUR', 'KZT', 'UAH'])
@pytest.mark.parametrize(
    'yandex_uid,billing_wallet_response,plus_wallet_response',
    [
        [
            'user_id2',
            {
                'status': 200,
                'balances': [
                    {
                        'amount': '500.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id5',
                    },
                    {
                        'amount': '200.9999',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id6',
                    },
                    {
                        'amount': '300.1234',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id7',
                    },
                ],
            },
            {
                'balances': [
                    {
                        'balance': '500.0000',
                        'currency': 'RUB',
                        'wallet_id': 'wallet_id5',
                    },
                    {
                        'balance': '200.0000',
                        'currency': 'EUR',
                        'wallet_id': 'wallet_id6',
                    },
                    {
                        'balance': '300.0000',
                        'currency': 'KZT',
                        'wallet_id': 'wallet_id7',
                    },
                    {
                        'balance': '0.0000',
                        'currency': 'UAH',
                        'wallet_id': 'zcb611046e28c6dada9738706bbdaf49',
                    },
                ],
            },
        ],
    ],
)
async def test_stq_not_called_if_update_disabled_in_config(
        taxi_plus_wallet,
        load_json,
        mockserver,
        stq,
        yandex_uid,
        billing_wallet_response,
        plus_wallet_response,
):
    @mockserver.json_handler('/billing-wallet/balances')
    def _mock_order_core(request):
        return billing_wallet_response

    response = await taxi_plus_wallet.get(
        f'v1/balances?yandex_uid={yandex_uid}',
    )
    assert response.status_code == 200
    assert response.json() == plus_wallet_response
    assert stq.personal_wallet_update_balance.times_called == 0
    with pytest.raises(testsuite.utils.callinfo.CallQueueEmptyError):
        stq.personal_wallet_update_balance.next_call()
