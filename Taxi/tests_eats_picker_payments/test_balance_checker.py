import pytest


@pytest.mark.config(
    EATS_PICKER_PAYMENTS_BALANCE_THRESHOLDS={
        'accounts_thresholds': [
            {'account_number': '1', 'thresholds': [1000000, 10000]},
            {'account_number': '2', 'thresholds': [1000000, 10000]},
            {'account_number': '3', 'thresholds': [1000000]},
        ],
    },
)
async def test_balance_checker(
        taxi_eats_picker_payments,
        tinkoff_service,
        taxi_eats_picker_payments_monitor,
):
    account1_name = 'First Account'
    tinkoff_service.add_account(
        name=account1_name, account_number='1', balance=9000.00,
    )
    account2_name = 'Second Account'
    tinkoff_service.add_account(
        name=account2_name, account_number='2', balance=11000.00,
    )
    account3_name = 'Third Account'
    tinkoff_service.add_account(
        name=account3_name, account_number='3', balance=10000000.00,
    )
    await taxi_eats_picker_payments.run_distlock_task(
        'balance-checker-component',
    )

    metrics = await taxi_eats_picker_payments_monitor.get_metric(
        'balance-checker-component',
    )
    assert metrics
    assert account1_name in metrics
    assert account2_name in metrics
    assert account3_name not in metrics

    account1 = metrics[account1_name]
    account2 = metrics[account2_name]

    assert '10000' in account1
    assert '1000000' in account2


API_TOKEN_TINKOFF = 'tinkoff-access-token'
API_TOKEN_TINKOFF_FALLBACK = 'tinkoff-access-token-fallback'

SECURED_TINKOFF_CLIENT = 'tinkoff-secured'
SECURED_TINKOFF_FALLBACK_CLIENT = 'tinkoff-secured-fallback'


@pytest.mark.parametrize('status_code', [200, 401, 403])
@pytest.mark.parametrize(
    'main_client', [SECURED_TINKOFF_CLIENT, SECURED_TINKOFF_FALLBACK_CLIENT],
)
@pytest.mark.parametrize('fallback_codes', [[], [401], [403], [401, 403]])
async def test_balance_checker_fallback(
        taxi_eats_picker_payments,
        mockserver,
        status_code,
        taxi_config,
        main_client,
        fallback_codes,
):
    taxi_config.set_values(
        {
            'EATS_PICKER_PAYMENTS_CLIENTS_SETTINGS': {
                'main_client': main_client,
                'use_fallback_if': fallback_codes,
            },
        },
    )
    await taxi_eats_picker_payments.invalidate_caches()

    def check_auth(headers, expected_token):
        assert 'Authorization' in headers
        auth = headers['Authorization']
        assert auth == 'Bearer ' + expected_token

    @mockserver.json_handler('/tinkoff-secured/api/v3/bank-accounts')
    def _get_accounts(request):
        check_auth(request.headers, API_TOKEN_TINKOFF)
        assert request.method == 'GET'
        if main_client == SECURED_TINKOFF_CLIENT:
            assert _get_accounts_fallback.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response(json=[])

    @mockserver.json_handler('/tinkoff-secured-fallback/api/v3/bank-accounts')
    def _get_accounts_fallback(request):
        check_auth(request.headers, API_TOKEN_TINKOFF_FALLBACK)
        assert request.method == 'GET'
        if main_client == SECURED_TINKOFF_FALLBACK_CLIENT:
            assert _get_accounts.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response(json=[])

    await taxi_eats_picker_payments.run_distlock_task(
        'balance-checker-component',
    )

    main_client_calls = (
        0
        if main_client == SECURED_TINKOFF_FALLBACK_CLIENT
        and status_code not in fallback_codes
        else 1
    )

    fallback_client_calls = (
        0
        if main_client == SECURED_TINKOFF_CLIENT
        and status_code not in fallback_codes
        else 1
    )

    assert _get_accounts.times_called == main_client_calls
    assert _get_accounts_fallback.times_called == fallback_client_calls
