import datetime
import json

TIMESTAMPS = [
    1234267000,
    1234327000,
    1234387000,
    1234447000,
    1234507000,
    1234567000,
    1234627000,
    1234687000,
    1234747000,
]

VALUES = [0.94, 26.916, 1.376, 5.084, 1.441, 1.27, 1.063, 0.731, 0.882]

JSON_TS = {'timestamps': TIMESTAMPS, 'values': VALUES}

JSON_DATA_DB = [
    {'entry_point_id': 'entry1', 'timeseries': JSON_TS},
    {'entry_point_id': 'entry2', 'timeseries': JSON_TS},
]


def build_json_body(schema_id, description):
    json_data_req = [
        {
            'entry_point_id': 'entry1',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps({'timeseries': JSON_TS}),
            },
        },
        {
            'entry_point_id': 'entry2',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps({'timeseries': JSON_TS}),
            },
        },
    ]
    return {
        'schema_id': schema_id,
        'description': description,
        'entry_point_inputs': json_data_req,
    }


def to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def check_create_result(pgsql, response, description):
    # Check DB data
    cursor = pgsql['hejmdal'].cursor()
    query = (
        'select test_id, description, schema_id, start_time, '
        + 'precedent_time, end_time, data, meta '
        + ' from test_data'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    test_data = db_res[0]
    assert len(test_data) == 8
    assert test_data[0] == 1
    assert test_data[1] == description
    assert test_data[2] == 'schema_test'
    assert test_data[3] == to_datetime('1970-01-15T06:51:07.000Z')
    assert test_data[4] == to_datetime('1970-01-15T06:51:07.000Z')
    assert test_data[5] == to_datetime('1970-01-15T06:59:07.000Z')
    assert test_data[6] == JSON_DATA_DB
    assert test_data[7]['source'] == 'test-data/create'
    assert test_data[7]['created'] is not None

    # Check v1/test-data/read data
    json_ts_with_type = {
        'timestamps': TIMESTAMPS,
        'values': VALUES,
        'type': 'data',
    }
    response_json_data = [
        {'name': 'entry1', 'timeseries': json_ts_with_type},
        {'name': 'entry2', 'timeseries': json_ts_with_type},
    ]

    assert response.status_code == 200
    resp_json = response.json()

    assert resp_json['description'] == description
    assert resp_json['schema_id'] == 'schema_test'
    assert resp_json['start_time'] == '1970-01-15T06:51:07+00:00'
    assert resp_json['end_time'] == '1970-01-15T06:59:07+00:00'
    assert resp_json['test_data'] == response_json_data


async def test_data_from_json(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create
    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test', 'test_data_from_json'),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_data_id'] is not None
    assert resp_json['test_data_id'] == 1
    assert resp_json['start_time'] is not None
    assert resp_json['end_time'] is not None

    # Check
    read_response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    check_create_result(pgsql, read_response, 'test_data_from_json')


async def test_data_create_from_solomon(mockserver, taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    solomon_data_req = [
        {
            'entry_point_id': 'entry1',
            'input_data': {
                'input_type': 'solomon_url',
                'data': (
                    'https://solomon.yandex-team.ru/'
                    '?project=test_project'
                    '&cluster=test_cluster'
                    '&service=test_service'
                    '&l.sensor=test_sensor'
                    '&b=1970-01-15T06%3A51%3A07.000Z'
                    '&e=1970-01-15T06%3A59%3A10.000Z'
                ),
            },
        },
        {
            'entry_point_id': 'entry2',
            'input_data': {
                'input_type': 'solomon_url',
                'data': (
                    'https://solomon.yandex-team.ru/'
                    '?project=test_project'
                    '&cluster=test_cluster'
                    '&service=test_service'
                    '&l.sensor=test_sensor'
                    '&b=1970-01-15T06%3A51%3A07.000Z'
                    '&e=1970-01-15T06%3A59%3A10.000Z'
                ),
            },
        },
    ]

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
                        **JSON_TS,
                    },
                },
            ],
        }

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json={
            'schema_id': 'schema_test',
            'description': 'test_data_create_from_solomon',
            'entry_point_inputs': solomon_data_req,
        },
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_data_id'] is not None
    assert resp_json['test_data_id'] == 1
    assert resp_json['start_time'] is not None
    assert resp_json['end_time'] is not None

    # Check
    read_response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    check_create_result(pgsql, read_response, 'test_data_create_from_solomon')


