import datetime

import pytest

TIMEOUT = 10
MULTIOFFER_ID = '01234567-89ab-cdef-0123-456789abcdef'


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_stq_contractor_orders_multioffer_assign(
        stq_runner, mocked_time, driver_orders_app_api, stq,
):
    await stq_runner.contractor_orders_multioffer_assign.call(
        task_id='task-id',
        args=[
            MULTIOFFER_ID,
            'order_id',
            TIMEOUT,
            [
                {
                    'park_id': 'park_id_1',
                    'driver_profile_id': 'driver_profile_id_1',
                    'alias_id': 'alias_id_1',
                },
                {
                    'park_id': 'park_id_2',
                    'driver_profile_id': 'driver_profile_id_2',
                    'alias_id': 'alias_id_2',
                },
            ],
        ],
        expect_fail=False,
    )

    assert driver_orders_app_api.bulk_create_called == 1
    assert stq.contractor_orders_multioffer_complete.times_called == 1

    complete = stq.contractor_orders_multioffer_complete.next_call()
    kwargs = complete['kwargs']
    assert kwargs['multioffer_id'] == MULTIOFFER_ID
    eta = complete['eta']
    assert eta == mocked_time.now() + datetime.timedelta(seconds=TIMEOUT)
