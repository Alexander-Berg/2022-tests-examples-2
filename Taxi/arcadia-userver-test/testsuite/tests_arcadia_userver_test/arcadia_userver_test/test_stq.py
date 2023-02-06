async def test_stq_client(taxi_arcadia_userver_test, stq):
    response = await taxi_arcadia_userver_test.post(
        '/stq/create-task', data='task id',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {}

    assert stq.sample_queue_with_args.times_called == 1
    stq_call = stq.sample_queue_with_args.next_call()
    assert stq_call['id'] == 'internal id'
    assert stq_call['kwargs']['task_id'] == 'task id'
    assert stq_call['kwargs']['optional_arg'] == 42


async def test_stq_client_bare(taxi_arcadia_userver_test, stq):
    response = await taxi_arcadia_userver_test.post(
        '/stq/create-task', data='task id', params={'queue': 'sample_queue'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {}

    assert stq.sample_queue.times_called == 1
    stq_call = stq.sample_queue.next_call()
    assert stq_call['id'] == 'internal id'
    assert stq_call['args'] == ['task id']


async def test_stq_worker_task(stq_runner, pgsql):
    await stq_runner.sample_queue_with_args.call(
        task_id='sample_task',
        kwargs={'task_id': 'task id', 'double_param': 1.0, 'optional_arg': 42},
        expect_fail=False,
    )


async def test_stq_worker_task_bare(stq_runner, pgsql):
    await stq_runner.sample_queue.call(
        task_id='sample_task',
        args=[42, 'foobar'],
        kwargs={'some_arg': 'some_value'},
        expect_fail=False,
    )


async def test_stq_worker_task_fails(stq_runner, pgsql):
    await stq_runner.sample_queue_with_args.call(
        task_id='sample_task',
        kwargs={'task_id': 'task id', 'double_param': 1.0},
        expect_fail=True,
    )
