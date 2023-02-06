import pytest

from test_persey_payments import conftest

PPREFIX = 'persey-payments.pay_ride_screen'
TPREFIX = 'persey-payments.thank_ride_screen'
CLIENT_MESSAGES = {
    f'{PPREFIX}.entry.title': {'ru': 'Подтвердить пожертвование'},
    f'{PPREFIX}.entry.text': {'ru': 'Перевести $AMOUNT$'},
    f'{PPREFIX}.confirmation_dialog.title': {'ru': 'Подтвердить помощь'},
    f'{PPREFIX}.confirmation_dialog.text': {'ru': 'Длинный текст $AMOUNT$'},
    f'{PPREFIX}.confirmation_dialog.cancel_button_text': {'ru': 'Закрыть'},
    f'{PPREFIX}.confirmation_dialog.confirm_button_text': {'ru': 'Здорово'},
    f'{TPREFIX}.entry.title': {'ru': 'Спасибо за помощь'},
    f'{TPREFIX}.entry.text': {'ru': 'Вы пожертвовали $AMOUNT$'},
    'some_tanker_key': {'ru': 'Донат друзьям'},
    'tanker_override': {'ru': 'Текст подменен'},
}
TARIFF = {
    'currency.rub': {'ru': 'руб.'},
    'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
    'currency_sign.rub': {'ru': '₽'},
}


@conftest.ride_subs_config()
@pytest.mark.config(
    PERSEY_PAYMENTS_FUNDS={
        'operator_uid': '123',
        'funds': [
            {
                'fund_id': 'some_fund',
                'name': 'Имя фонда',
                'balance_client_id': '123',
                'offer_link': '456',
            },
            {
                'fund_id': 'applepay_fund',
                'name': 'Имя фонда',
                'balance_client_id': '123',
                'offer_link': '456',
                'applepay': {
                    'merchant_ids': ['taxi', 'taxi1'],
                    'country_code': 'ru',
                    'item_title_tanker_key': 'some_tanker_key',
                    'trust_service_token': 'some_service_token',
                },
            },
        ],
    },
)
@pytest.mark.translations(client_messages=CLIENT_MESSAGES, tariff=TARIFF)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'request_params, expected_resp',
    [
        (
            {
                'order_id': 'order1',
                'payment_tech_type': 'applepay',
                'ride_cost': '6',
            },
            'expected_resp_pay.json',
        ),
        pytest.param(
            {
                'order_id': 'order1',
                'payment_tech_type': 'applepay',
                'ride_cost': '6',
            },
            'expecter_resp_pay_tanker_override.json',
            marks=conftest.ride_subs_config(
                callback=lambda c: c['pay_ride_screen_static'].update(
                    {
                        '__tanker_overrides__': {
                            'persey-payments.pay_ride_screen.entry.title': (
                                'tanker_override'
                            ),
                        },
                    },
                ),
            ),
        ),
        (
            {
                'order_id': 'order1',
                'payment_tech_type': 'applepay',
                'ride_cost': '10',
            },
            'expected_resp_empty.json',
        ),
        (
            {
                'order_id': 'order1',
                'payment_tech_type': 'card',
                'ride_cost': '6',
            },
            'expected_resp_empty.json',
        ),
        (
            {
                'order_id': 'order2',
                'payment_tech_type': 'applepay',
                'ride_cost': '6',
            },
            'expected_resp_thank.json',
        ),
        pytest.param(
            {
                'order_id': 'order2',
                'payment_tech_type': 'applepay',
                'ride_cost': '6',
            },
            'expected_resp_thank_tanker_override.json',
            marks=conftest.ride_subs_config(
                callback=lambda c: c['thank_ride_screen_static'].update(
                    {
                        '__tanker_overrides__': {
                            'persey-payments.thank_ride_screen.entry.text': (
                                'tanker_override'
                            ),
                        },
                    },
                ),
            ),
        ),
        (
            {
                'order_id': 'order3',
                'payment_tech_type': 'applepay',
                'ride_cost': '6',
            },
            'expected_resp_empty.json',
        ),
        (
            {
                'order_id': 'nonexistent',
                'payment_tech_type': 'applepay',
                'ride_cost': '6',
            },
            'expected_resp_empty.json',
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web, load_json, request_params, expected_resp,
):
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/ride_donation/calculate',
        params=request_params,
        headers={'X-Request-Language': 'ru'},
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)
