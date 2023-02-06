import pytest

from taxi_driver_metrics.common.models.sql_query.schema import (
    OrderMetricsSchema,
)

HANDLER_PATH = 'v1/service/entity/history'


_CLICKHOUSE_RECORDS = [
    {
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
    },
    {
        OrderMetricsSchema.timestamp: 1546332043.049,
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
        OrderMetricsSchema.order_cost: None,
        OrderMetricsSchema.surge: None,
        OrderMetricsSchema.reject_reason: 'bad',
        OrderMetricsSchema.driver_tags: None,
        OrderMetricsSchema.rider_tags: None,
        OrderMetricsSchema.event_tags: None,
    },
    {
        OrderMetricsSchema.timestamp: 1546332043.049,
        OrderMetricsSchema.event_type: 'order',
        OrderMetricsSchema.key: 'handle_reject',
        OrderMetricsSchema.name: 'reject',
        OrderMetricsSchema.order_id: 'order_id',
        OrderMetricsSchema.order_alias_id: 'order_alias_id',
        OrderMetricsSchema.unique_driver_id: 'unique_driver_id',
        OrderMetricsSchema.park_driver_profile_id: 'park_driver_profile_id',
        OrderMetricsSchema.user_phone_id: 'user_phone_id',
        OrderMetricsSchema.user_id: 'user_id',
        OrderMetricsSchema.zone: 'spb',
        OrderMetricsSchema.tariff_class: 'econom',
        OrderMetricsSchema.order_cost: None,
        OrderMetricsSchema.surge: None,
        OrderMetricsSchema.reject_reason: 'bad',
        OrderMetricsSchema.driver_tags: ['drier_tags', 'driver_tags2'],
        OrderMetricsSchema.rider_tags: None,
        OrderMetricsSchema.event_tags: None,
    },
    {
        OrderMetricsSchema.timestamp: None,
        OrderMetricsSchema.rider_tags: None,
        OrderMetricsSchema.event_tags: None,
    },
]


_PARSED_CLICKHOUSE_RECORDS = [
    {
        'driver_tags': [],
        'event_key': 'handle_complete',
        'event_tags': [],
        'event_timestamp': '2019-01-01T08:40:31.043000+00:00',
        'event_type': 'order',
        'name': 'complete',
        'order_alias_id': 'order_alias_id',
        'order_cost': 10.0,
        'order_id': 'order_id',
        'park_driver_profile_id': 'park_driver_profile_id',
        'reject_reason': 'bad',
        'rider_tags': [],
        'surge': 1.0,
        'tariff_class': 'econom',
        'tariff_zone': 'spb',
        'unique_driver_id': 'unique_driver_id',
        'user_id': 'user_id',
        'user_phone_id': 'user_phone_id',
    },
    {
        'event_key': 'handle_complete',
        'event_timestamp': '2019-01-01T08:40:43.049000+00:00',
        'event_type': 'order',
        'name': 'complete',
        'order_alias_id': 'order_alias_id',
        'order_id': 'order_id',
        'park_driver_profile_id': 'park_driver_profile_id',
        'reject_reason': 'bad',
        'tariff_class': 'econom',
        'tariff_zone': 'spb',
        'unique_driver_id': 'unique_driver_id',
        'user_id': 'user_id',
        'user_phone_id': 'user_phone_id',
    },
    {
        'driver_tags': ['drier_tags', 'driver_tags2'],
        'event_key': 'handle_reject',
        'event_timestamp': '2019-01-01T08:40:43.049000+00:00',
        'event_type': 'order',
        'name': 'reject',
        'order_alias_id': 'order_alias_id',
        'order_id': 'order_id',
        'park_driver_profile_id': 'park_driver_profile_id',
        'reject_reason': 'bad',
        'tariff_class': 'econom',
        'tariff_zone': 'spb',
        'unique_driver_id': 'unique_driver_id',
        'user_id': 'user_id',
        'user_phone_id': 'user_phone_id',
    },
]


@pytest.mark.parametrize(
    'json_request, sql_expected_filter_part, clickhouse_res, status,'
    ' expected_response',
    (
        pytest.param(None, '', [], 400, None, id='0'),
        pytest.param({'unique_driver_id': 'yes'}, '', [], 400, None, id='1'),
        pytest.param(
            {
                'unique_driver_id': 'yes',
                'older_than': '2019-01-01T11:40:31.043',
            },
            ' AND unique_driver_id = \'yes\' '
            'AND event_timestamp < 1546342831.043 '
            'ORDER BY event_timestamp DESC LIMIT 500 FORMAT JSON',
            _CLICKHOUSE_RECORDS,
            200,
            _PARSED_CLICKHOUSE_RECORDS,
            id='2',
        ),
        pytest.param(
            {
                'unique_driver_id': '123',
                'limit': 100,
                'older_than': '2019-01-01T11:40:31.043',
            },
            ' AND unique_driver_id = \'123\' '
            'AND event_timestamp < 1546342831.043 '
            'ORDER BY event_timestamp DESC LIMIT 100 FORMAT JSON',
            _CLICKHOUSE_RECORDS[:1],
            200,
            _PARSED_CLICKHOUSE_RECORDS[:1],
            id='3',
        ),
        pytest.param(
            {
                'unique_driver_id': 'driver',
                'older_than': '2019-01-01T11:40:31.043',
            },
            ' AND unique_driver_id = \'driver\' AND '
            'event_timestamp < 1546342831.043 '
            'ORDER BY event_timestamp DESC LIMIT 500 FORMAT JSON',
            _CLICKHOUSE_RECORDS[1:],
            200,
            _PARSED_CLICKHOUSE_RECORDS[1:],
            id='4',
        ),
        pytest.param(
            {'unique_driver_id': 333, 'limit': '200'}, '', [], 400, [], id='5',
        ),
    ),
)
async def test_clickhouse_history(
        stq3_context,
        taxi_driver_metrics,
        mockserver_clickhouse_host,
        json_request,
        sql_expected_filter_part,
        clickhouse_res,
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

    sql_main_part = (
        'SELECT event_timestamp,event_type,event_key,name,'
        'order_id,order_alias,unique_driver_id,park_driver_profile_id,'
        'user_phone_id,user_id,tariff_zone,tariff_class,order_cost,'
        'surge,reject_reason,driver_tags,user_tags,event_tags,other '
        'FROM dbordermetrics.order_metrics WHERE 1'
    )

    resulted_sql = ''

    def response(request):
        data = request._data.decode('utf-8')
        nonlocal resulted_sql
        resulted_sql = data
        return _build_meta(clickhouse_res)

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mockserver_clickhouse_host(response, host_list[0][11:] + ':test_pass/')

    expected_sql = sql_main_part + sql_expected_filter_part

    result = await taxi_driver_metrics.post(HANDLER_PATH, json=json_request)
    assert result.status == status

    if status == 200:
        assert await result.json() == {'items': expected_response}
        assert resulted_sql == expected_sql
