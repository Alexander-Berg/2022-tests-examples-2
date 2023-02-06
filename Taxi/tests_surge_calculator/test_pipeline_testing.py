import pytest


@pytest.mark.now('2021-03-22T04:05:00+0300')
@pytest.mark.parametrize(
    'pipeline,test_name',
    [
        ('regular', 'test'),
        ('global_scope', 'test'),
        ('use_prefetched', 'test'),
        ('native', 'test_native'),
    ],
)
async def test_basic(taxi_surge_calculator, load_json, pipeline, test_name):
    pipeline_body = load_json(f'{pipeline}_pipeline.json')

    pipeline_test = load_json(f'{test_name}.json')
    prefetched_resources = {
        'config': {'empty': {}, 'simple': {'surge_coefficient_precision': 1}},
        'dynamic_config': {'empty': {}},
        'experiments3': {'empty': {}},
        'zone': {'simple': load_json('zone_mock.json')},
    }
    resources_mocks = load_json('resources_mocks.json')
    input_mocks = {
        'simple': {
            'request': {'point_a': [38.0, 51]},
            'required_categories': ['econom'],
        },
    }
    output_checks = load_json('output_checks.json')

    response = await taxi_surge_calculator.post(
        'v1/js/pipeline/test',
        json={
            'pipeline': pipeline_body,
            'tests': [pipeline_test],
            'prefetched_resources_mocks': prefetched_resources,
            'resources_mocks': resources_mocks,
            'input_mocks': input_mocks,
            'output_checks': output_checks,
        },
    )
    assert response.status_code == 200
    testcases = 0
    for test in response.json()['tests_results']['tests']:
        for testcase in test['testcases']:
            # in case of errors see `expected_output.json` as
            # approximately expected result
            if testcase['name'] == 'simple':
                assert testcase['passed'], testcase['error_message']
            else:
                assert not testcase['passed'], testcase['name']
            testcases += 1
    assert testcases == 6
