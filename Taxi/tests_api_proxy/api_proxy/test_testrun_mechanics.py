import json
import re
import uuid

import dateutil.parser
import pytest

from tests_api_proxy.api_proxy.utils import autotests as tests


async def test_endpoint_tests_handler(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_handler.yaml')
    tests_def = load_yaml('simple_test.yaml')
    path = '/test/foo/bar' + str(uuid.uuid4())

    await endpoints.safely_create_endpoint(
        path, post_handler=handler_def, tests=tests_def,
    )

    # Launch tests
    response = await taxi_api_proxy.post(
        'admin/v1/endpoints/tests', json={'endpoint': path, 'method': 'post'},
    )
    assert response.status_code == 200
    response = json.loads(response.content)
    assert re.match(r'[\da-fA-F]{16}', response['test_run_id'])
    dateutil.parser.isoparse(response['created'])
    assert response['status'] == 'success'
    assert 'messages' not in response


@pytest.mark.parametrize(
    'code,success,errors',
    [
        (200, True, None),
        (400, False, [tests.code_mismatch_error('simple_test', 200, 400)]),
    ],
)
async def test_simple_testrun(
        taxi_api_proxy, endpoints, load_yaml, code, success, errors,
):
    handler_def = load_yaml('simple_handler.yaml')
    tests_def = load_yaml('simple_test.yaml')

    response = tests_def[0]['source']['expectations']['response']
    response['status-code'] = code

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors,
    )


async def test_multiple_tests(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_handler.yaml')
    tests_def = load_yaml('multiple_tests.yaml')

    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        success=False,
        errors=[
            tests.body_mismatch_error(
                'multiple_test_2',
                '{"result":"Ok"}',
                '{"result":"wrong"}',
                '{\n  result:\n  - "wrong"\n  + "Ok"\n}',
            ),
            tests.code_mismatch_error('multiple_test_3', 200, 401),
            tests.headers_mismatch_error(
                'multiple_test_4',
                '{"X-Test-Header":"test"}',
                '{"X-Test-Header":"error"}',
                """{
  X-Test-Header:
  - "error"
  + "test"
}""",
            ),
            tests.body_mismatch_error(
                'multiple_test_5',
                '{"arg":"test","result":"Ok"}',
                '{"result":"Ok"}',
                '{\n+ arg: "test"\n}',
            ),
            tests.code_mismatch_error('multiple_test_6', 200, 401)
            + tests.body_mismatch_error(
                'multiple_test_6',
                '{"result":"Ok"}',
                '{"result":"Bad Request"}',
                '{\n  result:\n  - "Bad Request"\n  + "Ok"\n}',
            ),
            tests.exception_error(
                'multiple_test_7',
                (
                    'object is neither Map nor json. location stack: '
                    'responses[0].body#object[0].value#switch.input#get; '
                    'responses[0].body#object[0].value#switch; '
                    'responses[0].body#object; responses; /; '
                ),
            ),
        ],
    )


