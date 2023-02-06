import json

SIMPLE_CIRCUIT_SCHEMA = {
    'blocks': [
        {
            'alpha': 0.7,
            'debug': True,
            'id': 'smooth_data',
            'type': 'smooth_data',
        },
    ],
    'entry_points': [
        {'debug': True, 'id': 'entry_1', 'type': 'data_entry_point'},
        {'debug': True, 'id': 'entry_2', 'type': 'data_entry_point'},
    ],
    'history_data_duration_sec': 0,
    'name': 'TEST CIRCUIT',
    'type': 'schema',
    'out_points': [
        {'id': 'out_1', 'type': 'bypass'},
        {'id': 'out_2', 'type': 'bypass'},
    ],
    'wires': [
        {'from': 'entry_1', 'to': 'smooth_data', 'type': 'data'},
        {'from': 'smooth_data', 'to': 'out_1', 'type': 'data'},
        {'from': 'entry_2', 'to': 'out_2', 'type': 'data'},
    ],
}

NO_DATA_SCHEMA = {
    'name': 'test_name',
    'type': 'schema',
    'history_data_duration_sec': 10,
    'entry_points': [
        {'id': 'entry', 'type': 'data_entry_point', 'debug': ['data']},
    ],
    'out_points': [
        {'id': 'alert', 'type': 'state_out_point', 'debug': ['state']},
    ],
    'blocks': [
        {
            'id': 'no_data_block',
            'type': 'no_data_state',
            'no_data_duration_before_warn_sec': 60,
            'no_data_duration_before_crit_sec': 120,
            'start_state': 'Ok',
        },
    ],
    'wires': [
        {'to': 'no_data_block', 'from': 'entry', 'type': 'state'},
        {'to': 'alert', 'from': 'no_data_block', 'type': 'state'},
    ],
}

ENTRY_1_INPUT_JSON = {
    'timeseries': {
        'timestamps': [
            1574853600000,
            1574853660000,
            1574853720000,
            1574853780000,
            1574853840000,
            1574853900000,
            1574853960000,
            1574854020000,
            1574854080000,
            1574854140000,
            1574854200000,
            1574854260000,
            1574854320000,
            1574854380000,
            1574854440000,
            1574854500000,
            1574854560000,
            1574854620000,
            1574854680000,
            1574854740000,
        ],
        'values': [
            10.0,
            18.0,
            50.0,
            4.0,
            7.0,
            21.0,
            17.0,
            9.0,
            4.0,
            4.0,
            7.0,
            11.0,
            9.0,
            11.0,
            4.0,
            6.0,
            5.0,
            11.0,
            10.0,
            17.0,
        ],
        'type': 'data',
    },
}

ENTRY_2_INPUT_JSON = {
    'timeseries': {
        'timestamps': [
            1574853600000,
            1574853660000,
            1574853720000,
            1574853780000,
            1574853840000,
            1574853900000,
            1574853960000,
            1574854020000,
            1574854080000,
            1574854140000,
            1574854200000,
            1574854260000,
            1574854320000,
            1574854380000,
            1574854440000,
            1574854500000,
            1574854560000,
            1574854620000,
            1574854680000,
            1574854740000,
        ],
        'values': [
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
            50.0,
        ],
        'type': 'data',
    },
}

TICK_TEST_CIRCUIT_SCHEMA = {
    'blocks': [
        {
            'id': 'static_bounds',
            'type': 'static_bounds_generator',
            'lower': 5,
            'upper': 10,
        },
        {
            'id': 'oob',
            'type': 'out_of_bounds_state',
            'yield_state_on_bounds_in': False,
            'debug': True,
        },
    ],
    'entry_points': [{'id': 'entry_1', 'type': 'data_entry_point'}],
    'history_data_duration_sec': 0,
    'name': 'TEST TICK CIRCUIT',
    'type': 'schema',
    'out_points': [{'id': 'out_1', 'type': 'bypass'}],
    'wires': [
        {'from': 'entry_1', 'to': 'oob', 'type': 'data'},
        {'from': 'static_bounds', 'to': 'oob', 'type': 'bounds'},
        {'from': 'oob', 'to': 'out_1', 'type': 'state'},
    ],
}

OK = 0
WARN = 1

