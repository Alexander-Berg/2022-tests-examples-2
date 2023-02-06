import pytest

TASK_NAME = 'proactive-order-cancel'
URL_CORE_CANCEL_ORDER = '/eats-core-cancel-order/internal-api/v1/cancel-order'


async def test_dummy(taxi_eats_orders_tracking):
    # Workaround for TAXIDATA-3002: This test just loads service.
    pass


@pytest.mark.config(
    EATS_ORDERS_TRACKING_PROACTIVE_ORDERS_CANCEL={
        'task_period_seconds': 300,
        'is_order_cancellation_enabled': True,
        'batch_size': 2,
        'maximum_seconds_after_created': 14400,
        'minimum_seconds_from_status_place_confirmed': 3600,
        'brand_slugs': ['makdonalds'],
        'shipping_types': ['delivery'],
        'cancel_reason': 'cancel_reason',
        'maximum_cancellation_tries_for_one_periodic_tick': 999999,
    },
)
@pytest.mark.now('2021-01-01T03:30:00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_orders.sql'])
async def test_green_flow(taxi_eats_orders_tracking, mockserver):
    requested_order_nrs = []

    @mockserver.json_handler(URL_CORE_CANCEL_ORDER)
    def _handler_core_resend_orders(request):
        requested_order_nrs.append(request.json['order_nr'])
        return mockserver.make_response(status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    expected_order_nrs = ['000000-000005', '000000-000006', '000000-000007']
    requested_order_nrs.sort()
    expected_order_nrs.sort()
    assert requested_order_nrs == expected_order_nrs
    assert _handler_core_resend_orders.times_called == 3


@pytest.mark.config(
    EATS_ORDERS_TRACKING_PROACTIVE_ORDERS_CANCEL={
        'task_period_seconds': 300,
        'is_order_cancellation_enabled': False,
        'batch_size': 2,
        'maximum_seconds_after_created': 14400,
        'minimum_seconds_from_status_place_confirmed': 3600,
        'brand_slugs': ['makdonalds'],
        'shipping_types': ['delivery'],
        'cancel_reason': 'cancel_reason',
        'maximum_cancellation_tries_for_one_periodic_tick': 999999,
    },
)
@pytest.mark.now('2021-01-01T03:30:00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_orders.sql'])
async def test_disabled(taxi_eats_orders_tracking, mockserver):
    @mockserver.json_handler(URL_CORE_CANCEL_ORDER)
    def _handler_core_resend_orders(request):
        return mockserver.make_response(status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    assert _handler_core_resend_orders.times_called == 0


@pytest.mark.config(
    EATS_ORDERS_TRACKING_PROACTIVE_ORDERS_CANCEL={
        'task_period_seconds': 300,
        'is_order_cancellation_enabled': True,
        'batch_size': 2,
        'maximum_seconds_after_created': 14400,
        'minimum_seconds_from_status_place_confirmed': 3600,
        'brand_slugs': ['makdonalds'],
        'shipping_types': ['delivery'],
        'cancel_reason': 'cancel_reason',
        'maximum_cancellation_tries_for_one_periodic_tick': 2,
    },
)
@pytest.mark.now('2021-01-01T03:30:00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_orders.sql'])
async def test_max_ticks_reached(taxi_eats_orders_tracking, mockserver):
    requested_order_nrs = []

    @mockserver.json_handler(URL_CORE_CANCEL_ORDER)
    def _handler_core_resend_orders(request):
        requested_order_nrs.append(request.json['order_nr'])
        return mockserver.make_response(status=200)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    expected_order_nrs = ['000000-000005', '000000-000006']
    requested_order_nrs.sort()
    expected_order_nrs.sort()
    assert requested_order_nrs == expected_order_nrs
    assert _handler_core_resend_orders.times_called == 2
