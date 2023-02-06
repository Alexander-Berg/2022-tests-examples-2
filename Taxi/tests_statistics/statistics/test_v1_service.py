import datetime

import pytest
import yatest.common  # pylint: disable=import-error


_NOW = datetime.datetime(2019, 8, 2, 11, 52, 37, 12325)
_DEFAULT_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.lpm.success', 393),
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.lpm.error', 7),
('2019-8-2 11:52:20+0000', 'cardstorage', 'card.lpm.success', 395),
('2019-8-2 11:52:20+0000', 'cardstorage', 'card.lpm.error', 5),

('2019-8-2 11:52:20+0000', 'cardstorage', 'uber.lpm.error', 100),
('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.lpm.success', 10000),

('2019-8-2 11:52:20+0000', 'buffer-dispatch', 'error', 10),
('2019-8-2 11:52:20+0000', 'buffer-dispatch', 'total', 10),
('2019-8-2 11:52:10+0000', 'buffer-dispatch', 'error', 100),
('2019-8-2 11:52:10+0000', 'buffer-dispatch', 'total', 100)
"""

# Statistics service uses Postrgesql NOW() on writes, reads and deletes from DB
# So we need to use real time for these tests
REAL_NOW = datetime.datetime.utcnow()
SOME_TIME_AGO = REAL_NOW - datetime.timedelta(seconds=27)
SOME_TIME_SOON = REAL_NOW + datetime.timedelta(seconds=120)


@pytest.mark.parametrize(
    'service, fallback',
    [
        ('cardstorage', ['card-lpm', 'uber-lpm']),
        ('buffer-dispatch', ['buffer-dispatch']),
    ],
)
@pytest.mark.parametrize(
    'interval, can_be_fired',
    [(20, ['uber-lpm']), (30, ['card-lpm', 'buffer-dispatch'])],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_DEFAULT_STATS])
async def test_service_health(
        taxi_statistics,
        now,
        taxi_config,
        interval,
        can_be_fired,
        service,
        fallback,
):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {
                'service': 'cardstorage',
                'fallbacks': [
                    {
                        'name': 'card-lpm',
                        'errors': ['card.lpm.error'],
                        'totals': ['card.lpm.error', 'card.lpm.success'],
                        'interval': interval,
                        'min_events': 100,
                        'threshold': 1.5,
                    },
                    {
                        'name': 'uber-lpm',
                        'errors': ['uber.lpm.error'],
                        'totals': ['uber.lpm.error', 'uber.lpm.success'],
                        'interval': interval,
                        'min_events': 100,
                        'threshold': 5,
                    },
                ],
            },
            {
                'service': 'buffer-dispatch',
                'fallbacks': [
                    {
                        'name': 'buffer-dispatch',
                        'errors': ['error'],
                        'totals': ['total'],
                        'interval': interval,
                        'min_events': 100,
                        'threshold': 2,
                    },
                ],
            },
        ],
    )
    expected_fallback = set(can_be_fired) & set(fallback)
    response = await taxi_statistics.get(
        'v1/service/health',
        params={'service': service},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    assert set(response['fallbacks']) == expected_fallback


_PATTERNS_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.lpm.error', 2),
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.lpm.total', 100),

('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.lpm.error', 1),
('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.lpm.total', 100),

('2019-8-2 11:52:10+0000', 'buffer-dispatch', 'dispatched.error', 1),
('2019-8-2 11:52:10+0000', 'buffer-dispatch', 'dispatched.total', 100)
"""


_PARTICULAR_SERVICE = [
    {
        'fallbacks': [
            {
                'errors': ['card.lpm.error'],
                'interval': 120,
                'min_events': 0,
                'name': 'card.lpm',
                'threshold': 2,
                'totals': ['card.lpm.total'],
            },
        ],
        'service': 'cardstorage',
    },
]


_PATTERN_SERVICE = [
    {
        'fallbacks': [
            {
                'errors': ['(.*).error'],
                'interval': 120,
                'min_events': 0,
                'name': '{1}',
                'threshold': 1,
                'totals': ['(.*).total'],
            },
        ],
        'service': '.*',
    },
]