SCHEMA_DEBUG_VALS = [1, 1, 1, 1]
SCHEMA_DEBUG_STATES = [0, 0, 0, 1, 1, 1, 3, 3, 0, 0, 0, 0, 1, 0, 0]
SCHEMA_DEBUG_TS = [
    1601640000000,  # 12:00:00
    1601640180000,  # 12:03:00 - Crit
    1601640270000,  # 12:04:30 - Warn
    1601640300000,  # 12:05:00
]
SCHEMA_DEBUG_STATE_TS = [
    1601640000000,  # Data at 12:00:00
    1601640040000,  # NoData at 12:00:40
    1601640060000,  # NoData at 12:01:00
    1601640080000,  # NoData at 12:01:20
    1601640100000,  # NoData at 12:01:40
    1601640120000,  # NoData at 12:02:00
    1601640140000,  # NoData at 12:02:20
    1601640160000,  # NoData at 12:02:40
    1601640180000,  # Data at 12:03:00
    1601640200000,  # NoData at 12:03:20
    1601640220000,  # NoData at 12:03:40
    1601640240000,  # NoData at 12:04:00
    1601640260000,  # NoData at 12:04:20
    1601640270000,  # Data at 12:04:30
    1601640300000,  # Data at 12:05:00
]


def find_ts(ts_list, name):
    for timeseries in ts_list:
        if timeseries['name'] == name:
            return timeseries['timeseries']
    return {}


async def test_debug_run_circuit(taxi_hejmdal):
    request = {
        'schema': SIMPLE_CIRCUIT_SCHEMA,
        'test_data': [
            {
                'entry_point_id': 'entry_1',
                'input_data': {
                    'input_type': 'json',
                    'data': json.dumps(ENTRY_1_INPUT_JSON),
                },
            },
            {
                'entry_point_id': 'entry_2',
                'input_data': {
                    'input_type': 'json',
                    'data': json.dumps(ENTRY_2_INPUT_JSON),
                },
            },
        ],
    }
    response = await taxi_hejmdal.post('v1/debug/run-test-data', json=request)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['named_timeseries_list'] is not None
    ts_list = resp_json['named_timeseries_list']
    timeseries = find_ts(ts_list, 'entry_1_data')
    assert timeseries == ENTRY_1_INPUT_JSON['timeseries']
    timeseries = find_ts(ts_list, 'entry_2_data')
    assert timeseries == ENTRY_2_INPUT_JSON['timeseries']
    timeseries = find_ts(ts_list, 'smooth_data_data')
    assert timeseries == {
        'timestamps': [
            1574853600000,
            1574853660000,
            1574853720000,
            1574853780000,
            1574853840000,
            1574853900000,
            1574853960000,
            1574854020000,
            1574854080000,
            1574854140000,
            1574854200000,
            1574854260000,
            1574854320000,
            1574854380000,
            1574854440000,
            1574854500000,
            1574854560000,
            1574854620000,
            1574854680000,
            1574854740000,
        ],
        'values': [
            10.0,
            12.4,
            23.68,
            17.776,
            14.543199999999999,
            16.48024,
            16.636167999999999,
            14.345317599999998,
            11.241722319999998,
            9.069205623999999,
            8.4484439368,
            9.21391075576,
            9.149737529032,
            9.7048162703224,
            7.99337138922568,
            7.395359972457976,
            6.676751980720583,
            7.973726386504409,
            8.581608470553088,
            11.107125929387161,
        ],
        'type': 'data',
    }


async def test_debug_tick_run_circuit(taxi_hejmdal):
    request = {
        'schema': TICK_TEST_CIRCUIT_SCHEMA,
        'test_data': [
            {
                'entry_point_id': 'entry_1',
                'input_data': {
                    'input_type': 'json',
                    'data': json.dumps(ENTRY_1_INPUT_JSON),
                },
            },
        ],
    }
    response = await taxi_hejmdal.post('v1/debug/run-test-data', json=request)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['named_timeseries_list'] is not None
    ts_list = resp_json['named_timeseries_list']
    out_states = find_ts(ts_list, 'oob_state')
    assert out_states == {
        'timestamps': ENTRY_1_INPUT_JSON['timeseries']['timestamps'],
        'values': [
            OK if 5 <= v <= 10 else WARN
            for v in ENTRY_1_INPUT_JSON['timeseries']['values']
        ],
        'type': 'state',
    }


