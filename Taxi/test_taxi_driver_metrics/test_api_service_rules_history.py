# pylint:disable=unused-variable
import copy
import datetime

import pytest
from yt import yson

from taxi_driver_metrics.common.storage import clickhouse


CONTEXT = yson.dumps(
    {
        'driver': {'activity': 100, 'tags': ['some_tag']},
        'event': {'tags': ['event_tag']},
    },
).decode()

RULES_1 = [
    yson.dumps(
        {
            'rule_type': 'activity',
            'rule_config_id': None,
            'action_result': 2,
            'rule_name': 'ActivityTrip',
        },
    ).decode(),
    yson.dumps(
        {
            'rule_type': 'tagging',
            'rule_config_id': None,
            'action_result': [{'name': 'AweSomeTag', 'ttl': 100500}],
            'rule_name': 'FirstOrder',
        },
    ).decode(),
]
RULES_2 = [
    yson.dumps(
        {
            'rule_type': 'blocking',
            'rule_config_id': '123asd123',
            'action_result': None,
            'rule_name': 'CoronaBlock',
        },
    ).decode(),
]

CONTENT = {
    'meta': [
        {'name': 'event_id', 'type': 'Nullable(String)'},
        {'name': 'event_zone', 'type': 'Nullable(String)'},
        {'name': 'event_type', 'type': 'Nullable(String)'},
        {'name': 'event_name', 'type': 'Nullable(String)'},
        {'name': 'context', 'type': 'Nullable(String)'},
        {'name': 'rules', 'type': 'Array(String)'},
        {'name': 'trace_id', 'type': 'Nullable(String)'},
        {'name': 'link', 'type': 'Nullable(String)'},
        {'name': 'additional_info', 'type': 'Nullable(String)'},
    ],
    'data': [
        {
            'created': 1584947698,
            'event_id': '1346775000',
            'entity_id': '123',
            'entity_type': 'driver',
            'event_zone': 'nalchik',
            'event_type': 'order',
            'event_name': 'complete',
            'context': CONTEXT,
            'rules': RULES_1,
            'trace_id': 'd20e383f50ba4f51afb237692443acec',
            'link': '7452b16ee9ad47158cde0bd19a9841d0',
            'additional_info': '{}',
        },
        {
            'created': 1584947698,
            'event_id': '1347999080',
            'entity_id': '123',
            'entity_type': 'driver',
            'event_zone': 'nalchik',
            'event_type': 'order',
            'event_name': 'reject_missing_tariff',
            'context': CONTEXT,
            'rules': RULES_2,
            'trace_id': '1a55b99327fb429e8bd5fb867ad0034a',
            'link': '66a21ecf4a214527b74991c1a241573e',
            'additional_info': yson.dumps(
                {'order_id': 'actually_order_id'},
            ).decode(),
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
    '2020-03-19T00:00:00',
    '2020-03-18T23:30:00',
    '2020-03-19T00:30:00',
]
TABLE_RANGE_1D = ['2020-03-18', '2020-03-17', '2020-03-16']
TABLES = {
    clickhouse.PATH_30MIN: TABLE_RANGE_30MIN,
    clickhouse.PATH_1D: TABLE_RANGE_1D,
}

HANDLER_PATH = 'v1/service/rules/history'


def build_thresholds(start, step, times):
    return [
        (start + datetime.timedelta(minutes=step * i)).strftime(
            clickhouse.TIME_FORMAT_MIN,
        )
        for i in range(times)
    ]


@pytest.mark.now('2020-03-19T01:00:01')
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_conditions',
    [
        ({'entity_type': 'driver'}, 400, []),
        (
            {'entity_type': 'driver', 'entity_id': 'damir'},
            200,
            ['entity_type = \'driver\'', 'entity_id = \'damir\''],
        ),
        (
            {'entity_type': 'driver', 'entity_id': 'damir'},
            200,
            ['entity_type = \'driver\'', 'entity_id = \'damir\''],
        ),
        ({'rule_type': 'activity'}, 200, ['rule_type = \'activity\'']),
        (
            {
                'rule_name': 'CoronaBlock',
                'processing_type': 'query_processing',
                'datetime_from': '2020-03-16T19:15:00Z',
                'datetime_to': '2220-08-05T19:15:00Z',
            },
            200,
            ['rule_name = \'CoronaBlock\''],
        ),
        ({'event_zone': 'naberezhnyechelny'}, 400, []),
    ],
)
async def test_rules_history(
        web_app_client,
        patch_aiohttp_session,
        patch,
        response_mock,
        tst_request,
        expected_status,
        expected_conditions,
):
    base_path = clickhouse.get_env_base_path()

    @patch('taxi.clients.yt.YtClient.get')
    async def get_cypress_node_content(*args, **kwargs):
        assert base_path in args[0]
        return TABLES

    @patch_aiohttp_session('http://hahn.yt.yandex.net/query', 'POST')
    def query_chyt(*args, **kwargs):
        data = kwargs['data']
        assert max(TABLE_RANGE_1D) in data
        assert min(TABLE_RANGE_1D) in data

        assert TABLE_RANGE_30MIN[0] in data
        assert max(TABLE_RANGE_30MIN) in data
        # because we have no 5min tables
        assert clickhouse.PATH_5MIN not in data

        for expected_condition in expected_conditions:
            assert expected_condition in data

        return response_mock(json=copy.deepcopy(CONTENT))

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == expected_status

    if expected_status >= 400:
        return
    assert query_chyt.calls
    assert get_cypress_node_content.calls


@pytest.mark.parametrize(
    'tst_request, yt_tables, expected_thresholds, expected_condition',
    [
        (
            {
                'rule_name': 'CoronaBlock',
                'processing_type': 'query_processing',
            },
            {
                clickhouse.PATH_1D: ['2020-08-09', '2020-08-08', '2020-08-07'],
                clickhouse.PATH_30MIN: build_thresholds(
                    datetime.datetime(2020, 8, 9, 23), step=30, times=26,
                ),
                clickhouse.PATH_STREAM: {
                    clickhouse.PATH_5MIN: build_thresholds(
                        datetime.datetime(2020, 8, 10, 11, 50),
                        step=5,
                        times=26,
                    ),
                },
            },
            {
                clickhouse.PATH_1D: ('2020-08-07', '2020-08-09'),
                clickhouse.PATH_30MIN: (
                    '2020-08-10T00:00:00',
                    '2020-08-10T11:30:00',
                ),
                f'{clickhouse.PATH_STREAM}/{clickhouse.PATH_5MIN}': (
                    '2020-08-10T12:00:00',
                    '2020-08-10T13:55:00',
                ),
            },
            None,
        ),
        (
            {
                'rule_name': 'CoronaBlock',
                'processing_type': 'query_processing',
                'datetime_from': '2020-08-08T09:30:00Z',
            },
            {
                clickhouse.PATH_1D: ['2020-08-09', '2020-08-08', '2020-08-07'],
                clickhouse.PATH_30MIN: build_thresholds(
                    datetime.datetime(2020, 8, 9, 23), step=30, times=26,
                ),
                clickhouse.PATH_STREAM: {
                    clickhouse.PATH_5MIN: build_thresholds(
                        datetime.datetime(2020, 8, 10, 11, 50),
                        step=5,
                        times=26,
                    ),
                },
            },
            {
                clickhouse.PATH_1D: ('2020-08-08', '2020-08-09'),
                clickhouse.PATH_30MIN: (
                    '2020-08-10T00:00:00',
                    '2020-08-10T11:30:00',
                ),
                f'{clickhouse.PATH_STREAM}/{clickhouse.PATH_5MIN}': (
                    '2020-08-10T12:00:00',
                    '2020-08-10T13:55:00',
                ),
            },
            'timestamp > 1596879000',
        ),
        (
            {
                'rule_name': 'CoronaBlock',
                'processing_type': 'query_processing',
                'datetime_to': '2020-08-10T10:51:00Z',
            },
            {
                clickhouse.PATH_1D: ['2020-08-09', '2020-08-08', '2020-08-07'],
                clickhouse.PATH_30MIN: build_thresholds(
                    datetime.datetime(2020, 8, 9, 23), step=30, times=26,
                ),
                clickhouse.PATH_STREAM: {
                    clickhouse.PATH_5MIN: build_thresholds(
                        datetime.datetime(2020, 8, 10, 11, 50),
                        step=5,
                        times=26,
                    ),
                },
            },
            {
                clickhouse.PATH_1D: ('2020-08-07', '2020-08-09'),
                clickhouse.PATH_30MIN: (
                    '2020-08-10T00:00:00',
                    '2020-08-10T11:30:00',
                ),
                f'{clickhouse.PATH_STREAM}/{clickhouse.PATH_5MIN}': (
                    '2020-08-10T12:00:00',
                    '2020-08-10T13:50:00',
                ),
            },
            'timestamp < 1597056660',
        ),
        (
            {
                'rule_name': 'CoronaBlock',
                'processing_type': 'query_processing',
                'datetime_to': '2020-08-10T08:51:00Z',
                'datetime_from': '2020-08-09T09:30:00Z',
            },
            {
                clickhouse.PATH_1D: ['2020-08-09', '2020-08-08', '2020-08-07'],
                clickhouse.PATH_30MIN: build_thresholds(
                    datetime.datetime(2020, 8, 9, 23), step=30, times=26,
                ),
                clickhouse.PATH_STREAM: {
                    clickhouse.PATH_5MIN: build_thresholds(
                        datetime.datetime(2020, 8, 10, 11, 50),
                        step=5,
                        times=26,
                    ),
                },
            },
            {
                clickhouse.PATH_1D: ('2020-08-09', '2020-08-09'),
                clickhouse.PATH_30MIN: (
                    '2020-08-10T00:00:00',
                    '2020-08-10T11:30:00',
                ),
            },
            'timestamp > 1596965400 AND timestamp < 1597049460',
        ),
    ],
)
async def test_threshold(
        web_app_client,
        patch_aiohttp_session,
        patch,
        response_mock,
        tst_request,
        yt_tables,
        expected_thresholds,
        expected_condition,
):
    base_path = clickhouse.get_env_base_path()

    @patch('taxi.clients.yt.YtClient.get')
    async def get_cypress_node_content(*args, **kwargs):
        assert base_path in args[0]
        return yt_tables

    @patch_aiohttp_session('http://hahn.yt.yandex.net/query', 'POST')
    def query_chyt(*args, **kwargs):
        data = kwargs['data']
        for path, dates in expected_thresholds.items():
            provided_path = (
                f'(\'{base_path}/{path}\', \'{dates[0]}\', \'{dates[1]}\')'
            )
            assert provided_path in data
        if expected_condition:
            assert expected_condition in data
        return response_mock(json=copy.deepcopy(CONTENT))

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == 200


@pytest.mark.now('2020-08-10T11:00:00Z')
@pytest.mark.parametrize(
    'tst_request, yt_tables, expected_thresholds, expected_condition',
    [
        (
            {
                'rule_name': 'CoronaBlock',
                'processing_type': 'query_processing',
            },
            {
                clickhouse.PATH_1D: ['2020-08-09', '2020-08-08', '2020-08-07'],
                clickhouse.PATH_30MIN: build_thresholds(
                    datetime.datetime(2020, 8, 9, 23), step=30, times=26,
                ),
                clickhouse.PATH_STREAM: {
                    clickhouse.PATH_5MIN: build_thresholds(
                        datetime.datetime(2020, 8, 10, 11, 50),
                        step=5,
                        times=26,
                    ),
                },
            },
            {
                clickhouse.PATH_1D: ('2020-08-07', '2020-08-09'),
                clickhouse.PATH_30MIN: (
                    '2020-08-10T00:00:00',
                    '2020-08-10T11:30:00',
                ),
                f'{clickhouse.PATH_STREAM}/{clickhouse.PATH_5MIN}': (
                    '2020-08-10T12:00:00',
                    '2020-08-10T13:55:00',
                ),
            },
            None,
        ),
    ],
)
async def test_threshold_with_now(
        web_app_client,
        patch_aiohttp_session,
        patch,
        response_mock,
        tst_request,
        yt_tables,
        expected_thresholds,
        expected_condition,
):
    base_path = clickhouse.get_env_base_path()

    @patch('taxi.clients.yt.YtClient.get')
    async def get_cypress_node_content(*args, **kwargs):
        assert base_path in args[0]
        return yt_tables

    @patch_aiohttp_session('http://hahn.yt.yandex.net/query', 'POST')
    def query_chyt(*args, **kwargs):
        data = kwargs['data']
        for path, dates in expected_thresholds.items():
            provided_path = (
                f'(\'{base_path}/{path}\', \'{dates[0]}\', \'{dates[1]}\')'
            )
            assert provided_path in data
        if expected_condition:
            assert expected_condition in data
        return response_mock(json=copy.deepcopy(CONTENT))

    response = await web_app_client.post(HANDLER_PATH, json=tst_request)
    assert response.status == 200
