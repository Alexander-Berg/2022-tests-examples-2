import json

import pytest


@pytest.mark.parametrize(
    'percent,expect_fail', [(30, False), (31, True), (50, True), (100, True)],
)
@pytest.mark.parametrize('resolution', ['release', 'dismiss'])
async def test_resources_prestable(
        taxi_api_proxy,
        resources,
        endpoints,
        mockserver,
        percent,
        expect_fail,
        resolution,
):
    @mockserver.json_handler('/mock-me-stable')
    def _mock_stable_mock(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        body = json.loads(request.get_data())
        assert body == {'foo': 'bar'}
        return {'data-from-ext-handler': 'Hello stable world!'}

    @mockserver.json_handler('/mock-me-prestable')
    def _mock_prestable_mock(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/json'
        body = json.loads(request.get_data())
        assert body == {'foo': 'bar'}
        return {'data-from-ext-handler': 'Hello prestable world!'}

    # create resource
    await resources.safely_create_resource(
        resource_id='test-resource',
        url=mockserver.url('mock-me-stable'),
        method='post',
        timeout=1000,
    )

    # build header def
    handler_def = {
        'default-response': 'resp-ok',
        'enabled': True,
        'allow-unauthorized': True,
        'sources': [
            {
                'id': 'test-source',
                'resource': 'test-resource',
                'body#object': [{'key': 'foo', 'value#string': 'bar'}],
                'content-type': 'application/json',
            },
        ],
        'responses': [
            {
                'id': 'resp-ok',
                'content-type': 'application/json',
                'body#object': [
                    {
                        'key': 'data',
                        'value#get': {
                            'object#source-response-body': 'test-source',
                            'key#string': 'data-from-ext-handler',
                        },
                    },
                ],
            },
        ],
    }

    # create an endpoint
    path = '/tests/api-proxy/test_resources_prestable'
    await endpoints.safely_create_endpoint(path, get_handler=handler_def)

    # call the endpoint
    response = await taxi_api_proxy.get(path)
    assert response.status_code == 200
    assert response.json() == {'data': 'Hello stable world!'}

    # create prestable
    try:
        await resources.safely_update_resource(
            resource_id='test-resource',
            url=mockserver.url('mock-me-prestable'),
            method='post',
            prestable=percent,
        )
    except resources.Failure as exc:
        assert expect_fail
        assert exc.response.status_code == 400
    else:
        assert not expect_fail

        # call the endpoint
        hellos = set()
        hellos_expected = set(
            ['Hello stable world!', 'Hello prestable world!'],
        )
        while hellos != hellos_expected:
            response = await taxi_api_proxy.get(path)
            assert response.status_code == 200
            hello = response.json()['data']
            hellos.add(hello)
        assert hellos == hellos_expected

    # try alter endpoint while there is a prestable
    if not expect_fail:
        with pytest.raises(resources.Failure) as excinfo:
            await resources.safely_update_resource(
                resource_id='test-resource',
                url='http://whatever',
                method='post',
            )
        assert excinfo.value.response.status_code == 409
        assert excinfo.value.response.json()['code'] == 'prestable_exists'

        # can't delete while prestable exists
        with pytest.raises(resources.Failure) as delexc:
            await resources.safely_delete_resource('test-resource')
        assert delexc.value.response.status_code == 409
        assert delexc.value.response.json()['code'] == 'prestable_exists'

    # finalize wrong prestable
    if not expect_fail:
        with pytest.raises(resources.Failure) as excinfo:
            await resources.finalize_resource_prestable(
                resource_id='test-resource',
                resolution=resolution,
                force_prestable_revision=1234,
                force_recall=3,  # to ensure idempotency
            )
        assert excinfo.value.response.status_code == 400
        assert excinfo.value.response.json()['code'] == 'no_prestable_revision'
        current = await resources.fetch_current_stable('test-resource')
        assert current['revision'] == 0

    # finalize prestable
    if not expect_fail:
        await resources.finalize_resource_prestable(
            resource_id='test-resource',
            resolution=resolution,
            force_recall=3,  # to ensure idempotency
        )
        current = await resources.fetch_current_stable('test-resource')
        assert current['revision'] == (1 if resolution == 'release' else 0)


async def test_resources_prestable_not_found(taxi_api_proxy, resources):
    with pytest.raises(resources.Failure) as exc:
        await resources.safely_create_resource(
            resource_id='not-exists',
            url='http://whatever',
            method='post',
            timeout=1000,
            prestable=10,
        )
    assert exc.value.response.status_code == 409
    assert (
        exc.value.response.json()['code']
        == 'prestable_on_non_existing_resource'
    )


@pytest.mark.parametrize('existing', [True, False])
async def test_resources_release_prestable_not_found(resources, existing):
    if existing:
        # create resource
        await resources.safely_create_resource(
            resource_id='foo-resource',
            url='http://whatever',
            method='post',
            timeout=1000,
        )

    # try to finalize it
    with pytest.raises(resources.Failure) as exc:
        await resources.release_prestable_resource(
            params={
                'id': 'foo-resource',
                'last_revision': 0,
                'prestable_revision': 120,
            },
            no_check=True,
        )

    # asserts
    assert exc.value.response.status_code == 400
    code = exc.value.response.json()['code']
    assert code == (
        'prestable_not_exists' if existing else 'resource_not_found'
    )


@pytest.mark.parametrize('existing', [True, False])
async def test_resources_delete_prestable_not_found(resources, existing):
    if existing:
        # create resoutce
        await resources.safely_create_resource(
            resource_id='foo-resource',
            url='http://whatever',
            method='post',
            timeout=1000,
        )

    # try to finalize it
    with pytest.raises(resources.Failure) as exc:
        await resources.delete_prestable_resource(
            params={
                'id': 'foo-resource',
                'stable_revision': 0,
                'prestable_revision': 120,
            },
            no_check=True,
        )

    # asserts
    assert exc.value.response.status_code == 400
    code = exc.value.response.json()['code']
    assert code == (
        'prestable_not_exists' if existing else 'resource_not_found'
    )
