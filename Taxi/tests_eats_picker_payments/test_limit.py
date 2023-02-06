import pytest


@pytest.mark.parametrize(
    'params,status',
    [
        ({'card_type': 'TinkoffBank', 'card_value': '12345678'}, 404),
        ({'card_type': 'unknown-type', 'card_value': '1234567'}, 400),
        ({'card_type': 'TinkoffBank', 'card_value': 'bad-value'}, 400),
    ],
)
async def test_get_limit_wrong_request(
        taxi_eats_picker_payments, tinkoff_service, params, status,
):
    response = await taxi_eats_picker_payments.get(
        '/api/v1/limit', params=params,
    )

    assert response.status == status


async def test_get_limit_ok(taxi_eats_picker_payments, tinkoff_service):
    get_limit = 100000.0
    card_value = '10000000'

    tinkoff_service.set_limit(card_value, get_limit)

    response = await taxi_eats_picker_payments.get(
        '/api/v1/limit',
        params={'card_type': 'TinkoffBank', 'card_value': card_value},
    )
    assert response.status == 200
    assert response.json()['amount'] == 100000.0


async def test_set_limit_ok(taxi_eats_picker_payments, tinkoff_service):
    params = {'card_type': 'TinkoffBank', 'card_value': '10000000'}
    response = await taxi_eats_picker_payments.post(
        '/api/v1/limit',
        params=params,
        json={'order_id': 'order-id-1', 'amount': 1000},
    )
    assert response.status == 200

    response = await taxi_eats_picker_payments.get(
        '/api/v1/limit', params=params,
    )
    assert response.status == 200
    assert response.json()['amount'] == 1000

    tinkoff_service.decrease_limit_remains(params['card_value'], 500)

    response = await taxi_eats_picker_payments.get(
        '/api/v1/limit', params=params,
    )
    assert response.status == 200
    assert response.json()['amount'] == 500


@pytest.mark.parametrize(
    'params,body,status',
    [
        (
            {'card_type': 'TinkoffBank', 'card_value': '10000000'},
            {'order_id': 'order-id-1', 'amount': 1000},
            200,
        ),
        (
            {'card_type': 'TinkoffBank', 'card_value': 'bad-cid'},
            {'order_id': 'order-id-1', 'amount': 1000},
            400,
        ),
        (
            {'card_type': 'TinkoffBank', 'card_value': '10000000'},
            {'order_id': 'order-id-1', 'amount': -1000},
            400,
        ),
    ],
)
async def test_set_limit_wrong_request(
        taxi_eats_picker_payments, tinkoff_service, params, body, status,
):
    response = await taxi_eats_picker_payments.post(
        '/api/v1/limit', params=params, json=body,
    )
    assert response.status == status


API_TOKEN_TINKOFF = 'tinkoff-access-token'
API_TOKEN_TINKOFF_FALLBACK = 'tinkoff-access-token-fallback'

SECURED_TINKOFF_CLIENT = 'tinkoff-secured'
SECURED_TINKOFF_FALLBACK_CLIENT = 'tinkoff-secured-fallback'


def check_auth(headers, expected_token):
    assert 'Authorization' in headers
    auth = headers['Authorization']
    assert auth == 'Bearer ' + expected_token


