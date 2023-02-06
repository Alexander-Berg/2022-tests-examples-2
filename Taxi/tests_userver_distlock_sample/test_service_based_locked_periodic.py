import pytest


async def test_task(testpoint, taxi_userver_distlock_sample):
    @testpoint('samples::locked-periodic-finished')
    def handle_finished(arg):
        pass

    await taxi_userver_distlock_sample.run_distlock_task('test-task')

    result = handle_finished.next_call()
    assert result == {'arg': 'test'}


async def test_task_failure(testpoint, taxi_userver_distlock_sample):
    @testpoint('samples::locked-periodic-finished')
    def handle_finished(arg):
        return {'inject_failure': True}

    with pytest.raises(taxi_userver_distlock_sample.TestsuiteTaskFailed):
        await taxi_userver_distlock_sample.run_distlock_task('test-task')
    assert handle_finished.times_called == 1


async def test_task_aiohttp(testpoint, taxi_userver_distlock_sample_aiohttp):
    @testpoint('samples::locked-periodic-finished')
    def handle_finished(arg):
        pass

    await taxi_userver_distlock_sample_aiohttp.run_distlock_task('test-task')

    result = handle_finished.next_call()
    assert result == {'arg': 'test'}


async def test_task_failure_aiohttp(
        testpoint, taxi_userver_distlock_sample_aiohttp,
):
    @testpoint('samples::locked-periodic-finished')
    def handle_finished(arg):
        return {'inject_failure': True}

    with pytest.raises(
            taxi_userver_distlock_sample_aiohttp.TestsuiteTaskFailed,
    ):
        await taxi_userver_distlock_sample_aiohttp.run_distlock_task(
            'test-task',
        )
    assert handle_finished.times_called == 1