async def test_test_with_deps(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_handler.yaml')
    tests_def = load_yaml('test_with_deps.yaml')
    path = '/test/foo/bar' + str(uuid.uuid4())

    with pytest.raises(endpoints.Failure) as failure:
        await endpoints.safely_create_endpoint(
            path, post_handler=handler_def, tests=tests_def, check_draft=False,
        )

    assert failure.value.response.status_code == 400
    body = json.loads(failure.value.response.content)
    assert body['code'] == 'validation_failed'
    assert (
        body['details']['errors'][0]['message']
        == 'Test operator \'values\' contains dependency on experiments. '
        'This is not supported now'
    )


async def test_test_with_content_type(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('handler_with_text_content_type.yaml')
    tests_def = load_yaml('test_with_content_type.yaml')

    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        success=False,
        errors=[
            tests.content_type_mismatch_error(
                'test_with_content_type', 'text', 'application/json',
            ),
        ],
    )


async def test_test_with_auth_context(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('handler_with_auth_context.yaml')
    tests_def = load_yaml('test_with_auth_context.yaml')

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success=True,
    )


async def test_test_with_duplicating_ids(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_handler.yaml')
    tests_def = load_yaml('test_with_duplicating_ids.yaml')
    path = '/test/foo/bar' + str(uuid.uuid4())

    with pytest.raises(endpoints.Failure) as failure:
        await endpoints.safely_create_endpoint(
            path, post_handler=handler_def, tests=tests_def, check_draft=False,
        )

    assert failure.value.response.status_code == 400
    body = json.loads(failure.value.response.content)
    assert body['code'] == 'validation_failed'
    assert (
        body['details']['errors'][0]['message']
        == 'Test id shall be unique: \'duplicating_test_name\''
    )


@pytest.mark.parametrize(
    'req_arc,check_url,success,errors',
    [
        ('onikakushi-hen', False, True, []),
        (
            'watanagashi-hen',
            False,
            False,
            [
                tests.mock_request_mismatch(
                    'test_with_mock_path_params',
                    'library',
                    'path-params',
                    '{"arc":"watanagashi-hen"'
                    ',"novel":"higurahi-no-naku-koro-ni"}',
                    '{"arc":"onikakushi-hen"'
                    ',"novel":"higurahi-no-naku-koro-ni"}',
                    '{\n  arc:\n  - "onikakushi-hen"'
                    '\n  + "watanagashi-hen"\n}',
                ),
            ],
        ),
        (
            'watanagashi-hen',
            True,
            False,
            [
                tests.mock_request_mismatch(
                    'test_with_mock_path_params',
                    'library',
                    'url',
                    'http://lib-url/higurahi-no-naku-koro-ni-watanagashi-hen',
                    'http://lib-url/higurahi-no-naku-koro-ni-onikakushi-hen',
                ),
            ],
        ),
    ],
)
async def test_test_with_source_variable_path_url(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        req_arc,
        check_url,
        success,
        errors,
):
    handler_def = load_yaml('handler_with_source_path_params.yaml')
    tests_def = load_yaml('test_with_mock_path_params.yaml')

    if check_url:
        exp_req = tests_def[0]['mocks'][0]['expectations']['request']
        kwargs = exp_req.pop('path-params')
        exp_req['url'] = 'http://lib-url/{novel}-{arc}'.format(**kwargs)

    tests_def[0]['source']['request']['body']['arc'] = req_arc

    await resources.safely_create_resource(
        resource_id='library',
        url='http://lib-url/{novel}-{arc}',
        method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors,
    )


@pytest.mark.parametrize(
    'city,success,errors',
    [
        ('yoburg', True, []),
        (
            'shenzhen',
            False,
            [
                tests.url_path_params_mismatch_error(
                    'test_with_endpoint_path_params',
                    '{"category":"cookies","city":"yoburg"}',
                    '{"city":"shenzhen","category":"cookies"}',
                    '{\n  city:\n  - "shenzhen"\n  + "yoburg"\n}',
                ),
            ],
        ),
    ],
)
async def test_endpoint_with_variable_path_url(
        taxi_api_proxy, resources, endpoints, load_yaml, city, success, errors,
):
    handler_def = load_yaml('handler_with_endpoint_path_params.yaml')
    tests_def = load_yaml('test_with_endpoint_path_params.yaml')

    tests_def[0]['source']['expectations']['path-params']['city'] = city

    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        success=success,
        errors=errors,
        path=r'/lavka/(?<city>\w+)/catalog/(?<category>\w+)/menu',
    )


@pytest.mark.parametrize(
    'code,mock_resource,success,errors',
    [
        (200, 'resource', True, None),
        (
            500,
            'resource',
            False,
            [
                tests.exception_error(
                    'test_with_mock',
                    'Raise for status exception, code = 500: '
                    'source_id=0 (test-resource). location stack: '
                    'sources[0]; sources; responses; /; ',
                ),
            ],
        ),
        (
            200,
            'not-exist',
            False,
            [
                tests.exception_error(
                    'test_with_mock', 'no such resource: "not-exist"',
                ),
            ],
        ),
        (
            200,
            None,
            False,
            [
                '%s: %s\n'
                % (
                    'test_with_mock',
                    'Failed to find mock for resource [id=resource] with url: '
                    '\'http://test-url\'. Have you registered it?. location '
                    'stack: sources[0]; sources; responses; /; ',
                ),
            ],
        ),
    ],
)
async def test_test_with_source(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        code,
        mock_resource,
        success,
        errors,
):
    handler_def = load_yaml('handler_with_source.yaml')
    tests_def = load_yaml('test_with_mock.yaml')

    tests_def[0]['mocks'][0]['response']['status-code'] = code

    if mock_resource:
        tests_def[0]['mocks'][0]['resource'] = mock_resource
    else:
        tests_def[0].pop('mocks')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors,
    )


