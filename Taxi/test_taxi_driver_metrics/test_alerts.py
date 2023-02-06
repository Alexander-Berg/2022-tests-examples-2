# pylint:disable=unused-variable
import datetime

import pytest

from taxi_driver_metrics.common.models import rule_statistic
from taxi_driver_metrics.common.storage import clickhouse


CONTENT = {
    'data': [
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip',
            'trigger_count': 120,
            'seed': 1584580800,
            'timestamp_min': 1603375093,
        },
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip',
            'trigger_count': 10,
            'seed': 1584580500,
            'timestamp_min': 1603375093,
        },
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip',
            'trigger_count': 20,
            'seed': 1584579900,
            'timestamp_min': 1603375093,
        },
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip',
            'trigger_count': 50,
            'seed': 1584579300,
            'timestamp_min': 1603375093,
        },
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip2',
            'trigger_count': 0,
            'seed': 1603374900,
            'timestamp_min': 1603375093,
        },
        {
            'action_result_pos': 150,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip2',
            'trigger_count': 120,
            'seed': 1603374900,
            'timestamp_min': 1603375093,
        },
        {
            'action_result_pos': 10,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip2',
            'trigger_count': 10,
            'seed': 1603374900,
            'timestamp_min': 1584579300,
        },
        {
            'action_result_pos': 75,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip2',
            'trigger_count': 20,
            'seed': 1603374900,
            'timestamp_min': 1584579300,
        },
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip2',
            'trigger_count': 50,
            'seed': 1603374900,
            'timestamp_min': 1584579000,
        },
        {
            'action_result_pos': 100,
            'action_result_neg': 0,
            'rule_name': 'ActivityTrip2',
            'trigger_count': 0,
            'seed': 1603374900,
            'timestamp_min': 1603375093,
        },
    ],
    'rows': 2,
    'statistics': {
        'elapsed': 6.357179065,
        'rows_read': 19295984,
        'bytes_read': 19121398083,
    },
}


TABLE_RANGE_30MIN = [
    '2020-03-19T03:00:00',
    '2020-03-19T03:30:00',
    '2020-03-19T04:00:00',
]
TABLES = {
    clickhouse.PATH_1D: ('2020-02-02', '2020-02-03'),
    clickhouse.PATH_30MIN: TABLE_RANGE_30MIN,
}


def build_thresholds(start, step, times):
    return [
        (start + datetime.timedelta(minutes=step * i)).strftime(
            clickhouse.TIME_FORMAT_MIN,
        )
        for i in range(times)
    ]


@pytest.mark.config(
    DRIVER_METRICS_RULE_ALERTS_RULES={
        'ActivityTrip': {
            'checks': [
                {
                    'aggregation': 'max',
                    'field': 'trigger_count',
                    'window': 5,
                    'thresholds': {'lower': 200},
                },
                {
                    'aggregation': 'avg',
                    'field': 'action_result_pos',
                    'window': 15,
                    'thresholds': {'upper': 400},
                },
            ],
        },
        'ActivityTrip2': {
            'checks': [
                {
                    'aggregation': 'avg',
                    'field': 'action_result_pos',
                    'window': 10,
                    'thresholds': {'upper': 100},
                },
            ],
        },
        'ActivityTrip3': {
            'checks': [
                {
                    'aggregation': 'avg',
                    'field': 'action_result_pos',
                    'window': 10,
                    'thresholds': {'upper': 100},
                },
            ],
        },
    },
)
@pytest.mark.now('2020-03-19T01:44:01')
@pytest.mark.parametrize(
    'clickhouse_return, expected_alert_result',
    [
        (
            CONTENT,
            [
                rule_statistic.AggregationResult(
                    value=120, check_result=True, aggr_func_name='max',
                ),
                rule_statistic.AggregationResult(
                    value=133, check_result=False, aggr_func_name='avg',
                ),
                rule_statistic.AggregationResult(
                    value=0, check_result=False, aggr_func_name='avg',
                ),
                rule_statistic.AggregationResult(
                    value=0, check_result=False, aggr_func_name='avg',
                ),
            ],
        ),
    ],
)
async def test_rules_alerts(
        web_context,
        web_app_client,
        patch_aiohttp_session,
        patch,
        response_mock,
        clickhouse_return,
        expected_alert_result,
):
    base_path = clickhouse.constants.get_env_base_path()

    @patch('taxi.clients.yt.YtClient.get')
    async def get_cypress_node_content(*args, **kwargs):
        assert base_path in args[0]
        return TABLES

    @patch_aiohttp_session('http://hahn.yt.yandex.net/query', 'POST')
    def query_chyt(*args, **kwargs):
        return response_mock(json=clickhouse_return)

    res = await rule_statistic.run_rules_check(web_context)

    assert res == expected_alert_result


@pytest.mark.parametrize(
    'list_to_aggregate, window, func, result',
    [
        (
            [
                {'trigger_count': 1, 'seed': 1603374900},
                {'trigger_count': 15, 'seed': 1603374600},
                {'trigger_count': 1, 'seed': 1603374300},
                {'trigger_count': 1, 'seed': 1603373700},
            ],
            5,
            'avg',
            2,
        ),
        (
            [
                {'trigger_count': 10, 'seed': 1603374900},
                {'trigger_count': 0, 'seed': 1603374600},
                {'trigger_count': 1, 'seed': 1603374300},
                {'trigger_count': 100, 'seed': 1603374000},
                {'trigger_count': -10, 'seed': 1603373700},
                {'trigger_count': -10, 'seed': 1603373100},
                {'trigger_count': 200, 'seed': 1603372800},
            ],
            10,
            'max',
            200,
        ),
        (
            [
                {'trigger_count': 10, 'seed': 1603372800},
                {'trigger_count': 0, 'seed': 1603373100},
            ],
            15,
            'avg',
            3,
        ),
    ],
)
def test_get_aggregation(list_to_aggregate, window, func, result):
    assert (
        rule_statistic.get_aggregation_check_result(
            'rule',
            {'window': window, 'aggregation': func, 'field': 'trigger_count'},
            list_to_aggregate,
            datetime_from=datetime.datetime.strptime(
                '2020-10-22 13:10:00', '%Y-%m-%d %H:%M:%S',
            ),
            datetime_to=datetime.datetime.strptime(
                '2020-10-22 14:00:10', '%Y-%m-%d %H:%M:%S',
            ),
        )
        == rule_statistic.AggregationResult(
            value=result,
            check_result=True,  # no thresholds rules
            aggr_func_name=func,
        )
    )
