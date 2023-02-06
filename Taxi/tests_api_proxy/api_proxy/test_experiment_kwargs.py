import pytest


@pytest.mark.parametrize(
    'match,foo1_value,foo2_value',
    [
        [True, ['foo', 'bar', 'baz'], []],
        [True, ['foo', 'baz'], [42, 24]],
        [True, [], [54, 42, 24]],
        [False, ['foo', 'baz'], [54, 24]],
        [False, [], []],
    ],
)
@pytest.mark.experiments3(filename='exp3_set_kwargs_test.json')
async def test_experiment_set_kwargs(
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        load_yaml,
        match,
        foo1_value,
        foo2_value,
):
    @mockserver.json_handler('/mock-me')
    def _mock_cardstorage_card(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        assert request.json == {'foo': 'bar'}
        return {
            'data-from-ext-handler': 'Hello world!',
            'experiment-value': '1234',
        }

    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    # create endpoint
    handler_def = load_yaml('experiment_kwargs_set.yaml')
    handler_def['experiments']['kwargs'][0]['value'] = foo1_value
    handler_def['experiments']['kwargs'][1]['value'] = foo2_value

    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.post('test/foo/bar')
    assert response.status_code == 200
    body = {'data': 'Hello world!'}
    if match:
        body['exp'] = '1234'
    assert response.json() == body


@pytest.mark.parametrize(
    'match,send_foo3', [(True, True), (False, True), (False, False)],
)
@pytest.mark.experiments3(filename='exp3_kwargs_test.json')
async def test_experiment_kwargs(
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        match,
        send_foo3,
        load_yaml,
):
    @mockserver.json_handler('/mock-me')
    def _mock_cardstorage_card(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        assert request.json == {'foo': 'bar'}
        return {
            'data-from-ext-handler': 'Hello world!',
            'experiment-value': '1234',
        }

    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )

    # create endpoint
    handler_def = load_yaml('experiment_kwargs.yaml')
    path = '/test/foo/bar'
    await endpoints.safely_create_endpoint(path, post_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.post(
        'test/foo/bar',
        json={'property': 'value'} if send_foo3 else {},
        headers={'X-Test-Header': 'correct' if match else 'wrong_value'},
    )
    assert response.status_code == 200
    body = {'data': 'Hello world!'}
    if match:
        body['exp'] = '1234'
    assert response.json() == body


@pytest.mark.parametrize(
    'test_uid,exp_effective',
    [('12345', True), ('4444', True), ('5555', True), ('3456', False)],
)
async def test_experiment_kwargs_set(
        taxi_api_proxy,
        endpoints,
        load_yaml,
        experiments3,
        test_uid,
        exp_effective,
):
    experiments3.add_experiment(
        match={
            'predicate': {
                'type': 'contains',
                'init': {
                    'arg_name': 'yandex_uid',
                    'set_elem_type': 'string',
                    'value': test_uid,
                },
            },
            'enabled': True,
        },
        name='exp3_foo',
        consumers=['api-proxy/test-handler'],
        clauses=[],
        default_value={'data': 'from experiment'},
    )
    await taxi_api_proxy.invalidate_caches()

    path = '/path/to/test/handler'
    await endpoints.safely_create_endpoint(
        path=path,
        endpoint_id='test-handler',
        get_handler=load_yaml('test_experiment_kwargs_set.yaml'),
    )
    response = await taxi_api_proxy.get(
        path,
        headers={'X-Yandex-UID': '12345', 'X-YaTaxi-Bound-Uids': '4444,5555'},
    )
    assert response.status_code == 200
    assert response.json()['effective'] == exp_effective
    if exp_effective:
        assert response.json()['value'] == {'data': 'from experiment'}


async def test_experiment_source_deps(
        taxi_api_proxy, mockserver, resources, endpoints, load_yaml,
):
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me'),
        method='post',
    )
    post_handler = load_yaml('experiment_source_deps.yaml')

    with pytest.raises(endpoints.Failure) as exc:
        await endpoints.safely_create_endpoint(
            path='/test/foo/bar', post_handler=post_handler,
        )
    assert exc.value.response.status_code == 400
    assert exc.value.response.json()['code'] == 'validation_failed'
