async def start_watch_stq(
        stq_runner,
        testpoint,
        driver_id,
        destination,
        service_id,
        meta,
        order_id=None,
        taxi_status=None,
        expected_testpoint_result='ok',
):
    queue_name = 'driver_route_watcher_new_destination'

    @testpoint('stq-event-new-destination-done')
    def _mock_performer(request):
        return {}

    kwargs = {
        'driver_uuid': driver_id['uuid'],
        'driver_dbid': driver_id['dbid'],
        'service_id': service_id,
        'metainfo': meta,
    }
    if order_id is not None:
        kwargs.update({'order_id': order_id})

    if service_id == 'processing:transporting':
        kwargs.update(
            {
                'field': 'destinations',
                'destinations': [destination],
                'destinations_statuses': [],
                'taxi_status': 'transporting',
            },
        )
    elif service_id == 'processing:driving':
        kwargs.update(
            {
                'field': 'source',
                'source': destination,
                'taxi_status': 'driving',
            },
        )
    else:
        kwargs.update({'field': 'source', 'source': destination})
    if taxi_status is not None:
        kwargs.update({'taxi_status': taxi_status})

    await getattr(stq_runner, queue_name).call(
        task_id='sample_task',
        kwargs=kwargs,
        expect_fail=False,
        reschedule_counter=0,
        exec_tries=0,
    )
    assert (await _mock_performer.wait_call())[
        'request'
    ] == expected_testpoint_result


async def stop_watch_stq(
        stq_runner, testpoint, driver_id, destinations, service_id,
):
    queue_name = 'driver_route_watcher_reset_destination'

    @testpoint('stq-event-reset-destination-done')
    def _mock_performer(request):
        return {}

    kwargs = {
        'driver_uuid': driver_id['uuid'],
        'driver_dbid': driver_id['dbid'],
        'service_id': service_id,
    }

    if service_id == 'processing':
        kwargs.update(
            {
                'field': 'all',
                'source': destinations[0],
                'destinations': destinations[1:],
                'destinations_statuses': [],
            },
        )
    else:
        kwargs.update({'field': 'source', 'source': destinations[0]})

    await getattr(stq_runner, queue_name).call(
        task_id='sample_task',
        kwargs=kwargs,
        expect_fail=False,
        reschedule_counter=0,
        exec_tries=0,
    )
    assert (await _mock_performer.wait_call())['request'] == 'ok'
