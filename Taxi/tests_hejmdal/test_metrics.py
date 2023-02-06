import pytest


@pytest.mark.now('1970-01-15T06:59:40+0000')
async def test_juggler_metrics(
        taxi_hejmdal, taxi_hejmdal_monitor, mockserver, testpoint,
):

    json_ts = {
        'timestamps': [
            1234267000,
            1234327000,
            1234387000,
            1234447000,
            1234507000,
            1234567000,
            1234627000,
            1234687000,
            1234747000,
        ],
        'values': [
            0.94,
            26.916,
            1.376,
            5.084,
            1.441,
            1.27,
            1.063,
            0.731,
            0.882,
        ],
    }

    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(request):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'project': 'test_project',
                            'cluster': 'test_cluster',
                            'service': 'test_service',
                            'sensor': 'test-service-sensor',
                        },
                        **json_ts,
                    },
                },
            ],
        }

    @testpoint('send-juggler-events')
    def handle(data):
        return

    await taxi_hejmdal.enable_testpoints()

    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_periodic_task('transceiving')

    await handle.wait_call()

    metrics = await taxi_hejmdal_monitor.get_metric('notification-center')
    assert 'hejmdal-test' in metrics['juggler']['sending-lag-ms']
    assert 'total' in metrics['juggler']['sending-lag-ms']
    assert 'hejmdal-test' in metrics['juggler']['total-lag-ms']
    assert 'total' in metrics['juggler']['total-lag-ms']
