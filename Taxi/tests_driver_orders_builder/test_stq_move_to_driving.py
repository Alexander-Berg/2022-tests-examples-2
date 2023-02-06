async def test_stq_move_to_driving_success(
        stq_runner, driver_orders_app_api, mockserver,
):
    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/driving',
    )
    def status_driving(self):
        return mockserver.make_response(json={'status': 'driving'}, status=200)

    await stq_runner.driver_orders_builder_multioffer_move_to_driving.call(
        task_id='task-id',
        args=['park_id', 'driver_id', 'order_id'],
        kwargs={
            'seen_data': (
                '{"reason":"123", "timestamp": 1234567890,'
                ' "lat": 13.4, "lon": 13.5}'
            ),
        },
        expect_fail=False,
    )

    assert status_driving.times_called == 1
    assert driver_orders_app_api.cancel_v2.times_called == 0


async def test_stq_move_to_driving_with_cancel(
        stq_runner, driver_orders_app_api, mockserver,
):
    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/driving',
    )
    def status_driving(self):
        return mockserver.make_response(
            json={'message': 'some error', 'code': '404'}, status=404,
        )

    await stq_runner.driver_orders_builder_multioffer_move_to_driving.call(
        task_id='task-id',
        args=['park_id', 'driver_id', 'order_id'],
        kwargs={
            'seen_data': (
                '{"reason":"123", "timestamp": 1234567890,'
                ' "lat": 13.4, "lon": 13.5}'
            ),
        },
        expect_fail=False,
    )

    assert status_driving.times_called == 1
    assert driver_orders_app_api.cancel_v2.times_called == 1
