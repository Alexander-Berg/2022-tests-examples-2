import datetime

import pytest


@pytest.mark.now('2019-08-02 11:52:25+0000')
@pytest.mark.config(
    STATISTICS_FALLBACK_DESCRIPTIONS=[
        {
            'service': 'client',
            'fallbacks': [
                {
                    'name': '1.fallback',
                    'errors': [r'1\.error'],
                    'totals': [r'1\.error', r'1\.success'],
                    'interval': 10,
                    'min_events': 1,
                    'threshold': 1,
                },
                {
                    'name': '{1}.common-fallback',
                    'errors': [r'(.*)\.error'],
                    'totals': [r'(.*)\.error', r'(.*)\.success'],
                    'interval': 20,
                    'min_events': 1,
                    'threshold': 99,
                },
            ],
        },
    ],
)
async def test_different_intervals(taxi_statistics, now):
    response = await taxi_statistics.get(
        'v1/service/health',
        params={'service': 'client'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()

    assert response['fallbacks'] == []


@pytest.mark.parametrize(
    'errors, totals, time_shifts',
    [
        (
            ['timeshift.test.created', 'timeshift.test.updated'],
            [
                'timeshift.test.created',
                'timeshift.test.updated',
                'timeshift.test.found',
            ],
            {'timeshift.test.created': 20, 'timeshift.test.updated': 10},
        ),
        (
            [r'timeshift\.(.*)\.created', r'timeshift\.(.*)\.updated'],
            [
                r'timeshift\.(.*)\.created',
                r'timeshift\.(.*)\.updated',
                r'timeshift\.(.*)\.found',
            ],
            {r'timeshift\.(.*)\.created': 20, r'timeshift\.(.*)\.updated': 10},
        ),
    ],
)
@pytest.mark.now('2021-11-15 12:00:00+0000')
async def test_time_shift(
        taxi_statistics,
        taxi_config,
        now,
        mocked_time,
        errors,
        totals,
        time_shifts,
):
    taxi_config.set_values(
        {
            'STATISTICS_FALLBACK_DESCRIPTIONS': [
                {
                    'service': 'client',
                    'fallbacks': [
                        {
                            'name': 'timeshift.fallback',
                            'errors': errors,
                            'totals': totals,
                            'interval': 60,
                            'min_events': 1,
                            'threshold': 90,
                            'time_shifts': time_shifts,
                        },
                    ],
                },
            ],
        },
    )

    async def check_fallbacks(fallbacks):
        response = await taxi_statistics.get(
            'v1/service/health',
            params={'service': 'client'},
            headers={'Date': f'{now.isoformat()}Z'},
        )
        assert response.status_code == 200
        response = response.json()
        assert response['fallbacks'] == fallbacks

    # no fallback: (created + updated) / (created + updated + found)
    # (10 + 10) / (10 + 10 + 10) = 0.66
    await check_fallbacks([])

    now = now + datetime.timedelta(seconds=10)
    mocked_time.set(now)
    await taxi_statistics.run_periodic_task('UpdateTask')

    # no fallback: (10 + 60) / (10 + 60 + 10) = 0.875
    await check_fallbacks([])

    now = now + datetime.timedelta(seconds=10)
    mocked_time.set(now)
    await taxi_statistics.run_periodic_task('UpdateTask')

    # fallback fires: (60 + 60) / (60 + 60 + 10) = 0.923
    await check_fallbacks(['timeshift.fallback'])
