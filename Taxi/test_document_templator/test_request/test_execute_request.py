import http
import json

import pytest

DOCUMENT_TEMPLATOR_REQUESTS = {
    'Test name': {
        'method': 'GET',
        'url_pattern': '$mockserver/tariff/{city}',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    'DOCUMENT_TEMPLATOR_REQUESTS': {
        'method': 'GET',
        'url_pattern': 'DOCUMENT_TEMPLATOR_REQUESTS',
        'service_name': 'configs',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    'INVALID_CONFIG': {
        'method': 'GET',
        'timeout_in_ms': 100,
        'url_pattern': 'INVALID_CONFIG',
        'service_name': 'configs',
        'retries_count': 3,
    },
    'lower_case_invalid_config': {
        'method': 'GET',
        'timeout_in_ms': 100,
        'url_pattern': '_reload_time',
        'service_name': 'configs',
        'retries_count': 3,
    },
}
CONFIG = {'DOCUMENT_TEMPLATOR_REQUESTS': DOCUMENT_TEMPLATOR_REQUESTS}


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    [
        (
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'param is required property'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {
                'request': {
                    'name': 'Invalid name',
                    'endpoint_name': 'Invalid name',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {}},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_ENDPOINT_NAME',
                'details': {'endpoint_name': 'Invalid name'},
                'message': (
                    'Request with endpoint_name="Invalid name" not allowed.'
                ),
            },
        ),
        (
            {
                'request': {
                    'name': 'Test name',
                    'endpoint_name': 'Test name',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {}},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_SUBSTITUTION_DOES_NOT_MATCH',
                'details': {'actual': [], 'expected': ['city']},
                'message': 'Substitutions does not match.',
            },
        ),
        (
            {
                'request': {
                    'name': 'Test name',
                    'endpoint_name': 'Test name',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {'city': {}}},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_SUBSTITUTION_HAS_INVALID_TYPE',
                'details': {'type': '<class \'dict\'>', 'value': '{}'},
                'message': 'Substitution has invalid type.',
            },
        ),
        (
            {
                'request': {
                    'name': 'Test name',
                    'endpoint_name': 'Test name',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {'city': 'moscow'}},
            },
            http.HTTPStatus.OK,
            {'activation_zone': 'moscow_activation', 'home_zone': 'moscow'},
        ),
        (
            {
                'request': {
                    'name': 'Test name',
                    'endpoint_name': 'DOCUMENT_TEMPLATOR_REQUESTS',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {},
            },
            http.HTTPStatus.OK,
            {'value': CONFIG['DOCUMENT_TEMPLATOR_REQUESTS']},
        ),
        (
            {
                'request': {
                    'name': 'Invalid name',
                    'endpoint_name': 'INVALID_CONFIG',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {}},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_CONFIG_NAME',
                'details': {},
                'message': (
                    'For using config="INVALID_CONFIG", '
                    'please add it to service.yaml'
                ),
            },
        ),
        (
            {
                'request': {
                    'name': 'Invalid name',
                    'endpoint_name': 'INVALID_CONFIG',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {}},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_CONFIG_NAME',
                'details': {},
                'message': (
                    'For using config="INVALID_CONFIG", '
                    'please add it to service.yaml'
                ),
            },
        ),
    ],
)
@pytest.mark.config(**CONFIG)
@pytest.mark.usefixtures('requests_handlers')
async def test_execute_request(
        api_app_client, body, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.post(
        '/v1/requests/execute/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    assert content == expected_content


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    [
        (
            {
                'request': {
                    'name': 'Test name',
                    'endpoint_name': 'Test name',
                    'description': 'test description',
                    'type': 'common',
                    'response_schema': {},
                },
                'param': {'substitutions': {'city': 'moscow'}},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'EXECUTING_REQUEST_FAILED',
                'details': {
                    'endpoint_name': 'Test name',
                    'reason': 'Internal Server Error',
                    'status': 500,
                },
                'message': (
                    'Executing request '
                    'with endpoint_name="Test name" failed with '
                    'status="500" and reason="Internal Server Error"'
                ),
            },
        ),
    ],
)
@pytest.mark.config(**CONFIG)
async def test_execute_failing_request(
        api_app_client, body, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.post(
        '/v1/requests/execute/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    assert content == expected_content
