import pytest

TASK_NAME = 'order-status-correction'
URL_CORE = (
    '/eats-core-orders-tracking'
    + '/internal-api/v1/orders-tracking/resend-orders'
)


async def test_dummy(taxi_eats_orders_tracking):
    # Workaround for TAXIDATA-3002: This test just loads service.
    pass


@pytest.mark.config(
    EATS_ORDERS_TRACKING_ORDER_STATUS_CORRECTION={
        'is_order_status_correction_enabled': True,
        'task_period_seconds': 600,
        'maximal_order_info_age_seconds': 1800,
        'maximal_orders_number_in_request': 100,
    },
)
@pytest.mark.now('2021-01-01T10:00:00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_orders.sql'])
async def test_order_status_correction(taxi_eats_orders_tracking, mockserver):
    requested_order_nrs = set()

    @mockserver.json_handler(URL_CORE)
    def _handler_core_resend_orders(request):
        for order_nr in request.json['order_nrs']:
            requested_order_nrs.add(order_nr)
        return mockserver.make_response(status=204)

    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)

    expected_order_nrs = {'000000-000005', '000000-000006', '000000-000010'}
    assert requested_order_nrs == expected_order_nrs
    assert _handler_core_resend_orders.times_called == 1


@pytest.mark.config(
    EATS_ORDERS_TRACKING_ORDER_STATUS_CORRECTION={
        'is_order_status_correction_enabled': False,
        'task_period_seconds': 600,
        'maximal_order_info_age_seconds': 1800,
        'maximal_orders_number_in_request': 100,
    },
)
@pytest.mark.now('2021-01-01T10:00:00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['fill_orders.sql'])
async def test_order_status_correction_disabled(
        taxi_eats_orders_tracking, pgsql,
):
    # Core must not be called. Mock is not required.
    await taxi_eats_orders_tracking.run_distlock_task(TASK_NAME)
