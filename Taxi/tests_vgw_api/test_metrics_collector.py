import logging
import typing

import pytest

from testsuite.utils import callinfo

logger = logging.getLogger(__name__)


def _check_stats(stats: typing.Dict, expected_stats: typing.Dict):
    for stat_key, expected_value in expected_stats.items():
        keys = stat_key.split('.')
        value = stats['vgw']
        for key in keys:
            value = value[key]
        logger.info('Checking stat path %s', stat_key)
        assert value == expected_value
        logger.info('ok')


@pytest.mark.config(
    VGW_API_METRICS_COLLECTOR_SETTINGS={
        'enabled': True,
        'work_period_sec': 60,
        'metrics_period_sec': 900,
    },
)
@pytest.mark.now('2018-02-28T19:20:00+0300')
async def test_metrics(
        taxi_vgw_api, taxi_vgw_api_monitor, mockserver, testpoint,
):
    @mockserver.json_handler('/redirections')
    def _mock_redirections(request):
        return [
            {'id': '1', 'phone': '+75557775522', 'ext': '007'},
            {'id': '2', 'phone': '+75557775522', 'ext': '008'},
            {'id': '3', 'phone': '+75557775522', 'ext': '009'},
        ]

    @testpoint('metrics-collector/finished')
    def finished(data):
        return

    async with taxi_vgw_api.spawn_task('distlock/update-metrics'):
        await finished.wait_call()

    expected_stats = {
        'gateway.gateway_id_1.enabled.too many errors': 1,
        'gateway.gateway_id_1.enabled.$meta.solomon_children_labels': (
            'disable_reason'
        ),
        'gateway.gateway_id_2.enabled.too many errors': 0,
        'gateway.gateway_id_2.enabled.$meta.solomon_children_labels': (
            'disable_reason'
        ),
        'gateway.gateway_id_3.enabled': 1,
        'forwardings.used.gateway.gateway_id_1': 1,
        'forwardings.used.gateway.gateway_id_2': 2,
        'forwardings.active.gateway.gateway_id_1': 3,
        'forwardings.active.gateway.gateway_id_3': 3,
        'forwardings.used.type.passenger_to_driver': 1,
        'forwardings.used.type.driver_to_passenger': 2,
        'talks.length.avg.gateway.gateway_id_1.region.1': 25,
        'talks.length.avg.gateway.gateway_id_2.region.2': 20,
        'talks.length.avg.gateway.gateway_id_2.region.0': 50,
        'talks.total.type.passenger_to_driver': 1,
        'talks.total.type.driver_to_passenger': 5,
        'talks.length.avg.type.passenger_to_driver': 20,
        'talks.length.avg.type.driver_to_passenger': 30,
        'talks.download_delay.max.gateway.gateway_id_1': 288,
    }
    stats = await taxi_vgw_api_monitor.get_metrics('vgw')
    _check_stats(stats, expected_stats)


@pytest.mark.config(
    VGW_API_METRICS_COLLECTOR_SETTINGS={
        'enabled': False,
        'work_period_sec': 60,
        'metrics_period_sec': 900,
    },
)
@pytest.mark.now('2018-02-28T19:20:00+0300')
async def test_disabled(taxi_vgw_api, taxi_vgw_api_monitor, testpoint):
    @testpoint('metrics-collector/finished')
    def finished(data):
        return

    async with taxi_vgw_api.spawn_task('distlock/update-metrics'):
        with pytest.raises(callinfo.CallQueueTimeoutError):
            await finished.wait_call(timeout=0.5)

    stats = await taxi_vgw_api_monitor.get_metrics('vgw')
    for prefix in ['forwardings', 'talks']:
        assert prefix not in stats['vgw']
