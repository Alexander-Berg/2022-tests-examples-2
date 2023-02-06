import copy
import decimal

import pytest

from tests_contractor_merch import util

TRANSLATIONS = util.STQ_TRANSLATIONS
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS

REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT = {
    'id_in_set': ['park_id_driver_id'],
    'projection': ['data.balance_limit'],
}

RESPONSE_FROM_DRIVER_PROFILES_BALANCE_LIMIT = {
    'profiles': [
        {
            'data': {'balance_limit': '0'},
            'park_driver_profile_id': 'change this id in mock',
        },
    ],
}

DEFAULT_TASK_ID = 'some_task_id'
DEFAULT_STQ_KWARGS = {
    'driver_id': 'driver1',
    'park_id': 'park_id',
    'feed_id': 'some_id',
    'idempotency_token': 'idemp1',
    'accept_language': 'en_GB',
    'price': '2.4',
    'price_with_currency': {'value': '2.4', 'currency': 'RUB'},
    'feed_payload': {
        'category': 'cat',
        'feeds_admin_id': 'feeds-admin-id-1',
        'balance_payment': True,
        'title': 'Gift card (1000 rub)',
        'partner': {'name': 'Apple'},
        'meta_info': {},
    },
}
DEFAULT_CALL_ARGS = dict(task_id=DEFAULT_TASK_ID, kwargs=DEFAULT_STQ_KWARGS)
DEFAULT_OK_VOUCHER = {
    'id': 'idemp1',
    'park_id': 'park_id',
    'driver_id': 'driver1',
    'idempotency_token': 'idemp1',
    'price': decimal.Decimal('2.4000'),
    'currency': 'RUB',
    'promocode_id': 'p1',
    'feeds_admin_id': 'feeds-admin-id-1',
    'feed_id': 'some_id',
    'status': 'fulfilled',
    'status_reason': None,
}


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.now('2021-07-01T14:00:00Z')
@pytest.mark.parametrize(
    ['total_balance', 'balance_limit'],
    [
        pytest.param(
            '119', '0', id='not enough total_balance with balance_limit = 0',
        ),
        pytest.param('130', '11', id='not enough with balance_limit > 0'),
        pytest.param('119', '-1', id='not enough with balance_limit < 0'),
    ],
)
async def test_balance(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
        mockserver,
        total_balance,
        balance_limit,
):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles(request):
        resp = copy.deepcopy(RESPONSE_FROM_DRIVER_PROFILES_BALANCE_LIMIT)
        resp['profiles'][0]['data']['balance_limit'] = balance_limit
        resp['profiles'][0]['park_driver_profile_id'] = request.json[
            'id_in_set'
        ][0]
        return resp

    mock_fleet_transactions_api.balance = total_balance
    mock_driver_profiles.driver_profiles = _driver_profiles

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '120',
            'price_with_currency': {'value': '120', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {},
            },
        },
    )

    request_to_driver_profiles = copy.deepcopy(
        REQUEST_TO_DRIVER_PROFILES_BALANCE_LIMIT,
    )
    request_to_driver_profiles['id_in_set'] = ['park_id_driver_id']
    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert (
        mock_driver_profiles.driver_profiles.next_call()['request'].json
        == request_to_driver_profiles
    )

    voucher = util.get_voucher_by_idemp(
        cursor, 'park_id', 'driver_id', 'idemp3', with_created_at=False,
    )
    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': 'driver_id',
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('120'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None,
        'status': 'failed',
        'status_reason': 'not_enough_money_on_drivers_balance',
    }

    assert mock_fleet_transactions_api.balances_list.times_called == 1
    assert (
        mock_fleet_transactions_api.balances_list.next_call()['request'].json
        == {
            'query': {
                'balance': {'accrued_ats': ['2021-07-01T14:00:00+00:00']},
                'park': {
                    'driver_profile': {'ids': ['driver_id']},
                    'id': 'park_id',
                },
            },
        }
    )

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': 'park_id_driver_id'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': 'not_enough_money_on_drivers_balance-tr',
            'title': 'Gift card (1000 rub): failed',
            'type': 'newsletter',
        },
    }