async def test_debug_run_circuit_solomon_input(taxi_hejmdal, mockserver):
    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(solomon_request, *args, **kwargs):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {
                            'cluster': 'production_mongo',
                            'application': 'mongo-stats',
                            'service': 'mongo_stats',
                            'host': 'main-mrs-shard3-myt-01',
                            'project': 'taxi',
                            'sensor': 'slow-queries_total',
                            'group': 'taxi_db_mongo_main_shard3',
                        },
                        'timestamps': [
                            1586927101000,
                            1586927161000,
                            1586927221000,
                            1586927281000,
                            1586927341000,
                        ],
                        'values': [28.0, 22.0, 23.0, 25.0, 25.0],
                    },
                },
            ],
        }

    request = {
        'schema': SIMPLE_CIRCUIT_SCHEMA,
        'test_data': [
            {
                'entry_point_id': 'entry_1',
                'input_data': {
                    'input_type': 'solomon_url',
                    'data': (
                        'https://solomon.yandex-team.ru/?project=taxi&'
                        'cluster=production_mongo&service=mongo_stats&'
                        'l.sensor=slow-queries_total&'
                        'l.host=main-mrs-shard3-myt-01&graph=auto&'
                        'b=2020-04-15T05%3A05%3A00.000Z&'
                        'e=2020-04-15T05%3A10%3A00.000Z'
                    ),
                },
            },
            {
                'entry_point_id': 'entry_2',
                'input_data': {
                    'input_type': 'json',
                    'data': json.dumps(ENTRY_2_INPUT_JSON),
                },
            },
        ],
    }

    response = await taxi_hejmdal.post('v1/debug/run-test-data', json=request)
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['named_timeseries_list'] is not None
    ts_list = resp_json['named_timeseries_list']
    timeseries = find_ts(ts_list, 'smooth_data_data')
    assert timeseries == {
        'timestamps': [
            1586927101000,
            1586927161000,
            1586927221000,
            1586927281000,
            1586927341000,
        ],
        'values': [28.0, 26.2, 25.240000000000003, 25.168, 25.1176],
        'type': 'data',
    }


async def test_run_test_data(taxi_hejmdal):
    input_data = {
        'timeseries': {
            'values': SCHEMA_DEBUG_VALS,
            'timestamps': SCHEMA_DEBUG_TS,
        },
        'entry_point_id': 'entry',
    }

    test_data = [
        {
            'entry_point_id': 'entry',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps(input_data),
            },
        },
    ]

    response = await taxi_hejmdal.post(
        'v1/debug/run-test-data',
        json={'schema': NO_DATA_SCHEMA, 'test_data': test_data},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'named_timeseries_list' in resp_json
    assert len(resp_json['named_timeseries_list']) == 2

    data_ts = resp_json['named_timeseries_list'][0]
    assert data_ts['name'] == 'entry_data'
    assert data_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_TS,
        'values': SCHEMA_DEBUG_VALS,
        'type': 'data',
    }

    state_ts = resp_json['named_timeseries_list'][1]
    assert state_ts['name'] == 'alert_state'
    assert state_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_STATE_TS,
        'values': SCHEMA_DEBUG_STATES,
        'type': 'state',
    }


async def test_run_test_case(taxi_hejmdal):
    input_data = {
        'timeseries': {
            'values': SCHEMA_DEBUG_VALS,
            'timestamps': SCHEMA_DEBUG_TS,
        },
        'entry_point_id': 'entry',
    }

    test_data = [
        {
            'entry_point_id': 'entry',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps(input_data),
            },
        },
    ]

    test_case = {
        'out_point_id': 'alert',
        'start_time': '2020-10-02T12:00:00.000Z',
        'end_time': '2020-10-02T12:05:00.000Z',
        'check_type': 'has_alert',
        'check_params': {'min_alert_state': 'Warning'},
    }

    response = await taxi_hejmdal.post(
        'v1/debug/run-test-case',
        json={
            'schema': NO_DATA_SCHEMA,
            'test_data': test_data,
            'test_case': test_case,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['passed'] is True

    assert 'named_timeseries_list' in resp_json
    assert len(resp_json['named_timeseries_list']) == 2

    data_ts = resp_json['named_timeseries_list'][0]
    assert data_ts['name'] == 'entry_data'
    assert data_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_TS,
        'values': SCHEMA_DEBUG_VALS,
        'type': 'data',
    }

    state_ts = resp_json['named_timeseries_list'][1]
    assert state_ts['name'] == 'alert_state'
    assert state_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_STATE_TS,
        'values': SCHEMA_DEBUG_STATES,
        'type': 'state',
    }


