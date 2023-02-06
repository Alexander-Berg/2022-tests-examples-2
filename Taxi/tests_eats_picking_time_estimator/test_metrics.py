import collections

import pytest

from tests_eats_picking_time_estimator import utils


def settings():
    return {
        'min_estimated_time_seconds': 1200,
        'max_estimated_time_seconds': 1300,
    }


@pytest.mark.config(EATS_PICKING_TIME_ESTIMATOR_CONFIDENCE_INTERVAL=settings())
@utils.picking_formula()
@pytest.mark.parametrize(
    'request_file, expected_metrics',
    [
        ['eta_too_low_request.json', {'too_low': 1, 'too_high': 0}],
        ['eta_normal_request.json', {'too_low': 0, 'too_high': 0}],
        ['eta_too_high_request.json', {'too_low': 0, 'too_high': 1}],
    ],
)
async def test_metrics(
        load_order,
        taxi_eats_picking_time_estimator,
        taxi_eats_picking_time_estimator_monitor,
        request_file,
        expected_metrics,
):
    async def _action():
        response = await taxi_eats_picking_time_estimator.post(
            'api/v1/order/estimate', load_order(request_file),
        )
        assert response.status_code == 200

    await check_metrics(
        taxi_eats_picking_time_estimator_monitor, expected_metrics, _action,
    )


async def check_metrics(
        taxi_eats_picking_time_estimator_monitor, expected_metrics, action,
):
    async def _get_metrics(monitor):
        return collections.Counter(
            (await monitor.get_metrics())['estimated_time'],
        )

    metrics_before = await _get_metrics(
        taxi_eats_picking_time_estimator_monitor,
    )
    await action()
    metrics = await _get_metrics(taxi_eats_picking_time_estimator_monitor)
    metrics.subtract(metrics_before)
    assert metrics == expected_metrics
