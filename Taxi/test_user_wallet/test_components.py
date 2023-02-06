import pytest

import user_wallet.components as user_wallet


@pytest.mark.parametrize(
    'plus_wallet_balances, expected_wallet_id',
    [
        (
            [
                {'wallet_id': 'wallet_1', 'balance': '0', 'currency': 'RUB'},
                {'wallet_id': 'wallet_2', 'balance': '0', 'currency': 'USD'},
            ],
            'wallet_1',
        ),
        ([], None),
    ],
)
async def test_get_user_wallet(
        library_context,
        mock_plus_wallet,
        plus_wallet_balances,
        expected_wallet_id,
):
    @mock_plus_wallet('/v1/balances')
    def _mock_plus_wallet_balances(request):
        assert request.query['yandex_uid'] == 'yandex_uid'
        assert request.query['currencies'] == 'RUB'
        return {'balances': plus_wallet_balances}

    wallet = await library_context.user_wallet.get_wallet('yandex_uid', 'RUB')
    assert getattr(wallet, 'wallet_id', None) == expected_wallet_id


@pytest.mark.parametrize(
    'wallet_id, expected_result', [('wallet_1', False), ('z_wallet_2', True)],
)
def test_is_z_wallet(wallet_id, expected_result):
    assert user_wallet.UserWallet.is_z_wallet(wallet_id) == expected_result


@pytest.mark.parametrize(
    'use_plus_wallet',
    [
        pytest.param(
            True,
            id='use-plus-wallet',
            marks=pytest.mark.client_experiments3(
                consumer='user-wallet/create',
                experiment_name='user_wallet_create_via_plus_wallet',
                args=[
                    {
                        'name': 'yandex_uid',
                        'type': 'string',
                        'value': 'yandex_uid',
                    },
                    {'name': 'currency', 'type': 'string', 'value': 'RUB'},
                ],
                value={},
            ),
        ),
        pytest.param(
            False,
            id='use-billing-wallet',
            marks=pytest.mark.client_experiments3(
                consumer='user-wallet/create',
                experiment_name='other_exp',
                args=[],
                value={},
            ),
        ),
    ],
)
async def test_create_user_wallet(
        library_context,
        mock_billing_wallet,
        mock_plus_wallet,
        use_plus_wallet,
        client_experiments3,
):
    @mock_billing_wallet('/create')
    def _mock_billing_wallet_create(request):
        assert request.json == {'yandex_uid': 'yandex_uid', 'currency': 'RUB'}
        return {'wallet_id': 'wallet_1'}

    @mock_plus_wallet('/v1/create')
    def _mock_plus_wallet_create(request):
        assert request.json == {
            'yandex_uid': 'yandex_uid',
            'currency': 'RUB',
            'user_ip': '1.2.3.4',
        }
        return {'wallet_id': 'wallet_1'}

    wallet_id = await library_context.user_wallet.create_wallet(
        yandex_uid='yandex_uid',
        currency='RUB',
        user_ip='1.2.3.4',
        experiments=client_experiments3,
    )

    if use_plus_wallet:
        assert not _mock_billing_wallet_create.has_calls
        assert _mock_plus_wallet_create.has_calls
    else:
        assert _mock_billing_wallet_create.has_calls
        assert not _mock_plus_wallet_create.has_calls

    assert wallet_id == 'wallet_1'
