# pylint: disable=redefined-outer-name
from order_route_sharing.generated.cron import run_cron

EXPECTED_SENSORS = [
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'android',
            'is_shown': 'True',
            'is_user_exists': 'True',
            'sensor': 'active_shared_orders',
            'tariff_class': 'econom',
        },
        'value': 2,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'android',
            'is_shown': 'False',
            'is_user_exists': 'False',
            'sensor': 'active_shared_orders',
            'tariff_class': 'express',
        },
        'value': 1,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'call_center',
            'is_shown': 'False',
            'is_user_exists': 'False',
            'sensor': 'active_shared_orders',
            'tariff_class': 'express',
        },
        'value': 2,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'None',
            'is_shown': 'False',
            'is_user_exists': 'False',
            'sensor': 'active_shared_orders',
            'tariff_class': 'None',
        },
        'value': 1,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'android',
            'sensor': 'active_orders',
            'tariff_class': 'econom',
        },
        'value': 1,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'android',
            'sensor': 'active_orders',
            'tariff_class': 'express',
        },
        'value': 1,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'call_center',
            'sensor': 'active_orders',
            'tariff_class': 'express',
        },
        'value': 2,
    },
    {
        'kind': 'IGAUGE',
        'labels': {
            'application': 'order_route_sharing_cron',
            'taxi_application': 'None',
            'sensor': 'active_orders',
            'tariff_class': 'None',
        },
        'value': 1,
    },
]


async def test_send_metrics(pgsql, mockserver):
    @mockserver.json_handler('/solomon/')
    def _mock_solomon(request):
        sensors = request.json['sensors']
        assert len(sensors) == len(EXPECTED_SENSORS)
        for sensor in request.json['sensors']:
            assert sensor in EXPECTED_SENSORS
        return {}

    await run_cron.main(
        ['order_route_sharing.crontasks.send_metrics', '-t', '0'],
    )
