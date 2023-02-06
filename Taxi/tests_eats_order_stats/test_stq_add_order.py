import datetime

import pytest
import pytz

EATS_CATALOG_STORAGE_CACHE_SETTINGS = [
    {
        'id': 45678,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 56789,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
    {
        'id': 234,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 432,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'store',
    },
    {
        'id': 1000,
        'revision_id': 5,
        'updated_at': '2020-11-26T10:00:00.000000Z',
        'brand': {
            'id': 1000,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
    },
]


def make_eats_core_order(order_nr, card_id, eater_id, device_id):
    core_response = {
        'order_nr': order_nr,
        'location_latitude': 1.0,
        'location_longitude': 1.0,
        'is_asap': True,
        'place_id': '12345',
        'region_id': '1',
    }
    if card_id:
        core_response['card_id'] = card_id

    if device_id:
        core_response['order_user_information'] = {
            'eater_id': eater_id,
            'device_id': 'new_device',
        }
    return core_response


def check_counter(counter, pgsql):
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT counter_value FROM eats_order_stats.orders_counters '
        f'WHERE identity_type=\'{counter.get("identity_type")}\' '
        f'AND identity_value=\'{counter.get("identity")}\' '
        f'AND place_id=\'{counter.get("place_id")}\' '
        f'AND brand_id=\'{counter.get("brand_id")}\' '
        f'AND delivery_type=\'{counter.get("delivery_type")}\' '
        f'AND business_type=\'{counter.get("business_type")}\';',
    )
    assert cursor.fetchone()[0] == counter['value']


def check_processed_orders(order, pgsql):
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT * FROM eats_order_stats.processed_orders '
        f'WHERE identity_type=\'{order.get("identity_type")}\' '
        f'AND order_id=\'{order.get("order_id")}\' '
        f'AND canceled={order.get("canceled")};',
    )
    assert cursor.fetchone()


