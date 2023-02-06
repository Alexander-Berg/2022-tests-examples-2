import pytest


@pytest.mark.config(
    MAAS_MONITORING_SETTINGS={
        'monitoring_task_interval_ms': 100,
        'reserved_subscription_thresholds_m': [1, 10, 3500],
    },
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_main(taxi_maas, taxi_maas_monitor):
    await taxi_maas.run_periodic_task('collect_monitoring_stats')

    stats_json = await taxi_maas_monitor.get_metric('subscriptions-manager')

    assert stats_json['canceled']['count'] == 1
    assert stats_json['expired']['count'] == 1
    assert stats_json['active']['count'] == 2
    assert stats_json['reserved']['count'] == 4
    assert stats_json['reserved']['time_thresholds']['1'] == 2
    assert stats_json['reserved']['time_thresholds']['10'] == 1
    assert stats_json['reserved']['time_thresholds']['3500'] == 0
