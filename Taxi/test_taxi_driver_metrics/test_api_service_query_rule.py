import pytest

from taxi_driver_metrics.common.models.sql_query.schema import (
    OrderMetricsSchema,
)


HANDLER_PATH = 'v1/service/query/validate'


def _get_record(**values):
    record = {
        OrderMetricsSchema.timestamp: 1546332031.043,
        OrderMetricsSchema.event_type: 'order',
        OrderMetricsSchema.key: 'handle_complete',
        OrderMetricsSchema.name: 'complete',
        OrderMetricsSchema.order_id: 'order_id',
        OrderMetricsSchema.order_alias_id: 'order_alias_id',
        OrderMetricsSchema.unique_driver_id: 'unique_driver_id',
        OrderMetricsSchema.park_driver_profile_id: 'park_driver_profile_id',
        OrderMetricsSchema.user_phone_id: 'user_phone_id',
        OrderMetricsSchema.user_id: 'user_id',
        OrderMetricsSchema.zone: 'spb',
        OrderMetricsSchema.tariff_class: 'econom',
        OrderMetricsSchema.order_cost: 10.0,
        OrderMetricsSchema.surge: 1.0,
        OrderMetricsSchema.reject_reason: 'bad',
        OrderMetricsSchema.driver_tags: [],
        OrderMetricsSchema.rider_tags: [],
        OrderMetricsSchema.event_tags: [],
    }

    record.update(values)

    return record


@pytest.mark.parametrize(
    'query, clickhouse_result, status, expected_response',
    (
        (
            'SELECT * FROM $order_metrics '
            'where unique_driver_id in $unique_driver_ids',
            [_get_record()],
            200,
            {
                'query_result': {
                    'driver_tags': [],
                    'event_key': 'handle_complete',
                    'event_tags': [],
                    'event_timestamp': 1546332031.043,
                    'event_type': 'order',
                    'name': 'complete',
                    'order_alias': 'order_alias_id',
                    'order_cost': 10.0,
                    'order_id': 'order_id',
                    'park_driver_profile_id': 'park_driver_profile_id',
                    'reject_reason': 'bad',
                    'surge': 1.0,
                    'tariff_class': 'econom',
                    'tariff_zone': 'spb',
                    'unique_driver_id': 'unique_driver_id',
                    'user_id': 'user_id',
                    'user_phone_id': 'user_phone_id',
                    'user_tags': [],
                },
                'query_statistic': {
                    'bytes_read': 10,
                    'elapsed': 0.5,
                    'rows_read': 100,
                },
                'success': True,
            },
        ),
        (
            'DROP TABLE $order_metrics $unique_driver_ids',
            None,
            200,
            {
                'details': 'Query does not start with a Select',
                'success': False,
            },
        ),
        (
            'Select * from where $unique_driver_ids;'
            ' DROP TABLE $order_metrics',
            None,
            200,
            {
                'details': 'Query contains more than one statement',
                'success': False,
            },
        ),
        (
            'Select * from $order_metrics where driver = $good '
            'and unique_driver_id in $unique_driver_ids',
            [],
            500,
            {
                'code': 'INTERNAL_SERVER_ERROR',
                'details': {
                    'reason': 'Failed to get context record from clickhouse',
                },
                'message': 'Internal server error',
            },
        ),
        (
            'SELECT * FROM $order_metrics',
            [_get_record()],
            200,
            {
                'details': 'Query does not contain identifier filter',
                'success': False,
            },
        ),
    ),
)
async def test_query_validation(
        stq3_context,
        taxi_driver_metrics,
        mockserver_clickhouse_host,
        query,
        clickhouse_result,
        status,
        expected_response,
):
    # pylint: disable=protected-access
    def _build_meta(data):
        return {
            'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
            'meta': [],
            'data': data,
            'rows': 1,
        }

    def response(request):
        return _build_meta(clickhouse_result)

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mockserver_clickhouse_host(response, host_list[0][11:] + ':test_pass/')

    result = await taxi_driver_metrics.post(
        HANDLER_PATH, json={'query': query},
    )

    assert result.status == status
    assert await result.json() == expected_response
