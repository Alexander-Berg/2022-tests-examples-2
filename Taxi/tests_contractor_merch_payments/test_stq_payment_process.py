# pylint: disable=C0302

import pytest

from tests_contractor_merch_payments import utils

REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT = {
    'id_in_set': ['park-id-1_contractor-id-1'],
    'projection': ['data.balance_limit'],
}


@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.parametrize(
    ['payment_id', 'integrator'],
    [
        pytest.param(
            'payment_id-merchant_accepted', 'payments-bot', id='payments-bot',
        ),
        pytest.param(
            'payment_id-merchant_accepted-v2',
            'integration-api-mobi',
            id='mobi',
        ),
        pytest.param(
            'payment_id-merchant_accepted-v3',
            'integration-api-universal',
            id='universal',
        ),
    ],
)
async def test_action_approval(
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
        payment_id,
        integrator,
):
    park_id, contractor_id, merchant_id, price = (
        utils.get_fields_by_payment_id(
            pgsql,
            payment_id,
            ['park_id', 'contractor_id', 'merchant_id', 'price'],
        )
    )

    mock_merchant_profiles.park_id = 'merchant_park_id'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'{park_id}_{contractor_id}_{payment_id}',
        kwargs={
            'action_type': 'approve',
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
    )

    if integrator == 'payments-bot':
        notify_handler = mock_payments_bot.notify_on_payment_completion
        expected_request = {
            'payment': {
                'payment_id': payment_id,
                'status': 'payment_passed',
                'price': str(int(price)),
                'merchant_id': merchant_id,
                'created_at': '2021-11-12T12:00:00+00:00',
                'updated_at': '2021-11-12T12:00:00+00:00',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
        }
        assert notify_handler.times_called == 1
        assert notify_handler.next_call()['request'].json == expected_request
    elif integrator == 'integration-api-mobi':
        notify_handler = mock_integration_api.notify
        expected_request = {
            'payment': {
                'payment_id': payment_id,
                'status': 'payment_passed',
                'price': str(int(price)),
                'merchant_id': merchant_id,
                'contractor': {
                    'park_id': park_id,
                    'contractor_id': contractor_id,
                },
                'created_at': '2021-11-12T12:00:00+00:00',
                'updated_at': '2021-11-12T12:00:00+00:00',
            },
        }
        assert notify_handler.times_called == 1
        assert notify_handler.next_call()['request'].json == expected_request
    elif integrator == 'integration-api-universal':
        assert mock_integration_api.notify.times_called == 0
        assert mock_payments_bot.notify_on_payment_completion.times_called == 0

    assert mock_fleet_transactions_api.balances_list.times_called == 1
    balances_request = mock_fleet_transactions_api.balances_list.next_call()[
        'request'
    ]
    balances_request.json['query']['balance'].pop('accrued_ats')
    assert balances_request.json == {
        'query': {
            'balance': {},
            'park': {
                'driver_profile': {'ids': ['contractor-id-1']},
                'id': 'park-id-1',
            },
        },
    }

    assert mock_parks_activation.handler.times_called == 1
    assert mock_parks_activation.handler.next_call()['request'].json == {
        'ids_in_set': ['clid1'],
    }

    assert mock_fleet_parks.park_list.times_called == 2
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['park-id-1']}},
    }
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['merchant_park_id']}},
    }

    (new_status,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status'],
    )
    assert new_status == 'success'


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize('action_type', ['approve', 'decline'])
@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id,'
    'notifying, terminal_status, expected_status',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-draft',
            0,
            None,
            'draft',
            id='payment in draft state',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-success',
            0,
            None,
            'success',
            id='payment in success state',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-failed',
            0,
            None,
            'failed',
            id='payment in failed state',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-contractor_declined',
            0,
            None,
            'contractor_declined',
            id='payment in contractor_declined state',
        ),
        pytest.param(
            'park-id-2',
            'contractor-id-5',
            'payment_id-merchant_canceled',
            0,
            None,
            'merchant_canceled',
            id='payment in merchant_canceled state',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-another',
            'payment_id-merchant_accepted',
            0,
            None,
            'merchant_accepted',
            id='another driver wants to do smth',
        ),
    ],
)
async def test_states_except_draft(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_fleet_transactions_api,
        mock_merchant_profiles,
        mock_parks_activation,
        mock_fleet_parks,
        action_type,
        park_id,
        contractor_id,
        payment_id,
        notifying,
        terminal_status,
        expected_status,
):
    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'{park_id}_{contractor_id}_{payment_id}',
        kwargs={
            'action_type': action_type,
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
    )

    assert (
        mock_payments_bot.notify_on_payment_completion.times_called
        == notifying
    )

    (new_status,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status'],
    )
    assert new_status == expected_status


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id,'
    'notifying, terminal_status, expected_status',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_success',
            1,
            'payment_passed',
            'success',
            id='payment in target_success state',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_failed',
            1,
            'payment_failed',
            'failed',
            id='payment in target_failed state',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_contractor_declined',
            0,
            None,
            'target_contractor_declined',
            id='payment in target_contractor_declined state(invalid input)',
        ),
    ],
)
async def test_target_states_approve(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        park_id,
        contractor_id,
        payment_id,
        notifying,
        terminal_status,
        expected_status,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
):
    merchant_id, price = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['merchant_id', 'price'],
    )

    mock_merchant_profiles.park_id = 'merchant_park_id'

    # TODO: добавить `payment_method` после полной выкатки
    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'{park_id}_{contractor_id}_{payment_id}',
        kwargs={
            'action_type': 'approve',
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
        },
    )

    assert (
        mock_payments_bot.notify_on_payment_completion.times_called
        == notifying
    )

    if notifying:
        assert (
            mock_payments_bot.notify_on_payment_completion.next_call()[
                'request'
            ].json
            == {
                'payment': {
                    'payment_id': payment_id,
                    'status': terminal_status,
                    'price': str(int(price)),
                    'merchant_id': merchant_id,
                    'created_at': '2021-11-12T12:00:00+00:00',
                    'updated_at': '2021-11-12T12:00:00+00:00',
                    'metadata': {
                        'telegram_chat_id': 0,
                        'telegram_personal_id': 'telegram-personal-id-0',
                    },
                },
            }
        )

    (new_status,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status'],
    )
    assert new_status == expected_status


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id,'
    'notifying, terminal_status, expected_status',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_success',
            0,
            None,
            'target_success',
            id='payment in target_success state(invalid input)',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_failed',
            0,
            None,
            'target_failed',
            id='payment in target_failed state(invalid input)',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_contractor_declined',
            1,
            'contractor_declined',
            'contractor_declined',
            id='payment in target_contractor_declined state',
        ),
    ],
)
async def test_target_states_decline(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_fleet_parks,
        mock_merchant_profiles,
        park_id,
        contractor_id,
        payment_id,
        notifying,
        terminal_status,
        expected_status,
):
    merchant_id, price = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['merchant_id', 'price'],
    )

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'{park_id}_{contractor_id}_{payment_id}',
        kwargs={
            'action_type': 'decline',
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
    )

    assert (
        mock_payments_bot.notify_on_payment_completion.times_called
        == notifying
    )

    if notifying:
        assert (
            mock_payments_bot.notify_on_payment_completion.next_call()[
                'request'
            ].json
            == {
                'payment': {
                    'payment_id': payment_id,
                    'status': terminal_status,
                    'price': str(int(price)),
                    'merchant_id': merchant_id,
                    'created_at': '2021-11-12T12:00:00+00:00',
                    'updated_at': '2021-11-12T12:00:00+00:00',
                    'metadata': {
                        'telegram_chat_id': 0,
                        'telegram_personal_id': 'telegram-personal-id-0',
                    },
                },
            }
        )

    (new_status,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status'],
    )
    assert new_status == expected_status


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id,'
    'notifying, terminal_status, expected_status',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-merchant_accepted',
            1,
            'payment_passed',
            'success',
            id='payment in merchant_accepted state(happy pass)',
        ),
    ],
)
async def test_race_in_merchant_accepted_state(
        stq_runner,
        pgsql,
        testpoint,
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
        park_id,
        contractor_id,
        payment_id,
        notifying,
        terminal_status,
        expected_status,
):
    @testpoint('BeforeSettingTargetStatus')
    def before_setting_target_status(data):
        utils.update_status(pgsql, payment_id, 'target_contractor_declined')
        return data

    mock_merchant_profiles.park_id = 'merchant_park_id'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'{park_id}_{contractor_id}_{payment_id}',
        kwargs={
            'action_type': 'approve',
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
        expect_fail=True,
    )

    assert before_setting_target_status.times_called == 1

    assert mock_payments_bot.notify_on_payment_completion.times_called == 0

    assert mock_billing_orders.times_called == 0

    (new_status,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status'],
    )
    assert new_status == 'target_contractor_declined'


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id,'
    'notifying, terminal_status, expected_status',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-merchant_accepted',
            1,
            'contractor_declined',
            'contractor_declined',
            id='payment in merchant_accepted state(happy pass)',
        ),
    ],
)
async def test_action_refusal(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_fleet_transactions_api,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_parks,
        mock_merchant_profiles,
        park_id,
        contractor_id,
        payment_id,
        notifying,
        terminal_status,
        expected_status,
):
    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'{park_id}_{contractor_id}_{payment_id}',
        kwargs={
            'action_type': 'decline',
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
    )

    assert (
        mock_payments_bot.notify_on_payment_completion.times_called
        == notifying
    )
    (new_status,) = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status'],
    )
    assert new_status == expected_status


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.parametrize(
    [
        'balance',
        'balance_limit',
        'can_cash',
        'park_fields_update',
        'expected_status_reason',
    ],
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
            '1.000000',
            None,
            None,
            'not_enough_money_on_drivers_balance',
            id='not_enough_money_on_drivers_balance with balance_limit > 0',
        ),
        pytest.param(
            '39',
            '-1.000000',
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
            False,
            None,
            None,
            marks=[
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=True,
                ),
                pytest.mark.experiments3(
                    filename='contractor_merch_test_params_1.json',
                ),
            ],
            id='found in no_cash_check_park_ids and no_billing_merchant_ids',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            'park_has_not_enough_money',
            marks=[
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=True,
                ),
                pytest.mark.experiments3(
                    filename='contractor_merch_test_params_2.json',
                ),
            ],
            id='not found in no_cash_check_park_ids',
        ),
        pytest.param(
            None,
            None,
            False,
            None,
            'park_has_not_enough_money',
            marks=[
                pytest.mark.config(
                    CONTRACTOR_MERCH_PAYMENTS_ENABLE_CASH_CHECK=True,
                ),
                pytest.mark.experiments3(
                    filename='contractor_merch_test_params_3.json',
                ),
            ],
            id='not found in no_billing_merchant_ids',
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
            'payment_method': 'with_approval',
        },
    )

    assert mock_payments_bot.notify_on_payment_completion.times_called == 1

    if balance_limit:
        assert mock_driver_profiles.driver_profiles.times_called == 1
        assert (
            mock_driver_profiles.driver_profiles.next_call()['request'].json
            == REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT
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


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
async def test_cannot_prepare_billing_data(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_billing_replication,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mockserver,
):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _parks_replica(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'invalid_request',
                'message': 'Incorrect request arguments',
            },
        )

    mock_merchant_profiles.park_id = 'merchant_park_id'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': 'payment_id-target_success',
            'payment_method': 'with_approval',
        },
        expect_fail=True,
    )

    assert mock_payments_bot.notify_on_payment_completion.times_called == 0

    new_status = utils.get_fields_by_payment_id(
        pgsql, 'payment_id-target_success', ['status'],
    )[0]
    assert new_status == 'target_success'


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
async def test_happy_path(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        load_json,
):
    payment_id = 'payment_id-merchant_accepted'

    mock_merchant_profiles.park_id = 'merchant_park_id'
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

    assert mock_fleet_parks.park_list.times_called == 2
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['park-id-1']}},
    }
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['merchant_park_id']}},
    }

    billing_replication_request = (
        mock_billing_replication.billing_replication.next_call()['request']
    )
    assert utils.pop_keys(
        billing_replication_request.query, ['active_ts', 'actual_ts'],
    ) == {'client_id': 'buyer-client-id', 'service_id': '124'}

    billing_replication_request = (
        mock_billing_replication.billing_replication.next_call()['request']
    )
    assert utils.pop_keys(
        billing_replication_request.query, ['active_ts', 'actual_ts'],
    ) == {'client_id': 'merchant-client-id', 'service_id': '222'}

    parks_replice_request = mock_parks_replica.next_call()['request']
    assert utils.pop_keys(parks_replice_request.query, ['timestamp']) == {
        'consumer': 'contractor-merch',
        'park_id': 'buyer-clid',
    }

    parks_replice_request = mock_parks_replica.next_call()['request']
    assert utils.pop_keys(parks_replice_request.query, ['timestamp']) == {
        'consumer': 'contractor-merch',
        'park_id': 'merchant-clid',
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
            [
                'orders',
                0,
                'data',
                'sender',
                'template_entries',
                0,
                'context',
                'event_at',
            ],
            [
                'orders',
                0,
                'data',
                'recipient',
                'template_entries',
                0,
                'context',
                'event_at',
            ],
        ],
    ) == load_json('billing_orders_request_body.json')


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.pgsql(
    'contractor_merch_payments', files=['pending_purchases.sql'],
)
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=10)
@pytest.mark.parametrize(
    'park_id, contractor_id, payment_id, ok_expected',
    [
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-merchant_accepted',
            False,
            marks=pytest.mark.now('2021-07-01T14:00:56'),
            id='another in target_success is not ok',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-1',
            'payment_id-target_success',
            True,
            marks=pytest.mark.now('2021-07-01T14:00:06'),
            id='already in target_success is ok',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-2',
            'payment_id-merchant_accepted2',
            False,
            marks=pytest.mark.now('2021-07-01T14:00:06'),
            id='another in recent success is not ok',
        ),
        pytest.param(
            'park-id-1',
            'contractor-id-2',
            'payment_id-merchant_accepted2',
            True,
            marks=pytest.mark.now('2021-07-01T14:00:56'),
            id='another in old success is not ok',
        ),
    ],
)
async def test_pending_payments(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        park_id,
        contractor_id,
        payment_id,
        ok_expected,
):
    mock_merchant_profiles.park_id = 'merchant_park_id'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': park_id,
            'contractor_id': contractor_id,
            'payment_id': payment_id,
            'payment_method': 'with_approval',
        },
    )

    status, status_reason = utils.get_fields_by_payment_id(
        pgsql, payment_id, ['status', 'status_reason'],
    )

    assert status == ('success' if ok_expected else 'failed')
    assert status_reason == (
        None if ok_expected else 'contractor_has_pending_payments'
    )


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
async def test_payment_method(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
):
    mock_merchant_profiles.park_id = 'merchant_park_id'
    payment_id = 'payment_id-merchant_accepted-v3'

    await stq_runner.contractor_merch_payments_payment_process.call(
        task_id=f'some_task_id',
        kwargs={
            'action_type': 'approve',
            'park_id': 'park-id-1',
            'contractor_id': 'contractor-id-1',
            'payment_id': 'payment_id-merchant_accepted-v3',
            'payment_method': 'async',
            'async_pay_params': {
                'integrator': 'integration-api-universal',
                'merchant_id': 'merchant-id-2',
                'price': '40',
            },
        },
    )

    status = utils.get_fields_by_payment_id(pgsql, payment_id, ['status'])[0]
    assert status == 'merchant_accepted'


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.pgsql('contractor_merch_payments', files=['async_pay.sql'])
@pytest.mark.parametrize(
    'payment_id, async_pay_params, expected_status',
    [
        pytest.param(
            'payment_id-merchant_accepted-with-metadata',
            None,
            'success',
            id='not async_pay request',
        ),
        pytest.param(
            'payment_id-merchant_accepted-with-metadata',
            {
                'integrator': 'payments-bot',
                'merchant_id': 'merchant-id-2',
                'price': '40',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'success',
            id='async_pay ok with metadata',
        ),
        pytest.param(
            'payment_id-merchant_accepted-without-metadata',
            {
                'integrator': 'integration-api-universal',
                'merchant_id': 'merchant-id-2',
                'price': '40',
            },
            'success',
            id='async_pay ok with metadata',
        ),
        pytest.param(
            'payment_id-draft',
            {
                'integrator': 'payments-bot',
                'merchant_id': 'merchant-id-2',
                'price': '40',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'draft',
            id='async_pay params is not committed to db',
        ),
        pytest.param(
            'payment_id-merchant_accepted-with-metadata',
            {
                'integrator': 'asd',
                'merchant_id': 'merchant-id-2',
                'price': '40',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'merchant_accepted',
            id='async_pay params differs integrator',
        ),
        pytest.param(
            'payment_id-merchant_accepted-with-metadata',
            {
                'integrator': 'payments-bot',
                'merchant_id': 'asd',
                'price': '40',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'merchant_accepted',
            id='async_pay params differs merchant',
        ),
        pytest.param(
            'payment_id-merchant_accepted-with-metadata',
            {
                'integrator': 'payments-bot',
                'merchant_id': 'merchant-id-2',
                'price': '100',
                'metadata': {
                    'telegram_chat_id': 0,
                    'telegram_personal_id': 'telegram-personal-id-0',
                },
            },
            'merchant_accepted',
            id='async_pay params differs price',
        ),
        pytest.param(
            'payment_id-merchant_accepted-with-metadata',
            {
                'integrator': 'payments-bot',
                'merchant_id': 'merchant-id-2',
                'price': '40',
                'metadata': {},
            },
            'merchant_accepted',
            id='async_pay params differs metadata 1',
        ),
        pytest.param(
            'payment_id-merchant_accepted-without-metadata',
            {
                'integrator': 'integration-api-universal',
                'merchant_id': 'merchant-id-2',
                'price': '40',
                'metadata': {},
            },
            'merchant_accepted',
            id='async_pay params differs metadata 2',
        ),
    ],
)
async def test_async_pay_params_check(
        stq_runner,
        pgsql,
        mock_payments_bot,
        mock_integration_api,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_fleet_transactions_api,
        mock_fleet_parks,
        mock_parks_activation,
        mock_merchant_profiles,
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
        load_json,
        payment_id,
        async_pay_params,
        expected_status,
):
    mock_merchant_profiles.park_id = 'merchant_park_id'
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
            'payment_method': 'async',
            'async_pay_params': async_pay_params,
        },
    )

    new_status = utils.get_fields_by_payment_id(pgsql, payment_id, ['status'])[
        0
    ]
    assert new_status == expected_status


@pytest.mark.experiments3(filename='contractor_merch_test_params_default.json')
@pytest.mark.experiments3(filename='contractor_merch_permissions_enabled.json')
@pytest.mark.config(CONTRACTOR_MERCH_PAYMENTS_PAYMENTS_MIN_PERIOD_SEC=0)
@pytest.mark.pgsql('contractor_merch_payments', files=['async_pay.sql'])
async def test_async_pay_is_still_holding_lock(
        taxi_contractor_merch_payments,
        mock_merchant_profiles,
        stq_runner,
        pgsql,
        testpoint,
):
    @testpoint('async-pay-after-stq-call')
    async def async_pay_after_stq_call(data):
        await stq_runner.contractor_merch_payments_payment_process.call(
            task_id=f'some_task_id',
            kwargs={
                'action_type': 'approve',
                'park_id': 'park-id-1',
                'contractor_id': 'contractor-id-1',
                'payment_id': 'payment_id-draft',
                'async_pay_params': {
                    'integrator': 'integration-api-universal',
                    'merchant_id': 'merchant-id-2',
                    'price': '111',
                },
            },
            expect_fail=True,
        )

        return {}

    response = await taxi_contractor_merch_payments.post(
        '/internal/contractor-merch-payments/v1/payment/pay-async',
        params={'payment_id': 'payment_id-draft'},
        json={
            'merchant_id': 'merchant-id-2',
            'price': '111',
            'currency': 'rub',
            'integrator': 'integration-api-universal',
            'contractor': {
                'park_id': 'park-id-1',
                'contractor_id': 'contractor-id-1',
            },
        },
    )

    assert response.status == 200
    assert async_pay_after_stq_call.times_called == 1
    new_status = utils.get_fields_by_payment_id(
        pgsql, 'payment_id-draft', ['status'],
    )[0]
    assert new_status == 'merchant_accepted'
