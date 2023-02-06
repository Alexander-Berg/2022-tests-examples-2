import asyncio


async def test_simple(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        load_json,
        jaeger_collector_mock,
):
    jaeger_collector_mock.set_request_bench(load_json('received_1.json'))
    fill_pilorama_config('jaeger_conf.json')
    fill_service_logs('1.log')

    await taxi_pilorama.run_task('pilorama/restart')

    while not jaeger_collector_mock.is_ready():
        await asyncio.sleep(1)

    assert jaeger_collector_mock.is_succeed()
