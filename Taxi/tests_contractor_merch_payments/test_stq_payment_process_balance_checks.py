import pytest

from tests_contractor_merch_payments import utils

REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT = {
    'id_in_set': ['park-id-1_contractor-id-1'],
    'projection': ['data.balance_limit'],
}


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.parametrize(
    'balance, balance_limit,'
    'can_cash, park_fields_update, expected_status_reason',
    [
        pytest.param(
            '39',
            '0',
            None,
            None,
            'not_enough_money_on_drivers_balance',
            id='not_enough_money_on_drivers_balance with balance_limit = 0',
        ),
        pytest.param(
            '40', '0', None, None, None, id='balance >= price - is ok',
        ),
        pytest.param(
            '40',
            '1',
            None,
            None,
            'not_enough_money_on_drivers_balance',
            id='not_enough_money_on_drivers_balance with balance_limit > 0',
        ),
        pytest.param(
            '39',
            '-1',
            None,
            None,
            'not_enough_money_on_drivers_balance',
            id='not_enough_money_on_drivers_balance with balance_limit < 0',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            'park_has_not_enough_money',
            id='park_has_not_enough_money enabled check',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            None,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=False,
            ),
            id='park_has_not_enough_money disabled check',
        ),
        pytest.param(
            None,
            None,
            None,
            {'is_billing_enabled': False},
            'billing_is_disabled_for_park',
            id='billing_is_disabled_for_park',
        ),
        pytest.param(
            None,
            None,
            None,
            {'country_id': 'ukr'},
            'unsupported_country',
            id='unsupported_country',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            'balance_payments_is_disabled_for_park',
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_DISABLED_PARK_IDS=['park-id-1'],
            ),
            id='balance_payments_is_disabled_for_park',
        ),
    ],
)
async def test_cannot_buy(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mockserver,
        balance,
        can_cash,
        park_fields_update,
        expected_status_reason,
        balance_limit,
):
    mock_driver_profiles.balance_limit = balance_limit

    mock_merchant_profiles.park_id = 'merchant_park_id'

    if balance:
        mock_fleet_transactions_api.balance = balance
    if can_cash is not None:
        mock_parks_activation.can_cash = can_cash
    if park_fields_update:
        mock_fleet_parks.fields_update = park_fields_update

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': 'payment_id-merchant_accepted',
        },
    )

    if balance_limit:
        assert mock_driver_profiles.driver_profiles.times_called == 1
        request_driver_profiles = (
            mock_driver_profiles.driver_profiles.next_call()['request'].json
        )
        assert (
            request_driver_profiles == REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT
        )

    new_status, status_reason = utils.get_fields_by_payment_id(
        pgsql, 'payment_id-merchant_accepted', ['status', 'status_reason'],
    )

    if expected_status_reason:
        assert new_status == 'failed'
        assert status_reason == expected_status_reason
    else:
        assert new_status == 'success'
        assert status_reason is None


REQUEST_TO_FLEET_ANTIFRAUD = {
    'park_id': 'park-id-1',
    'contractor_id': 'contractor-id-1',
    'do_update': 'false',
}


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.parametrize(
    'balance, fleet_antifraud_limit,' 'expected_status_reason',
    [
        pytest.param(
            '39',
            '0',
            'not_enough_money_on_drivers_balance',
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not_enough_money_on_drivers_balance with '
            'fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '39',
            '0',
            'not_enough_money_on_drivers_balance',
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not_enough_money_on_drivers_balance with '
            'fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '40',
            '1',
            'not_enough_money_on_drivers_balance',
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='balance >= price - is not' ' ok with enable_antifraud_check',
        ),
        pytest.param(
            '40',
            '1',
            None,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='balance >= price - is' ' ok without enable_antifraud_check',
        ),
        pytest.param(
            '39',
            '-1',
            'not_enough_money_on_drivers_balance',
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not_enough_money_on_drivers_balance '
            'with fleet_antifraud_limit < 0',
        ),
        pytest.param(
            '39',
            '-1',
            'not_enough_money_on_drivers_balance',
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not_enough_money_on_drivers_balance '
            'with fleet_antifraud_limit < 0',
        ),
    ],
)
async def test_cannot_pass_antifraud_limit(
        taxi_config,
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mockserver,
        balance,
        expected_status_reason,
        fleet_antifraud_limit,
):
    mock_fleet_antifraud.fleet_antifraud_limit = fleet_antifraud_limit

    mock_merchant_profiles.park_id = 'merchant_park_id'

    mock_fleet_transactions_api.balance = balance

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': 'payment_id-merchant_accepted',
        },
    )

    if (
            taxi_config.get('CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK')
            is not None
            and taxi_config.get(
                'CONTRACTOR_MERCH_PAYMENTS_ENABLE_ANTIFRAUD_CHECK',
            )
    ):
        assert mock_fleet_antifraud.fleet_antifraud.times_called == 1

        request_query_fleet_antifraud = dict(
            mock_fleet_antifraud.fleet_antifraud.next_call()['request'].query,
        )
        assert request_query_fleet_antifraud == REQUEST_TO_FLEET_ANTIFRAUD

    new_status, status_reason = utils.get_fields_by_payment_id(
        pgsql, 'payment_id-merchant_accepted', ['status', 'status_reason'],
    )

    if expected_status_reason:
        assert new_status == 'failed'
        assert status_reason == expected_status_reason
    else:
        assert new_status == 'success'
        assert status_reason is None


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_1.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_MAX_BALANCE_DEBT='-250.00')
@pytest.mark.parametrize(
    'initial_balance, status', [('-100', 'success'), ('-240', 'failed')],
)
async def test_optional_balance_check(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mockserver,
        initial_balance,
        status,
):
    mock_merchant_profiles.park_id = 'merchant_park_id'
    mock_fleet_transactions_api.balance = initial_balance
    mock_merchant_profiles.enable_balance_check_on_pay = False

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': 'payment_id-merchant_accepted',
        },
    )

    new_status, status_reason = utils.get_fields_by_payment_id(
        pgsql, 'payment_id-merchant_accepted', ['status', 'status_reason'],
    )

    assert mock_merchant_profiles.merchant.times_called == 1

    assert new_status == status
    if status == 'failed':
        assert status_reason == 'not_enough_money_on_drivers_balance'