@pytest.mark.parametrize(
    'order,db_data',
    [
        # new counter
        (
            {
                'eater_id': '234567',
                'phone_id': '6723abd82323cbe',
                'order_nr': '202106-32213',
                'place_id': '45678',
                'delivery_type': 'marketplace',
                'created_at': '2020-11-26T00:00:00.000000Z',
                'payment_method': 'googlepay',
            },
            {
                'counters': [
                    {
                        'identity': '234567',
                        'identity_type': 'eater_id',
                        'place_id': '45678',
                        'brand_id': '56789',
                        'business_type': 'restaurant',
                        'delivery_type': 'marketplace',
                        'value': 1,
                    },
                    {
                        'identity': '6723abd82323cbe',
                        'identity_type': 'phone_id',
                        'place_id': '45678',
                        'brand_id': '56789',
                        'business_type': 'restaurant',
                        'delivery_type': 'marketplace',
                        'value': 1,
                    },
                ],
                'processed_orders': [
                    {
                        'order_id': '202106-32213',
                        'identity_type': 'eater_id',
                        'canceled': False,
                    },
                    {
                        'order_id': '202106-32213',
                        'identity_type': 'phone_id',
                        'canceled': False,
                    },
                ],
            },
        ),
        # increment
        (
            {
                'eater_id': '2222',
                'phone_id': '2222',
                'order_nr': '202106-24343',
                'place_id': '234',
                'delivery_type': 'our_delivery',
                'created_at': '2020-11-26T00:00:00.000000Z',
                'payment_method': 'applepay',
            },
            {
                'counters': [
                    {
                        'identity': '2222',
                        'identity_type': 'eater_id',
                        'place_id': '234',
                        'brand_id': '432',
                        'business_type': 'grocery',
                        'delivery_type': 'native',
                        'value': 4,
                    },
                    {
                        'identity': '2222',
                        'identity_type': 'phone_id',
                        'place_id': '234',
                        'brand_id': '432',
                        'business_type': 'grocery',
                        'delivery_type': 'native',
                        'value': 5,
                    },
                ],
                'processed_orders': [
                    {
                        'order_id': '202106-24343',
                        'identity_type': 'eater_id',
                        'canceled': False,
                    },
                    {
                        'order_id': '202106-24343',
                        'identity_type': 'phone_id',
                        'canceled': False,
                    },
                ],
            },
        ),
        # already updated
        (
            {
                'eater_id': '999',
                'phone_id': '999',
                'order_nr': '202106-76563',
                'place_id': '45678',
                'delivery_type': 'our_delivery',
                'created_at': '2020-11-26T00:00:00.000000Z',
                'payment_method': 'taxi',
            },
            {
                'counters': [
                    {
                        'identity': '999',
                        'identity_type': 'eater_id',
                        'place_id': '45678',
                        'brand_id': '56789',
                        'business_type': 'restaurant',
                        'delivery_type': 'native',
                        'value': 1,
                    },
                    {
                        'identity': '999',
                        'identity_type': 'phone_id',
                        'place_id': '45678',
                        'brand_id': '56789',
                        'business_type': 'restaurant',
                        'delivery_type': 'native',
                        'value': 1,
                    },
                ],
                'processed_orders': [
                    {
                        'order_id': '202106-76563',
                        'identity_type': 'eater_id',
                        'canceled': False,
                    },
                    {
                        'order_id': '202106-76563',
                        'identity_type': 'phone_id',
                        'canceled': False,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
async def test_save_order_counters(stq_runner, pgsql, order, db_data):
    await stq_runner.eats_order_stats_save_order.call(
        task_id='new_counter', kwargs=order,
    )
    for counter in db_data['counters']:
        check_counter(counter, pgsql)

    for processed_order in db_data['processed_orders']:
        check_processed_orders(processed_order, pgsql)


@pytest.mark.config(
    EATS_ORDER_STATS_MIGRATION={
        'save_only_events_after': '2021-06-12T12:00:00+0300',
    },
)
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
async def test_eats_order_stats_migration(stq_runner, pgsql):
    order = {
        'eater_id': 'new_one',
        'phone_id': 'new_one',
        'order_nr': '321-321',
        'place_id': '1000',
        'delivery_type': 'our_delivery',
        'created_at': '2020-11-26T00:00:00.000000Z',
        'payment_method': 'cash',
    }
    await stq_runner.eats_order_stats_save_order.call(
        task_id='new_counter', kwargs=order,
    )
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT * FROM eats_order_stats.processed_orders '
        f'WHERE order_id=\'321-321\';',
    )
    assert not cursor.fetchall()


@pytest.mark.parametrize(
    'on_new_identities',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_ORDER_STATS_ON_NEW_IDENTITIES={
                    'on_device_and_card_ids': True,
                },
            ),
            id='on_new_identities',
        ),
        pytest.param(False, id='off_new_identities'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
@pytest.mark.parametrize('device_id', ['new_device', None])
@pytest.mark.parametrize(
    'relevant_cart, card_id',
    [
        (False, None),
        (False, 'card-x1234'),
        (True, 'card-xa1aaa11a111a111aaa11a11a'),
    ],
)
async def test_processed_orders_created_at_value(
        stq_runner,
        pgsql,
        device_id,
        relevant_cart,
        card_id,
        on_new_identities,
        mockserver,
):
    order_date = datetime.datetime(
        year=2021,
        month=8,
        day=1,
        hour=17,
        minute=46,
        second=23,
        tzinfo=pytz.utc,
    )
    order_nr = '321-321'
    eater_id = 'new_one'
    order = {
        'eater_id': eater_id,
        'phone_id': 'new_one',
        'order_nr': order_nr,
        'place_id': '1000',
        'delivery_type': 'our_delivery',
        'created_at': order_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'payment_method': 'card',
    }

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def mock_eats_core_order(request):
        return mockserver.make_response(
            status=200,
            json=make_eats_core_order(order_nr, card_id, eater_id, device_id),
        )

    await stq_runner.eats_order_stats_save_order.call(
        task_id='new_counter', kwargs=order,
    )
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT identity_type, order_id, created_at FROM eats_order_stats.processed_orders '
        f'WHERE order_id=\'{order["order_nr"]}\';',
    )
    all = cursor.fetchall()
    exp_result = set(
        [
            ('eater_id', order_nr, order_date),
            ('phone_id', order_nr, order_date),
        ],
    )
    if on_new_identities:
        assert mock_eats_core_order.times_called == 1
        if device_id:
            exp_result.add(('device_id', order_nr, order_date))
        if relevant_cart:
            exp_result.add(('card_id', order_nr, order_date))
    assert set(all) == exp_result


DEFAULT_EATS_ORDER_STATS_NEXT_GEN_SETTINGS = {
    'next_gen_write_enabled': False,
    'next_gen_read_enabled': False,
}


def _read_table(db_cursor, schema, table_name):
    db_cursor.execute(f'SELECT * FROM {schema}.{table_name}')
    columns = [desc[0] for desc in db_cursor.description]
    rows = list(db_cursor)
    return [dict(zip(columns, row)) for row in rows]


@pytest.mark.parametrize(
    'on_new_identities',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_ORDER_STATS_ON_NEW_IDENTITIES={
                    'on_device_and_card_ids': True,
                },
            ),
            id='on_new_identities',
        ),
        pytest.param(False, id='off_new_identities'),
    ],
)
@pytest.mark.parametrize('write_enabled', [True, False])
@pytest.mark.parametrize('device_id', ['new_device', None])
@pytest.mark.parametrize(
    'relevant_cart, card_id',
    [
        (False, None),
        (False, 'card-x1234'),
        (True, 'card-xa1aaa11a111a111aaa11a11a'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(EATS_CATALOG_STORAGE_CACHE_SETTINGS)
async def test_next_gen_write(
        taxi_eats_order_stats,
        write_enabled,
        pgsql,
        stq_runner,
        taxi_config,
        device_id,
        relevant_cart,
        card_id,
        on_new_identities,
        mockserver,
):
    taxi_config.set_values(
        {
            'EATS_ORDER_STATS_NEXT_GEN_SETTINGS': dict(
                DEFAULT_EATS_ORDER_STATS_NEXT_GEN_SETTINGS,
                next_gen_write_enabled=write_enabled,
            ),
        },
    )
    await taxi_eats_order_stats.invalidate_caches()
    order_nr = '321-321'
    eater_id = 'new_one'
    order = {
        'eater_id': eater_id,
        'phone_id': 'new_one',
        'order_nr': order_nr,
        'place_id': '1000',
        'delivery_type': 'native',
        'created_at': '2020-11-26T00:00:00.000000Z',
        'payment_method': 'card',
    }

    @mockserver.json_handler(
        f'eats-core-orders/internal-api/v1/order/{order_nr}/metainfo',
    )
    def mock_eats_core_order(request):
        return mockserver.make_response(
            status=200,
            json=make_eats_core_order(order_nr, card_id, eater_id, device_id),
        )

    await stq_runner.eats_order_stats_save_order.call(
        task_id='new_counter', kwargs=order,
    )

    cursor = pgsql['eats_order_stats'].cursor()
    rows = _read_table(cursor, 'eats_order_stats_v2', 'orders_counters')
    exp_row_len = 2
    if on_new_identities:
        assert mock_eats_core_order.times_called == 1
        if device_id:
            exp_row_len += 1
        if relevant_cart:
            exp_row_len += 1
    if not write_enabled:
        exp_row_len = 0
    assert len(rows) == exp_row_len

    for row in rows:
        for column in ['place_id', 'delivery_type', 'payment_method']:
            assert row[column] == order[column], column
        assert row['counter_value'] == 1

    rows = _read_table(cursor, 'eats_order_stats_v2', 'processed_orders')
    assert len(rows) == exp_row_len

    if write_enabled:
        await stq_runner.eats_order_stats_cancel_order.call(
            task_id='cancel_counter',
            kwargs={
                'order_nr': '321-321',
                'place_id': '1000',
                'shipping_type': 'delivery',
                'order_type': 'native',
                'cancelled_at': '2020-11-26T01:00:00.000000Z',
                'cancellation_reason': 'not_ready',
                'cancelled_by': 'courier',
            },
        )
        rows = _read_table(cursor, 'eats_order_stats_v2', 'orders_counters')
        assert not rows
        rows = _read_table(cursor, 'eats_order_stats_v2', 'processed_orders')
        if on_new_identities:
            assert (
                len(rows) == 4 - exp_row_len
            )  # because of logic when we delete identity which not exist
        else:
            assert not rows
