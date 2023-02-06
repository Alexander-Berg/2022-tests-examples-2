import json
import random
import string

import pytest

from tests_api_proxy.api_proxy.utils import endpoints as utils_endpoints


ENDPOINTS_ENDPOINT = 'admin/v1/endpoints'


async def test_admin_endpoints_blank_db(taxi_api_proxy):
    response = await taxi_api_proxy.get(ENDPOINTS_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    assert body['endpoints'] == []


async def test_admin_endpoints_crud_cycle(taxi_api_proxy):
    doc = {
        'revision': 0,
        'enabled': True,
        'summary': 'Some test endpoint',
        'dev_team': 'joe',
        'duty_group_id': 'joe-duty-id',
        'duty_abc': 'joe-abc',
        'handlers': {
            'get': _make_handler(),
            'post': _make_handler(),
            'put': _make_handler(),
            'patch': _make_handler(),
            'delete': _make_handler(),
        },
    }
    doc_cluster = 'api-proxy'
    doc_id = 'example-foo-bar'
    doc_path = '/example/foo/bar'

    # create the doc
    response = await taxi_api_proxy.put(
        ENDPOINTS_ENDPOINT, params={'id': doc_id, 'path': doc_path}, json=doc,
    )
    assert response.status_code == 201
    assert json.loads(response.content) == {'status': 'succeeded'}

    # read the doc
    response = await taxi_api_proxy.get(ENDPOINTS_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    utils_endpoints.remove_plain_yaml_handlers(body['endpoints'][0])
    doc_with_path = {'cluster': doc_cluster, 'id': doc_id, 'path': doc_path}
    doc_with_path.update(doc)
    doc_with_path.update({'created': body['endpoints'][0]['created']})
    assert body['endpoints'] == [doc_with_path]
    last_revision = body['endpoints'][0]['revision']

    # update the doc
    doc['revision'] += 1
    doc['enabled'] = False  # NOTE: must be disable to be deleted
    doc['summary'] = 'This is summery for example/foo/bar endpoint'
    doc['dev_team'] = 'joe'
    doc['duty_group_id'] = 'joe-duty-id'
    doc['duty_abc'] = 'joe-abc'
    doc['handlers']['get'] = _make_handler()
    doc['handlers']['post'] = _make_handler()
    doc['handlers']['put'] = _make_handler()
    doc['handlers']['patch'] = _make_handler()
    doc['handlers']['delete'] = _make_handler()
    response = await taxi_api_proxy.put(
        ENDPOINTS_ENDPOINT,
        params={
            'id': doc_id,
            'path': doc_path,
            'last_revision': last_revision,
        },
        json=doc,
    )
    assert response.status_code == 200

    # read the doc
    response = await taxi_api_proxy.get(ENDPOINTS_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    utils_endpoints.remove_plain_yaml_handlers(body['endpoints'][0])
    doc_with_path = {'cluster': doc_cluster, 'id': doc_id, 'path': doc_path}
    doc_with_path.update(doc)
    doc_with_path.update({'created': body['endpoints'][0]['created']})
    assert body['endpoints'] == [doc_with_path]
    last_revision = body['endpoints'][0]['revision']

    # delete the doc
    response = await taxi_api_proxy.delete(
        ENDPOINTS_ENDPOINT,
        params={'id': doc_id, 'path': doc_path, 'revision': last_revision},
    )
    assert response.status_code == 200

    # read the doc
    response = await taxi_api_proxy.get(ENDPOINTS_ENDPOINT)
    assert response.status_code == 200
    body = json.loads(response.content)
    assert body['endpoints'] == []


@pytest.mark.parametrize(
    'handler_method', ['get', 'post', 'put', 'patch', 'delete'],
)
@pytest.mark.parametrize(
    'handler_body,expected_message,expected_location,' 'expected_status',
    [
        (
            {
                'default-response': 'resp-ok',
                'responses': [{'id': 'resp-ok', 'body#map': {}}],
                'enabled': True,
            },
            '"iterator" cannot be converted into string: '
            'responses[0].body#map',
            '/handlers/{method}/responses/0/body#map',
            400,
        ),
        (
            {
                'default-response': 'resp-ok',
                'responses': [
                    {'id': 'misc'},
                    {'id': 'resp-ok', 'body#eat-my-shorts': {}},
                ],
                'enabled': True,
            },
            'no parser for operator "eat-my-shorts"',
            '/handlers/{method}/responses/1/body#eat-my-shorts',
            400,
        ),
    ],
)  # noqa: E122
async def test_validation_failed(
        taxi_api_proxy,
        handler_method,
        handler_body,
        expected_message,
        expected_location,
        expected_status,
):
    doc = {
        'revision': 0,
        'enabled': True,
        'summary': 'Some test endpoint',
        'dev_team': 'joe',
        'duty_group_id': 'joe-duty-id',
        'duty_abc': 'joe-abc',
        'handlers': {handler_method: handler_body},
    }
    doc_path = '/example/foo/bar'

    def _subst(text):
        return text.format(**{'method': handler_method})

    # create the doc
    response = await taxi_api_proxy.put(
        ENDPOINTS_ENDPOINT,
        params={'id': doc_path, 'path': doc_path},
        json=doc,
    )
    assert response.status_code == expected_status
    assert json.loads(response.content) == {
        'code': 'validation_failed',
        'message': 'Validation failed',
        'details': {
            'endpoint-path': doc_path,
            'errors': [
                {
                    'code': 'validation_failed',
                    'message': _subst(expected_message),
                    'location': _subst(expected_location),
                },
            ],
        },
    }


def _make_id():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(15))


def _make_handler():
    default_response = _make_id()

    return {
        'default-response': default_response,
        'responses': [
            {
                'id': default_response,
                'status-code': random.choice([200, 201, 202, 203]),
                'body#string': 'hello',
                'content-type': 'application/json',
            },
        ],
        'enabled': random.choice([True, False]),
    }


async def test_ep_source_not_exists(
        mockserver, resources, load_yaml, endpoints, taxi_api_proxy,
):
    await resources.safely_create_resource(
        resource_id='billing-subventions-rules-create-draft',
        url=mockserver.url('billing-subventions-rules-create-draft'),
        method='post',
    )
    with pytest.raises(utils_endpoints.Failure) as validation_result:
        await endpoints.safely_create_endpoint(
            '/endpoint/', get_handler=load_yaml('ep_source_not_exists.yaml'),
        )
    assert validation_result.value.response.json() == {
        'code': 'validation_failed',
        'details': {
            'endpoint-path': '/endpoint/',
            'errors': [
                {
                    'code': 'validation_failed',
                    'location': '/handlers/get/sources/0/body#xget',
                    'message': (
                        'Cannot carry operator '
                        '/superapp-misc/response/body/zone_name: '
                        'no key superapp-misc'
                    ),
                },
            ],
        },
        'message': 'Validation failed',
    }


async def test_simple_testrun_ok(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_post_handler.yaml')
    tests_def = load_yaml('simple_test.yaml')
    path = '/test/foo/ok'
    await endpoints.safely_create_endpoint(
        path, post_handler=handler_def, tests=tests_def,
    )


def _code_mismatch_error(test_name, response_code, expected_code):
    return (
        '%s: Response code value doesn\'t match the expected one:\n'
        'Response: \'%s\'\n'
        'Expected: \'%s\'.\n' % (test_name, response_code, expected_code)
    )


async def test_simple_testrun_fail(taxi_api_proxy, endpoints, load_yaml):
    handler_def = load_yaml('simple_post_handler.yaml')
    tests_def = load_yaml('simple_test.yaml')
    path = '/test/foo/fail'

    response = tests_def[0]['source']['expectations']['response']
    response['status-code'] = 400

    with pytest.raises(utils_endpoints.Failure) as validation_result:
        await endpoints.safely_create_endpoint(
            path, post_handler=handler_def, tests=tests_def,
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


async def test_all_handlers_tests(taxi_api_proxy, endpoints, load_yaml):
    path = '/test/foo/all_tests_fail'
    post_handler = load_yaml('simple_post_handler.yaml')
    get_handler = load_yaml('simple_get_handler.yaml')
    tests_def = load_yaml('double_test.yaml')

    with pytest.raises(utils_endpoints.Failure) as validation_result:
        await endpoints.safely_create_endpoint(
            path,
            post_handler=post_handler,
            get_handler=get_handler,
            tests=tests_def,
        )
    post_message = _code_mismatch_error('post_test', 200, 400)
    get_message = _code_mismatch_error('get_test', 200, 400)
    assert validation_result.value.response.json() == {
        'code': 'tests_failed',
        'message': (
            'Endpoint \''
            + path
            + '\' tests failed. Messages: \''
            + get_message
            + ', '
            + post_message
            + '\'.'
        ),
    }
