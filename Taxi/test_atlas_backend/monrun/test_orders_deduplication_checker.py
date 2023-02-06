import json

import pytest

from atlas_backend.generated.cron import run_monrun
from atlas_backend.generated.service.swagger.models import api

MODULE = 'atlas_backend.monrun.orders_deduplication_checker'


@pytest.mark.now('2022-04-08 10:09:00')
@pytest.mark.config(
    ATLAS_BACKEND_METRICS_FOR_COMPARISON=[
        {
            'metric': 'flink_order',
            'metric_for_comparison': 'requests_volume',
            'warn_threshold_in_difference': 0,
            'crit_threshold_in_difference': 0,
            'warn_threshold_in_frame': 5,
            'crit_threshold_in_frame': 10,
            'monrun_check': 'orders-deduplication-checker',
            'is_active': True,
        },
    ],
)
async def test_orders_deduplication_checker_with_normal_status(
        patch, open_file,
) -> None:
    @patch('atlas_backend.internal.metrics.report_utils.get_plot_data')
    # pylint: disable=W0612
    async def get_plot_data(
            request_params: api.PlotRequestParameters, *args, **kwargs,
    ):
        file_name = f'{request_params.metric}_plot_data.json'
        try:
            with open_file(file_name) as file_:
                return json.load(file_)
        except FileNotFoundError:
            return []

    result = await run_monrun.run(
        [MODULE, '--start-date-window', '10', '--end-date-window', '4'],
    )
    assert result == '0; OK'


@pytest.mark.now('2022-04-08 10:09:00')
@pytest.mark.config(
    ATLAS_BACKEND_METRICS_FOR_COMPARISON=[
        {
            'metric': 'flink_order',
            'metric_for_comparison': 'requests_volume',
            'warn_threshold_in_difference': 0,
            'crit_threshold_in_difference': 0,
            'warn_threshold_in_frame': 2,
            'crit_threshold_in_frame': 3,
            'monrun_check': 'orders-deduplication-checker',
            'is_active': True,
        },
    ],
)
async def test_orders_deduplication_checker_with_alert_statuses(
        patch, open_file,
) -> None:
    @patch('atlas_backend.internal.metrics.report_utils.get_plot_data')
    # pylint: disable=W0612
    async def get_plot_data(
            request_params: api.PlotRequestParameters, *args, **kwargs,
    ):
        file_name = f'{request_params.metric}_plot_data.json'
        try:
            with open_file(file_name) as file_:
                return json.load(file_)
        except FileNotFoundError:
            return []

    result = await run_monrun.run(
        [MODULE, '--start-date-window', '10', '--end-date-window', '4'],
    )
    assert result == (
        '2; Plot data do not match for metrics: '
        '(flink_order, requests_volume): '
        'WARN detected from 2022-04-08 10:01:00 to 2022-04-08 10:03:00; '
        'CRIT detected from 2022-04-08 10:06:00 to 2022-04-08 10:09:00; '
    )