@pytest.mark.parametrize('status_code', [200, 401, 403])
@pytest.mark.parametrize(
    'main_client', [SECURED_TINKOFF_CLIENT, SECURED_TINKOFF_FALLBACK_CLIENT],
)
@pytest.mark.parametrize('fallback_codes', [[], [401], [403], [401, 403]])
async def test_get_limit_fallback(
        taxi_eats_picker_payments,
        mockserver,
        status_code,
        main_client,
        fallback_codes,
        taxi_config,
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

    ucid = 123456
    mock_response = {
        'ucid': ucid,
        'spendLimit': {
            'limitPeriod': 'IRREGULAR',
            'limitValue': 1234,
            'limitRemain': 5678,
        },
        'cashLimit': {
            'limitPeriod': 'IRREGULAR',
            'limitValue': 0,
            'limitRemain': 0,
        },
    }

    @mockserver.json_handler(f'/tinkoff-secured/api/v1/card/{ucid}/limits')
    def _get_limit(request):
        check_auth(request.headers, API_TOKEN_TINKOFF)
        assert request.method == 'GET'
        if main_client == SECURED_TINKOFF_CLIENT:
            assert _get_limit_fallback.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response(json=mock_response)

    @mockserver.json_handler(
        f'/tinkoff-secured-fallback/api/v1/card/{ucid}/limits',
    )
    def _get_limit_fallback(request):
        check_auth(request.headers, API_TOKEN_TINKOFF_FALLBACK)
        assert request.method == 'GET'
        if main_client == SECURED_TINKOFF_FALLBACK_CLIENT:
            assert _get_limit.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response(json=mock_response)

    await taxi_eats_picker_payments.get(
        '/api/v1/limit',
        params={'card_type': 'TinkoffBank', 'card_value': f'{ucid}'},
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

    assert _get_limit.times_called == main_client_calls
    assert _get_limit_fallback.times_called == fallback_client_calls


@pytest.mark.parametrize('status_code', [200, 401, 403])
@pytest.mark.parametrize(
    'main_client', [SECURED_TINKOFF_CLIENT, SECURED_TINKOFF_FALLBACK_CLIENT],
)
@pytest.mark.parametrize('fallback_codes', [[], [401], [403], [401, 403]])
async def test_set_limit_fallback(
        taxi_eats_picker_payments,
        mockserver,
        status_code,
        main_client,
        fallback_codes,
        taxi_config,
):
    ucid = 123456

    taxi_config.set_values(
        {
            'EATS_PICKER_PAYMENTS_CLIENTS_SETTINGS': {
                'main_client': main_client,
                'use_fallback_if': fallback_codes,
            },
        },
    )
    await taxi_eats_picker_payments.invalidate_caches()

    @mockserver.json_handler(
        f'/tinkoff-secured/api/v1/card/{ucid}/spend-limit',
    )
    def _set_spend_limit(request):
        check_auth(request.headers, API_TOKEN_TINKOFF)
        assert request.method == 'POST'
        if main_client == SECURED_TINKOFF_CLIENT:
            assert _set_spend_limit_fallback.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response()

    @mockserver.json_handler(f'/tinkoff-secured/api/v1/card/{ucid}/cash-limit')
    def _set_cash_limit(request):
        check_auth(request.headers, API_TOKEN_TINKOFF)
        assert request.method == 'POST'
        if main_client == SECURED_TINKOFF_CLIENT:
            assert _set_cash_limit_fallback.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response()

    @mockserver.json_handler(
        f'/tinkoff-secured-fallback/api/v1/card/{ucid}/spend-limit',
    )
    def _set_spend_limit_fallback(request):
        check_auth(request.headers, API_TOKEN_TINKOFF_FALLBACK)
        assert request.method == 'POST'
        if main_client == SECURED_TINKOFF_FALLBACK_CLIENT:
            assert _set_spend_limit.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response()

    @mockserver.json_handler(
        f'/tinkoff-secured-fallback/api/v1/card/{ucid}/cash-limit',
    )
    def _set_cash_limit_fallback(request):
        check_auth(request.headers, API_TOKEN_TINKOFF_FALLBACK)
        assert request.method == 'POST'
        if main_client == SECURED_TINKOFF_FALLBACK_CLIENT:
            assert _set_cash_limit.times_called == 0
            return mockserver.make_response(status=status_code, json=[])
        return mockserver.make_response()

    await taxi_eats_picker_payments.post(
        '/api/v1/limit',
        params={'card_type': 'TinkoffBank', 'card_value': f'{ucid}'},
        json={'order_id': 'order-id-1', 'amount': 1000},
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

    assert _set_spend_limit.times_called == main_client_calls
    assert _set_spend_limit_fallback.times_called == fallback_client_calls
    assert _set_cash_limit.times_called == (
        main_client_calls
        if (main_client == SECURED_TINKOFF_CLIENT and status_code == 200)
        or main_client == SECURED_TINKOFF_FALLBACK_CLIENT
        else 0
    )
    assert _set_cash_limit_fallback.times_called == (
        fallback_client_calls
        if (
            main_client == SECURED_TINKOFF_FALLBACK_CLIENT
            and status_code == 200
        )
        or main_client == SECURED_TINKOFF_CLIENT
        else 0
    )