@pytest.mark.parametrize(
    'fallback_descriptions, expected_fallbacks',
    [
        (
            _PARTICULAR_SERVICE + _PATTERN_SERVICE,
            {'cardstorage': {'card.lpm'}, 'buffer-dispatch': {'dispatched'}},
        ),
        (
            _PATTERN_SERVICE + _PARTICULAR_SERVICE,
            {
                'cardstorage': {'card.lpm', 'uber.lpm'},
                'buffer-dispatch': {'dispatched'},
            },
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_PATTERNS_STATS])
async def test_fallback_service_patterns(
        taxi_statistics,
        now,
        taxi_config,
        fallback_descriptions,
        expected_fallbacks,
):
    taxi_config.set(STATISTICS_FALLBACK_DESCRIPTIONS=fallback_descriptions)
    for service, expected_service_fallbacks in expected_fallbacks.items():
        response = await taxi_statistics.get(
            '/v1/service/health/',
            params={'service': service},
            headers={'Date': f'{now.isoformat()}Z'},
        )
        assert response.status_code == 200
        response = response.json()
        assert set(response['fallbacks']) == expected_service_fallbacks


_COMPLEX_PATTERNS_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.foo.total', 100),
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.foo.error', 1),
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.bar.error', 1),

('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.foo.total', 100),
('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.foo.error', 2),
('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.bar.error', 2)
"""


_SHORT_FALLBACK = [
    {
        'name': '{1}',
        'errors': ['(.*).(foo|bar).error'],
        'totals': ['(.*).(foo|bar).total'],
        'interval': 120,
        'min_events': 100,
        'threshold': 1.5,
    },
]


_FULL_FALLBACK = [
    {
        'name': '{1}.{2}.{1}',
        'errors': ['(.*).(foo|bar).error'],
        'totals': ['(.*).(foo|bar).total'],
        'interval': 120,
        'min_events': 100,
        'threshold': 1.5,
    },
]


@pytest.mark.parametrize(
    'fallback_descriptions, expected_fallbacks',
    [
        (_SHORT_FALLBACK + _FULL_FALLBACK, {'cardstorage': {'card', 'uber'}}),
        (_FULL_FALLBACK + _SHORT_FALLBACK, {'cardstorage': {'uber.foo.uber'}}),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_COMPLEX_PATTERNS_STATS])
async def test_fallback_service_complex_patterns(
        taxi_statistics,
        now,
        taxi_config,
        fallback_descriptions,
        expected_fallbacks,
):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {'service': 'cardstorage', 'fallbacks': fallback_descriptions},
        ],
    )
    for service, expected_service_fallbacks in expected_fallbacks.items():
        response = await taxi_statistics.get(
            '/v1/service/health/',
            params={'service': service},
            headers={'Date': f'{now.isoformat()}Z'},
        )
        assert response.status_code == 200
        response = response.json()
        # No 'total' metric specified for 'uber.bar' for fallback '{1}.{2}'
        assert set(response['fallbacks']) == expected_service_fallbacks


_RESOURCE_LAUNCH_STATS = f"""
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('{SOME_TIME_AGO.isoformat()}Z', 'api-proxy',
    'resource.taxi-3.0-launch.success', 20),
('{SOME_TIME_AGO.isoformat()}Z', 'api-proxy',
    'resource.taxi-3.0-launch.error.http.502', 15),
('{SOME_TIME_AGO.isoformat()}Z', 'api-proxy',
    'resource.taxi-3.0-launch.error.timeout', 15)
"""


@pytest.mark.parametrize(
    'fallback_name,num_records,expected_fallbacks',
    [
        (
            'resource.taxi-3_0-launch.fallback',
            1,
            {'resource.taxi-3_0-launch.fallback'},
        ),
        ('resource.taxi-3_0-launch.{1}.fallback', 0, set()),
    ],
)
@pytest.mark.now(REAL_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_RESOURCE_LAUNCH_STATS])
async def test_fallback_service_real_config(
        taxi_statistics,
        now,
        taxi_config,
        pgsql,
        fallback_name,
        num_records,
        expected_fallbacks,
):
    """
    In case of 'resource.taxi-3_0-launch.{1}.fallback' metrics for 'http.502'
    and 'timeout' do not merge, so there are not enough errors to overcome
    threshold. 'success' metric does not count either, so there are
    not enough total events to enable fallback.
    """
    resource_launch_fallback = {
        'critical_time': 300,
        'errors': [
            'resource.taxi-3.0-launch.error.(http.5[0-9]+|timeout|tech)',
        ],
        'interval': 60,
        'min_events': 25,
        'name': fallback_name,
        'threshold': 10,
        'totals': [
            'resource.taxi-3.0-launch.error.(http.5[0-9]+|timeout|tech)',
            'resource.taxi-3.0-launch.success',
        ],
    }
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {'service': 'api-proxy', 'fallbacks': [resource_launch_fallback]},
        ],
    )
    response = await taxi_statistics.get(
        '/v1/service/health/',
        params={'service': 'api-proxy'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    await taxi_statistics.invalidate_caches()
    cursor = pgsql['statistics'].cursor()
    cursor.execute('SELECT * FROM statistics.fallbacks')
    result_list = list(row for row in cursor)
    assert set(response['fallbacks']) == expected_fallbacks
    assert len(result_list) == num_records


_SINGLE_FALLBACK = {
    'errors': ['card.lpm.error'],
    'interval': 120,
    'min_events': 0,
    'name': 'card.lpm',
    'threshold': 3,
    'totals': ['card.lpm.total'],
}

_PATTERN_FALLBACK = {
    'errors': ['(.*).error'],
    'interval': 120,
    'min_events': 0,
    'name': '{1}',
    'threshold': 1,
    'totals': ['(.*).total'],
}


@pytest.mark.parametrize(
    'fallbacks,expected_fallbacks',
    [
        ([_SINGLE_FALLBACK, _PATTERN_FALLBACK], {'uber.lpm'}),
        ([_PATTERN_FALLBACK, _SINGLE_FALLBACK], {'card.lpm', 'uber.lpm'}),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_PATTERNS_STATS])
async def test_fallback_combined_with_patterns(
        taxi_statistics, now, taxi_config, fallbacks, expected_fallbacks,
):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {'service': 'cardstorage', 'fallbacks': fallbacks},
        ],
    )
    response = await taxi_statistics.get(
        '/v1/service/health/',
        params={'service': 'cardstorage'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    assert set(response['fallbacks']) == expected_fallbacks


_FALLBACK_OLD_STATS = f"""
INSERT INTO statistics.fallbacks (service, fallback_name, created,
                                  due, error, total)
VALUES
('cardstorage', 'card.lpm', '2019-8-2 11:52:10+0000',
'2019-8-2 11:52:11+0000', 1, 100),
('cardstorage', 'uber.lpm', '2019-8-2 11:52:10+0000',
'2019-8-2 11:52:11+0000', 1, 100)
"""

_FALLBACK_FRESH_STATS = f"""
INSERT INTO statistics.fallbacks (service, fallback_name, created,
                                  due, error, total)
VALUES
('cardstorage', 'card.lpm', '2019-8-2 11:52:10+0000',
'{SOME_TIME_SOON.isoformat()}Z', 1, 100),
('cardstorage', 'uber.lpm', '2019-8-2 11:52:10+0000',
'{SOME_TIME_SOON.isoformat()}Z', 1, 100)
"""

_SINGLE_CRIT_TIME_FALLBACK = {
    'errors': ['card.lpm.error'],
    'interval': 120,
    'critical_time': 1000000000,
    'min_events': 0,
    'name': 'card.lpm',
    'threshold': 3,
    'totals': ['card.lpm.total'],
}

_PATTERN_CRIT_TIME_FALLBACK = {
    'errors': ['(.*).error'],
    'interval': 120,
    'critical_time': 1000000000,
    'min_events': 0,
    'name': '{1}',
    'threshold': 1,
    'totals': ['(.*).total'],
}


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_FALLBACK_OLD_STATS])
async def test_outdated_fallbacks(taxi_statistics, now, taxi_config):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {
                'service': 'cardstorage',
                'fallbacks': [
                    _SINGLE_CRIT_TIME_FALLBACK,
                    _PATTERN_CRIT_TIME_FALLBACK,
                ],
            },
        ],
    )
    response = await taxi_statistics.get(
        '/v1/service/health/',
        params={'service': 'cardstorage'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    assert set(response['fallbacks']) == set()


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_FALLBACK_FRESH_STATS])
async def test_fresh_fallbacks(taxi_statistics, now, taxi_config):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {
                'service': 'cardstorage',
                'fallbacks': [
                    _PATTERN_CRIT_TIME_FALLBACK,
                    _SINGLE_CRIT_TIME_FALLBACK,
                ],
            },
        ],
    )
    response = await taxi_statistics.get(
        '/v1/service/health/',
        params={'service': 'cardstorage'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    assert set(response['fallbacks']) == {'card.lpm', 'uber.lpm'}


_RECENT_PATTERNS_STATS = f"""
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('{SOME_TIME_AGO.isoformat()}Z', 'cardstorage', 'card.lpm.error', 2),
('{SOME_TIME_AGO.isoformat()}Z', 'cardstorage', 'card.lpm.total', 100),

('{SOME_TIME_AGO.isoformat()}Z', 'cardstorage', 'uber.lpm.error', 1),
('{SOME_TIME_AGO.isoformat()}Z', 'cardstorage', 'uber.lpm.total', 100),

('{SOME_TIME_AGO.isoformat()}Z', 'buffer-dispatch', 'dispatched.error', 1),
('{SOME_TIME_AGO.isoformat()}Z', 'buffer-dispatch', 'dispatched.total', 100)
"""


@pytest.mark.now(REAL_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_RECENT_PATTERNS_STATS])
@pytest.mark.pgsql('statistics', queries=[_FALLBACK_OLD_STATS])
async def test_fallbacks_db_update(taxi_statistics, now, taxi_config, pgsql):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {
                'service': 'cardstorage',
                'fallbacks': [
                    _PATTERN_CRIT_TIME_FALLBACK,
                    _SINGLE_CRIT_TIME_FALLBACK,
                ],
            },
        ],
    )
    await taxi_statistics.invalidate_caches()
    cursor = pgsql['statistics'].cursor()
    cursor.execute('SELECT * FROM statistics.fallbacks')
    result_list = list(row for row in cursor)
    assert len(result_list) == 2
    assert result_list[0][3].replace(tzinfo=None) > REAL_NOW
    assert result_list[1][3].replace(tzinfo=None) > REAL_NOW


@pytest.mark.now(REAL_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_FALLBACK_FRESH_STATS])
async def test_fallbacks_db_error(taxi_statistics, now, taxi_config, pgsql):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {
                'service': 'cardstorage',
                'fallbacks': [
                    _PATTERN_CRIT_TIME_FALLBACK,
                    _SINGLE_CRIT_TIME_FALLBACK,
                ],
            },
        ],
    )
    # Update cache
    await taxi_statistics.invalidate_caches()

    # Remove a column from table to cause en exception in statistics_service
    try:
        pgsql['statistics'].cursor().execute(
            'ALTER TABLE statistics.fallbacks DROP COLUMN created',
        )

        # Try to update cache again without access to DB
        await taxi_statistics.invalidate_caches()

        # Call handler as usual and check result
        response = await taxi_statistics.get(
            '/v1/service/health/',
            params={'service': 'cardstorage'},
            headers={'Date': f'{now.isoformat()}Z'},
        )
        assert response.status_code == 200
        response = response.json()
        assert set(response['fallbacks']) == {'card.lpm', 'uber.lpm'}
    finally:
        pgsql['statistics'].cursor().execute(
            """
            ALTER TABLE statistics.fallbacks ADD COLUMN IF NOT EXISTS
            created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
            """,
        )


_MONRUN_FALLBACK_DESCIPTIONS = [
    {
        'service': 'cardstorage',
        'monrun_alert': True,
        'fallbacks': [
            {
                'name': 'card.lpm',
                'errors': ['card.lpm.error'],
                'totals': ['card.lpm.total'],
                'interval': 30,
                'min_events': 0,
                'threshold': 1.5,
            },
            {
                'name': 'uber.lpm',
                'errors': ['uber.lpm.error'],
                'totals': ['uber.lpm.total'],
                'interval': 30,
                'min_events': 0,
                'threshold': 1,
            },
        ],
    },
    {
        'service': 'buffer-dispatch',
        'fallbacks': [
            {
                'name': 'dispatched',
                'errors': ['dispatched.error'],
                'totals': ['dispatched.total'],
                'interval': 30,
                'min_events': 100,
                'threshold': 2,
            },
        ],
    },
]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_PATTERNS_STATS])
@pytest.mark.config(
    STATISTICS_FALLBACK_DESCRIPTIONS=_MONRUN_FALLBACK_DESCIPTIONS,
)
async def test_monrun_configuration_create(taxi_statistics, taxi_config, load):
    await taxi_statistics.run_periodic_task('monrun-conf-updater/generator')
    conf_path = yatest.common.work_path(
        'taxi-statistics-autogen_service_fallbacks'
        '_5701320dc521426d6ec146f324723fb0e29906af.conf',
    )
    exp_file = load('expected.conf')
    gen_file = load(conf_path)
    assert gen_file == exp_file


_TEST_RATIO_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.lpm.error', 10),
('2019-8-2 11:52:10+0000', 'cardstorage', 'card.lpm.total', 300),

('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.lpm.error', 1),
('2019-8-2 11:52:10+0000', 'cardstorage', 'uber.lpm.total', 100),

('2019-8-2 11:52:10+0000', 'buffer-dispatch', 'dispatched.error', 1),
('2019-8-2 11:52:10+0000', 'buffer-dispatch', 'dispatched.total', 100)
"""


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_TEST_RATIO_STATS])
@pytest.mark.config(
    STATISTICS_FALLBACK_DESCRIPTIONS=_MONRUN_FALLBACK_DESCIPTIONS,
)
async def test_monrun_fallback_status(
        taxi_statistics, taxi_statistics_monitor, now,
):
    unexisted = (
        '/service/monrun/fallback-status?service=i-do-not-exist',
        '0; OK: None',
    )
    cardstorage = (
        '/service/monrun/fallback-status?service=cardstorage',
        '2; CRIT: card.lpm: 3.3% (10 / 300), uber.lpm: 1.0% (1 / 100)',
    )
    buffer_dispatch = (
        '/service/monrun/fallback-status?service=buffer-dispatch',
        '0; OK: dispatched: 1.0% (1 / 100)',
    )

    async def request(params):
        resp = await taxi_statistics_monitor.get(params[0])
        assert resp.status_code == 200
        assert resp.text.strip() == params[1]

    await taxi_statistics.run_periodic_task('monrun-conf-updater/generator')
    await request(unexisted)
    await request(cardstorage)
    await request(buffer_dispatch)


