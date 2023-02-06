import pytest


@pytest.mark.now('2021-03-22T04:05:00+0300')
async def test_basic(taxi_eda_surge_calculator, load_json):
    pipeline = load_json('pipeline.json')

    resources_mocks = load_json('resources_mocks.json')
    input_mocks = {
        'surge_input_default': {'places': [{'place_id': 1, 'zone_id': None}]},
        'surge_input_test': {'places': [{'place_id': 1, 'zone_id': None}]},
    }
    output_checks = load_json('output_checks.json')

    response = await taxi_eda_surge_calculator.post(
        'v1/js/pipeline/test',
        json={
            'pipeline': pipeline,
            'tests': [
                load_json('test.json'),
                load_json('test1.json'),
                load_json('test2.json'),
            ],
            'prefetched_resources_mocks': {},
            'resources_mocks': resources_mocks,
            'input_mocks': input_mocks,
            'output_checks': output_checks,
        },
    )
    assert response.status_code == 200
    testcases = 0
    for test in response.json()['tests_results']['tests']:
        for testcase in test['testcases']:
            assert testcase['passed'], testcase['error_message']
            testcases += 1
    assert testcases == 5
