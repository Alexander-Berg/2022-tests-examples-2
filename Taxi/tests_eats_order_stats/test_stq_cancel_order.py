import pytest


def check_counter(counter, pgsql):
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT counter_value, last_order_at '
        'FROM eats_order_stats.orders_counters '
        f'WHERE id=\'{counter.get("id")}\';',
    )
    value, last_order_created_at = cursor.fetchone()
    assert value == counter['value']
    assert (
        last_order_created_at.strftime('%Y-%m-%d %H:%M:%S%z')
        == counter['last_order_created_at']
    )


def check_processed_order(order, pgsql):
    cursor = pgsql['eats_order_stats'].cursor()
    cursor.execute(
        'SELECT canceled FROM eats_order_stats.processed_orders '
        f'WHERE identity_type=\'{order.get("identity_type")}\' '
        f'AND order_id=\'{order.get("order_id")}\';',
    )
    assert cursor.fetchone()[0] == order['canceled']


@pytest.mark.config(
    EATS_ORDER_STATS_ON_NEW_IDENTITIES={'on_device_and_card_ids': True},
)
async def test_stq_cancel_order(stq_runner, pgsql, mockserver):
    await stq_runner.eats_order_stats_cancel_order.call(
        task_id='cancel_counter',
        kwargs={
            'order_nr': '100-200',
            'place_id': 'place_id',
            'shipping_type': 'shipping_type',
            'order_type': 'order_type',
            'cancelled_at': '2021-05-31T18:35:00+0300',
            'cancellation_reason': 'not_ready',
            'cancelled_by': 'operator',
        },
    )
    check_counter(
        {
            'id': 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebe',
            'value': 1,
            'last_order_created_at': '2021-05-31 18:32:00+0300',
        },
        pgsql,
    )
    check_counter(
        {
            'id': 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ebf',
            'value': 1,
            'last_order_created_at': '2021-05-31 18:32:00+0300',
        },
        pgsql,
    )
    check_counter(
        {
            'id': 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2ccc',
            'value': 1,
            'last_order_created_at': '2021-05-31 18:32:00+0300',
        },
        pgsql,
    )
    check_counter(
        {
            'id': 'a0ba06b1-c9fa-49b9-aa54-5ecd28bd2aaa',
            'value': 1,
            'last_order_created_at': '2021-05-31 18:32:00+0300',
        },
        pgsql,
    )
    check_processed_order(
        {'order_id': '100-200', 'identity_type': 'phone_id', 'canceled': True},
        pgsql,
    )
    check_processed_order(
        {'order_id': '100-200', 'identity_type': 'eater_id', 'canceled': True},
        pgsql,
    )
    check_processed_order(
        {
            'order_id': '100-200',
            'identity_type': 'device_id',
            'canceled': True,
        },
        pgsql,
    )
    check_processed_order(
        {'order_id': '100-200', 'identity_type': 'card_id', 'canceled': True},
        pgsql,
    )


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
async def test_stq_cancel_order_unknown(
        stq_runner, pgsql, mockserver, on_new_identities,
):
    await stq_runner.eats_order_stats_cancel_order.call(
        task_id='cancel_counter',
        kwargs={
            'order_nr': '404-404',
            'place_id': 'place_id',
            'shipping_type': 'shipping_type',
            'order_type': 'order_type',
            'cancelled_at': '2021-05-31T18:35:00+0300',
            'cancellation_reason': 'not_ready',
            'cancelled_by': 'operator',
        },
    )
    check_processed_order(
        {'order_id': '404-404', 'identity_type': 'phone_id', 'canceled': True},
        pgsql,
    )
    check_processed_order(
        {'order_id': '404-404', 'identity_type': 'eater_id', 'canceled': True},
        pgsql,
    )
    if on_new_identities:
        check_processed_order(
            {
                'order_id': '404-404',
                'identity_type': 'device_id',
                'canceled': True,
            },
            pgsql,
        )
        check_processed_order(
            {
                'order_id': '404-404',
                'identity_type': 'card_id',
                'canceled': True,
            },
            pgsql,
        )