@pytest.mark.parametrize(
    'expected_count,success,errors',
    [
        (1, True, None),
        (2, False, [tests.call_count_error('test_with_mock', 1, 2)]),
    ],
)
async def test_call_count(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        expected_count,
        success,
        errors,
):
    handler_def = load_yaml('handler_with_source.yaml')
    tests_def = load_yaml('test_with_mock.yaml')

    tests_def[0]['mocks'][0]['expectations']['call-count'] = expected_count

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors,
    )


@pytest.mark.parametrize(
    'failure_type,success,errors',
    [
        (None, True, None),
        (
            'before',
            False,
            [
                tests.call_order_mismatch(
                    'hierarchy_test', 'resource1', 'before', 'resource2',
                ),
            ],
        ),
        (
            'after',
            False,
            [
                tests.call_order_mismatch(
                    'hierarchy_test', 'resource2', 'after', 'resource1',
                ),
            ],
        ),
    ],
)
async def test_call_hierarchy(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        failure_type,
        success,
        errors,
):
    handler_def = load_yaml('handler_with_source_hierarchy.yaml')
    tests_def = load_yaml('test_with_call_hierarchy.yaml')

    if failure_type:
        # resource1 will be called after resource3
        handler_def['sources'][0].pop('before')
        handler_def['sources'][0]['after'] = ['test-resource3']
    if failure_type == 'after':
        # Removing call order expectations from resource1.
        # Thus test will start checking resource2 call order
        tests_def[0]['mocks'][0]['expectations'].pop('called-before')

    for i in range(1, 4):
        await resources.safely_create_resource(
            resource_id='resource' + str(i),
            url='http://test-url' + str(i),
            method='post',
        )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors,
    )


@pytest.mark.parametrize(
    'failure_type,success,errors',
    [
        (None, True, None),
        (
            'method',
            False,
            [
                tests.mock_request_mismatch(
                    'test_with_mock_asserts',
                    'resource1',
                    'method',
                    '"put"',
                    '"get"',
                    0,
                ),
            ],
        ),
        (
            'query',
            False,
            [
                tests.mock_request_mismatch(
                    'test_with_mock_asserts',
                    'resource1',
                    'query',
                    '{"arg2":"wrong"}',
                    '{"arg1":"test-arg"}',
                    '{\n- arg1: "test-arg"\n+ arg2: "wrong"\n}',
                    0,
                ),
            ],
        ),
        (
            'body',
            False,
            [
                tests.mock_request_mismatch(
                    'test_with_mock_asserts',
                    'resource2',
                    'body',
                    '{"request":1234}',
                    '{"request":5678}',
                    '{\n  request:\n  - 5678\n  + 1234\n}',
                    1,
                ),
            ],
        ),
        (
            'content-type',
            False,
            [
                tests.mock_request_mismatch(
                    'test_with_mock_asserts',
                    'resource2',
                    'content type',
                    '"text"',
                    '"application/json"',
                    None,
                    1,
                ),
            ],
        ),
    ],
)
async def test_request_check_in_mock(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        failure_type,
        success,
        errors,
):
    handler_def = load_yaml('handler_with_two_sources.yaml')
    tests_def = load_yaml('test_with_mock_asserts.yaml')

    if failure_type == 'query':
        handler_def['sources'][0]['query'] = {'arg2': 'wrong'}
    elif failure_type == 'body':
        handler_def['sources'][1]['body'] = {'request': 1234}
    elif failure_type == 'content-type':
        handler_def['sources'][1]['content-type'] = 'text'
        handler_def['sources'][1]['body'] = 'test-string'

    await resources.safely_create_resource(
        resource_id='resource1',
        url='http://test-url1',
        method='get' if failure_type != 'method' else 'put',
    )
    await resources.safely_create_resource(
        resource_id='resource2', url='http://test-url2', method='post',
    )
    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors,
    )


