import tests_contractor_order_setcar.redis_helpers as rh

PARK_ID = 'park_id_0'
ALIAS_ID = 'alias_id_0'
PROFILE_ID = 'profile_id_0'


async def test_delete_order_request(
        taxi_contractor_order_setcar, redis_store, stq,
):
    rh.set_redis_for_order_cancelling(
        redis_store, PARK_ID, ALIAS_ID, PROFILE_ID,
    )
    response = await taxi_contractor_order_setcar.post(
        '/v1/order/delete',
        json={
            'park_id': PARK_ID,
            'driver_profile_id': PROFILE_ID,
            'alias_id': ALIAS_ID,
        },
    )
    assert response.json() == {}
    assert response.status_code == 200

    rh.check_remove_setcar(redis_store, PARK_ID, ALIAS_ID, PROFILE_ID)

    assert stq.contractor_order_setcar_delete_order.times_called == 1
    kwargs = stq.contractor_order_setcar_delete_order.next_call()['kwargs']
    assert kwargs['park_id'] == PARK_ID
    assert kwargs['driver_profile_id'] == PROFILE_ID
    assert kwargs['alias_id'] == ALIAS_ID


DELETE_TASK_ID = 'contractor_order_setcar_delete_order'
NOT_REMOVED_STAT = 'not_removed_keys_statistics'


async def test_delete_order_task(stq_runner, redis_store):
    rh.set_redis_for_order_cancelling(
        redis_store, PARK_ID, ALIAS_ID, PROFILE_ID,
    )
    await stq_runner.contractor_order_setcar_delete_order.call(
        task_id=DELETE_TASK_ID,
        kwargs={
            'park_id': PARK_ID,
            'driver_profile_id': PROFILE_ID,
            'alias_id': ALIAS_ID,
        },
        expect_fail=False,
    )

    rh.check_remove_setcar(redis_store, PARK_ID, ALIAS_ID, PROFILE_ID)


def check_not_removed_metrics(metrics, num_try):
    #  {'0': 1} for first try, {'0': 1, '1': 1} for second try
    val_expected = {}
    for num in range(num_try + 1):
        val_expected[str(num)] = 1

    for key in [
            'ClientGeoSharing',
            'Driver::Reserv',
            'Drivers',
            'Items',
            'Providers',
    ]:
        assert metrics[key]['num_try'] == val_expected


async def test_not_removed_keys_metric(
        stq_runner,
        redis_store,
        taxi_contractor_order_setcar,
        taxi_contractor_order_setcar_monitor,
):
    await taxi_contractor_order_setcar.tests_control(
        reset_metrics=True, invalidate_caches=True,
    )

    first_success_try = 3
    num_failed_tries = first_success_try - 1

    rh.set_redis_for_order_cancelling(
        redis_store, PARK_ID, ALIAS_ID, PROFILE_ID,
    )

    for num_try in range(first_success_try):
        if num_try < num_failed_tries:
            rh.set_redis_for_order_cancelling(
                redis_store, PARK_ID, ALIAS_ID, PROFILE_ID,
            )

        await stq_runner.contractor_order_setcar_delete_order.call(
            task_id=DELETE_TASK_ID,
            kwargs={
                'park_id': PARK_ID,
                'driver_profile_id': PROFILE_ID,
                'alias_id': ALIAS_ID,
            },
            expect_fail=False,
            reschedule_counter=num_try,
        )

        metrics = await taxi_contractor_order_setcar_monitor.get_metric(
            NOT_REMOVED_STAT,
        )

        check_not_removed_metrics(
            metrics['key'], num_try - int(num_try == num_failed_tries),
        )

    rh.check_remove_setcar(redis_store, PARK_ID, ALIAS_ID, PROFILE_ID)
