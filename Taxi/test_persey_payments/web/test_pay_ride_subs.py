import pytest

from test_persey_payments import conftest


TPREFIX = 'persey-payments.thank_ride_screen'
CLIENT_MESSAGES = {
    f'{TPREFIX}.entry.title': {'ru': 'Спасибо за помощь'},
    f'{TPREFIX}.entry.text': {'ru': 'Вы пожертвовали $AMOUNT$'},
    'tanker_override': {'ru': 'Текст подменен'},
}
TARIFF = {
    'currency.rub': {'ru': 'руб.'},
    'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
    'currency_sign.rub': {'ru': '₽'},
}


@conftest.ride_subs_config()
@pytest.mark.translations(client_messages=CLIENT_MESSAGES, tariff=TARIFF)
@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    [
        'expected_invoice_create_request',
        'expected_invoice_update_request',
        'expected_donations',
        'invoice_started',
        'expected_paid_orders',
        'expected_resp',
        'expected_resp_code',
    ],
    [
        pytest.param(
            'expected_invoice_create_request_phonish.json',
            'expected_invoice_update_request.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '777',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            1,
            [['order777', '777.0000']],
            'expected_resp_simple.json',
            200,
        ),
        pytest.param(
            'expected_invoice_create_request_phonish.json',
            'expected_invoice_update_request.json',
            [
                (
                    'friends',
                    'phonish_uid',
                    '777',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'started',
                ),
            ],
            1,
            [['order777', '777.0000']],
            'expected_resp_tanker_override.json',
            200,
            marks=conftest.ride_subs_config(
                callback=lambda c: c['thank_ride_screen_static'].update(
                    {
                        '__tanker_overrides__': {
                            'persey-payments.thank_ride_screen.entry.title': (
                                'tanker_override'
                            ),
                        },
                    },
                ),
            ),
        ),
        pytest.param(
            None,
            None,
            [
                (
                    'friends',
                    'portal_uid',
                    '777',
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1,
                    'yataxi',
                    'order777',
                    'finished',
                ),
            ],
            0,
            [],
            'expected_resp_donation_conflict.json',
            400,
            marks=pytest.mark.pgsql(
                'persey_payments', files=['order_id_brand_conflict.sql'],
            ),
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        load_json,
        get_ride_subs,
        get_ride_subs_cache,
        get_donations,
        mock_invoice_create,
        mock_invoice_update,
        expected_invoice_create_request,
        expected_invoice_update_request,
        expected_donations,
        invoice_started,
        expected_paid_orders,
        expected_resp,
        expected_resp_code,
):
    invoice_create_mock = mock_invoice_create(expected_invoice_create_request)
    invoice_update_mock = mock_invoice_update(expected_invoice_update_request)

    response = await taxi_persey_payments_web.post(
        '/4.0/persey-payments/v1/charity/ride_subs/pay',
        json={
            'order_id': 'order777',
            'amount_info': {'amount': '777', 'currency_code': 'RUB'},
            'payment_tech': {
                'payment_method_id': (
                    'apple_token-685_BE7A5F59-AAAA-1111-2222-1CB9029C76AA'
                ),
                'payment_type': 'applepay',
            },
        },
        headers={
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-Request-Language': 'ru',
            'X-Yandex-UID': 'phonish_uid',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-Remote-IP': '127.0.0.1',
            'X-YaTaxi-UserId': 'some_taxi_user_id',
        },
    )

    assert response.status == expected_resp_code
    assert await response.json() == load_json(expected_resp)

    assert invoice_create_mock.times_called == invoice_started
    assert invoice_update_mock.times_called == invoice_started
    assert get_ride_subs_cache()['paid_order'] == expected_paid_orders
    assert get_donations() == expected_donations
