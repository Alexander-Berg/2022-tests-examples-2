TEST_SCHEMA = {
    'name': 'test_name',
    'type': 'schema',
    'history_data_duration_sec': 10,
    'entry_points': [{'id': 'entry', 'type': 'data_entry_point'}],
    'out_points': [{'id': 'alert', 'type': 'state_out_point'}],
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


async def test_circuit_tester_run_tests_for_schema_dont_break(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={'schema_id': 'test_schema_id', 'schema_json': TEST_SCHEMA},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'WithFailures'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 4


async def test_circuit_tester_run_tests_for_schema_with_break(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id',
            'schema_json': TEST_SCHEMA,
            'break_on_failure': True,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'WithFailures'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 3


async def test_circuit_tester_run_tests_for_schema_success(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={'schema_id': 'test_schema_id_7', 'schema_json': TEST_SCHEMA},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'Success'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 1


async def test_circuit_tester_run_tests_by_ids_success(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id',
            'schema_json': TEST_SCHEMA,
            'test_case_ids': [1, 3],
            'break_on_failure': False,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'Success'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 2


async def test_circuit_tester_run_tests_by_ids_with_failures(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id',
            'schema_json': TEST_SCHEMA,
            'test_case_ids': [1, 2, 3],
            'break_on_failure': False,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'WithFailures'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 3


async def test_circuit_tester_fail_test_no_test_data(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id',
            'schema_json': TEST_SCHEMA,
            'test_case_ids': [6],
            'break_on_failure': False,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'WithFailures'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 1
    test_case_result = resp_json['test_case_results'][0]
    assert test_case_result['test_case_id'] == 6
    assert test_case_result['passed'] is False
    assert (
        test_case_result['error_message']
        == 'data with id 2 is not found in database'
    )


async def test_circuit_tester_ignore_disabled_test(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id_3',
            'schema_json': TEST_SCHEMA,
            'break_on_failure': False,
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['state'] is not None
    assert resp_json['state'] == 'Success'
    assert 'error_message' not in resp_json
    assert resp_json['test_case_results'] is not None
    assert len(resp_json['test_case_results']) == 1
    test_case_result = resp_json['test_case_results'][0]
    assert test_case_result['passed'] is False
    assert test_case_result['ignored'] is True
    assert test_case_result['error_message'] == 'test_case 4 is disabled'


async def test_circuit_tester_error_incorrect_schema(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id',
            'schema_json': TEST_SCHEMA,
            'test_case_ids': [5],
            'break_on_failure': False,
        },
    )
    assert response.status_code == 400
    resp_json = response.json()
    expected_msg = (
        'test_case 5 uses schema \'test_schema_id_2\' but tester uses '
        'schema \'test_schema_id\''
    )
    assert resp_json['message'] == expected_msg


async def test_circuit_tester_error_not_found(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/test-case/run',
        json={
            'schema_id': 'test_schema_id',
            'schema_json': TEST_SCHEMA,
            'test_case_ids': [10],
            'break_on_failure': False,
        },
    )
    assert response.status_code == 404
    resp_json = response.json()
    expected_msg = (
        'requested test cases not found: test_case with id 10 '
        'is not found in database'
    )
    assert resp_json['message'] == expected_msg
