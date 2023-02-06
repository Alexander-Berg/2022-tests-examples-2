import pytest


@pytest.fixture(name='extract_metric')
async def _extract_metric(taxi_userver_sample_monitor):
    async def wrapper():
        metric = await taxi_userver_sample_monitor.get_metrics('envoy')

        for arg in ['envoy', 'userver-sample', 'operations']:
            assert arg in metric
            metric = metric[arg]

        return metric

    return wrapper


@pytest.fixture(name='reset_metric')
async def _reset_metric(taxi_userver_sample, extract_metric):
    async def wrapper():
        await taxi_userver_sample.tests_control(reset_metrics=True)
        assert (await extract_metric()) == {}

    return wrapper


async def test_empty(
        taxi_userver_sample, mockserver, extract_metric, reset_metric,
):
    await reset_metric()

    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return mockserver.make_response()

    response = await taxi_userver_sample.get('external-echo-empty')
    assert response.status_code == 200
    assert _handler.times_called == 1

    assert (await extract_metric()) == {}


async def test_vhost(
        taxi_userver_sample, mockserver, extract_metric, reset_metric,
):
    await reset_metric()

    @mockserver.json_handler('/userver-sample/autogen/empty')
    def _handler(request):
        return mockserver.make_response(
            headers={'X-Taxi-EnvoyProxy-DstVhost': 'test-vhost'},
        )

    for _ in range(5):
        response = await taxi_userver_sample.get('external-echo-empty')
        assert response.status_code == 200

    assert _handler.times_called == 5

    metric = await extract_metric()
    assert metric == {'/autogen/empty-get': {'test-vhost': 5}}
