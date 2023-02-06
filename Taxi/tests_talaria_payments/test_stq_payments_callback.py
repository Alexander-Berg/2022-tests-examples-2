import pytest


@pytest.mark.parametrize(
    'operation_status, notification_type, notification_status',
    [
        ('done', 'operation_finish', 'success'),
        ('failed', 'operation_finish', 'failed'),
        ('processing', 'operation_finish', None),
        ('done', 'transaction_clear', None),
    ],
)
async def test_wind_notification(
        load_json,
        mockserver,
        stq_runner,
        operation_status,
        notification_type,
        notification_status,
):
    @mockserver.json_handler(
        '/wind/pf/server/v1/yandexPayment/payment-callback',
    )
    def wind_payment_callback(request):
        assert request.headers['x-api-key'] == 'windapikey'
        assert request.json == {
            'operation_id': 'payment_id',
            'version': 2,
            'status': notification_status,
        }
        return {'result': 0}

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def transactions_invoice_retrieve(request):
        assert request.json == load_json('invoice_retrieve_request.json')
        return load_json('invoice_retrieve_response_held.json')

    kwargs = {
        'invoice_id': 'payment_id',
        'operation_id': '2',
        'operation_status': operation_status,
        'notification_type': notification_type,
        'transactions': [],
    }

    await stq_runner.talaria_payments_transactions_callback.call(
        task_id='task_id', kwargs=kwargs,
    )

    if notification_status:
        assert wind_payment_callback.times_called == 1
    else:
        assert wind_payment_callback.times_called == 0
    assert transactions_invoice_retrieve.times_called == 1


@pytest.mark.now('2021-12-31T21:02:00+00:00')
@pytest.mark.config(
    TALARIA_PAYMENTS_BILLING_NOTIFICATIONS={
        'ride_notifications': {
            'cost_default_settings': {},
            'cost_type_overrides': {},
            'discount_default_settings': {},
            'discount_type_overrides': {},
            'is_enabled': False,
            'stq_rescheduling_delay': 60,
        },
        'transaction_notifications': {
            'default_settings': {
                'is_enabled': True,
                'product': 'default_product',
                'payment_kind': 'default_payment_kind',
                'billing_client_id': 'default_billing_client_id',
                'contract_id': 'default_contract_id',
                'service_id': 123,
                'tariff_class': 'default_tariff_class',
                'transaction_type': 'default_transaction_type',
                'refunded_transaction_type': (
                    'default_refunded_transaction_type'
                ),
                'default_agglomeration': 'default_agglomeration',
                'vat': '0.1',
                'topic_prefix': '/taxi/scooters/talaria',
            },
            'charge_type_overrides': {
                'topup': {
                    'detailed_product': 'topup_detailed_product',
                    'payment_kind': 'topup_payment_kind',
                    'payload_extra': {
                        'topup_extra_payload_param': (
                            'topup_extra_payload_value'
                        ),
                    },
                },
            },
            'is_enabled': True,
        },
    },
)
async def test_billing_notification(load_json, mockserver, stq_runner):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def transactions_invoice_retrieve(request):
        assert request.json == load_json('invoice_retrieve_request.json')
        return load_json('invoice_retrieve_response_cleared.json')

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def billing_orders_process(request):
        assert request.json == load_json('billing_orders_process_request.json')
        return load_json('billing_orders_process_response.json')

    kwargs = {
        'invoice_id': 'payment_id',
        'operation_id': '2',
        'operation_status': 'done',
        'notification_type': 'transaction_clear',
        'transactions': [],
    }

    await stq_runner.talaria_payments_transactions_callback.call(
        task_id='task_id', kwargs=kwargs,
    )

    assert transactions_invoice_retrieve.times_called == 1
    assert billing_orders_process.times_called == 1
