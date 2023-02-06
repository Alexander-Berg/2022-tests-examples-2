import http
import json

import pytest

from test_document_templator.test_request import common


@pytest.mark.parametrize(
    'query, body, expected_status, expected_content',
    [
        (
            {'id': common.REQUEST_ID_BY_NAME[common.TARIFF]},
            {
                'name': common.TARIFF,
                'endpoint_name': common.TARIFF,
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
            http.HTTPStatus.OK,
            {
                'name': common.TARIFF,
                'endpoint_name': common.TARIFF,
                'id': common.REQUEST_ID_BY_NAME[common.TARIFF],
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'substitutions': ['tariff', 'zone'],
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
        ),
        (
            {'id': common.REQUEST_ID_BY_NAME[common.SURGE]},
            {
                'name': common.NOT_IN_DB,
                'endpoint_name': common.NOT_IN_DB,
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
            http.HTTPStatus.OK,
            {
                'name': common.NOT_IN_DB,
                'endpoint_name': common.NOT_IN_DB,
                'id': common.REQUEST_ID_BY_NAME[common.SURGE],
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'substitutions': ['db'],
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
        ),
        (
            {'id': common.REQUEST_ID_BY_NAME[common.SURGE]},
            {
                'name': f'{common.TARIFF} name',
                'endpoint_name': common.TARIFF,
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_WITH_NAME_ALREADY_EXIST',
                'details': {'name': 'Tariff name'},
                'message': 'Request with name="Tariff name" already exist.',
            },
        ),
        (
            {'id': common.REQUEST_ID_BY_NAME[common.SURGE]},
            {
                'name': 'Not allowed name',
                'endpoint_name': 'Not allowed alias',
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_ENDPOINT_NAME',
                'details': {'endpoint_name': 'Not allowed alias'},
                'message': (
                    'Request with endpoint_name='
                    '"Not allowed alias" not allowed.'
                ),
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bd6'},
            {
                'name': common.TARIFF,
                'endpoint_name': common.TARIFF,
                'description': f'{common.TARIFF} description',
                'response_schema': {'response_schema': 1},
                'query': ['query'],
                'body_schema': {'schema': 'test'},
            },
            http.HTTPStatus.NOT_FOUND,
            '',
        ),
        (
            {},
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'id is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bd1'},
            None,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
@pytest.mark.config(**common.CONFIG)
async def test_put_request(
        api_app_client, query, body, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.put(
        '/v1/requests/', params=query, json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    if expected_status == http.HTTPStatus.OK:
        response = await api_app_client.get(
            '/v1/requests/', params=query, headers=headers,
        )
        assert await response.json() == expected_content
    if expected_status != http.HTTPStatus.NOT_FOUND:
        content = json.loads(content)
        assert content == expected_content
