import pytest

from tests_contractor_merch_payments import utils


@pytest.mark.experiments3(filename='contractor_merch_test_params_1.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.pgsql('contractor_merch_payments', files=['pg_loyka_test.sql'])
async def test_loyka_no_billing(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_merchant_profiles,
        load_json,
):
    payment_id = 'payment_id-merchant_accepted-2'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'loyka_process',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-2',
            'contractor_id': 'contractor-id-2',
            'payment_id': payment_id,
        },
    )

    new_status = utils.get_fields_by_payment_id(pgsql, payment_id, ['status'])[
        0
    ]
    assert new_status == 'success'

    assert mock_billing_orders.times_called == 0


@pytest.mark.experiments3(filename='contractor_merch_test_params_1.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.pgsql('contractor_merch_payments', files=['pg_mobi_test.sql'])
async def test_mobi_no_billing(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_merchant_profiles,
        load_json,
):
    payment_id = 'payment_id-merchant_accepted'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': payment_id,
        },
    )

    new_status = utils.get_fields_by_payment_id(pgsql, payment_id, ['status'])[
        0
    ]
    assert new_status == 'success'

    assert mock_billing_orders.times_called == 0


@pytest.mark.experiments3(filename='contractor_merch_test_params_2.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.pgsql('contractor_merch_payments', files=['pg_mobi_test.sql'])
async def test_secret_shoppers(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_merchant_profiles,
        load_json,
):
    payment_id = 'payment_id-merchant_accepted'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': payment_id,
        },
    )

    new_status, status_reason = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status', 'status_reason'],
    )
    assert new_status == 'failed'
    assert status_reason == 'not_enough_money_on_drivers_balance'

    assert mock_billing_orders.times_called == 0
