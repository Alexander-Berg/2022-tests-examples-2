from tests_api_proxy.api_proxy.utils import autotests as tests


async def test_xget_disabled_source_no_default_value(
        resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_disabled_source_no_default_value.yaml')
    tests_def = load_yaml('test_disabled_source_no_default_value.yaml')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )
    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            tests.disabled_source_error(
                'test_disabled_source_no_default_value',
                'test-resource',
                [
                    '/',
                    'responses[0].body#object[0].value#xget',
                    'responses[0].body#object[0].value#xget',
                    'responses[0].body#object',
                    'responses',
                    '/',
                ],
            ),
        ],
    )


async def test_xget_disabled_source_default_value(
        resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_disabled_source_default_value.yaml')
    tests_def = load_yaml('test_disabled_source_default_value.yaml')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )


async def test_xget_failing_source_no_default_value(
        resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_failing_source_no_default_value.yaml')
    tests_def = load_yaml('test_failing_source_no_default_value.yaml')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )
    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            tests.exception_error(
                'test_failing_source_no_default_value',
                'void #xget projection: '
                'cannot iterate over non-json scalar, path is "/value". '
                'location stack: '
                'responses[0].body#object[0].value#xget; '
                'responses[0].body#object[0].value#xget; '
                'responses[0].body#object; '
                'responses; '
                '/; ',
            ),
        ],
    )


async def test_xget_failing_source_default_value(
        resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_failing_source_default_value.yaml')
    tests_def = load_yaml('test_failing_source_default_value.yaml')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )


async def test_xget_failing_alias_no_default_value(
        resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_failing_alias_no_default_value.yaml')
    tests_def = load_yaml('test_failing_alias_no_default_value.yaml')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints,
        handler_def,
        tests_def,
        False,
        [
            tests.exception_error(
                'test_failing_alias_no_default_value',
                'cannot convert object to string. '
                'location stack: '
                'aliases.foo#concat-strings; '
                '/; '
                'responses[0].body#object[0].value#xget; '
                'responses[0].body#object; '
                'responses; '
                '/; ',
            ),
        ],
    )


async def test_xget_failing_alias_default_value(
        resources, endpoints, load_yaml,
):
    handler_def = load_yaml('handler_failing_alias_default_value.yaml')
    tests_def = load_yaml('test_failing_alias_default_value.yaml')

    await resources.safely_create_resource(
        resource_id='resource', url='http://test-url', method='post',
    )

    await tests.check_testrun_status(
        endpoints, handler_def, tests_def, True, None,
    )
