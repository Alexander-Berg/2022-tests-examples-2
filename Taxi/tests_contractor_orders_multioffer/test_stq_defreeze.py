import pytest


@pytest.mark.config(
    CONTRACTOR_ORDERS_MULTIOFFER_STQ_MAX_RETRIES={
        'contractor_orders_multioffer_defreeze': {'max_retries': 3},
    },
)
@pytest.mark.parametrize('defreeze_bulk', [None, False, True])
async def test_stq_contractor_orders_multioffer_defreeze(
        stq_runner, driver_freeze, defreeze_bulk, stq, taxi_config,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS': {
                'enable': True,
                'freeze_duration': 60,
                'defreeze_bulk': defreeze_bulk,
            },
        },
    )

    if defreeze_bulk:
        driver_freeze.n_of_request_drivers = 2

    await stq_runner.contractor_orders_multioffer_defreeze.call(
        task_id='task-id',
        args=[
            'order_id',
            [
                {
                    'unique_driver_id': 'unique_driver_id_1',
                    'car_id': 'car_id_1',
                },
                {
                    'unique_driver_id': 'unique_driver_id_2',
                    'car_id': 'car_id_2',
                },
            ],
        ],
        expect_fail=False,
        exec_tries=0,
    )

    assert driver_freeze.defreeze_called == (0 if defreeze_bulk else 2)
    assert driver_freeze.defreeze_bulk_called == (1 if defreeze_bulk else 0)

    driver_freeze.defreeze_called = 0
    driver_freeze.defreeze_bulk_called = 0

    await stq_runner.contractor_orders_multioffer_defreeze.call(
        task_id='task-id',
        args=[
            'order_id',
            [
                {
                    'unique_driver_id': 'unique_driver_id_1',
                    'car_id': 'car_id_1',
                },
                {
                    'unique_driver_id': 'unique_driver_id_2',
                    'car_id': 'car_id_2',
                },
            ],
        ],
        expect_fail=False,
        exec_tries=4,
    )
    assert driver_freeze.defreeze_called == 0
    assert driver_freeze.defreeze_bulk_called == 0

    driver_freeze.defreeze_response = 404
    await stq_runner.contractor_orders_multioffer_defreeze.call(
        task_id='task-id',
        args=[
            'order_id',
            [
                {
                    'unique_driver_id': 'unique_driver_id_1',
                    'car_id': 'car_id_1',
                },
                {
                    'unique_driver_id': 'unique_driver_id_404',
                    'car_id': 'car_id_2',
                },
            ],
        ],
        expect_fail=False,
        exec_tries=1,
    )

    assert driver_freeze.defreeze_called == (0 if defreeze_bulk else 2)
    assert driver_freeze.defreeze_bulk_called == (1 if defreeze_bulk else 0)

    if not defreeze_bulk:
        driver_freeze.defreeze_response = 500
    else:
        driver_freeze.defreeze_bulk_response = 500
    await stq_runner.contractor_orders_multioffer_defreeze.call(
        task_id='task-id',
        args=[
            'order_id',
            [
                {
                    'unique_driver_id': 'unique_driver_id_1',
                    'car_id': 'car_id_1',
                },
                {
                    'unique_driver_id': 'unique_driver_id_500',
                    'car_id': 'car_id_2',
                },
            ],
        ],
        expect_fail=True,
        exec_tries=1,
    )
