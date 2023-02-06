from .plugins import mock_yandex_stocks

CURRENCY_RATES_RESPONSE = {
    'rates': [
        {
            'from': 'RUB',
            'to': 'ILS',
            'rate': str(mock_yandex_stocks.STOCK_PRICE_2),
        },
    ],
}


async def test_currency_rates(taxi_grocery_payments, yandex_stocks):
    response = await taxi_grocery_payments.post(
        '/internal/v1/payments/currency-rates', json={},
    )

    assert response.status_code == 200

    assert yandex_stocks.ils_rub_stock.times_called == 1
    assert response.json() == CURRENCY_RATES_RESPONSE
