import pytest


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.pgsql('contractor_merch_payments', files=['one_refund.sql'])
async def test_going_to_call_billing(
        taxi_contractor_merch_payments,
        stq_runner,
        pgsql,
        testpoint,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_taxi_tariffs,
        mock_taxi_agglomerations,
        mock_merchant_profiles,
        mock_billing_orders,
):
    mock_merchant_profiles.park_id = 'keking'

    @testpoint('refund-stq-is-going-to-call-billing')
    async def refund_stq_calls_billing(data):
        return {}

    await stq_runner.contractor_merch_payments_refund.call(
        task_id=f'some_task_id',
        kwargs={
            'payment_id': 'payment_id-success',
            'transaction_id': 'refund-id',
        },
    )

    assert refund_stq_calls_billing.times_called == 1


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.pgsql('contractor_merch_payments', files=['one_refund.sql'])
async def test_no_refund(
        taxi_contractor_merch_payments, stq_runner, pgsql, testpoint,
):
    @testpoint('refund-stq-is-going-to-call-billing')
    async def refund_stq_calls_billing(data):
        return {}

    await stq_runner.contractor_merch_payments_refund.call(
        task_id=f'some_task_id',
        kwargs={'payment_id': 'payment_id-success', 'transaction_id': 'some'},
    )

    assert refund_stq_calls_billing.times_called == 0


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.pgsql('contractor_merch_payments', files=['one_refund.sql'])
async def test_refund_handler_is_still_holding_lock(
        taxi_contractor_merch_payments, stq_runner, pgsql, testpoint,
):
    @testpoint('refund-stq-is-going-to-call-billing')
    async def refund_stq_calls_billing(data):
        return {}

    @testpoint('refund-after-stq-call')
    async def refund_after_stq_call(data):
        await stq_runner.contractor_merch_payments_refund.call(
            task_id=f'some_task_id',
            kwargs={
                'payment_id': 'payment_id-success',
                'transaction_id': 'some',
            },
            expect_fail=True,
        )

        return {}

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/refund',
        params={
            'payment_id': 'payment_id-success',
            'merchant_id': 'merchant-id-2',
        },
        headers={'X-Idempotency-Token': 'idemp1000000000000000000000000000'},
        json={'currency': 'RUB', 'amount': '10'},
    )

    assert response.status == 200

    assert refund_after_stq_call.times_called == 1
    assert refund_stq_calls_billing.times_called == 0


MOCK_TIME_NOW = '2021-07-01T14:00:00+00:00'

REQUEST_TO_FLEET_PARKS = {'query': {'park': {'ids': ['park-id-1']}}}
REQUEST_TO_PARKS_REPLICA = {
    'timestamp': '2021-07-01T14:00:00+00:00',
    'park_id': 'clid1',
    'consumer': 'contractor-merch',
}
REQUEST_TO_BILLING_REPLICATION = {
    'active_ts': '2021-07-01T14:00:00+0000',
    'service_id': '137',
    'actual_ts': '2021-07-01T14:00:00+0000',
    'client_id': 'some-billing-client-id',
}

REQUEST_TO_TAXI_TARIFFS = {'city_ids': 'city1', 'locale': 'en'}

REQUEST_TO_TAXI_AGGLOMERATIONS = {'tariff_zone': 'spb'}

REQUEST_TO_MERCHANT_PROFILES = {'merchant_id': 'merchant-id-2'}


@pytest.mark.now(MOCK_TIME_NOW)
@pytest.mark.pgsql('contractor_merch_payments', files=['one_refund.sql'])
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
async def test_call_billing_refund(
        taxi_contractor_merch_payments,
        load_json,
        stq_runner,
        pgsql,
        testpoint,
        mock_fleet_parks,
        mock_parks_replica,
        mock_billing_replication,
        mock_taxi_tariffs,
        mock_taxi_agglomerations,
        mock_merchant_profiles,
        mock_billing_orders,
):
    mock_merchant_profiles.park_id = 'merchant-park-id-1'
    billing_request_ok = load_json('billing_orders_request.json')

    billing_request_ok['orders'][0]['data']['payments'][0][
        'invoice_date'
    ] = MOCK_TIME_NOW
    billing_request_ok['orders'][0]['data']['template_entries'][0]['context'][
        'event_at'
    ] = MOCK_TIME_NOW
    billing_request_ok['orders'][0]['data']['template_entries'][1]['context'][
        'event_at'
    ] = MOCK_TIME_NOW
    billing_request_ok['orders'][0]['data']['topic_begin_at'] = MOCK_TIME_NOW
    billing_request_ok['orders'][0]['event_at'] = MOCK_TIME_NOW

    await stq_runner.contractor_merch_payments_refund.call(
        task_id=f'some_task_id',
        kwargs={
            'payment_id': 'payment_id-success',
            'transaction_id': 'refund-id',
        },
    )

    assert mock_billing_orders.times_called == 1

    request_to_billing = mock_billing_orders.next_call()['request'].json
    assert request_to_billing == billing_request_ok

    assert (
        REQUEST_TO_FLEET_PARKS
        == mock_fleet_parks.park_list.next_call()['request'].json
    )

    assert REQUEST_TO_BILLING_REPLICATION == dict(
        mock_billing_replication.billing_replication.next_call()[
            'request'
        ].query,
    )
    assert REQUEST_TO_TAXI_TARIFFS == dict(
        mock_taxi_tariffs.tariffs.next_call()['request'].query,
    )
    assert REQUEST_TO_TAXI_AGGLOMERATIONS == dict(
        mock_taxi_agglomerations.next_call()['request'].query,
    )
    assert REQUEST_TO_MERCHANT_PROFILES == dict(
        mock_merchant_profiles.merchant.next_call()['request'].query,
    )
