# pylint: disable=W0621
import datetime

from dateutil import tz
import pytest

from . import common

NOW = datetime.datetime(2020, 5, 27, 14, 3, 10, 0, tz.UTC)
NOW_ISO8601 = NOW.strftime('%Y-%m-%dT%H:%M:%S%z')
# yt_logger returns local tz
NOW_RFC3339 = NOW.astimezone(tz.tzlocal()).isoformat()
YT_LOGS = []


@pytest.fixture(autouse=True)
def testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business'])
@pytest.mark.now(NOW.isoformat())
async def test(taxi_surge_calculator):
    request = {
        'point_a': [37.583369, 55.778821],
        'classes': ['econom', 'business'],
    }
    expected = {
        'zone_id': 'MSK-Yandex HQ',
        'user_layer': 'default',
        'experiment_id': 'a29e6a811131450f9a28337906594207',
        'experiment_name': 'default',
        'experiment_layer': 'default',
        'is_cached': False,
        'classes': [
            {'name': 'econom', 'value_raw': 1.0, 'surge': {'value': 5.0}},
            {'name': 'business', 'value_raw': 1.0, 'surge': {'value': 11.0}},
        ],
        'experiments': [],
        'experiment_errors': [],
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    actual = response.json()

    calculation_id = actual.pop('calculation_id', '')

    assert len(calculation_id) == 32

    common.sort_data(expected)
    common.sort_data(actual)

    assert actual == expected
    del YT_LOGS[0]['calculation']['$pipeline_id']
    assert YT_LOGS == [
        {
            'calculation': {
                '$logs': [],
                '$meta': [
                    {
                        '$logs': [
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'info',
                                '$message': 'calc econom',
                                '$region': 'user_code',
                            },
                        ],
                        '$stage': 'main',
                        '$iteration': 0,
                    },
                    {
                        '$logs': [
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'info',
                                '$message': 'calc business',
                                '$region': 'user_code',
                            },
                        ],
                        '$stage': 'main',
                        '$iteration': 1,
                    },
                    {
                        '$logs': [
                            {
                                '$message': (
                                    'Stage failed: Error: while setting key '
                                    '\'econom\'; to \'__output__.classes\'; '
                                    'at stage \'failable\': '
                                    'at econom.value_raw: Incompatible '
                                    'assignment of value type "string" to '
                                    'value with schema type "number"'
                                ),
                                '$level': 'error',
                                '$timestamp': NOW_ISO8601,
                                '$region': 'out_bindings',
                            },
                        ],
                        '$stage': 'failable',
                        '$iteration': 0,
                    },
                    {
                        '$logs': [
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'info',
                                '$message': 'important info in predicate call',
                                '$region': 'predicate_always_true',
                            },
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'info',
                                '$message': 'logic information',
                                '$region': 'user_code',
                            },
                        ],
                        '$stage': 'test_predicate_logs',
                        '$iteration': 0,
                    },
                    {
                        '$logs': [
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'info',
                                '$message': 'get ready for exception',
                                '$region': 'user_code',
                            },
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'error',
                                '$message': (
                                    'Stage failed: you better catch that'
                                ),
                                '$region': 'user_code',
                            },
                        ],
                        '$stage': 'fetch_but_fail',
                        '$iteration': 0,
                    },
                    {
                        '$logs': [
                            {
                                '$timestamp': NOW_ISO8601,
                                '$level': 'error',
                                '$message': (
                                    'Stage failed: returned "number", '
                                    'but only "object" allowed. Value: 42'
                                ),
                                '$region': 'user_code',
                            },
                        ],
                        '$stage': 'test_non_object_return_fail',
                        '$iteration': 0,
                    },
                ],
                '$pipeline_name': 'default',
                'extra': {
                    'local_time_shift': {
                        '$history': [{'$meta_idx': 1, '$value': 3}],
                    },
                    'type': {
                        '$history': [{'$meta_idx': 1, '$value': 'some_type'}],
                    },
                },
                'classes': {
                    'econom': {
                        'name': {
                            '$history': [{'$meta_idx': 0, '$value': 'econom'}],
                        },
                        'surge': {
                            'value': {
                                '$history': [{'$meta_idx': 0, '$value': 5}],
                            },
                        },
                        'value_raw': {
                            '$history': [{'$meta_idx': 0, '$value': 1}],
                        },
                    },
                    'business': {
                        'name': {
                            '$history': [
                                {'$meta_idx': 1, '$value': 'business'},
                            ],
                        },
                        'surge': {
                            'value': {
                                '$history': [{'$meta_idx': 1, '$value': 11}],
                            },
                        },
                        'value_raw': {
                            '$history': [{'$meta_idx': 1, '$value': 1}],
                        },
                    },
                },
            },
            'calculation_id': calculation_id,
            'experiment_id': 'a29e6a811131450f9a28337906594207',
            'experiment_name': 'default',
            'lat': 55.778821,
            'lon': 37.583369,
            'surge_id': 'MSK-Yandex HQ',
            'timestamp': NOW_RFC3339,
        },
    ]
