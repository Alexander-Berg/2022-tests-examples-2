import pytest

from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints


@pytest.mark.parametrize(
    'percent,expect_fail', [(30, False), (31, True), (50, True), (100, True)],
)
@pytest.mark.parametrize('resolution', ['release', 'dismiss'])
async def test_endpoint_prestable(
        taxi_api_proxy,
        load_json,
        load_yaml,
        endpoints,
        percent,
        expect_fail,
        resolution,
        testpoint,
):
    # build header def
    handler_def = load_json('simple_handler.json')
    tests_def = load_yaml('simple_test.yaml')

    # create an endpoint
    path = '/tests/api-proxy/test_endpoint_prestable'
    await endpoints.safely_create_endpoint(
        path, post_handler=handler_def, tests=tests_def,
    )

    # call the endpoint
    response = await taxi_api_proxy.post(path, json={'code': 200})
    assert response.status_code == 200
    assert response.json() == {'env': 'stable', 'result': 'Ok'}

    # create prestable
    try:
        handler_def['responses'][0]['body']['env'] = 'prestable'
        await endpoints.safely_update_endpoint(
            path, post_handler=handler_def, prestable=percent,
        )
    except endpoints.Failure as exc:
        assert expect_fail
        assert exc.response.status_code == 400
    else:
        assert not expect_fail

        # call the endpoint
        for env_expected in ('stable', 'prestable'):

            @testpoint('prestable_match_decision')
            def make_decision(request, env=env_expected):
                assert (
                    request['tag']
                    == '/tests/api-proxy/test_endpoint_prestable'
                )
                return {'decision': env}

            response = await taxi_api_proxy.post(path, json={'code': 200})
            assert response.status_code == 200
            assert make_decision.times_called == 1

    # try alter endpoint while there is a prestable
    if not expect_fail:
        with pytest.raises(endpoints.Failure) as excinfo:
            handler_def['responses'][0]['body']['env'] = 'whatever'
            await endpoints.safely_update_endpoint(
                path, post_handler=handler_def,
            )
        assert excinfo.value.response.status_code == 409
        assert excinfo.value.response.json()['code'] == 'prestable_exists'

        # can't delete while prestable exists
        with pytest.raises(endpoints.Failure) as delexc:
            await endpoints.safely_delete_endpoint(path)
        assert delexc.value.response.status_code == 409
        assert delexc.value.response.json()['code'] == 'prestable_exists'

    # finalize wrong prestable
    if not expect_fail:
        with pytest.raises(endpoints.Failure) as excinfo:
            await endpoints.finalize_endpoint_prestable(
                path, resolution=resolution, force_prestable_revision=1234,
            )
        assert excinfo.value.response.status_code == 400
        assert excinfo.value.response.json()['code'] == 'no_prestable_revision'
        current = await endpoints.fetch_current_stable(path)
        assert current['revision'] == 0

    # finalize prestable
    if not expect_fail:
        await endpoints.finalize_endpoint_prestable(
            path,
            resolution=resolution,
            force_recall=3,  # to ensure idempotency
        )
        current = await endpoints.fetch_current_stable(path)
        assert current['revision'] == (1 if resolution == 'release' else 0)


def _code_mismatch_error(test_name, response_code, expected_code):
    return (
        '%s: Response code value doesn\'t match the expected one:\n'
        'Response: \'%s\'\n'
        'Expected: \'%s\'.\n' % (test_name, response_code, expected_code)
    )


async def test_endpoint_prestable_tests_failed(
        taxi_api_proxy, load_json, load_yaml, endpoints,
):
    # build header def
    handler_def = load_json('simple_handler.json')
    path = '/tests/api-proxy/test_endpoint_prestable'
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    tests_def = load_yaml('simple_test.yaml')
    response = tests_def[0]['source']['expectations']['response']
    response['body']['env'] = 'prestable'
    response['status-code'] = 400
    handler_def['responses'][0]['body']['env'] = 'prestable'
    with pytest.raises(utils_endpoints.Failure) as validation_result:
        await endpoints.safely_update_endpoint(
            path, post_handler=handler_def, prestable=30, tests=tests_def,
        )
    message = _code_mismatch_error('simple_test', 200, 400)
    assert validation_result.value.response.json() == {
        'code': 'tests_failed',
        'message': (
            'Endpoint \''
            + path
            + '\' tests failed. Messages: \''
            + message
            + '\'.'
        ),
    }


async def test_endpoint_prestable_not_found(endpoints, load_json):
    # build header def
    handler_def = load_json('simple_handler.json')

    # create an endpoint
    with pytest.raises(endpoints.Failure) as exc:
        path = '/tests/api-proxy/not_exists'
        await endpoints.safely_create_endpoint(
            path, post_handler=handler_def, prestable=10,
        )
    assert exc.value.response.status_code == 409
    assert (
        exc.value.response.json()['code']
        == 'prestable_on_non_existing_endpoint'
    )


@pytest.mark.parametrize('existing', [True, False])
async def test_endpoints_release_prestable_not_found(endpoints, existing):
    if existing:
        # create resource
        await endpoints.safely_create_endpoint(path='/foo-endpoint')

    # try to finalize it
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.release_prestable_endpoint(
            params={
                'id': '/foo-endpoint',
                'last_revision': 0,
                'prestable_revision': 123,
            },
            no_check=True,
        )

    # asserts
    assert exc.value.response.status_code == 400
    code = exc.value.response.json()['code']
    assert code == (
        'prestable_not_exists' if existing else 'endpoint_not_found'
    )


@pytest.mark.parametrize('existing', [True, False])
async def test_endpoints_delete_prestable_not_found(endpoints, existing):
    if existing:
        # create resoutce
        await endpoints.safely_create_endpoint(path='/foo-endpoint')

    # try to finalize it
    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.delete_prestable_endpoint(
            params={
                'id': '/foo-endpoint',
                'stable_revision': 0,
                'prestable_revision': 123,
            },
            no_check=True,
        )

    # asserts
    assert exc.value.response.status_code == 400
    code = exc.value.response.json()['code']
    assert code == (
        'prestable_not_exists' if existing else 'endpoint_not_found'
    )


async def test_endpoints_prestable_url_priority(
        taxi_api_proxy, endpoints, load_yaml, testpoint,
):
    hello_handler = load_yaml('hello_handler.yaml')
    v1_handler = load_yaml('simple_handler.yaml')
    v2_handler = load_yaml('not_so_simple_handler.yaml')

    general_path = r'/foo/(?<source>\w+)/(?<path>.+)'
    spec_path = '/foo/maps/v1/orders/estimate'

    await endpoints.safely_create_endpoint(
        endpoint_id='general', path=general_path, post_handler=v1_handler,
    )

    await endpoints.safely_create_endpoint(
        endpoint_id='specialized', path=spec_path, post_handler=hello_handler,
    )

    await endpoints.safely_update_endpoint(
        endpoint_id='general',
        path=general_path,
        post_handler=v2_handler,
        prestable=30,
    )

    # call the endpoints
    for env, path, decision_called, msg in [
            ('stable', spec_path, 0, 'Hello world!'),
            ('prestable', spec_path, 0, 'Hello world!'),
            ('stable', '/foo/bar/baz', 1, 'Failure'),
            ('prestable', '/foo/bar/baz', 1, 'Created'),
    ]:

        @testpoint('prestable_match_decision')
        def make_decision(request, env_=env, path_=path):
            assert request['tag'] == path_
            return {'decision': env_}

        response = await taxi_api_proxy.post(path, json={'code': 201})
        assert make_decision.times_called == decision_called
        assert response.status_code == 200
        assert response.json()['result'] == msg
