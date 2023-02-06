import pytest


_OEP_PIPELINES = [
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {'sink_name': 'bulk-sink'},
        'name': 'order-events',
    },
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {
            'sink_name': 'bulk-sink-2',
            'arguments': {'number_of_threads': 7},
        },
        'name': 'order-events2',
    },
]


@pytest.mark.parametrize('number_of_threads', [(1, 2), (13, 15)])
async def test_pipeline_number_of_threads(
        taxi_eventus_sample,
        testpoint,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        number_of_threads,
):
    @testpoint('eventus::pipeline_number_of_threads')
    def pipeline_number_of_threads(data):
        pass

    for i in range(2):
        _OEP_PIPELINES[i]['number_of_threads'] = number_of_threads[i]

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, _OEP_PIPELINES,
    )

    assert pipeline_number_of_threads.times_called == 1
    call_result = await pipeline_number_of_threads.wait_call()
    assert call_result['data']['number_of_threads'] == max(number_of_threads)


@pytest.mark.parametrize('number_of_threads, should_be', [(-5, 1), (7, 7)])
async def test_sink_number_of_threads(
        taxi_eventus_sample,
        testpoint,
        taxi_config,
        taxi_eventus_orchestrator_mock,
        number_of_threads,
        should_be,
):
    @testpoint('eventus::sink_number_of_threads')
    def sink_number_of_threads(data):
        pass

    _OEP_PIPELINES[1]['root']['arguments'][
        'number_of_threads'
    ] = number_of_threads
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, _OEP_PIPELINES,
    )

    assert sink_number_of_threads.times_called == 2
    calls = []
    for _ in range(2):
        calls.append(await sink_number_of_threads.wait_call())
    # one sink with custom number of threads - 7, and one with default - 3
    assert list(
        sorted(map(lambda x: x['data']['number_of_threads'], calls)),
    ) == list(sorted([3, should_be]))
