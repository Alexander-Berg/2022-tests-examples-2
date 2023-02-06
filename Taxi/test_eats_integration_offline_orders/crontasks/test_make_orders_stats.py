import typing

import pytest

from eats_integration_offline_orders.crontasks import make_orders_stats
from eats_integration_offline_orders.generated.cron import run_cron


def sorting_dict_condition(item):
    return (
        item['labels']['stats_type'],
        item['labels']['data_type'],
        item['value'],
    )


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


def _make_stat_response(
        value: float, stats_type: str, data_type: str,
) -> typing.Dict:
    return _make_base_stat_response(
        value=value,
        labels={
            'stats_type': stats_type,
            'data_type': data_type,
            'sensor': make_orders_stats.SENSOR_NAME,
        },
    )


def _make_base_stat_response(value: float, labels: typing.Dict) -> typing.Dict:
    return {'value': value, 'labels': labels}


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'orders.sql', 'payment_transactions.sql'],
)
@pytest.mark.now('2022-05-04T12:30:30.0+03:00')
async def test_make_orders_stats(cron_context, mock_stats):
    await run_cron.main(
        [
            'eats_integration_offline_orders.crontasks.make_orders_stats',
            '-t',
            '0',
        ],
    )
    result = sorted(
        [sensor_to_dict(x) for sensors in mock_stats for x in sensors],
        key=sorting_dict_condition,
    )
    assert result == sorted(
        [
            _make_stat_response(2, 'last_transactions', 'orders'),
            _make_stat_response(
                2, 'last_transactions', 'avg_sum_of_trs_per_order',
            ),
            _make_stat_response(3, 'last_transactions', 'max_trs_per_order'),
            _make_stat_response(4, 'last_transactions', 'failed_transactions'),
            _make_stat_response(2, 'successful_orders', 'orders'),
            _make_stat_response(
                1.5, 'successful_orders', 'avg_sum_of_trs_per_order',
            ),
            _make_stat_response(2, 'successful_orders', 'max_trs_per_order'),
            _make_stat_response(3, 'successful_orders', 'failed_transactions'),
            _make_stat_response(2, 'failed_orders', 'orders'),
            _make_stat_response(
                1.5, 'failed_orders', 'avg_sum_of_trs_per_order',
            ),
            _make_stat_response(2, 'failed_orders', 'max_trs_per_order'),
            _make_stat_response(3, 'failed_orders', 'failed_transactions'),
            _make_stat_response(4, 'total_orders', 'orders'),
            _make_stat_response(
                1.5, 'total_orders', 'avg_sum_of_trs_per_order',
            ),
            _make_stat_response(2, 'total_orders', 'max_trs_per_order'),
            _make_stat_response(6, 'total_orders', 'failed_transactions'),
        ],
        key=sorting_dict_condition,
    )
