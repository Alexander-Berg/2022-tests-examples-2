import pytest

from test_iiko_integration import stubs

EXPECTED_RESPONSE_STATUS = 400
EXPECTED_RESPONSE_JSON = {
    'code': 'service_unavailable',
    'message': 'Service is turned off by config',
}


@pytest.mark.config(
    **stubs.RESTAURANT_INFO_CONFIGS, IIKO_INTEGRATION_SERVICE_AVAILABLE=False,
)
async def test_create_order(web_app_client):
    response = await web_app_client.post(
        '/external/v1/orders',
        headers={
            'X-YaTaxi-Api-Key': stubs.ApiKey.RESTAURANT_01,
            'X-Idempotency-Token': 'idempotency',
        },
        json={
            'restaurant_order_id': '123',
            'total_price': '1337.00',
            'currency': 'RUB',
            'discount': '0',
            'items': [
                {
                    'product_id': '1',
                    'name': 'afood',
                    'price_per_unit': '1337.00',
                    'quantity': '1.00',
                    'price_without_discount': '1337.00',
                    'price_for_customer': '1337.00',
                    'discount_amount': '0.00',
                    'discount_percent': '0.00',
                    'vat_amount': '240.66',
                    'vat_percent': '18',
                },
            ],
        },
    )
    assert response.status == EXPECTED_RESPONSE_STATUS
    response_json = await response.json()
    assert response_json == EXPECTED_RESPONSE_JSON


@pytest.mark.config(IIKO_INTEGRATION_SERVICE_AVAILABLE=False)
async def test_get_order(web_app_client):
    response = await web_app_client.get('/v1/order?id=01&locale=EN')
    assert response.status == EXPECTED_RESPONSE_STATUS
    response_json = await response.json()
    assert response_json == EXPECTED_RESPONSE_JSON
