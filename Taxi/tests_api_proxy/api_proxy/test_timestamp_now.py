import pytest

from tests_api_proxy.api_proxy.utils import autotests as tests


async def test_endpoint_with_timestamp_handler(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_timestamp.yaml')
    tests_def = load_yaml('test_with_timestamp.yaml')
    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_endpoint_with_timestamp_handler_runtime(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_timestamp.yaml')
    await endpoints.safely_create_endpoint(
        path='/foo', post_handler=handler_def,
    )
    response = await taxi_api_proxy.post('/foo', params={'test_arg': 'FOO'})
    assert response.status_code == 200
    body = response.json()
    assert body == {'result': '2020-07-07T00:00:00+0000', 'arg': 'FOO'}


# Arslan do it
async def test_endpoint_with_wrong_timestamp_value_handler(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_timestamp.yaml')
    tests_def = load_yaml('test_with_wrong_timestamp.yaml')
    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            tests.body_mismatch_error(
                'simple_test',
                '{"result":"2021-08-12T07:22:40.721471+0000"}',
                '{"result":"2021-08-12T07:22:42.721471+0000"}',
                """{
  result:
  - "2021-08-12T07:22:42.721471+0000"
  + "2021-08-12T07:22:40.721471+0000"
}""",
            ),
        ],
    )


async def test_endpoint_with_invalid_timestamp_value_handler(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_timestamp.yaml')
    tests_def = load_yaml('test_with_invalid_timestamp_value.yaml')
    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            'simple_test',
            'Exception during test execution',
            'Error while parsing timestamp mock. '
            'Make sure you use the format: %Y-%m-%dT%H:%M:%E*S%z '
            'e. g.: 2021-08-12T07:22:40.721471+0000\n',
        ],
    )


async def test_endpoint_with_custom_timestamp_handler(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_custom_timestamp.yaml')
    tests_def = load_yaml('test_with_custom_timestamp.yaml')
    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )


async def test_endpoint_with_invalid_timestamp_handler(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_invalid_timestamp_format.yaml')
    tests_def = load_yaml('test_with_custom_timestamp.yaml')
    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            tests.body_mismatch_error(
                'simple_test',
                '{"result":"2021-08-12T07:22:40"}',
                '{"result":"2021-08-12T07:22:40+0000"}',
                """{
  result:
  - "2021-08-12T07:22:40+0000"
  + "2021-08-12T07:22:40"
}""",
            ),
        ],
    )


async def test_endpoint_with_no_timestamp_mock(
        taxi_api_proxy, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_timestamp.yaml')
    tests_def = load_yaml('test_with_empty_timestamp.yaml')
    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )
