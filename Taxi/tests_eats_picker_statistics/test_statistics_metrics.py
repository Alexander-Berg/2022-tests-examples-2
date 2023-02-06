import datetime

import pytest


@pytest.mark.config(
    EATS_PICKER_STATISTICS_YQL_QUERY_STATUS_POLLING_PARAMS={
        'retry-interval-ms': 50,
        'total-wait-ms': 100,
    },
)
@pytest.mark.experiments3(
    filename='config3_eats_picker_statistics_statistics_params.json',
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_picker_statistics_update_interval',
    consumers=['eats-picker-statistics/update-interval'],
    default_value={'update_interval_seconds': 900},
)
async def test_statistics_metrics(
        taxi_eats_picker_statistics,
        mockserver,
        taxi_eats_picker_statistics_monitor,
        testpoint,
        load_json,
        mocked_time,
):

    now = mocked_time.now()

    @testpoint('polling-iteration')
    async def _(_):
        nonlocal mocked_time

        delta = datetime.timedelta(seconds=300)
        mocked_time.set(now + delta)
        nonlocal taxi_eats_picker_statistics
        await taxi_eats_picker_statistics.invalidate_caches()

    operation_id = 0

    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_operations(request):
        nonlocal operation_id
        assert request.method == 'POST'
        operation_id += 1
        response = {'id': str(operation_id)}
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d+)', regex=True,
    )
    def mock_operation_status(_, operation_id):
        response = {'id': str(operation_id), 'status': 'COMPLETED'}
        return mockserver.make_response(json=response, status=200)

    cache = []

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d+)/results_data',
        regex=True,
    )
    def mock_results_data(_, operation_id):
        nonlocal cache
        if int(operation_id) > 6 or operation_id in cache:
            return mockserver.make_response(status=200)

        cache.append(operation_id)
        return mockserver.make_response(
            json={
                'picker_id': f'picker{operation_id}',
                'value': float(10) + float(operation_id),
                'final_items_count': 100 + int(operation_id),
                'picker_timezone': 'UTC',
                'utc_from': '2021-09-15T18:00:00+0000',
                'utc_to': '2021-09-15T19:00:00+0000',
            },
            status=200,
        )

    await taxi_eats_picker_statistics.run_periodic_task(
        'eats-picker-statistics-statistics-synchronizer-periodic',
    )

    assert mock_operations
    assert mock_operation_status
    assert mock_results_data

    metrics = await taxi_eats_picker_statistics_monitor.get_metric(
        'statistics-synchronizer',
    )
    assert metrics['periodic_starts'] == 1
    exp_data = load_json(
        'config3_eats_picker_statistics_statistics_params.json',
    )
    metrics_intervals = exp_data['configs'][0]['default_value'][
        'metrics_intervals'
    ]
    for metrics_interval in metrics_intervals:
        interval = metrics_interval['interval']
        for metric in metrics_interval['metrics']:
            metric_name = metric['name']
            assert metrics['picker_statistics'][metric_name][interval] == 1
    assert metrics['periodic_work_duration'] == 300
