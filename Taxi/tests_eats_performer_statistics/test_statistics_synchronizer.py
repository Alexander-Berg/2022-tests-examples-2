import datetime

import pytest


def assert_data(actual_data: list, expected_data: list):
    actual_data = [
        (
            row['performer_id'],
            row['metric_name'],
            row['metric_interval'],
            row['value'],
            row['final_items_count'],
        )
        for row in actual_data
    ]
    assert actual_data == expected_data


@pytest.mark.config(
    EATS_PERFORMER_STATISTICS_YQL_QUERY_STATUS_POLLING_PARAMS={
        'retry-interval-ms': 50,
        'total-wait-ms': 100,
    },
)
@pytest.mark.experiments3(
    filename='config3_eats_performer_statistics_statistics_params.json',
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_performer_statistics_update_interval',
    consumers=['eats-performer-statistics/update-interval'],
    default_value={'update_interval_seconds': 900},
)
async def test_statistics_synchronizer_happy_path(
        taxi_eats_performer_statistics, mockserver, get_statistics,
):
    operation_id = 0

    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_operations(request):
        nonlocal operation_id
        assert request.method == 'POST'
        operation_id += 1
        response = {'id': str(operation_id)}
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)', regex=True,
    )
    def mock_status(_, operation_id):
        response = {'id': str(operation_id), 'status': 'COMPLETED'}
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)/results_data',
        regex=True,
    )
    def mock_data(request, operation_id):
        return mockserver.make_response(status=200)

    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-statistics-synchronizer-periodic',
    )

    assert mock_operations.times_called == 6
    assert mock_status.times_called == 6
    assert mock_data.times_called == 6


@pytest.mark.config(
    EATS_PERFORMER_STATISTICS_YQL_QUERY_STATUS_POLLING_PARAMS={
        'retry-interval-ms': 100,
        'total-wait-ms': 1000,
    },
)
@pytest.mark.experiments3(
    filename='config3_eats_performer_statistics_statistics_params.json',
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_performer_statistics_update_interval',
    consumers=['eats-performer-statistics/update-interval'],
    default_value={'update_interval_seconds': 900},
)
async def test_statistics_synchronizer_polling(
        taxi_eats_performer_statistics, mockserver, get_statistics,
):
    operation_id = 0

    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_operations(request):
        nonlocal operation_id
        assert request.method == 'POST'
        operation_id += 1
        response = {'id': str(operation_id)}
        return mockserver.make_response(json=response, status=200)

    status_counter = 0

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)', regex=True,
    )
    def mock_status(request, operation_id):
        nonlocal status_counter
        response = {}
        if status_counter % 2:
            response = {'id': str(operation_id), 'status': 'COMPLETED'}
        else:
            response = {'id': str(operation_id), 'status': 'RUNNING'}
        status_counter += 1
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)/results_data',
        regex=True,
    )
    def mock_data(request, operation_id):
        return mockserver.make_response(status=200)

    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-statistics-synchronizer-periodic',
    )

    assert mock_operations.times_called == 6
    assert mock_status.times_called == 12
    assert mock_data.times_called == 6


@pytest.mark.config(
    EATS_PERFORMER_STATISTICS_YQL_QUERY_STATUS_POLLING_PARAMS={
        'retry-interval-ms': 50,
        'total-wait-ms': 100,
    },
)
@pytest.mark.experiments3(
    filename='config3_eats_performer_statistics_statistics_params.json',
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_performer_statistics_update_interval',
    consumers=['eats-performer-statistics/update-interval'],
    default_value={'update_interval_seconds': 900},
)
async def test_statistics_synchronizer_null_fields(
        taxi_eats_performer_statistics, mockserver, get_statistics,
):
    operation_id = 0

    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_operations(request):
        nonlocal operation_id
        assert request.method == 'POST'
        operation_id += 1
        response = {'id': str(operation_id)}
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)', regex=True,
    )
    def mock_status(_, operation_id):
        response = {'id': str(operation_id), 'status': 'COMPLETED'}
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)/results_data',
        regex=True,
    )
    def mock_data(request, operation_id):
        return mockserver.make_response(status=200)

    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-statistics-synchronizer-periodic',
    )

    assert mock_operations.times_called == 6
    assert mock_status.times_called == 6
    assert mock_data.times_called == 6


@pytest.mark.config(
    EATS_PERFORMER_STATISTICS_YQL_QUERY_STATUS_POLLING_PARAMS={
        'retry-interval-ms': 100,
        'total-wait-ms': 300,
    },
)
@pytest.mark.experiments3(
    filename='config3_eats_performer_statistics_statistics_params.json',
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_performer_statistics_update_interval',
    consumers=['eats-performer-statistics/update-interval'],
    default_value={'update_interval_seconds': 900},
)
@pytest.mark.now('2021-05-01T12:00:00+0000')
async def test_statistics_synchronizer_polling_errors(
        taxi_eats_performer_statistics,
        mockserver,
        get_statistics,
        testpoint,
        mocked_time,
):
    @testpoint('polling-iteration')
    async def _(_):
        nonlocal mocked_time
        now = mocked_time.now()
        delta = datetime.timedelta(milliseconds=300)
        mocked_time.set(now + delta)
        nonlocal taxi_eats_performer_statistics
        await taxi_eats_performer_statistics.invalidate_caches()

    operation_id = 0

    @mockserver.json_handler('/yql/api/v2/operations')
    def mock_operations(request):
        nonlocal operation_id
        assert request.method == 'POST'
        operation_id += 1
        response = {'id': str(operation_id)}
        return mockserver.make_response(json=response, status=200)

    @mockserver.json_handler('/yql/api/v2/operations/1')
    def mock_status1(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'id': str(2), 'status': 'ERROR'}, status=200,
        )

    @mockserver.json_handler('/yql/api/v2/operations/2')
    def mock_status2(request):
        assert request.method == 'GET'
        raise mockserver.TimeoutError()

    @mockserver.json_handler('/yql/api/v2/operations/3')
    def mock_status3(request):
        assert request.method == 'GET'
        raise mockserver.NetworkError()

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)', regex=True,
    )
    def mock_status(request, operation_id):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'id': str(1), 'status': 'COMPLETED'}, status=200,
        )

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\d)/results_data',
        regex=True,
    )
    def mock_data(request, operation_id):
        return mockserver.make_response(status=200)

    await taxi_eats_performer_statistics.run_periodic_task(
        'eats-performer-statistics-statistics-synchronizer-periodic',
    )

    assert mock_operations.times_called == 6
    assert mock_status1.times_called == 1
    assert mock_status2.times_called == 1
    assert mock_status3.times_called == 1
    assert mock_status.times_called == 3
    assert mock_data.times_called == 3