_REUSE_PATTERN_METRICS_STATS = """
INSERT INTO statistics.metrics (time_bucket, service, metric_name, count)
VALUES
('2019-8-2 11:52:10+0000', 'driver_assign', 'buffer.msk.delayed', 3),
('2019-8-2 11:52:10+0000', 'driver_assign', 'buffer.msk.conflict', 7),
('2019-8-2 11:52:10+0000', 'driver_assign', 'buffer.msk.total', 100),

('2019-8-2 11:52:10+0000', 'driver_assign', 'buffer.spb.delayed', 1),
('2019-8-2 11:52:10+0000', 'driver_assign', 'buffer.spb.conflict', 15),
('2019-8-2 11:52:10+0000', 'driver_assign', 'buffer.spb.total', 100)
"""

_MATCHING_GROUPS_FALLBACK_DESCRIPTIONS = [
    {
        'service': 'driver_assign',
        'fallbacks': [
            {
                'name': 'buffer.{1}.fallback_delay',
                'matching_group': 'delay',
                'errors': [r'buffer\.(.*)\.delayed'],
                'totals': [r'buffer\.(.*)\.delayed', r'buffer\.(.*)\.total'],
                'interval': 30,
                'min_events': 50,
                'threshold': 2,
            },
            {
                'name': 'buffer.{1}.fallback_conflict',
                'matching_group': 'conflict',
                'errors': [r'buffer\.(.*)\.conflict'],
                'totals': [r'buffer\.(.*)\.conflict', r'buffer\.(.*)\.total'],
                'interval': 30,
                'min_events': 50,
                'threshold': 10,
            },
        ],
    },
]


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_REUSE_PATTERN_METRICS_STATS])
@pytest.mark.config(
    STATISTICS_FALLBACK_DESCRIPTIONS=_MATCHING_GROUPS_FALLBACK_DESCRIPTIONS,
)
async def test_metrics_reuse_in_fallbacks(taxi_statistics, now):
    response = await taxi_statistics.get(
        '/v1/service/health/',
        params={'service': 'driver_assign'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    assert set(response['fallbacks']) == {
        'buffer.msk.fallback_delay',
        'buffer.spb.fallback_conflict',
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('statistics', queries=[_DEFAULT_STATS])
async def test_broken_metric_name(taxi_statistics, now, taxi_config):
    taxi_config.set(
        STATISTICS_FALLBACK_DESCRIPTIONS=[
            {
                'service': 'cardstorage',
                'fallbacks': [
                    {
                        'name': 'uber-lpm',
                        'errors': ['uber.lpm.error'],
                        'totals': ['uber.lpm.error', 'uber.lpm.success'],
                        'interval': 20,
                        'min_events': 100,
                        'threshold': 5,
                    },
                ],
            },
            {
                'service': '.*',
                'fallbacks': [
                    {
                        'critical_time': 60,
                        'errors': ['handler.(.*).error'],
                        'interval': 60,
                        'min_events': 180,
                        'name': 'handler.{1}.fallback',
                        'threshold': 10,
                        'totals': [
                            'handler.(.*).error',
                            'handler.(.*).success',
                        ],
                    },
                ],
            },
        ],
    )

    await taxi_statistics.post(
        'v1/metrics/store',
        json={
            'service': 'test-service',
            'time_bucket': '2019-08-02T11:52:10+0000',
            'metrics': [
                {'name': 'metric_name_with_broken_reference\\1', 'value': 0},
            ],
        },
    )

    response = await taxi_statistics.get(
        'v1/service/health',
        params={'service': 'cardstorage'},
        headers={'Date': f'{now.isoformat()}Z'},
    )
    assert response.status_code == 200
    response = response.json()
    assert set(response['fallbacks']) == {'uber-lpm'}
