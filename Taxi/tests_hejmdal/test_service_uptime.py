import pytest


@pytest.mark.now('2021-09-16T12:00:00+03')
async def test_service_uptime(mockserver, taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')

    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(request, *args, **kwargs):
        return {
            'vector': [{'scalar': 0.9}, {'scalar': 0.95}, {'scalar': 0.9975}],
        }

    await taxi_hejmdal.run_task('distlock/uptime_update')
    response = await taxi_hejmdal.get(
        'v1/analytics/service_uptime', params={'service_id': 139},
    )
    assert response.status_code == 200
    assert response.json()['uptime'] == [
        {'period': '1d', 'value': 0.9},
        {'period': '7d', 'value': 0.95},
        {'period': '30d', 'value': 0.9975},
    ]
