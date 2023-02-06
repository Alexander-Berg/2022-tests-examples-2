import decimal

import pytest

from tests_contractor_merch import util


@pytest.mark.translations(
    taximeter_backend_marketplace=util.STQ_TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=(
        util.CUSTOM_MESSAGES_TRANSLATIONS
    ),
)
@pytest.mark.parametrize('currency', ['RUB', 'USD', 'EUR'])
async def test_currencies(
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
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_parks_activation,
        currency,
):
    mock_billing_replication.set_currency(
        'RUR' if currency == 'RUB' else currency,
    )

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '200',
            'price_with_currency': {'value': '200', 'currency': currency},
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
            'driver_id': 'driver_id',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('200.0000'),
            'currency': currency,
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'fulfilled',
            'status_reason': None,
        },
    ]


@pytest.mark.translations(
    taximeter_backend_marketplace=util.STQ_TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=(
        util.CUSTOM_MESSAGES_TRANSLATIONS
    ),
)
async def test_currency_mismatch(
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
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_parks_activation,
):
    mock_billing_replication.set_currency('USD')

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '200',
            'price_with_currency': {'value': '200', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {},
            },
        },
        expect_fail=True,
    )

    assert util.get_vouchers(cursor) == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('200.0000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'pending',
            'status_reason': None,
        },
    ]


@pytest.mark.translations(
    taximeter_backend_marketplace=util.STQ_TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=(
        util.CUSTOM_MESSAGES_TRANSLATIONS
    ),
)
async def test_country_vat_not_found(
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
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_fleet_transactions_api,
        mock_parks_activation,
):
    mock_billing_replication.set_currency('NOK')
    mock_fleet_parks.country_id = 'nor'

    cursor = pgsql['contractor_merch'].cursor()

    await stq_runner.contractor_merch_purchase.call(
        task_id='some_task_id',
        kwargs={
            'driver_id': 'driver_id',
            'park_id': 'park_id',
            'feed_id': 'some_id',
            'idempotency_token': 'idemp1',
            'accept_language': 'en_GB',
            'price': '200',
            'price_with_currency': {'value': '200', 'currency': 'RUB'},
            'feed_payload': {
                'category': 'cat',
                'feeds_admin_id': 'feeds-admin-id-1',
                'balance_payment': True,
                'title': 'Gift card (1000 rub)',
                'partner': {'name': 'Apple'},
                'meta_info': {},
            },
        },
        expect_fail=True,
    )

    assert util.get_vouchers(cursor) == [
        {
            'id': 'idemp1',
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'idempotency_token': 'idemp1',
            'price': decimal.Decimal('200.0000'),
            'currency': 'RUB',
            'feeds_admin_id': 'feeds-admin-id-1',
            'feed_id': 'some_id',
            'promocode_id': 'p1',
            'status': 'pending',
            'status_reason': None,
        },
    ]
