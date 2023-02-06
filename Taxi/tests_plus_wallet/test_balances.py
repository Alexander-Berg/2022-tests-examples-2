import pytest


@pytest.mark.pgsql('personal_wallet', files=['wallets.sql'])
@pytest.mark.parametrize(
    'is_billing, allowed_currencies, is_resp_empty',
    [(True, ['RUB'], True), (False, ['RUB', 'KZT'], False)],
)
async def test_request_currencies_not_in_allowed(
        taxi_plus_wallet,
        taxi_config,
        mockserver,
        experiments3,
        load_json,
        is_billing,
        allowed_currencies,
        is_resp_empty,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/billing-wallet/balances')
    def handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'amount': '171.3000',
                'currency': 'RUB',
                'wallet_id': 'some_wallet_id',
            },
        )

    if is_billing:
        experiments3.add_experiments_json(
            load_json('exp3_billing_wallet_enabled.json'),
        )
        await taxi_plus_wallet.invalidate_caches()

    taxi_config.set(PLUS_WALLET_WALLET_CURRENCIES=allowed_currencies)

    yandex_uid = 'request_currency_not_in_allowed_id_rub'
    currencies = 'KZT'

    response = await taxi_plus_wallet.get(
        f'/v1/balances?currencies={currencies}&yandex_uid={yandex_uid}',
    )

    assert response.status_code == 200
    content = response.json()
    balances = content['balances']

    if is_resp_empty:
        assert balances == []
    else:
        assert len(balances) == 1
        wallet_id = balances[0]['wallet_id']
        assert wallet_id.startswith('z')


@pytest.mark.pgsql('personal_wallet', files=['wallets.sql'])
@pytest.mark.parametrize('currencies', ['?currencies=', '?'])
async def test_bad_currencies(taxi_plus_wallet, taxi_config, currencies):
    taxi_config.set(PLUS_WALLET_WALLET_CURRENCIES=['RUB'])

    yandex_uid = 'request_currency_not_in_allowed_id_rub'
    response = await taxi_plus_wallet.get(
        f'/v1/balances{currencies}&yandex_uid={yandex_uid}',
    )
    if currencies == '?':
        assert response.status_code == 200
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': 'bad_currencies',
            'message': 'Currencies can not be empty string',
        }
