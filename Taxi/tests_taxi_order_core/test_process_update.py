import datetime

import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_update_delivered(
        mockserver, stq_runner, mongodb, taxi_config,
):
    order_id = 'happy_path'

    @mockserver.handler(
        'driver-orders-app-api/internal/v1/order/update/', prefix=True,
    )
    def mock_update_order(req):
        assert req.path.split('/')[-1] == 'user_ready'
        assert req.json == {
            'order_id': order_id,
            'driver': {
                'park_id': 'df98ffa680714291882343e7df1ca5ab',
                'driver_profile_id': '957600cda6b74ca58fe20963d61ff060',
                'alias_id': 'cf0ae5ed549457a081fe9dd0c4bb6fcb',
            },
            'change_id': '36cae0c2c9b8493f5a5bb2dca5b94958',
        }
        return mockserver.make_response(status=200)

    kwargs = {'order_id': order_id, 'type': 'user_ready'}
    await stq_runner.process_update.call(
        task_id=f'{order_id}_user_ready', kwargs=kwargs,
    )

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['updated'] >= _NOW
    # do not edit changes with statuses
    assert proc['changes']['objects'][0]['si']['s'] == 'delivered'
    assert proc['changes']['objects'][1]['si']['s'] == 'skipped'
    assert proc['changes']['objects'][2]['si']['s'] == 'failed'
    # skip all but last
    assert proc['changes']['objects'][3]['si']['s'] == 'skipped'
    assert proc['changes']['objects'][4]['si']['s'] == 'skipped'
    # deliver last one
    assert proc['changes']['objects'][5]['si']['s'] == 'delivered'
    # other type, status is not changed
    assert proc['changes']['objects'][6]['si']['s'] == 'init'

    assert mock_update_order.times_called == 1


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_update_skipped(
        mockserver, stq_runner, mongodb, taxi_config,
):
    order_id = 'no_performer'

    kwargs = {'order_id': order_id, 'type': 'user_ready'}
    await stq_runner.process_update.call(
        task_id=f'{order_id}_user_ready', kwargs=kwargs, expect_fail=False,
    )

    proc = mongodb.order_proc.find_one({'_id': order_id})

    assert proc['updated'] < _NOW


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_update_failed(
        mockserver, stq_runner, mongodb, taxi_config,
):
    order_id = 'happy_path'

    @mockserver.handler(
        'driver-orders-app-api/internal/v1/order/update/', prefix=True,
    )
    def mock_update_order(req):
        return mockserver.make_response(status=410, json={'message': 'sorry'})

    kwargs = {'order_id': order_id, 'type': 'user_ready'}
    await stq_runner.process_update.call(
        task_id=f'{order_id}_user_ready', kwargs=kwargs, expect_fail=False,
    )

    proc = mongodb.order_proc.find_one({'_id': order_id})

    assert proc['updated'] < _NOW

    assert mock_update_order.times_called == 1


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_update_failed_no_reschedule(
        mockserver, stq_runner, mongodb, taxi_config,
):
    rescheduling_config = {'min_delay': 1, 'max_retries': 0, 'max_delay': 300}
    taxi_config.set(
        ORDER_CORE_STQ_PROCESS_UPDATE_RESCHEDULING=rescheduling_config,
    )
    order_id = 'happy_path'

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @mockserver.handler(
        'driver-orders-app-api/internal/v1/order/update/', prefix=True,
    )
    def mock_update_order(req):
        return mockserver.make_response(status=410, json={'message': 'sorry'})

    kwargs = {'order_id': order_id, 'type': 'user_ready'}
    await stq_runner.process_update.call(
        task_id=f'{order_id}_user_ready', kwargs=kwargs, expect_fail=False,
    )
    assert stq_runner

    proc = mongodb.order_proc.find_one({'_id': order_id})

    assert proc['updated'] < _NOW

    assert mock_update_order.times_called == 1
    assert mock_stq_reschedule.times_called == 0


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_update_errors(
        mockserver, stq_runner, mongodb, taxi_config,
):
    order_id = 'happy_path'

    @mockserver.handler(
        'driver-orders-app-api/internal/v1/order/update/', prefix=True,
    )
    def mock_update_order(req):
        return mockserver.make_response(status=500, json={'message': 'sorry'})

    kwargs = {'order_id': order_id, 'type': 'user_ready'}
    await stq_runner.process_update.call(
        task_id=f'{order_id}_user_ready', kwargs=kwargs, expect_fail=True,
    )

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['updated'] < _NOW
    assert mock_update_order.times_called > 0


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_process_update_finished(
        mockserver, stq_runner, mongodb, taxi_config,
):
    order_id = 'finished'

    @mockserver.handler(
        'driver-orders-app-api/internal/v1/order/update/', prefix=True,
    )
    def mock_update_order(req):
        return mockserver.make_response(status=410, json={'message': 'sorry'})

    kwargs = {'order_id': order_id, 'type': 'user_ready'}
    await stq_runner.process_update.call(
        task_id=f'{order_id}_user_ready', kwargs=kwargs, expect_fail=False,
    )

    proc = mongodb.order_proc.find_one({'_id': order_id})

    assert proc['updated'] >= _NOW
    # do not edit changes with statuses
    assert proc['changes']['objects'][0]['si']['s'] == 'delivered'
    assert proc['changes']['objects'][1]['si']['s'] == 'skipped'
    assert proc['changes']['objects'][2]['si']['s'] == 'failed'
    # skip all but last
    assert proc['changes']['objects'][3]['si']['s'] == 'skipped'
    assert proc['changes']['objects'][4]['si']['s'] == 'skipped'
    # skip last one too
    assert proc['changes']['objects'][5]['si']['s'] == 'skipped'
    # other type, status is not changed
    assert proc['changes']['objects'][6]['si']['s'] == 'init'

    assert mock_update_order.times_called == 0