REQUEST_TO_FLEET_ANTIFRAUD = {
    'park_id': 'park_id',
    'contractor_id': 'driver_id',
    'do_update': 'false',
}


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.now('2021-07-01T14:00:00Z')
@pytest.mark.parametrize(
    ['total_balance', 'fleet_antifraud_limit', 'is_enough'],
    [
        pytest.param(
            '119',
            '0',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not enough total_balance with fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '119',
            '0',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not enough total_balance with fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '120',
            '1',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not enough with fleet_antifraud_limit > 0',
        ),
        pytest.param(
            '120',
            '1',
            True,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='enough with fleet_antifraud_limit > 0'
            ' and config_antifraud_check off ',
        ),
        pytest.param(
            '119',
            '-1',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not enough with fleet_antifraud_limit < 0',
        ),
        pytest.param(
            '119',
            '-1',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not enough with fleet_antifraud_limit < 0',
        ),
    ],
)
async def test_fleet_antifraud(
        taxi_config,
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
        total_balance,
        fleet_antifraud_limit,
        is_enough,
):
    mock_fleet_transactions_api.balance = total_balance
    mock_fleet_antifraud.fleet_antifraud_limit = fleet_antifraud_limit

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '120',
            'price_with_currency': {'value': '120', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'meta_info': {},
                'partner': {'name': 'Apple'},
            },
        },
    )

    if (
            taxi_config.get('CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK')
            is not None
            and taxi_config.get('CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK')
    ):
        assert mock_fleet_antifraud.fleet_antifraud.times_called == 1

        request_query_fleet_antifraud = dict(
            mock_fleet_antifraud.fleet_antifraud.next_call()['request'].query,
        )
        assert request_query_fleet_antifraud == REQUEST_TO_FLEET_ANTIFRAUD

    voucher = util.get_voucher_by_idemp(
        cursor, 'park_id', 'driver_id', 'idemp3', with_created_at=False,
    )
    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': 'driver_id',
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('120'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None,
        'status': 'failed',
        'status_reason': (
            'not_enough_money_on_drivers_balance'
            if not is_enough
            else 'no_promocodes_left'
        ),
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch')
async def test_priority_coupons(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_driver_tags,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_fleet_antifraud,
        mock_driver_profiles,
        mock_tags,
):
    mock_fleet_transactions_api.balance = '2.4'
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='priority_task_id',
        kwargs={
            'driver_id': 'driver1',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '2.4',
            'price_with_currency': {'value': '2.4', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {
                    'priority_params': {
                        'tag_name': 'gold',
                        'duration_minutes': 60,
                    },
                    'chat_instructions_tanker_key_without_promocode_number': 'notification_v1.success.promocodeless.text',  # noqa: E501
                },
            },
        },
    )
    voucher = util.get_vouchers(cursor)
    assert voucher[0] == {
        'id': 'idemp1',
        'park_id': 'park_id',
        'driver_id': 'driver1',
        'idempotency_token': 'idemp1',
        'price': decimal.Decimal('2.4000'),
        'currency': 'RUB',
        'promocode_id': None,
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'status': 'fulfilled',
        'status_reason': None,
    }
    assert mock_tags.handler.times_called == 1
    assert mock_tags.handler.next_call()['request'].json == {
        'provider_id': 'contractor-merch',
        'append': [
            {
                'entity_type': 'dbid_uuid',
                'tags': [
                    {'name': 'gold', 'entity': 'park_id_driver1', 'ttl': 3600},
                ],
            },
        ],
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.now('2021-07-01T14:30:00+00:00')
@pytest.mark.pgsql('contractor_merch', files=['one_voucher.sql'])
async def test_priority_coupon_bought_already(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_tags,
):
    mock_fleet_transactions_api.balance = '2.4'
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='priority_task_id',
        kwargs={
            'driver_id': 'driver1',
            'park_id': 'park_id',
            'feed_id': 'feed-id-1',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '2.4',
            'price_with_currency': {'value': '2.4', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {
                    'priority_params': {
                        'tag_name': 'gold',
                        'duration_minutes': 60,
                    },
                    'chat_instructions_tanker_key_without_promocode_number': 'notification_v1.success.promocodeless.text',  # noqa: E501
                },
            },
        },
    )
    vouchers = util.get_vouchers(cursor)
    assert len(vouchers) == 1
    assert mock_tags.handler.times_called == 0


