import aiohttp.web
import pytest

TRANSACTION_PRODUCTS = [
    {
        'category_id': 'cashless',
        'products': [
            {'product': 'ALFA'},
            {'product': 'BRAINTREE'},
            {'product': 'CARDPAY'},
            {'product': 'ECOMMPAY'},
            {'product': 'KASSANOVA'},
            {'product': 'PAYBOX'},
            {'product': 'PAYCASH'},
            {'product': 'PAYTURE'},
            {'product': 'SBERBANK'},
            {'product': 'VTB'},
        ],
    },
    {
        'category_id': 'tips',
        'products': [
            {'product': 'ECOMMPAY_AZ', 'product_details': 'tips'},
            {'product': 'ALFA', 'product_details': 'tips'},
            {'product': 'BRAINTREE', 'product_details': 'tips'},
            {'product': 'CARDPAY', 'product_details': 'tips'},
            {'product': 'ECOMMPAY', 'product_details': 'tips'},
            {'product': 'KASSANOVA', 'product_details': 'tips'},
            {'product': 'OPEN', 'product_details': 'tips'},
            {'product': 'PAYBOX', 'product_details': 'tips'},
            {'product': 'PAYCASH', 'product_details': 'tips'},
            {'product': 'PAYTURE', 'product_details': 'tips'},
            {'product': 'SBERBANK', 'product_details': 'tips'},
            {'product': 'VTB', 'product_details': 'tips'},
        ],
    },
    {
        'category_id': 'gas_station',
        'products': [
            {'product': 'CORRECTION_FUEL_HOLD'},
            {'product': 'FUEL_FACT', 'product_details': 'comission'},
            {'product': 'FUEL_HOLD'},
            {'product': 'FUEL_HOLD_PAYMENT'},
            {'product': 'FUEL_HOLD_RETURN', 'product_details': 'comission'},
        ],
    },
    {
        'category_id': 'compensation',
        'products': [{'product': 'YA_COMPENSATION'}],
    },
    {'category_id': 'corporate', 'products': [{'product': 'YA_CORPORATE'}]},
    {
        'category_id': 'netting',
        'products': [
            {'product': 'YA_NETTING'},
            {'product': 'CORRECTION_NETTING'},
        ],
    },
    {'category_id': 'promocodes', 'products': [{'product': 'YA_PROMOCODES'}]},
    {'category_id': 'scouts', 'products': [{'product': 'YA_SCOUTS'}]},
]


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
async def test_success(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_billing_bank_orders,
):
    service_stub = load_json('service_success.json')
    billing_bank_orders_stub = load_json('billing_bank_orders_success.json')

    @mock_billing_bank_orders('/v1/parks/payments/summary')
    async def _v1_parks_payments_summary(request):
        assert request.json == billing_bank_orders_stub['request']
        return aiohttp.web.json_response(billing_bank_orders_stub['response'])

    response = await web_app_client.post(
        '/api/v1/reports/payouts/summary',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']


@pytest.mark.config(OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=[])
async def test_empty_config(web_app_client, headers, load_json):
    stub = load_json('service_success.json')
    response = await web_app_client.post(
        '/api/v1/reports/payouts/summary',
        headers=headers,
        json=stub['request'],
    )

    assert response.status == 500
