import datetime

import pytest


_NOW = datetime.datetime(2019, 8, 2, 11, 52, 37, 12325)

_FALLBACK_DESCRIPTIONS = [
    {
        'service': 'active-service',
        'fallbacks': [
            {
                'name': 'active-service.fallback',
                'errors': ['active-service.error'],
                'totals': ['active-service.total'],
                'interval': 120,
                'min_events': 100,
                'threshold': 2,
            },
        ],
    },
    {'service': '.*', 'fallbacks': []},
    {
        'service': 'faded-service',
        'fallbacks': [
            {
                'name': 'faded-service.fallback',
                'errors': ['faded-service.error'],
                'totals': ['faded-service.total'],
                'interval': 120,
                'min_events': 100,
                'threshold': 2,
            },
        ],
    },
    {
        'service': 'delayed-service',
        'inactivity_deadline': '2019-08-02T11:58:01Z',
        'fallbacks': [
            {
                'name': 'faded-service.fallback',
                'errors': ['faded-service.error'],
                'totals': ['faded-service.total'],
                'interval': 120,
                'min_events': 100,
                'threshold': 2,
            },
        ],
    },
]


@pytest.mark.now(_NOW.isoformat())
async def test_monrun_inactive_service(
        taxi_statistics,
        taxi_statistics_monitor,
        now,
        mocked_time,
        taxi_config,
):
    taxi_config.set_values(
        {
            'STATISTICS_FALLBACK_INACTIVITY_TIMEOUT_ON_CONFIG_UPDATE': 60,
            'STATISTICS_FALLBACK_DESCRIPTIONS': _FALLBACK_DESCRIPTIONS,
        },
    )

    inactive_url = '/service/monrun/inactive-fallback-services'
    store_path = '/v1/metrics/store'

    now_bucket = now.replace(second=0, microsecond=0)

    for service in ('active-service', 'faded-service'):
        response = await taxi_statistics.post(
            store_path,
            json={
                'service': service,
                'time_bucket': f'{now_bucket.isoformat()}Z',
                'metrics': [
                    {'name': f'{service}.error', 'value': 3},
                    {'name': f'{service}.total', 'value': 100},
                ],
            },
        )
        assert response.status_code == 200, response.body

    await taxi_statistics.run_periodic_task('UpdateTask')
    await taxi_statistics.tests_control()

    resp = await taxi_statistics_monitor.get(inactive_url)
    assert resp.status_code == 200
    assert resp.text == '0; OK: all service configurations are active\n'

    mocked_time.set(now + datetime.timedelta(seconds=61))
    await taxi_statistics.tests_control(invalidate_caches=False)

    resp = await taxi_statistics_monitor.get(inactive_url)
    assert resp.status_code == 200
    assert (
        resp.text == '1; WARN: inactive service fallback configurations: '
        'faded-service\n'
    )