async def test_run_test_case_from_solomon(mockserver, taxi_hejmdal):
    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/test_project/sensors/data',
    )
    def _mock_solomon_sensors_data(request):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'project': 'test_project',
                            'cluster': 'test_cluster',
                            'service': 'test_service',
                            'sensor': 'test_sensor',
                        },
                        'timestamps': SCHEMA_DEBUG_TS,
                        'values': SCHEMA_DEBUG_VALS,
                    },
                },
            ],
        }

    solomon_url = (
        'https://solomon.yandex-team.ru/'
        '?project=test_project'
        '&cluster=test_cluster'
        '&service=test_service'
        '&l.sensor=test_sensor'
        '&b=2020-10-02T12%3A00%3A00.000Z'
        '&e=2020-10-02T12%3A06%3A00.000Z'
    )

    test_data = [
        {
            'entry_point_id': 'entry',
            'input_data': {'input_type': 'solomon_url', 'data': solomon_url},
        },
    ]

    test_case = {
        'out_point_id': 'alert',
        'start_time': '2020-10-02T12:03:30.000Z',
        'end_time': '2020-10-02T12:05:00.000Z',
        'check_type': 'has_alert',
        'check_params': {'min_alert_state': 'Critical'},
    }

    response = await taxi_hejmdal.post(
        'v1/debug/run-test-case',
        json={
            'schema': NO_DATA_SCHEMA,
            'test_data': test_data,
            'test_case': test_case,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['passed'] is False
    assert (
        resp_json['message']
        == 'Only states less than Critical appeared in the given time range'
    )

    assert 'named_timeseries_list' in resp_json
    assert len(resp_json['named_timeseries_list']) == 2

    data_ts = resp_json['named_timeseries_list'][0]
    assert data_ts['name'] == 'entry_data'
    assert data_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_TS,
        'values': SCHEMA_DEBUG_VALS,
        'type': 'data',
    }

    state_ts = resp_json['named_timeseries_list'][1]
    assert state_ts['name'] == 'alert_state'
    assert state_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_STATE_TS,
        'values': SCHEMA_DEBUG_STATES,
        'type': 'state',
    }


async def test_run_test_case_fail(taxi_hejmdal):
    input_data = {
        'timeseries': {
            'values': SCHEMA_DEBUG_VALS,
            'timestamps': SCHEMA_DEBUG_TS,
        },
        'entry_point_id': 'entry',
    }

    test_data = [
        {
            'entry_point_id': 'entry',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps(input_data),
            },
        },
    ]

    test_case = {
        'out_point_id': 'alert',
        'start_time': '2020-10-02T12:03:30.000Z',
        'end_time': '2020-10-02T12:05:00.000Z',
        'check_type': 'has_alert',
        'check_params': {'min_alert_state': 'Critical'},
    }

    response = await taxi_hejmdal.post(
        'v1/debug/run-test-case',
        json={
            'schema': NO_DATA_SCHEMA,
            'test_data': test_data,
            'test_case': test_case,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['passed'] is False
    assert (
        resp_json['message']
        == 'Only states less than Critical appeared in the given time range'
    )

    assert 'named_timeseries_list' in resp_json
    assert len(resp_json['named_timeseries_list']) == 2

    data_ts = resp_json['named_timeseries_list'][0]
    assert data_ts['name'] == 'entry_data'
    assert data_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_TS,
        'values': SCHEMA_DEBUG_VALS,
        'type': 'data',
    }

    state_ts = resp_json['named_timeseries_list'][1]
    assert state_ts['name'] == 'alert_state'
    assert state_ts['timeseries'] == {
        'timestamps': SCHEMA_DEBUG_STATE_TS,
        'values': SCHEMA_DEBUG_STATES,
        'type': 'state',
    }
