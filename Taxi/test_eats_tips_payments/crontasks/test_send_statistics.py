# pylint: disable = invalid-name
import typing

import pytest

from eats_tips_payments.generated.cron import run_cron


def sorting_dict_condition(item):
    return (
        item['labels']['sensor'],
        item['value'],
        item['labels'].get('payment_type', ''),
        item['labels'].get('transaction_status', ''),
        item['labels'].get('stats_source', ''),
    )


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


def _get_sensor_plus_response(
        value: float, status: str, sensor: str = 'cron_plus_invoices_stats',
):
    return _get_sensor_base_response(
        value=value, labels={'sensor': sensor, 'status': status},
    )


def _get_sensor_plus_cfg_response(
        value: float, metric: str, action: str,
) -> typing.Dict:
    return _get_sensor_base_response(
        value=value,
        labels={
            'sensor': 'cron_plus_invoices_stats_threshold',
            'metric': metric,
            'action': action,
        },
    )


def _get_sensor_transactions_response(
        value: float,
        payment_type: str,
        transaction_status: str,
        stats_source: str,
) -> typing.Dict:
    return _get_sensor_base_response(
        value=value,
        labels={
            'payment_type': payment_type,
            'sensor': 'cron_transactions_stats',
            'transaction_status': transaction_status,
            'stats_source': stats_source,
        },
    )


def _get_sensor_transactions_cfg_response(
        value: float, payment_type: str, threshold_type: str,
) -> typing.Dict:
    return _get_sensor_base_response(
        value=value,
        labels={
            'payment_type': payment_type,
            'sensor': 'cron_transactions_stats_config',
            'threshold_type': threshold_type,
        },
    )


def _get_sensor_base_response(
        value: float, labels: typing.Dict,
) -> typing.Dict:
    return {'value': value, 'labels': labels}


THRESHOLDS_CFG = {'failed_invoices': {'alarm': 10, 'warn': 5}}
CFG_RESPONSE = [
    _get_sensor_plus_cfg_response(10.0, 'failed_invoices', 'alarm'),
    _get_sensor_plus_cfg_response(5.0, 'failed_invoices', 'warn'),
]


