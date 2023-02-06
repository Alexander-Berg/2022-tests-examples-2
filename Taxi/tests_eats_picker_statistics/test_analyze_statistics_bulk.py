import datetime

import pytest

from . import utils


@pytest.mark.experiments3(
    filename='config3_eats_picker_statistics_statistics_params.json',
)
@pytest.mark.pgsql('eats_picker_statistics', files=['fill_data.sql'])
@pytest.mark.parametrize(
    'picker_id, metric_name, date_from, date_to, expected_target, '
    'expected_metrics_ids',
    [
        (
            '1',
            'delivery_rate',
            '2021-06-01T00:00:00.000000+10:00',
            '2021-07-01T00:00:00.000000+10:00',
            1,
            [2, 5, 6, 7],
        ),
        (
            '1',
            'delivery_rate',
            '2021-06-20T00:00:00.000000+10:00',
            '2021-06-24T00:00:00.000000+10:00',
            1,
            [2, 5, 6, 7],
        ),
        (
            '1',
            'delivery_rate',
            '2021-06-20T23:59:59.999999+10:00',
            '2021-06-24T23:59:59.999999+10:00',
            1,
            [2, 5, 6, 7],
        ),
        (
            '1',
            'delivery_rate',
            '2021-06-21T00:00:00.000000+10:00',
            '2021-06-24T00:00:00.000000+10:00',
            1,
            [5, 6, 7],
        ),
        (
            '1',
            'delivery_rate',
            '2021-06-22T00:00:00.000000+10:00',
            '2021-06-24T00:00:00.000000+10:00',
            1,
            [6, 7],
        ),
        (
            '1',
            'delivery_rate',
            '2021-06-23T00:00:00.000000+10:00',
            '2021-06-24T00:00:00.000000+10:00',
            1,
            [7],
        ),
        (
            '1',
            'delivery_rate',
            '2021-06-24T00:00:00.000000+10:00',
            '2021-06-24T00:00:00.000000+10:00',
            1,
            [],
        ),
        (
            '1',
            'delivery_rate',
            '2021-05-01T00:00:00.000000+10:00',
            '2021-06-01T00:00:00.000000+10:00',
            1,
            [],
        ),
        (
            '1',
            'picking_duration_per_item',
            '2021-06-01T00:00:00.000000+10:00',
            '2021-07-01T00:00:00.000000+10:00',
            120,
            [3],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-01T00:00:00.000000+03:00',
            '2021-07-01T00:00:00.000000+03:00',
            1,
            [9, 12, 13, 14],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-20T00:00:00.000000+03:00',
            '2021-06-24T00:00:00.000000+03:00',
            1,
            [9, 12, 13, 14],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-20T23:59:59.999999+03:00',
            '2021-06-24T23:59:59.999999+03:00',
            1,
            [9, 12, 13, 14],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-21T00:00:00.000000+03:00',
            '2021-06-24T00:00:00.000000+03:00',
            1,
            [12, 13, 14],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-22T00:00:00.000000+03:00',
            '2021-06-24T00:00:00.000000+03:00',
            1,
            [13, 14],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-23T00:00:00.000000+03:00',
            '2021-06-24T00:00:00.000000+03:00',
            1,
            [14],
        ),
        (
            '2',
            'delivery_rate',
            '2021-06-24T00:00:00.000000+03:00',
            '2021-06-24T00:00:00.000000+03:00',
            1,
            [],
        ),
        (
            '2',
            'delivery_rate',
            '2021-05-01T00:00:00.000000+03:00',
            '2021-06-01T00:00:00.000000+03:00',
            1,
            [],
        ),
        (
            '2',
            'picking_duration_per_item',
            '2021-06-01T00:00:00.000000+03:00',
            '2021-07-01T00:00:00.000000+03:00',
            120,
            [10],
        ),
        (
            '3',
            'complete_orders_count',
            '2021-06-01T00:00:00.000000+03:00',
            '2021-07-01T00:00:00.000000+03:00',
            None,
            [15],
        ),
    ],
)
async def test_analyze_statistics_bulk_200(
        taxi_eats_picker_statistics,
        get_statistics,
        picker_id,
        metric_name,
        date_from,
        date_to,
        expected_target,
        expected_metrics_ids,
):
    interval = 'day'
    response = await taxi_eats_picker_statistics.post(
        '/4.0/eats-picker-statistics/api/v1/analyze-statistics/bulk',
        json={
            'picker_id': picker_id,
            'interval': interval,
            'metric_name': metric_name,
            'date_from': date_from,
            'date_to': date_to,
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status_code == 200
    response = response.json()

    metrics = get_statistics(picker_id, metric_name, interval)
    metrics = dict((metric['id'], metric) for metric in metrics)

    assert len(response['metrics']) == len(expected_metrics_ids)
    if expected_target is None:
        assert 'target' not in response
    else:
        assert response['target'] == expected_target

    for (actual_metric, expected_metric_id) in zip(
            response['metrics'], expected_metrics_ids,
    ):
        expected_metric = metrics[expected_metric_id]
        assert (
            datetime.datetime.fromisoformat(actual_metric['date_from'])
            == expected_metric['utc_from']
        )
        assert (
            datetime.datetime.fromisoformat(actual_metric['date_to'])
            == expected_metric['utc_to']
        )
        assert actual_metric['value'] == expected_metric['value']
        assert (
            datetime.datetime.fromisoformat(actual_metric['date'])
            == expected_metric['created_at']
        )
