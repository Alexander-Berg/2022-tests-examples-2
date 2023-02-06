async def test_service_based_distlocks(
        testpoint, taxi_userver_distlock_sample,
):
    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_userver_distlock_sample.spawn_task('distlock/sample-task'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


async def test_service_based_distlocks_aiohttp(
        testpoint, taxi_userver_distlock_sample_aiohttp,
):
    @testpoint('samples::service_based_distlock-finished')
    def handle_finished(arg):
        pass

    async with taxi_userver_distlock_sample_aiohttp.spawn_task(
            'distlock/sample-task',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
