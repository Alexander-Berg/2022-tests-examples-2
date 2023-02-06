import pytest


@pytest.fixture(name='mocker_robot_open')
def _mocker_robot_open(mockserver):
    def wrapper(result: dict = None, status: int = 200):
        @mockserver.json_handler(
            r'/robot-sdc/api/couriers/(?P<driver_id>\w+)/open_hatch',
            regex=True,
        )
        def mark_order_complete(request, driver_id):
            assert driver_id == 'driver_id1'

            return mockserver.make_response(
                json=result or {'job_id': 123}, status=status,
            )

        return mark_order_complete

    return wrapper


async def test_happy_path(stq_runner, default_order_id, mocker_robot_open):
    mock_robot = mocker_robot_open()

    await stq_runner.cargo_orders_open_rover.call(
        task_id='test_happy_path', kwargs={'cargo_order_id': default_order_id},
    )
    assert mock_robot.times_called == 1
    result = mock_robot.next_call()
    assert result['request'].json == {'number': 'order_alias_id'}


async def test_robot_400(stq_runner, default_order_id, mocker_robot_open):
    mock_robot = mocker_robot_open(status=400)

    await stq_runner.cargo_orders_open_rover.call(
        task_id='test_happy_path', kwargs={'cargo_order_id': default_order_id},
    )
    assert mock_robot.times_called == 1


async def test_robot_unknown_error(
        stq_runner, default_order_id, mocker_robot_open,
):
    mock_robot = mocker_robot_open(status=500)

    await stq_runner.cargo_orders_open_rover.call(
        task_id='test_happy_path',
        kwargs={'cargo_order_id': default_order_id},
        expect_fail=True,
    )
    assert mock_robot.times_called


async def test_resolved_waybill(
        stq_runner, my_waybill_info, default_order_id, mocker_robot_open,
):
    mock_robot = mocker_robot_open()

    # Resolve waybill
    my_waybill_info['dispatch']['status'] = 'resolved'
    my_waybill_info['dispatch']['resolution'] = 'complete'

    await stq_runner.cargo_orders_open_rover.call(
        task_id='test_happy_path', kwargs={'cargo_order_id': default_order_id},
    )
    assert not mock_robot.times_called
