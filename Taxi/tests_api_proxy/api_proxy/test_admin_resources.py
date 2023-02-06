import json


RESOURCES_ENDPOINT = 'admin/v1/resources'
ENDPOINTS_ENDPOINT = 'admin/v1/endpoints'


async def test_admin_resources_blank_db(taxi_api_proxy):
    response = await taxi_api_proxy.get(RESOURCES_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    assert body['resources'] == []


async def test_admin_resources_crud_cycle(taxi_api_proxy):
    doc = {
        'revision': 0,
        'url': 'http://example.com/foo',
        'tvm-name': 'example-tvm',
        'method': 'post',
        'timeout': 6,
        'timeout-taxi-config': 'EXAMPLE_FOO_TIMEOUT_MS',
        'max-retries': 11,
        'max-retries-taxi-config': 'EXAMPLE_FOO_TIMEOUT_RETRIES',
        'summary': 'Summary of the Foo at example.com',
        'dev_team': 'foo',
        'duty_group_id': 'joe-duty-id',
        'duty_abc': 'joe-abc',
        'caching-enabled': False,
        'use_envoy': True,
    }
    doc_id = 'example-foo'

    # create the doc
    response = await taxi_api_proxy.put(
        RESOURCES_ENDPOINT, params={'id': doc_id}, json=doc,
    )
    assert response.status_code == 201
    assert json.loads(response.content) == {'status': 'succeeded'}

    # read the doc
    response = await taxi_api_proxy.get(RESOURCES_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    doc_with_id = {'id': doc_id}
    doc_with_id.update(doc)
    doc_with_id.update({'created': body['resources'][0]['created']})
    assert body['resources'] == [doc_with_id]
    last_revision = body['resources'][0]['revision']

    # update the doc
    doc['revision'] += 1
    doc['url'] = 'http://example.net/foo'
    doc['tvm-name'] = 'tvm-example'
    doc['method'] = 'get'
    doc['timeout'] = 500
    doc['timeout-taxi-config'] = 'EXAMPLE_FOO_TIMEOUT_MS_2'
    doc['max-retries'] = 2
    doc['max-retries-taxi-config'] = 'EXAMPLE_FOO_TIMEOUT_RETRIES_2'
    doc['summary'] = 'This is summery for /foo handler'
    doc['use_envoy'] = False
    response = await taxi_api_proxy.put(
        RESOURCES_ENDPOINT,
        params={'id': doc_id, 'last_revision': last_revision},
        json=doc,
    )
    assert response.status_code == 200

    # read the doc
    response = await taxi_api_proxy.get(RESOURCES_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    doc_with_id = {'id': doc_id}
    doc_with_id.update(doc)
    doc_with_id.update({'created': body['resources'][0]['created']})
    assert body['resources'] == [doc_with_id]
    last_revision = body['resources'][0]['revision']

    # delete the doc
    response = await taxi_api_proxy.delete(
        RESOURCES_ENDPOINT, params={'id': doc_id, 'revision': last_revision},
    )
    assert response.status_code == 200

    # read the doc
    response = await taxi_api_proxy.get(RESOURCES_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    assert body['resources'] == []


async def test_admin_resources_dangling(taxi_api_proxy):
    # create resource doc
    resource_doc = {
        'revision': 0,
        'url': 'http://example.com/foo',
        'method': 'post',
        'summary': 'Summary of the Foo at example.com',
        'dev_team': 'foo',
    }
    doc_id = 'example-bar'

    response = await taxi_api_proxy.put(
        RESOURCES_ENDPOINT, params={'id': doc_id}, json=resource_doc,
    )
    assert response.status_code == 201
    assert json.loads(response.content) == {'status': 'succeeded'}

    # create endpoint doc
    endpoint_doc = {
        'revision': 0,
        'enabled': False,
        'summary': 'Some test endpoint',
        'dev_team': 'joe',
        'handlers': {
            'get': {
                'default-response': 'default-response',
                'responses': [{'id': 'default-response', 'status-code': 200}],
                'sources': [{'id': 'test-source', 'resource': doc_id}],
                'enabled': True,
            },
        },
    }
    doc_path = '/example/bar/foo'

    # create the doc
    response = await taxi_api_proxy.put(
        ENDPOINTS_ENDPOINT,
        params={'id': doc_path, 'path': doc_path},
        json=endpoint_doc,
    )
    assert response.status_code == 201
    assert json.loads(response.content) == {'status': 'succeeded'}

    # try to delete resource (which used by source)
    response = await taxi_api_proxy.delete(
        RESOURCES_ENDPOINT,
        params={'id': doc_id, 'revision': resource_doc['revision']},
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        'code': 'dangling_reference_prevented',
        'message': (
            'Resource \'example-bar\' still '
            'used by sources \'/example/bar/foo\''
        ),
    }
    assert (
        response.headers['X-YaTaxi-Error-Code']
        == 'dangling_reference_prevented'
    )

    # delete enpoint's doc
    response = await taxi_api_proxy.delete(
        ENDPOINTS_ENDPOINT,
        params={
            'id': doc_path,
            'path': doc_path,
            'revision': endpoint_doc['revision'],
        },
    )
    assert response.status_code == 200

    # now delete resouce
    response = await taxi_api_proxy.delete(
        RESOURCES_ENDPOINT,
        params={'id': doc_id, 'revision': resource_doc['revision']},
    )
    assert response.status_code == 200
