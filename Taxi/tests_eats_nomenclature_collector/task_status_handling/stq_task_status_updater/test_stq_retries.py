QUEUE_NAME = 'eats_nomenclature_collector_task_status_updater'

PLACE_ID = '1'


async def test_stq_error_limit(
        stq_enqueue_and_call,
        config_set_push_model,
        testpoint,
        update_taxi_config,
):
    config_set_push_model(place_ids=[PLACE_ID])

    max_retries_on_error = 2
    update_taxi_config(
        'EATS_NOMENCLATURE_COLLECTOR_STQ_PROCESSING',
        {
            '__default__': {
                'max_retries_on_error': max_retries_on_error,
                'max_retries_on_busy': 3,
                'max_busy_time_in_ms': 10000,
                'retry_on_busy_delay_ms': 5,
            },
        },
    )

    task_id = '1'
    kwargs = {
        'place_id': PLACE_ID,
        'integration_task_id': task_id,
        'integration_task_type': 'nomenclature',
        'status': 'created',
    }

    should_fail = True

    @testpoint(f'eats-nomenclature-collector::{QUEUE_NAME}::fail')
    def _fail(param):
        return {'inject_failure': should_fail}

    for i in range(max_retries_on_error):
        await stq_enqueue_and_call(
            QUEUE_NAME,
            task_id=task_id,
            kwargs=kwargs,
            expect_fail=True,
            exec_tries=i,
        )

    should_fail = False

    # should succeed because of the error limit
    await stq_enqueue_and_call(
        QUEUE_NAME,
        task_id=task_id,
        kwargs=kwargs,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )
