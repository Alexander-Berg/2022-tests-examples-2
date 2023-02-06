import datetime

import pytest

from . import utils


@pytest.mark.now('2021-08-01T12:00:00.123456+00:00')
@utils.synchronizer_config3()
async def test_order_history_synchronizer_and_order_updater_metrics(
        environment,
        testpoint,
        taxi_eats_retail_order_history,
        create_order,
        mocked_time,
        taxi_eats_retail_order_history_monitor,
):
    create_order()
    environment.set_default()

    await taxi_eats_retail_order_history.tests_control(reset_metrics=True)
    await taxi_eats_retail_order_history.invalidate_caches()

    @testpoint('eats-retail-order-history::autocomplete')
    async def _(arg):
        mocked_time.sleep(3600)
        await taxi_eats_retail_order_history.invalidate_caches()

    await taxi_eats_retail_order_history.run_distlock_task(
        'order-history-synchronizer',
    )

    metrics = await taxi_eats_retail_order_history_monitor.get_metric(
        'retail-order-history-metrics',
    )

    assert metrics['order-history-synchronizer']['orders_to_be_updated'] == 1
    assert (
        metrics['order-history-synchronizer']['periodic_work_duration'] == 3600
    )
    assert metrics['order-updater']['updated_orders'] == 1


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.experiments3(
    name='eats_retail_order_history_retail_info_synchronizer',
    is_config=True,
    match={
        'consumers': [
            {
                'name': (
                    'eats-retail-order-history/' 'retail-info-synchronizer'
                ),
            },
        ],
        'predicate': {'type': 'true'},
        'enabled': True,
    },
    clauses=[],
    default_value={
        'period_seconds': 5,
        'updated_after_offset': 3600,
        'orders_limit': 2,
    },
)
async def test_retail_info_synchronizer_metrics(
        taxi_eats_retail_order_history,
        taxi_eats_retail_order_history_monitor,
        mockserver,
        load_json,
        create_order,
        now,
        testpoint,
        mocked_time,
):
    now = now.replace(tzinfo=datetime.timezone.utc)
    existing_order_nr = '1'
    create_order(yandex_uid=utils.YANDEX_UID, order_nr=existing_order_nr)
    create_order(yandex_uid=None, order_nr=utils.ORDER_ID)

    cart_diff_for_history = load_json('cart_diff_for_history.json')

    last_order_id = 123

    @testpoint('eats-retail-order-history::info-synchronizer-loop-end')
    async def _(arg):
        mocked_time.sleep(3600)
        await taxi_eats_retail_order_history.invalidate_caches()

    @mockserver.json_handler(
        '/eats-picker-orders/api/v1/orders/cart/diff-for-history',
    )
    def _eats_picker_orders_get_order(request):
        assert request.method == 'POST'
        if _eats_picker_orders_get_order.times_called == 0:
            assert datetime.datetime.fromisoformat(
                request.json['updated_after'],
            ) == now - datetime.timedelta(hours=1)
            assert 'updated_after_id' not in request.json
            return {
                'orders': [
                    dict(cart_diff_for_history, status='complete'),
                    dict(cart_diff_for_history, eats_id=existing_order_nr),
                ],
                'last_updated_at': now.isoformat(),
                'last_order_id': last_order_id,
            }
        assert (
            datetime.datetime.fromisoformat(request.json['updated_after'])
            == now
        )
        assert request.json['updated_after_id'] == last_order_id
        return {'orders': []}

    await taxi_eats_retail_order_history.tests_control(reset_metrics=True)
    await taxi_eats_retail_order_history.invalidate_caches()

    await taxi_eats_retail_order_history.run_distlock_task(
        'retail-info-synchronizer',
    )

    metrics = await taxi_eats_retail_order_history_monitor.get_metric(
        'retail-order-history-metrics',
    )

    assert metrics['retail-info-synchronizer']['orders_for_history'] == 2
    assert (
        metrics['retail-info-synchronizer']['periodic_work_duration'] == 3600
    )
