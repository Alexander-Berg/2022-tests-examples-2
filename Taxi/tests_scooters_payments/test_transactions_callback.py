import pytest


@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
async def test_transactions_callback(
        taxi_scooters_payments,
        taxi_scooters_payments_monitor,
        mockserver,
        mocked_time,
        stq_runner,
        load_json,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json(
            'invoice_retrieve_expected_request.json',
        )
        return load_json('invoice_retrieve_held.json')

    await stq_runner.scooters_payments_transactions_callback.call(
        task_id='SESSION_ID:update:1:done:operation_finish',
        args=['SESSION_ID', 'update:1', 'done', 'operation_finish'],
        kwargs={
            'transactions': [
                {
                    'external_payment_id': 'EXTERNAL_PAYMENT_ID',
                    'status': 'hold_success',
                    'payment_type': 'card',
                },
            ],
        },
    )

    assert invoice_retrieve.times_called == 1

    mocked_time.sleep(5)
    await taxi_scooters_payments.tests_control(invalidate_caches=False)

    metrics = await taxi_scooters_payments_monitor.get_metric(
        'scooters_payments_metrics',
    )
    assert metrics == {
        'holding_time': {
            '$meta': {'solomon_children_labels': 'percentile'},
            'p100': 19,
            'p50': 19,
            'p75': 19,
            'p90': 19,
            'p95': 19,
            'p98': 19,
            'p99': 19,
        },
    }
