import http
import json

import pytest

from test_document_templator.test_request import common


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': common.REQUEST_ID_BY_NAME[common.TARIFF]},
            http.HTTPStatus.OK,
            {
                'id': common.REQUEST_ID_BY_NAME[common.TARIFF],
                'name': f'{common.TARIFF} name',
                'endpoint_name': common.TARIFF,
                'description': f'{common.TARIFF} description',
                'body_schema': {
                    'properties': {
                        'a': {
                            'properties': {
                                'b': {'type': 'array'},
                                'c': {'type': 'number'},
                            },
                            'type': 'object',
                        },
                    },
                    'type': 'object',
                },
                'query': ['q1', 'q2'],
                'response_schema': {
                    'properties': {'r1': {'type': 'string'}},
                    'type': 'object',
                },
                'substitutions': ['tariff', 'zone'],
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bd6'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'REQUEST_NOT_FOUND',
                'details': {},
                'message': (
                    'request with id=5ff4901c583745e089e55bd6 not found'
                ),
            },
        ),
        (
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'id is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
@pytest.mark.config(**common.CONFIG)
async def test_get_request(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/requests/', params=query, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    assert content == expected_content