async def test_data_create_from_yasm(mockserver, taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    yasm_data_req = [
        {
            'entry_point_id': 'entry1',
            'input_data': {
                'input_type': 'yasm',
                'data': {
                    'st': 1234267,
                    'et': 1234757,
                    'period': 5,
                    'host': 'test_host',
                    'signals': ['itype=test_itype:test_signal'],
                },
            },
        },
        {
            'entry_point_id': 'entry2',
            'input_data': {
                'input_type': 'yasm',
                'data': {
                    'st': 1234267,
                    'et': 1234757,
                    'period': 5,
                    'host': 'test_host',
                    'signals': ['itype=test_itype:test_signal'],
                },
            },
        },
    ]

    @mockserver.json_handler('/yasm/hist/series/')
    def _mock_yasm_signals_data(request):
        return {
            'status': 'ok',
            'response': {
                'errors': [],
                'test_host5_0': {
                    'content': {
                        'timeline': [
                            1234267,
                            1234327,
                            1234387,
                            1234447,
                            1234507,
                            1234567,
                            1234627,
                            1234687,
                            1234747,
                        ],
                        'values': {'itype=test_itype:test_signal': VALUES},
                    },
                    'messages': [],
                },
            },
        }

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json={
            'schema_id': 'schema_test',
            'description': 'test_data_create_from_yasm',
            'entry_point_inputs': yasm_data_req,
        },
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_data_id'] is not None
    assert resp_json['test_data_id'] == 1
    assert resp_json['start_time'] is not None
    assert resp_json['end_time'] is not None

    # Check
    read_response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    check_create_result(pgsql, read_response, 'test_data_create_from_yasm')


async def test_data_create_error_schema_not_found(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body(
            'schema_is_not_exist', 'test_data_create_error_schema_not_found',
        ),
    )
    assert response.status_code == 400


async def test_data_create_error_template(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body(
            'template_test', 'test_data_create_error_template',
        ),
    )
    assert response.status_code == 400


async def test_data_create_error_no_entry_point(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    json_data_req = [
        {
            'entry_point_id': 'entry1',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps({'timeseries': JSON_TS}),
            },
        },
        {
            'entry_point_id': 'wrong_entry',
            'input_data': {
                'input_type': 'json',
                'data': json.dumps({'timeseries': JSON_TS}),
            },
        },
    ]

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json={
            'schema_id': 'schema_test',
            'description': 'test_data_create_from_json',
            'entry_point_inputs': json_data_req,
        },
    )
    assert response.status_code == 400


async def test_data_read_error_not_found(taxi_hejmdal):
    response = await taxi_hejmdal.post('v1/test-data/read?id=12')
    assert response.status_code == 404


async def test_data_delete(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create
    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test', 'test_data_delete'),
    )
    assert response.json()['test_data_id'] == 1

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 200

    # Delete
    response = await taxi_hejmdal.delete('v1/test-data/delete?id=1')
    assert response.status_code == 200

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 404

    # Delete second time
    response = await taxi_hejmdal.delete('v1/test-data/delete?id=1')
    assert response.status_code == 404


async def test_data_update(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create
    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test', 'test_data_update'),
    )
    assert response.status_code == 200
    assert response.json()['test_data_id'] == 1

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 200
    assert response.json()['description'] == 'test_data_update'

    # Update
    response = await taxi_hejmdal.put(
        'v1/test-data/update?id=1',
        json=build_json_body('schema_test', 'test_data_update_new'),
    )
    assert response.status_code == 200
    assert response.json()['test_data_id'] == 1

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 200
    assert response.json()['description'] == 'test_data_update_new'

    # Update again
    response = await taxi_hejmdal.put(
        'v1/test-data/update?id=1',
        json=build_json_body('schema_test', 'test_data_update_very_new'),
    )
    assert response.status_code == 200

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 200
    assert response.json()['description'] == 'test_data_update_very_new'

    # Check meta
    cursor = pgsql['hejmdal'].cursor()
    query = 'select meta from test_data where test_id=1'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert len(db_res[0]) == 1
    meta = db_res[0][0]
    assert meta['created'] is not None
    assert meta['source'] == 'test-data/create'
    assert len(meta['updated']) == 2


async def test_data_update_error_not_found(taxi_hejmdal):
    response = await taxi_hejmdal.put(
        'v1/test-data/update?id=2',
        json=build_json_body('schema_test', 'test_data_update_new'),
    )
    assert response.status_code == 404


async def test_data_update_error_change_schema(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create
    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test', 'test_data_update'),
    )
    assert response.status_code == 200
    assert response.json()['test_data_id'] == 1

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 200
    assert response.json()['description'] == 'test_data_update'

    # Update
    response = await taxi_hejmdal.put(
        'v1/test-data/update?id=1',
        json=build_json_body('schema_test_new', 'test_data_update_new'),
    )
    assert response.status_code == 400

    # Check
    response = await taxi_hejmdal.post('v1/test-data/read?id=1')
    assert response.status_code == 200
    assert response.json()['description'] == 'test_data_update'


async def test_data_list(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create
    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test', 'test_data_list_1'),
    )
    assert response.status_code == 200
    assert response.json()['test_data_id'] == 1

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test', 'test_data_list_2'),
    )
    assert response.status_code == 200
    assert response.json()['test_data_id'] == 2

    response = await taxi_hejmdal.post(
        'v1/test-data/create',
        json=build_json_body('schema_test_2', 'test_data_list_3'),
    )
    assert response.status_code == 200
    assert response.json()['test_data_id'] == 3

    # Get List
    response = await taxi_hejmdal.post('v1/test-data/list')
    assert response.status_code == 200
    resp_json = response.json()
    items = resp_json['test_data_items']
    assert len(items) == 3
    assert items[0]['id'] == 3
    assert items[0]['description'] == 'test_data_list_3'
    assert items[0]['schema_id'] == 'schema_test_2'
    assert 'test_case_ids' in items[0]
    assert len(items[0]['test_case_ids']) == 1
    assert items[0]['test_case_ids'][0] == 1

    assert items[1]['id'] == 2
    assert items[1]['description'] == 'test_data_list_2'
    assert items[1]['schema_id'] == 'schema_test'
    assert 'test_case_ids' not in items[1]

    assert items[2]['id'] == 1
    assert items[2]['description'] == 'test_data_list_1'
    assert items[2]['schema_id'] == 'schema_test'
    assert 'test_case_ids' not in items[2]
