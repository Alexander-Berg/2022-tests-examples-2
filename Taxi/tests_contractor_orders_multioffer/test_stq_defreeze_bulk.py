import pytest


@pytest.mark.config(
    CONTRACTOR_ORDERS_MULTIOFFER_STQ_MAX_RETRIES={
        'contractor_orders_multioffer_defreeze': {'max_retries': 3},
    },
    CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS={
        'enable': True,
        'freeze_duration': 60,
        'defreeze_bulk': True,
    },
)
async def test_stq_contractor_orders_multioffer_defreeze_bulk(
        stq_runner, driver_freeze, stq,
):
    driver_freeze.n_of_request_drivers = 2

    driver_freeze.defreeze_bulk_driver_error = 'not_defreezed'

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
        expect_fail=False,
        exec_tries=1,
    )

    assert driver_freeze.defreeze_called == 0
    assert driver_freeze.defreeze_bulk_called == 1

    driver_freeze.defreeze_bulk_called = 0
    driver_freeze.defreeze_bulk_driver_error = 'internal_error'

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

    driver_freeze.defreeze_bulk_called = 0
    driver_freeze.defreeze_bulk_driver_error = None
    driver_freeze.n_of_request_drivers = 6

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
                {
                    'unique_driver_id': 'unique_driver_id_3',
                    'car_id': 'car_id_3',
                },
                {
                    'unique_driver_id': 'unique_driver_id_4',
                    'car_id': 'car_id_4',
                },
                {
                    'unique_driver_id': 'unique_driver_id_5',
                    'car_id': 'car_id_5',
                },
                {
                    'unique_driver_id': 'unique_driver_id_6',
                    'car_id': 'car_id_6',
                },
            ],
        ],
        expect_fail=False,
        exec_tries=1,
    )
