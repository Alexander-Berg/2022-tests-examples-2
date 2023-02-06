import codecs

import pytest

STATUSES = [
    {
        'fleet_status': 'created',
        'oebs_statuses': ['CREATED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_created',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'transmitted',
        'oebs_statuses': ['TRANSMITTED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_transmitted',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'paid',
        'oebs_statuses': ['CONFIRMED', 'RECONCILED'],
        'selected': True,
        'tanker_key': {
            'key': 'status_paid',
            'keyset': 'opteum_page_report_payouts',
        },
    },
    {
        'fleet_status': 'canceled',
        'oebs_statuses': ['VOID', 'DEFERRED', 'RETURNED'],
        'selected': False,
        'tanker_key': {
            'key': 'status_canceled',
            'keyset': 'opteum_page_report_payouts',
        },
    },
]
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
        'tanker_key': 'category_cashless',
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
TRANSLATIONS_BACKEND_FLEET_PAYOUTS_WEB = {
    'th_payment_number': {'ru': 'payment_number'},
    'th_contract_id': {'ru': 'contract_id'},
    'th_transaction_date': {'ru': 'transaction_date'},
    'th_payment_id': {'ru': 'payment_id'},
    'th_payment_date': {'ru': 'payment_date'},
    'th_order_id': {'ru': 'order_id'},
    'th_park_id': {'ru': 'park_id'},
    'th_driver_id': {'ru': 'driver_id'},
    'th_driver_name': {'ru': 'driver_name'},
    'th_transaction_type': {'ru': 'transaction_type'},
    'th_transaction_id': {'ru': 'transaction_id'},
    'th_amount': {'ru': 'amount'},
    'th_currency': {'ru': 'currency'},
}
TRANSLATIONS = {
    'category_cashless': {'ru': 'Безнал'},
    'category_other': {'ru': 'Прочее'},
}
RESPONSE409 = {'body': '', 'code': 'NOT_ALLOWED_STATUS', 'message': '409'}


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_STATUSES=STATUSES,
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
@pytest.mark.translations(
    opteum_page_report_payouts=TRANSLATIONS,
    backend_fleet_payouts_web=TRANSLATIONS_BACKEND_FLEET_PAYOUTS_WEB,
)
async def test_ok(stq_runner, mockserver, load, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_fleet_reports_storage_file_upload(request):
        content = request.get_data()
        assert content.decode('utf-8-sig').replace('\r\n', '\n') == load(
            'result.csv',
        )
        assert content.startswith(codecs.BOM_UTF8)

    driver_profiles_stub = load_json('driver_profiles_success.json')
    billing_bank_orders_stub1 = load_json(
        'billing_bank_orders__payments_search__success.json',
    )
    billing_bank_orders_stub2 = load_json(
        'billing_bank_orders__payments_details__success.json',
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == driver_profiles_stub['request']['query']
        assert request.json == driver_profiles_stub['request']['body']
        return driver_profiles_stub['response']

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    async def _v1_parks_payments_search(request):
        assert request.json == billing_bank_orders_stub1['request']
        return billing_bank_orders_stub1['response']

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _v1_parks_payments_details(request):
        assert request.json == billing_bank_orders_stub2['request']
        return billing_bank_orders_stub2['response']

    await stq_runner.payout_details_async_download_preparer.call(
        task_id='1',
        args=(),
        kwargs={
            'charset': 'UTF-8-SIG',
            'locale': 'ru',
            'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef',
            'payment_at_from': '2020-01-27T00:00:00+04:00',
            'payment_at_to': '2020-01-28T23:59:59+04:00',
            'park_clid': '111111',
            'park_timezone': 3,
            'statuses': ['paid'],
        },
    )

    assert _mock_fleet_reports_storage_file_upload.has_calls


@pytest.mark.config(
    OPTEUM_REPORT_PAYOUTS_STATUSES=STATUSES,
    OPTEUM_REPORT_PAYOUTS_TRANSACTION_PRODUCTS=TRANSACTION_PRODUCTS,
)
@pytest.mark.translations(
    opteum_page_report_payouts=TRANSLATIONS,
    backend_fleet_payouts_web=TRANSLATIONS_BACKEND_FLEET_PAYOUTS_WEB,
)
async def test_success409(stq_runner, mockserver, load, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return mockserver.make_response(status=409, json=RESPONSE409)

    driver_profiles_stub = load_json('driver_profiles_success.json')
    billing_bank_orders_stub1 = load_json(
        'billing_bank_orders__payments_search__success.json',
    )
    billing_bank_orders_stub2 = load_json(
        'billing_bank_orders__payments_details__success.json',
    )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == driver_profiles_stub['request']['query']
        assert request.json == driver_profiles_stub['request']['body']
        return driver_profiles_stub['response']

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    async def _v1_parks_payments_search(request):
        assert request.json == billing_bank_orders_stub1['request']
        return billing_bank_orders_stub1['response']

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    async def _v1_parks_payments_details(request):
        assert request.json == billing_bank_orders_stub2['request']
        return billing_bank_orders_stub2['response']

    await stq_runner.payout_details_async_download_preparer.call(
        task_id='1',
        args=(),
        kwargs={
            'charset': 'UTF-8',
            'locale': 'ru',
            'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef',
            'payment_at_from': '2020-01-27T00:00:00+04:00',
            'payment_at_to': '2020-01-28T23:59:59+04:00',
            'park_clid': '111111',
            'park_timezone': 3,
            'statuses': ['paid'],
        },
    )
