import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
async def test_happy_path(
        stq_runner,
        pgsql,
        mock_billing_orders,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_integration_api,
        mock_merchant_profiles,
        mock_parks_activation,
        mock_parks_replica,
        mock_payments_bot,
        mock_taxi_agglomerations,
        mock_taxi_tariffs,
        load_json,
):
    payment_id = 'payment_id-merchant_accepted'

    mock_merchant_profiles.park_id = 'merchant_park_id'
    mock_merchant_profiles.payment_scheme = 'yandex_withhold'

    mock_fleet_parks.clids_mapping = {
        'park-id-1': 'buyer-clid',
        'merchant_park_id': 'merchant-clid',
    }

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
    )

    new_status = utils.get_fields_by_payment_id(pgsql, payment_id, ['status'])[
        0
    ]
    assert new_status == 'success'

    assert mock_fleet_parks.park_list.times_called == 1
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['park-id-1']}},
    }

    billing_replication_request = (
        mock_billing_replication.billing_replication.next_call()['request']
    )
    assert utils.pop_keys(
        billing_replication_request.query, ['active_ts', 'actual_ts'],
    ) == {'client_id': 'buyer-client-id', 'service_id': '128'}

    parks_replica_request = mock_parks_replica.next_call()['request']
    assert utils.pop_keys(parks_replica_request.query, ['timestamp']) == {
        'consumer': 'contractor-merch',
        'park_id': 'buyer-clid',
    }

    fleet_transactions_api_request = (
        mock_fleet_transactions_api.balances_list.next_call()['request']
    )
    assert utils.pop_keys(
        fleet_transactions_api_request.json, [['query', 'balance']],
    ) == load_json('fleet_transactions_api_request_body.json')

    park_activation_request = mock_parks_activation.handler.next_call()[
        'request'
    ]
    assert park_activation_request.json == {'ids_in_set': ['buyer-clid']}

    billing_orders_request = mock_billing_orders.next_call()['request']
    assert utils.pop_keys(
        billing_orders_request.json,
        [
            ['orders', 0, 'event_at'],
            ['orders', 0, 'data', 'payments', 0, 'invoice_date'],
            [
                'orders',
                0,
                'data',
                'template_entries',
                0,
                'context',
                'event_at',
            ],
            ['orders', 0, 'data', 'topic_begin_at'],
        ],
    ) == load_json('billing_orders_request_body.json')
