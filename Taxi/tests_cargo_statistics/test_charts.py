import pytest


def make_pct(p00, p25, p50, p75, p90, p95, p99, p99_9, p100):
    return {
        'p0': p00,
        'p25': p25,
        'p50': p50,
        'p75': p75,
        'p90': p90,
        'p95': p95,
        'p99': p99,
        'p99_9': p99_9,
        'p100': p100,
        '$meta': {'solomon_children_labels': 'percentile'},
    }


def check_children_labels(stats, label):
    assert stats['$meta'] == {'solomon_children_labels': label}


@pytest.mark.now('2020-01-01T12:00:00+00:00')
@pytest.mark.suspend_periodic_tasks('chart-builder-periodic')
@pytest.mark.config(
    CARGO_STATISTICS_CHARTS_SETTINGS={
        'groups_settings': {
            '__default__': {
                'enabled': True,
                'range': 1e6,
                'thresholds': {'long_cancel': 10},
            },
        },
        'period': 55,
        'throttle_between_groups_ms': 500,
        'stats_ttl': 55,
    },
    CARGO_STATISTICS_SENSORS_WHITELIST=[
        {'zone_id': 'moscow', 'corp_client_id': 'corp_client_id_1'},
        {'zone_id': 'moscow', 'corp_client_id': '__total__'},
        {'zone_id': 'spb', 'corp_client_id': 'corp_client_id_1'},
        {'zone_id': 'spb', 'corp_client_id': '__total__'},
        {'zone_id': '__total__', 'corp_client_id': 'corp_client_id_1'},
        {'zone_id': '__total__', 'corp_client_id': '__total__'},
        {'zone_id': '__unknown__', 'corp_client_id': '__unknown__'},
    ],
)
async def test_cargo_claims_claims(
        load_events,
        taxi_cargo_statistics,
        taxi_cargo_statistics_monitor,
        cargo_claims_claims,
):
    await load_events()

    await taxi_cargo_statistics.run_periodic_task('chart-builder-periodic')
    stats = await taxi_cargo_statistics_monitor.get_metric('charts')
    check_children_labels(stats, 'event_group')

    stats['claims']['zone_corp'].pop('__total__')
    for zone_stats in stats['claims']['zone_corp'].values():
        zone_stats.pop('__total__', None)

    stats['claims']['zone_corp_router'].pop('__total__')
    for zone, zone_stats in stats['claims']['zone_corp_router'].items():
        if zone == '$meta':
            continue
        zone_stats.pop('__total__', None)
        for key, corp_stats in zone_stats.items():
            if key == '$meta':
                continue
            router_ids = [
                k for k in corp_stats.keys() if k not in ['__total__', '$meta']
            ]
            for router_id in router_ids:
                corp_stats.pop(router_id)

    assert stats['claims']['zone_corp_router'] == {
        '$meta': {'solomon_children_labels': 'zone_id'},
        'moscow': {
            '$meta': {'solomon_children_labels': 'corp_client_id'},
            'corp_client_id_1': {
                '$meta': {'solomon_children_labels': 'router_id'},
                '__total__': {
                    'long_cancelled': 1,
                    'not_found': 0,
                    'total': 2,
                    'performers_count': 1.5,
                },
            },
        },
        'spb': {
            '$meta': {'solomon_children_labels': 'corp_client_id'},
            'corp_client_id_1': {
                '$meta': {'solomon_children_labels': 'router_id'},
                '__total__': {
                    'long_cancelled': 1,
                    'not_found': 0,
                    'total': 1,
                    'performers_count': 0,
                },
            },
        },
        '__unknown__': {
            '$meta': {'solomon_children_labels': 'corp_client_id'},
            '__unknown__': {
                '$meta': {'solomon_children_labels': 'router_id'},
                '__total__': {
                    'long_cancelled': 0,
                    'not_found': 0,
                    'total': 1,
                    'performers_count': 0,
                },
            },
        },
    }

    assert stats['claims']['zone_corp'] == {
        '$meta': {'solomon_children_labels': 'zone_id'},
        'moscow': {
            '$meta': {'solomon_children_labels': 'corp_client_id'},
            'corp_client_id_1': {
                # 120, 1200
                'arrival_time': make_pct(
                    600, 600, 900, 900, 900, 900, 900, 900, 900,
                ),
                'cancelled': 1,
                'completion_time': make_pct(
                    4200, 4200, 4200, 4200, 4200, 4200, 4200, 4200, 4200,
                ),
                'resolved': 2,
                'search_time': make_pct(
                    1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800, 1800,
                ),
                'total': 2,
            },
        },
        'spb': {
            '$meta': {'solomon_children_labels': 'corp_client_id'},
            'corp_client_id_1': {
                'arrival_time': make_pct(0, 0, 0, 0, 0, 0, 0, 0, 0),
                'cancelled': 1,
                'completion_time': make_pct(
                    300, 300, 300, 300, 300, 300, 300, 300, 300,
                ),
                'resolved': 1,
                'search_time': make_pct(0, 0, 0, 0, 0, 0, 0, 0, 0),
                'total': 1,
            },
        },
        '__unknown__': {
            '$meta': {'solomon_children_labels': 'corp_client_id'},
            '__unknown__': {
                'arrival_time': make_pct(0, 0, 0, 0, 0, 0, 0, 0, 0),
                'cancelled': 0,
                'completion_time': make_pct(0, 0, 0, 0, 0, 0, 0, 0, 0),
                'resolved': 0,
                'search_time': make_pct(0, 0, 0, 0, 0, 0, 0, 0, 0),
                'total': 1,
            },
        },
    }


@pytest.mark.now('2020-01-01T12:00:00+00:00')
@pytest.mark.suspend_periodic_tasks('chart-builder-periodic')
@pytest.mark.config(
    CARGO_STATISTICS_CHARTS_SETTINGS={
        'groups_settings': {
            '__default__': {
                'enabled': True,
                'range': 1e6,
                'thresholds': {'long_cancel': 10},
            },
        },
        'period': 55,
        'throttle_between_groups_ms': 500,
        'stats_ttl': 55,
    },
)
async def test_charts_ok(
        load_events,
        taxi_cargo_statistics,
        taxi_cargo_statistics_monitor,
        cargo_claims_claims,
):
    """
        Validate SQL queries/mappings etc.
    """
    await load_events()

    await taxi_cargo_statistics.run_periodic_task('chart-builder-periodic')
    stats = await taxi_cargo_statistics_monitor.get_metric('charts')
    check_children_labels(stats, 'event_group')

    assert set(stats.keys()) == {
        '$meta',
        'claims',
        'dispatch_segments',
        'orders',
    }
