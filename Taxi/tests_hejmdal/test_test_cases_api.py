import datetime
import json

JSON_TS = {
    'timestamps': [
        1234267000,
        1234327000,
        1234387000,
        1234447000,
        1234507000,
        1234567000,
        1234627000,
        1234687000,
        1234747000,
    ],
    'values': [
        1234267000,
        1234327000,
        1234387000,
        1234447000,
        1234507000,
        1234567000,
        1234627000,
        1234687000,
        1234747000,
    ],
}

JSON_DATA_REQ = {
    'schema_id': 'schema_test',
    'description': 'description',
    'entry_point_inputs': [
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
    ],
}


def to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')


async def test_cases_main_test(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Get list
    response = await taxi_hejmdal.post('v1/test-case/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['enabled']) == 1
    assert not resp_json['disabled']
    assert resp_json['enabled'][0]['id'] == 1

    # Create test_data
    response = await taxi_hejmdal.post(
        'v1/test-data/create', json=JSON_DATA_REQ,
    )
    assert response.status_code == 200
    resp_json = response.json()
    test_data_id = resp_json['test_data_id']
    start_time = resp_json['start_time']
    end_time = resp_json['end_time']

    # Create test_case
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_case_id'] == 2

    # Read
    response = await taxi_hejmdal.post('v1/test-case/read?id=2')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_data_id'] == 1
    assert resp_json['schema_id'] == 'schema_test'
    assert resp_json['description'] == 'test case description'
    assert resp_json['is_enabled'] is False
    assert 'test_case_info' in resp_json
    assert resp_json['test_case_info']['start_time'] == start_time
    assert resp_json['test_case_info']['end_time'] == end_time
    assert resp_json['test_case_info']['out_point_id'] == 'alert1'
    assert resp_json['test_case_info']['check_type'] == 'has_alert'
    assert resp_json['test_case_info']['check_params'] == {
        'min_alert_state': 'Warning',
    }

    # Get List
    response = await taxi_hejmdal.post('v1/test-case/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['enabled']) == 1
    assert len(resp_json['disabled']) == 1
    assert resp_json['enabled'][0]['id'] == 1
    assert resp_json['disabled'][0]['id'] == 2

    # Activate
    response = await taxi_hejmdal.post(
        'v1/test-case/activate?id=2&do_activate=true',
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['is_enabled'] is True

    # Check
    response = await taxi_hejmdal.post('v1/test-case/read?id=2')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['description'] == 'test case description'
    assert resp_json['is_enabled'] is True

    # Get List
    response = await taxi_hejmdal.post('v1/test-case/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['enabled']) == 2
    assert not resp_json['disabled']
    assert resp_json['enabled'][0]['id'] == 2
    assert resp_json['enabled'][1]['id'] == 1

    # Delete
    response = await taxi_hejmdal.delete('v1/test-case/delete?id=1')
    assert response.status_code == 200

    # Check
    response = await taxi_hejmdal.post('v1/test-case/read?id=1')
    assert response.status_code == 404

    # Delete again
    response = await taxi_hejmdal.delete('v1/test-case/delete?id=1')
    assert response.status_code == 404

    # Update
    response = await taxi_hejmdal.put(
        'v1/test-case/update?id=2',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'new description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert2',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Critical'},
            },
        },
    )
    assert response.status_code == 200

    # Check
    response = await taxi_hejmdal.post('v1/test-case/read?id=2')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_data_id'] == test_data_id
    assert resp_json['schema_id'] == 'schema_test'
    assert resp_json['description'] == 'new description'
    assert resp_json['is_enabled'] is False
    assert 'test_case_info' in resp_json
    assert resp_json['test_case_info']['start_time'] == start_time
    assert resp_json['test_case_info']['end_time'] == end_time
    assert resp_json['test_case_info']['out_point_id'] == 'alert2'
    assert resp_json['test_case_info']['check_type'] == 'has_alert'
    assert resp_json['test_case_info']['check_params'] == {
        'min_alert_state': 'Critical',
    }


async def test_cases_create_errors(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create test_data
    response = await taxi_hejmdal.post(
        'v1/test-data/create', json=JSON_DATA_REQ,
    )
    assert response.status_code == 200
    resp_json = response.json()
    test_data_id = resp_json['test_data_id']
    start_time = resp_json['start_time']
    end_time = resp_json['end_time']

    # Schema is not exist in database
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'wrong_schema',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Schema is different from used by test_data
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test_2',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Test data is not exist in database
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test',
            'test_data_id': 11,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Time range is out of bounds of test_data
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': '1970-01-01T00:00:00+00:00',
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Wrong check_type
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'wrong_check_type',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Wrong check_params
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Wrong'},
            },
        },
    )
    assert response.status_code == 400


async def test_cases_update_errors(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    # Create test_data
    response = await taxi_hejmdal.post(
        'v1/test-data/create', json=JSON_DATA_REQ,
    )
    assert response.status_code == 200
    resp_json = response.json()
    test_data_id = resp_json['test_data_id']
    start_time = resp_json['start_time']
    end_time = resp_json['end_time']

    # Create test_case
    response = await taxi_hejmdal.post(
        'v1/test-case/create',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['test_case_id'] == 2

    # Update error: schema cannot be changed
    response = await taxi_hejmdal.put(
        'v1/test-case/update?id=2',
        json={
            'schema_id': 'schema_test_2',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Update error: test data not found
    response = await taxi_hejmdal.put(
        'v1/test-case/update?id=2',
        json={
            'schema_id': 'schema_test',
            'test_data_id': 10,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': start_time,
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400

    # Update error: test case range is out of test_data bounds
    response = await taxi_hejmdal.put(
        'v1/test-case/update?id=2',
        json={
            'schema_id': 'schema_test',
            'test_data_id': test_data_id,
            'description': 'test case description',
            'is_enabled': False,
            'test_case_info': {
                'start_time': '1970-01-01T00:00:00+00:00',
                'end_time': end_time,
                'out_point_id': 'alert1',
                'check_type': 'has_alert',
                'check_params': {'min_alert_state': 'Warning'},
            },
        },
    )
    assert response.status_code == 400