async def test_parallel_resource_call(
        taxi_api_proxy, resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_source.yaml')
    tests_def = load_yaml('test_with_mock.yaml')

    handler_def['sources'] = []
    response = handler_def['responses'][0]
    expectations = tests_def[0]['source']['expectations']
    response.pop('body#object')
    response['body#concat-objects'] = []
    expectations['response'].pop('body')
    expectations['response']['body'] = {}
    tests_def[0]['mocks'] = []

    # Create many resources which will be requested in parallel
    for i in range(100):
        name = 'test-resource' + str(i)
        resource_name = 'resource' + str(i)
        handler_def['sources'].append(
            {
                'id': name,
                'content-type': 'application/json',
                'resource': resource_name,
                'body': {},
            },
        )
        response['body#concat-objects'].append(
            {'value#source-response-body': name},
        )

        await resources.safely_create_resource(
            resource_id='resource' + str(i),
            url='http://test-url' + str(i),
            method='post',
        )

        expectations['response']['body']['value' + str(i)] = str(i)
        tests_def[0]['mocks'].append(
            {
                'resource': resource_name,
                'response': {
                    'status-code': 200,
                    'body': {'value' + str(i): str(i)},
                },
                'expectations': {'call-count': 1},
            },
        )
    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success=True,
    )


@pytest.mark.parametrize(
    'cfg_name,success,errors,error_json',
    [
        # expected to use value from test mock
        ('FOO_CONFIG', True, [], []),
        # expected to pass test but fail validation since
        # handle with non-existing config cannot be saved
        (
            'BAR_CONFIG',
            False,
            [],
            [
                {
                    'code': 'validation_failed',
                    'message': (
                        'Endpoint refers to non-existing configs: BAR_CONFIG'
                    ),
                },
            ],
        ),
        # should not find that config while running test
        # despite it is defined on config service
        (
            'BUZ_CONFIG',
            False,
            [
                tests.config_not_loaded(
                    'test_with_mock_config',
                    'BUZ_CONFIG',
                    [
                        '/',
                        'responses[0].body.xget#xget',
                        'responses[0].body',
                        'responses',
                        '/',
                    ],
                ),
            ],
            [],
        ),
    ],
)
@pytest.mark.disable_config_check
@pytest.mark.config(FOO_CONFIG='config_to_overwrite', BUZ_CONFIG='buz_config')
async def test_mock_config(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        cfg_name,
        success,
        errors,
        error_json,
):
    handler_def = load_yaml('test_with_mock_config_handler.yaml')
    tests_def = load_yaml('test_with_mock_config.yaml')
    # tests_defs defines FOO_CONFIG and BAR_CONFIG mocks

    body = handler_def['responses'][0]['body']
    body['op#taxi-config'] = cfg_name
    body['xget#xget'] = f'/taxi-configs/{cfg_name}'

    body = tests_def[0]['source']['expectations']['response']['body']
    body['op'] = cfg_name.lower()
    body['xget'] = cfg_name.lower()

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success, errors, error_json,
    )


