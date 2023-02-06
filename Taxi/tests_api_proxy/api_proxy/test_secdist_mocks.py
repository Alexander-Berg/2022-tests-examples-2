import pytest

from tests_api_proxy.api_proxy.utils import autotests as tests


@pytest.mark.parametrize(
    'test_file,key_to_request,success,errors',
    [
        ('test_with_mocked_secdist_good.yaml', 'foo', True, []),
        (
            'test_with_mocked_secdist_failed.yaml',
            'foo',
            False,
            [
                tests.body_mismatch_error(
                    'config_mocked_secdist_test',
                    '{"result":"definetely not bar"}',
                    '{"result":"bar"}',
                    '{\n  result:\n  - \"bar\"\n  + \"definetely not bar\"\n}',
                ),
            ],
        ),
        (
            'test_with_no_mocked_secdist_but_exists.yaml',
            'some-value-for-testsuite',
            True,
            [],
        ),
        (
            'test_with_no_mocked_secdist.yaml',
            'foo',
            False,
            [
                tests.secdist_no_toplevel(
                    'no_secdist_mocks',
                    'foo',
                    'responses[0].body.result#taxi-secdist',
                    'responses[0].body',
                    'responses',
                    '/',
                ),
            ],
        ),
        ('test_with_mocked_secdist_good_with_agl.yaml', 'foo', True, []),
    ],
)
async def test_test_with_mocked_secdist(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        test_file,
        key_to_request,
        success,
        errors,
):
    handler_def = load_yaml('test_with_mocked_secdist_handler.yaml')
    tests_def = load_yaml(test_file)
    handler_def['responses'][0]['body']['result#taxi-secdist'] = key_to_request
    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success=success, errors=errors,
    )
