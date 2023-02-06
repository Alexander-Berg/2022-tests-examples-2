import pytest


DEFAULT_RECEIPT_SETTINGS = {
    'show_trust_receipt_countries': ['rus'],
    'show_fetched_receipt_countries': ['kaz'],
    'show_trust_receipt_payment_methods': [
        'card',
        'applepay',
        'googlepay',
        'coop_account',
    ],
    'trust_receipt_url_tmpl': (
        'https://trust.yandex.ru/receipts/{order_id}/'
        '#receipt_url_pdf='
        'https://trust.yandex.ru/receipts/{order_id}/?mode=pdf'
    ),
    'check_url_tmpl': (
        'https://check.yandex.ru/mobile/?n={n}&fn={fn}&fpd={fpd}'
        '#receipt_url_pdf='
        'https://check.yandex.ru/pdf/?n={n}&fn={fn}&fpd={fpd}'
    ),
    'show_partial_receipts': True,
}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    [
        'trust_response',
        'expected_receipts',
        'trust_error',
        'exp_trust_times_called',
        'order_core_response',
        'trust_order_id',
    ],
    [
        (
            'yb_trust_payments_resp_simple.json',
            'expected_receipts_simple.json',
            False,
            1,
            'order_core_resp_receipts',
            '124-cba',
        ),
        (
            'yb_trust_payments_resp_one.json',
            'expected_receipts_one.json',
            False,
            1,
            'order_core_resp_receipts',
            '124-cba',
        ),
        (
            'yb_trust_payments_resp_empty.json',
            'expected_receipts_zero.json',
            False,
            1,
            'order_core_resp_receipts',
            '124-cba',
        ),
        pytest.param(
            'yb_trust_payments_resp_simple.json',
            'expected_receipts_simple.json',
            False,
            1,
            'order_core_resp_receipts_cargo',
            '4747-cba',
            marks=pytest.mark.config(
                RIDEHISTORY_DELIVERY_BILLING_SERVICE_FOR_RECEIPTS_SETTINGS={
                    'cargo_tariffs': [],
                    'delivery_billing_service': 4747,
                },
            ),
        ),
        pytest.param(
            'yb_trust_payments_resp_simple.json',
            'expected_receipts_simple.json',
            False,
            1,
            'order_core_resp_receipts',
            '124-cba',
            marks=pytest.mark.config(
                RIDEHISTORY_DELIVERY_BILLING_SERVICE_FOR_RECEIPTS_SETTINGS={
                    'cargo_tariffs': [],
                    'delivery_billing_service': 4747,
                },
            ),
        ),
        pytest.param(
            None,
            'expected_receipts_fallback.json',
            False,
            0,
            'order_core_resp_receipts',
            '124-cba',
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{'show_partial_receipts': False},
                },
            ),
        ),
        pytest.param(
            None,
            'expected_receipts_fallback.json',
            False,
            0,
            'order_core_resp_receipts',
            '124-cba',
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{'show_trust_receipt_payment_methods': []},
                },
            ),
        ),
        pytest.param(
            None,
            'expected_receipts_fallback.json',
            False,
            0,
            'order_core_resp_receipts',
            '124-cba',
            marks=pytest.mark.config(
                BILLING_SERVICE_NAME_MAP_BY_BRAND={
                    '__default__': 'nonexistent',
                },
            ),
        ),
        (
            None,
            'expected_receipts_fallback.json',
            True,
            2,
            'order_core_resp_receipts',
            '124-cba',
        ),
        pytest.param(
            None,
            'expected_receipts_fallback.json',
            False,
            0,
            'order_core_resp_receipts',
            '124-cba',
            marks=pytest.mark.config(
                RIDEHISTORY_RECEIPT_SETTINGS={
                    **DEFAULT_RECEIPT_SETTINGS,
                    **{
                        'show_trust_receipt_countries': [],
                        'show_fetched_receipt_countries': ['rus'],
                    },
                },
            ),
        ),
    ],
)
async def test_simple(
        taxi_ridehistory,
        load_json,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_yb_trust_payments,
        trust_response,
        expected_receipts,
        trust_error,
        exp_trust_times_called,
        order_core_response,
        trust_order_id,
):
    mock_order_core_query(['1'], order_core_response, True)
    mock_transactions_query(['1'], 'transactions_resp_simple')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    yb_trust_payments_mock = mock_yb_trust_payments(
        trust_order_id, trust_response, trust_error,
    )

    response = await taxi_ridehistory.get(
        '/4.0/ridehistory/v2/receipts/?order_id=1',
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json() == load_json(expected_receipts)
    assert yb_trust_payments_mock.times_called == exp_trust_times_called

    response = await taxi_ridehistory.post(
        '/v2/receipts',
        json={'order_id': '1'},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json() == load_json(expected_receipts)
    assert yb_trust_payments_mock.times_called == 2 * exp_trust_times_called