# Check default value of config 3.0 for park_balance check
# and config to enable park check
@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3(filename='experiments3_park_balance_check.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
async def test_park_can_buy_default_config_values_stq(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_tags,
):
    mock_driver_tags.tags = ['loyka_available']
    mock_fleet_transactions_api.balance = '2.4'

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(**DEFAULT_CALL_ARGS)

    assert mock_parks_activation.handler_balances.times_called == 0
    assert mock_parks_activation.handler_retrieve.times_called == 0

    assert mock_driver_profiles.driver_profiles.times_called == 1

    expected_voucher = DEFAULT_OK_VOUCHER

    assert util.get_vouchers(cursor) == [expected_voucher]


# Check if config value is park_balance_check
@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3(filename='experiments3_park_balance_check.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize(
    ('balance', 'threshold', 'threshold_dynamic', 'park_can_buy'),
    [
        pytest.param('200', '0', '0', True),
        pytest.param('0', '200', '0', True),
        pytest.param('0', '400', '200', True),
        pytest.param('0', '0', '0', False),
    ],
)
async def test_park_can_buy_park_balance_check_stq(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_tags,
        balance,
        threshold,
        threshold_dynamic,
        park_can_buy,
):
    mock_parks_activation.balance = balance
    mock_parks_activation.threshold = threshold
    mock_parks_activation.threshold_dynamic = threshold_dynamic

    mock_fleet_parks.updates = {'driver_partner_source': 'selfemployed_fns'}
    mock_fleet_transactions_api.balance = '2.4'

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(**DEFAULT_CALL_ARGS)

    assert mock_parks_activation.handler_balances.times_called == 1
    assert mock_parks_activation.handler_retrieve.times_called == 0

    call_args = mock_parks_activation.handler_balances.next_call()[
        'request'
    ].args
    assert call_args['park_id'] == 'clid1'

    expected_voucher = (
        DEFAULT_OK_VOUCHER
        if park_can_buy
        else {
            **DEFAULT_OK_VOUCHER,
            'promocode_id': None,
            'status': 'failed',
            'status_reason': 'park_has_not_enough_money',
        }
    )
    assert util.get_vouchers(cursor) == [expected_voucher]


# Check if config value is cash_check
@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3(filename='experiments3_park_balance_check.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('park_can_cash', [True, False])
async def test_park_can_buy_park_can_cash_check_stq(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_agglomerations,
        mock_billing_orders,
        mock_billing_replication,
        mock_parks_replica,
        mock_tariffs,
        mock_driver_wall,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_tags,
        park_can_cash,
):
    driver_id = 'a1d9721eefb94befa705fa0d86b58efb'
    stq_call_args = {
        'task_id': DEFAULT_TASK_ID,
        'kwargs': {**DEFAULT_STQ_KWARGS, 'driver_id': driver_id},
    }
    mock_parks_activation.can_cash = park_can_cash

    mock_fleet_transactions_api.balance = '2.4'

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(**stq_call_args)

    assert mock_parks_activation.handler_balances.times_called == 0
    assert mock_parks_activation.handler_retrieve.times_called == 1

    call_args = mock_parks_activation.handler_retrieve.next_call()[
        'request'
    ].json
    assert call_args == {'ids_in_set': ['clid1']}

    ok_voucher = {**DEFAULT_OK_VOUCHER, 'driver_id': driver_id}
    expected_voucher = (
        ok_voucher
        if park_can_cash
        else {
            **ok_voucher,
            'promocode_id': None,
            'status': 'failed',
            'status_reason': 'park_has_not_enough_money',
        }
    )
    assert util.get_vouchers(cursor) == [expected_voucher]