async def test_exception_in_test(
        taxi_api_proxy, resources, endpoints, testpoint, load_yaml, mockserver,
):
    @mockserver.json_handler('/mock-me')
    def mock_resource(request):
        return {
            'modes': [
                {'mode': 'grocery', 'parameters': {'available': True}},
                {'mode': 'eats', 'parameters': {'available': True}},
            ],
        }

    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    handler_def = load_yaml('bad_handler.yaml')
    tests_def = load_yaml('bad_handler_test.yaml')
    path = '/test/foo/bar' + str(uuid.uuid4())
    await endpoints.safely_create_endpoint(
        path, post_handler=handler_def, tests=tests_def,
    )
    assert mock_resource.times_called == 0


async def test_mock_assert_with_fail_policy(
        taxi_api_proxy, resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_source_and_fail_policy.yaml')
    tests_def = load_yaml('test_with_mock.yaml')

    tests_def[0]['mocks'][0]['expectations']['request'] = {
        'body': {
            'value': 5678,
            'old': False,
            'arr': ['a', 'B', 'c'],
            'deep': {'x': 'def', 'old': True},
        },
    }

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )
    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            tests.mock_request_mismatch(
                'test_with_mock',
                'resource',
                'body',
                '{"new":true,"value":1234,'
                '"deep":{"x":"abc"},"arr":["a","b","c","d"]}',
                '{"old":false,"value":5678,'
                '"deep":{"x":"def","old":true},"arr":["a","B","c"]}',
                """{
  arr: [
    1:
    - "B"
    + "b"
  + 3: "d"
  ]
  deep: {
  - old: true
    x:
    - "def"
    + "abc"
  }
- old: false
  value:
  - 5678
  + 1234
+ new: true
}""",
                0,
            ),
        ],
    )


@pytest.mark.parametrize(
    'fail,code,called',
    [
        ('timeout', 408, 1),
        ('fallbacking', 200, 0),
        ('tech', 503, 1),
        ('source_validation', 400, 1),
        ('rps-limit-breach', 429, 0),
    ],
)
async def test_mock_with_fallback(
        taxi_api_proxy, resources, endpoints, load_yaml, fail, code, called,
):
    handler_def = load_yaml('handler_with_source_and_fallbacks.yaml')
    test_def = load_yaml('test_with_mock_source_fail.yaml')

    exp_resp = test_def[0]['source']['expectations']['response']
    exp_resp['status-code'] = code
    exp_resp['body']['message'] = fail

    mock = test_def[0]['mocks'][0]
    mock['exception'] = fail
    mock['expectations']['call-count'] = called

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, test_def, success=True,
    )


@pytest.mark.parametrize(
    'ex_foo,ex_bar', [(None, None), ('F00', None), (None, 'B4R')],
)
async def test_mock_experiment(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        experiments3,
        resources,
        ex_foo,
        ex_bar,
):
    handler_def = load_yaml('test_with_mock_experiment_handler.yaml')
    tests_def = load_yaml('test_with_mock_experiment.yaml')

    path = '/test/foo/bar'

    for (name, value) in (('ex-foo', ex_foo), ('ex-bar', ex_bar)):
        if not value:
            continue
        experiments3.add_experiment(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name=name,
            consumers=['api-proxy' + path],
            clauses=[],
            default_value=value,
        )

    await taxi_api_proxy.invalidate_caches()

    await endpoints.safely_create_endpoint(
        path, post_handler=handler_def, tests=tests_def,
    )


@pytest.mark.parametrize(
    'handler_kwargs,handler_consumer,success,errors',
    [
        (
            [dict(key='foo', value='FOO', type='string', whitelisted=True)],
            'DAT_CONSUMER',
            True,
            [],
        ),
        (
            [dict(key='foo', value='FOO', type='string', whitelisted=True)],
            'NOT_DAT_CONSUMER',
            False,
            [
                tests.experiments_consumer_mismatch(
                    'experiment_kwargs_test',
                    'NOT_DAT_CONSUMER',
                    'DAT_CONSUMER',
                ),
            ],
        ),
        (
            [dict(key='foo', value='BAR', type='string', whitelisted=True)],
            'DAT_CONSUMER',
            False,
            [
                tests.experiments_kwargs_mismatch(
                    'experiment_kwargs_test', diff=[('foo', 'FOO', 'BAR')],
                ),
            ],
        ),
        (
            [dict(key='bar', value='BAR', type='string', whitelisted=True)],
            'DAT_CONSUMER',
            False,
            [
                tests.experiments_kwargs_mismatch(
                    'experiment_kwargs_test', extra=['bar'], lost=['foo'],
                ),
            ],
        ),
    ],
)
async def test_test_with_exp_kwargs(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        handler_consumer,
        handler_kwargs,
        success,
        errors,
):
    handler_def = load_yaml('test_with_experiments_kwargs_handler.yaml')
    tests_def = load_yaml('test_with_experiments_kwargs.yaml')

    handler_def['experiments']['kwargs'] = handler_kwargs
    handler_def['experiments']['consumer'] = handler_consumer

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success=success, errors=errors,
    )


