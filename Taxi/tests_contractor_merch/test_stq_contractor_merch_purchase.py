# pylint: disable=too-many-lines

import decimal

import pytest

from tests_contractor_merch import util

TRANSLATIONS = util.STQ_TRANSLATIONS
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS

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
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
async def test_ok(
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
        mock_driver_tags,
        mock_driver_profiles,
        mock_fleet_antifraud,
):
    mock_fleet_transactions_api.balance = '2.4'
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(**DEFAULT_CALL_ARGS)

    assert util.get_vouchers(cursor) == [DEFAULT_OK_VOUCHER]

    # now check that if no promocodes left
    # we create voucher without promocode id
    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver2',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp2',
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
        },
    )

    assert util.get_vouchers(cursor) == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver1',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('2.4000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'fulfilled',
            'status_reason': None,
        },
        {
            'id': 'idemp2',
            'park_id': 'park_id',
            'driver_id': 'driver2',
            'idempotency_token': 'idemp2',
            'price': decimal.Decimal('2.4000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': None,
            'status': 'failed',
            'status_reason': 'no_promocodes_left',
        },
    ]

    # check existing idemp token for other driver
    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver3',
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
        },
    )

    assert util.get_vouchers(cursor) == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver1',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('2.4000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'fulfilled',
            'status_reason': None,
        },
        {
            'id': 'idemp2',
            'park_id': 'park_id',
            'driver_id': 'driver2',
            'idempotency_token': 'idemp2',
            'price': decimal.Decimal('2.4000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': None,
            'status': 'failed',
            'status_reason': 'no_promocodes_left',
        },
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver3',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('2.4000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': None,
            'status': 'failed',
            'status_reason': 'no_promocodes_left',
        },
    ]

    assert mock_driver_profiles.driver_profiles.times_called == 3


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['pending_voucher.sql'])
@pytest.mark.parametrize('balance', ['100500', '-1'])
async def test_retry(
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
):
    mock_fleet_transactions_api.balance = balance
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'd1',
            'park_id': 'p1',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '1024.4',
            'price_with_currency': {'value': '1024.4', 'currency': 'RUB'},
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

    assert mock_driver_profiles.driver_profiles.times_called == 1

    assert util.get_vouchers(cursor) == [
        {
            'id': 'idemp1',
            'park_id': 'p1',
            'driver_id': 'd1',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('2.4000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'fulfilled',
            'status_reason': None,
        },
    ]


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
async def test_money_withhold(
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
        mock_fleet_antifraud,
        mock_driver_tags,
):
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver1',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
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

    assert mock_driver_profiles.driver_profiles.times_called == 1

    vouchers = util.get_vouchers(cursor, with_created_at=True)
    assert len(vouchers) == 1
    created_at = vouchers[0].pop('created_at')
    assert vouchers == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver1',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('120'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'fulfilled',
            'status_reason': None,
        },
    ]

    assert mock_fleet_parks.park_list.times_called == 1
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['park_id']}},
    }

    assert mock_parks_replica.billing_client_id_retrieve.times_called == 1
    assert (
        util.date_parsed(
            util.get_mock_query(
                mock_parks_replica.billing_client_id_retrieve.next_call(),
            ),
        )
        == {
            'consumer': 'contractor-merch',
            'park_id': 'clid1',
            'timestamp': created_at,
        }
    )

    assert mock_billing_replication.active_contracts.times_called == 1
    assert (
        util.date_parsed(
            util.get_mock_query(
                mock_billing_replication.active_contracts.next_call(),
            ),
        )
        == {
            'client_id': '187701087',
            'service_id': '128',
            'active_ts': created_at,
            'actual_ts': created_at,
        }
    )

    assert mock_tariffs.tariffs.times_called == 1
    assert util.get_mock_query(mock_tariffs.tariffs.next_call()) == {
        'city_ids': 'city1',
        'locale': 'en',
    }

    assert mock_agglomerations.times_called == 1
    assert util.get_mock_query(mock_agglomerations.next_call()) == {
        'tariff_zone': 'spb',
    }

    assert mock_billing_orders.times_called == 1
    assert (
        util.date_parsed(mock_billing_orders.next_call()['request'].json)
        == {
            'orders': [
                {
                    'data': {
                        'event_version': 2,
                        'payments': [
                            {
                                'amount': '100',
                                'billing_client_id': '187701087',
                                'contract_id': '2580789',
                                'currency': 'RUB',
                                'invoice_date': created_at,
                                'payload': {
                                    'agglomeration': 'ASKc',
                                    'alias_id': (
                                        'noorder/purchase_id/'
                                        'park_id_driver1_idemp1'
                                    ),
                                    'amount_details': {
                                        'base_amount': '100',
                                        'base_currency': 'RUB',
                                        'contract_currency_rate': '1.00000',
                                        'vat': '20',
                                    },
                                    'detailed_product': 'store_purchase',
                                    'driver_details': {
                                        'clid': 'clid1',
                                        'db_id': 'park_id',
                                        'uuid': 'driver1',
                                    },
                                    'product': 'store_purchase',
                                    'service_id': 128,
                                    'tariff_class': 'econom',
                                    'transaction_type': 'payment',
                                    'purchase_id': 'idemp1',
                                },
                                'payment_kind': 'store_purchase',
                            },
                        ],
                        'schema_version': 'v2',
                        'template_entries': [
                            {
                                'context': {
                                    'amount': '-120',
                                    'currency': 'RUB',
                                    'driver_uuid': 'driver1',
                                    'event_at': created_at,
                                    'park_id': 'park_id',
                                    'purchase_id': 'idemp1',
                                },
                                'template_name': 'store_purchase',
                            },
                        ],
                        'topic_begin_at': created_at,
                    },
                    'event_at': created_at,
                    'external_ref': '1',
                    'kind': 'arbitrary_payout',
                    'tags': ['taxi/purchase_id/park_id_driver1_idemp1'],
                    'topic': 'taxi/store_purchase/park_id_driver1_idemp1',
                },
            ],
        }
    )


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
async def test_fallback_mvp(
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
        mock_fleet_antifraud,
        mock_driver_tags,
):
    mock_tariffs.tariffs_response = {'zones': []}

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver1',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
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

    assert mock_driver_profiles.driver_profiles.times_called == 1

    cursor = pgsql['contractor_merch'].cursor()
    vouchers = util.get_vouchers(cursor, with_created_at=True)
    assert len(vouchers) == 1
    vouchers[0].pop('created_at')
    assert vouchers == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver1',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('120'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'fulfilled',
            'status_reason': None,
        },
    ]

    assert mock_tariffs.tariffs.times_called == 1
    assert util.get_mock_query(mock_tariffs.tariffs.next_call()) == {
        'city_ids': 'city1',
        'locale': 'en',
    }

    assert mock_agglomerations.times_called == 1
    assert util.get_mock_query(mock_agglomerations.next_call()) == {
        'tariff_zone': 'br_moscow',
    }

    assert mock_billing_orders.times_called == 1
    assert (
        mock_billing_orders.next_call()['request'].json['orders'][0]['data'][
            'payments'
        ][0]['payload']['agglomeration']
        == 'ASKc'
    )


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['limits.sql'])
@pytest.mark.parametrize(
    'driver_id, meta_info, expected_problem_description',
    [
        pytest.param(
            'one_offer_total_limit_excceded',
            {'total_per_driver_limit': 1},
            {
                'code': 'one_offer_total_limit_excceded',
                'localized_message': 'one_offer_total_limit_excceded-tr',
            },
            id='total_limit_excceded',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'total_per_driver_limit': 2},
            None,
            id='total_limit_unreached',
        ),
        pytest.param(
            'one_offer_total_limit_excceded', {}, None, id='total_limit_unset',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'daily_per_driver_limit': 1},
            {
                'code': 'one_offer_daily_limit_excceded',
                'localized_message': 'one_offer_daily_limit_excceded-tr',
            },
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='daily_limit_excceded',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'daily_per_driver_limit': 2},
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='daily_limit_unreached',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {'daily_per_driver_limit': 1},
            None,
            marks=[pytest.mark.now('2021-07-02T15:00:00Z')],
            id='daily_limit_last_purchases_long_time_ago',
        ),
        pytest.param(
            'one_offer_total_limit_excceded',
            {},
            None,
            marks=[pytest.mark.now('2021-07-02T13:00:00Z')],
            id='daily_limit_unset',
        ),
        pytest.param(
            'driver_has_pending_purchases',
            {},
            {
                'code': 'driver_has_pending_purchases',
                'localized_message': 'driver_has_pending_purchases-tr',
            },
        ),
        pytest.param(
            'purchase_period',
            {},
            {
                'code': 'driver_has_pending_purchases',
                'localized_message': 'driver_has_pending_purchases-tr',
            },
            marks=[
                pytest.mark.now('2021-07-01T14:00:20Z'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PURCHASES_MIN_PERIOD_SEC=15,
                ),
            ],
            id='purchase_period triggers',
        ),
        pytest.param(
            'purchase_period',
            {},
            None,
            marks=[
                pytest.mark.now('2021-07-01T14:00:30Z'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PURCHASES_MIN_PERIOD_SEC=15,
                ),
            ],
            id='purchase_period does not trigger 1',
        ),
        pytest.param(
            'purchase_period',
            {},
            None,
            marks=[
                pytest.mark.now('2021-07-01T14:00:10Z'),
                pytest.mark.config(
                    CONTRACTOR_MERCH_PURCHASES_MIN_PERIOD_SEC=0,
                ),
            ],
            id='purchase_period does not trigger 2',
        ),
    ],
)
async def test_driver_limits(
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
        mock_fleet_antifraud,
        mock_driver_tags,
        driver_id,
        meta_info,
        expected_problem_description,
):
    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': driver_id,
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
                'meta_info': meta_info,
            },
        },
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1

    voucher = util.get_voucher_by_idemp(
        cursor, 'park_id', driver_id, 'idemp3', with_created_at=False,
    )
    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': driver_id,
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('120'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None if expected_problem_description else 'p1',
        'status': 'failed' if expected_problem_description else 'fulfilled',
        'status_reason': (
            expected_problem_description.get('code')
            if expected_problem_description
            else None
        ),
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': f'park_id_{driver_id}'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': (
                expected_problem_description['localized_message']
                if expected_problem_description
                else 'Default text with number, here it is: 100500'
            ),
            'title': (
                'Gift card (1000 rub): failed'
                if expected_problem_description
                else 'Gift card (1000 rub): succ'
            ),
            'type': 'newsletter',
        },
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.now('2021-07-01T14:00:00Z')
async def test_balance(
        stq_runner,
        pgsql,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_tags,
):
    mock_fleet_transactions_api.balance = '119'

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


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
async def test_no_promocodes_left(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
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

    assert mock_driver_profiles.driver_profiles.times_called == 1

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
        'status_reason': 'no_promocodes_left',
    }

    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': 'park_id_driver_id'}],
        'id': 'some_task_id',
        'service': 'contractor-promo',
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': 'no_promocodes_left-tr',
            'title': 'Gift card (1000 rub): failed',
            'type': 'newsletter',
        },
    }


@pytest.mark.parametrize(
    'driver_id, driver_wall_service',
    [
        ('driver1', 'contractor-promo'),
        ('driver2', 'contractor-marketplace-messages'),
    ],
)
@pytest.mark.experiments3(
    filename='contractor_merch_send_to_separate_chat.json',
)
@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
async def test_billing_is_disabled_for_park(
        stq_runner,
        pgsql,
        mock_fleet_parks,
        mock_driver_wall,
        mock_fleet_transactions_api,
        mock_parks_activation,
        driver_id,
        driver_wall_service,
        mock_driver_profiles,
        mock_fleet_antifraud,
        mock_driver_tags,
):
    mock_fleet_parks.is_billing_enabled = False
    cursor = pgsql['contractor_merch'].cursor()
    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': driver_id,
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp3',
            'accept_language': 'en_GB',
            'price': '3',
            'price_with_currency': {'value': '3', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'GTA VI',
                'partner': {'name': 'Apple'},
                'meta_info': {},
            },
        },
    )

    assert mock_driver_profiles.driver_profiles.times_called == 1
    voucher = util.get_voucher_by_idemp(
        cursor, 'park_id', driver_id, 'idemp3', with_created_at=False,
    )
    assert voucher == {
        'id': 'idemp3',
        'park_id': 'park_id',
        'driver_id': driver_id,
        'idempotency_token': 'idemp3',
        'price': decimal.Decimal('3'),
        'currency': 'RUB',
        'feeds_admin_id': 'feeds-admin-id-1',
        'feed_id': 'some_id',
        'promocode_id': None,
        'status': 'failed',
        'status_reason': 'billing_is_disabled_for_park',
    }
    assert mock_driver_wall.times_called == 1
    assert mock_driver_wall.next_call()['request'].json == {
        'drivers': [{'driver': f'park_id_{driver_id}'}],
        'id': 'some_task_id',
        'service': driver_wall_service,
        'template': {
            'alert': False,
            'format': 'Markdown',
            'important': True,
            'text': 'billing_is_disabled_for_park-tr',
            'title': 'GTA VI: failed',
            'type': 'newsletter',
        },
    }
    assert mock_fleet_parks.park_list.times_called == 1
    assert mock_fleet_parks.park_list.next_call()['request'].json == {
        'query': {'park': {'ids': ['park_id']}},
    }