@pytest.mark.config(
    EATS_TIPS_PAYMENTS_CRON_TRANSACTIONS_STATS={
        'time_window': 120,
        'payments_thresholds': [
            {'payment_type': 'apple', 'total': 0, 'fail': 1, 'success': 1},
            {'payment_type': 'google', 'total': 2, 'fail': 3, 'success': 1},
            {'payment_type': 'yandex', 'total': 6, 'fail': 7, 'success': 1},
            {'payment_type': 'card', 'total': 8, 'fail': 9, 'success': 1},
        ],
    },
)
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.now('1970-01-01 03:04:01+03:00')
async def test_get_payments_transactions_stats(patch, mock_stats):
    @patch(
        'eats_tips_payments.crontasks.send_statistics'
        '.make_plus_invoices_stats',
    )
    async def _make_plus_invoices_stats(context):
        return

    await run_cron.main(
        ['eats_tips_payments.crontasks.send_statistics', '-t', '0'],
    )

    result = sorted(
        [sensor_to_dict(x) for sensors in mock_stats for x in sensors],
        key=sorting_dict_condition,
    )
    assert result == sorted(
        [
            _get_sensor_transactions_response(1.0, 'apple', 'failed', 'mysql'),
            _get_sensor_transactions_response(
                1.0, 'apple', 'succeeded', 'mysql',
            ),
            _get_sensor_transactions_response(
                2.0, 'apple', 'registered', 'mysql',
            ),
            _get_sensor_transactions_response(
                0.0, 'apple', 'on_half_path', 'mysql',
            ),
            _get_sensor_transactions_response(
                2.0, 'google', 'failed', 'mysql',
            ),
            _get_sensor_transactions_response(
                1.0, 'google', 'succeeded', 'mysql',
            ),
            _get_sensor_transactions_response(
                0.0, 'google', 'registered', 'mysql',
            ),
            _get_sensor_transactions_response(
                2.0, 'google', 'on_half_path', 'mysql',
            ),
            _get_sensor_transactions_response(
                0.0, 'yandex', 'failed', 'mysql',
            ),
            _get_sensor_transactions_response(
                0.0, 'yandex', 'succeeded', 'mysql',
            ),
            _get_sensor_transactions_response(
                0.0, 'yandex', 'registered', 'mysql',
            ),
            _get_sensor_transactions_response(
                0.0, 'yandex', 'on_half_path', 'mysql',
            ),
            _get_sensor_transactions_response(1.0, 'card', 'failed', 'mysql'),
            _get_sensor_transactions_response(
                1.0, 'card', 'succeeded', 'mysql',
            ),
            _get_sensor_transactions_response(
                1.0, 'card', 'registered', 'mysql',
            ),
            _get_sensor_transactions_response(
                1.0, 'card', 'on_half_path', 'mysql',
            ),
            _get_sensor_transactions_response(1.0, 'apple', 'failed', 'pg'),
            _get_sensor_transactions_response(2.0, 'apple', 'succeeded', 'pg'),
            _get_sensor_transactions_response(
                1.0, 'apple', 'registered', 'pg',
            ),
            _get_sensor_transactions_response(
                1.0, 'apple', 'on_half_path', 'pg',
            ),
            _get_sensor_transactions_response(1.0, 'google', 'failed', 'pg'),
            _get_sensor_transactions_response(
                1.0, 'google', 'succeeded', 'pg',
            ),
            _get_sensor_transactions_response(
                2.0, 'google', 'registered', 'pg',
            ),
            _get_sensor_transactions_response(
                1.0, 'google', 'on_half_path', 'pg',
            ),
            _get_sensor_transactions_response(2.0, 'yandex', 'failed', 'pg'),
            _get_sensor_transactions_response(
                1.0, 'yandex', 'succeeded', 'pg',
            ),
            _get_sensor_transactions_response(
                1.0, 'yandex', 'registered', 'pg',
            ),
            _get_sensor_transactions_response(
                1.0, 'yandex', 'on_half_path', 'pg',
            ),
            _get_sensor_transactions_response(1.0, 'card', 'failed', 'pg'),
            _get_sensor_transactions_response(1.0, 'card', 'succeeded', 'pg'),
            _get_sensor_transactions_response(1.0, 'card', 'registered', 'pg'),
            _get_sensor_transactions_response(
                2.0, 'card', 'on_half_path', 'pg',
            ),
            _get_sensor_base_response(
                120.0,
                {
                    'sensor': 'cron_transactions_stats',
                    'setting_type': 'time_window',
                },
            ),
            _get_sensor_transactions_cfg_response(0.0, 'apple', 'total'),
            _get_sensor_transactions_cfg_response(1.0, 'apple', 'fail'),
            _get_sensor_transactions_cfg_response(1.0, 'apple', 'success'),
            _get_sensor_transactions_cfg_response(2.0, 'google', 'total'),
            _get_sensor_transactions_cfg_response(3.0, 'google', 'fail'),
            _get_sensor_transactions_cfg_response(1.0, 'google', 'success'),
            _get_sensor_transactions_cfg_response(6.0, 'yandex', 'total'),
            _get_sensor_transactions_cfg_response(7.0, 'yandex', 'fail'),
            _get_sensor_transactions_cfg_response(1.0, 'yandex', 'success'),
            _get_sensor_transactions_cfg_response(8.0, 'card', 'total'),
            _get_sensor_transactions_cfg_response(9.0, 'card', 'fail'),
            _get_sensor_transactions_cfg_response(1.0, 'card', 'success'),
            _get_sensor_base_response(
                3.0,
                {
                    'sensor': 'cron_event_log_stats',
                    'stats_type': 'error_count',
                },
            ),
        ],
        key=sorting_dict_condition,
    )


@pytest.mark.parametrize(
    'time_window, expected_result',
    (
        (
            600,
            [
                _get_sensor_plus_response(2.0, 'in-progress'),
                _get_sensor_plus_response(2.0, 'failed'),
                _get_sensor_plus_response(3.0, 'success'),
                _get_sensor_plus_response(1.0, 'None'),
                *CFG_RESPONSE,
            ],
        ),
        (
            1200,
            [
                _get_sensor_plus_response(3.0, 'in-progress'),
                _get_sensor_plus_response(2.0, 'failed'),
                _get_sensor_plus_response(5.0, 'success'),
                _get_sensor_plus_response(1.0, 'None'),
                *CFG_RESPONSE,
            ],
        ),
        (
            60,
            [
                _get_sensor_plus_response(0.0, 'in-progress'),
                _get_sensor_plus_response(0.0, 'failed'),
                _get_sensor_plus_response(0.0, 'success'),
                *CFG_RESPONSE,
            ],
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_get_plus_invoices_stats(
        patch, mock_stats, taxi_config, time_window, expected_result,
):
    @patch(
        'eats_tips_payments.crontasks.send_statistics.make_transactions_stats',
    )
    async def _make_transactions_stats(
            config_settings, context, current_timestamp, utc_time,
    ):
        return

    taxi_config.set_values(
        {
            'EATS_TIPS_PAYMENTS_CRON_PLUS_STATS': {
                'time_window': time_window,
                'thresholds': THRESHOLDS_CFG,
            },
        },
    )
    await run_cron.main(
        ['eats_tips_payments.crontasks.send_statistics', '-t', '0'],
    )
    result = [sensor_to_dict(x) for senors in mock_stats for x in senors]
    assert result == expected_result