@pytest.mark.parametrize(
    'handler_kwargs,handler_consumer,success,errors',
    [
        (
            [dict(key='foo', value='FOO', type='string', whitelisted=True)],
            'DAT_CONSUMER',
            True,
            [],
        ),
        (
            [dict(key='foo', value='FOO', type='string', whitelisted=True)],
            'NOT_DAT_CONSUMER',
            False,
            [
                tests.configs_consumer_mismatch(
                    'config_kwargs_test', 'NOT_DAT_CONSUMER', 'DAT_CONSUMER',
                ),
            ],
        ),
        (
            [dict(key='foo', value='BAR', type='string', whitelisted=True)],
            'DAT_CONSUMER',
            False,
            [
                tests.configs_kwargs_mismatch(
                    'config_kwargs_test', diff=[('foo', 'FOO', 'BAR')],
                ),
            ],
        ),
        (
            [dict(key='bar', value='BAR', type='string', whitelisted=True)],
            'DAT_CONSUMER',
            False,
            [
                tests.configs_kwargs_mismatch(
                    'config_kwargs_test', extra=['bar'], lost=['foo'],
                ),
            ],
        ),
    ],
)
async def test_test_with_conf_kwargs(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        handler_consumer,
        handler_kwargs,
        success,
        errors,
):
    handler_def = load_yaml('test_with_configs_kwargs_handler.yaml')
    tests_def = load_yaml('test_with_configs_kwargs.yaml')

    handler_def['configs']['kwargs'] = handler_kwargs
    handler_def['configs']['consumer'] = handler_consumer

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, success=success, errors=errors,
    )


async def test_parametrized_test(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_handler.yaml')
    tests_def = load_yaml('test_with_parameters.yaml')

    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        success=False,
        errors=[
            tests.body_mismatch_error(
                'parametrized_test[status1-text0]',
                '{"result":"Bad request"}',
                '{"result":"Ok"}',
                '{\n  result:\n  - "Ok"\n  + "Bad request"\n}',
            ),
            tests.body_mismatch_error(
                'parametrized_test[status0-text1]',
                '{"result":"Ok"}',
                '{"result":"Bad request"}',
                '{\n  result:\n  - "Bad request"\n  + "Ok"\n}',
            ),
        ],
    )


async def test_resource_with_rps_limit(
        taxi_api_proxy, resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_with_source.yaml')
    tests_def = load_yaml('test_with_mock.yaml')

    tests_def[0]['mocks'][0]['response']['status-code'] = 200
    tests_def[0]['mocks'][0]['resource'] = 'resource'

    await resources.safely_create_resource(
        resource_id='resource',
        url='http://test-url',
        method='post',
        rps_limit=100,
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )


async def test_with_operator_any(
        taxi_api_proxy, resources, endpoints, load_yaml, mockserver,
):
    handler_def = load_yaml('handler_with_any.yaml')
    tests_def = load_yaml('test_with_any.yaml')

    mock_resources = [
        'exp3-matcher-typed-experiments',
        'zalogin-v1-launch-auth',
    ]

    for mock_id in mock_resources:
        await resources.safely_create_resource(
            resource_id=mock_id,
            url=mockserver.url(mock_id),
            method='post',
            rps_limit=100,
        )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )
