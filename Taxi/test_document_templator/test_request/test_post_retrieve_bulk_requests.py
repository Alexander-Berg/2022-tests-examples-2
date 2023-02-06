import http

import pytest

from test_document_templator.test_request import common


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    [
        (
            {'ids': ['5ff4901c583745e089e55bd1', '5ff4901c583745e089e55bd3']},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'body_schema': {},
                        'description': 'Surge description',
                        'endpoint_name': 'Surge',
                        'id': '5ff4901c583745e089e55bd3',
                        'name': 'Surge',
                        'query': [],
                        'response_schema': {
                            'properties': {'num': {'type': 'number'}},
                            'type': 'object',
                        },
                        'substitutions': [],
                    },
                    {
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
                        'description': 'Tariff description',
                        'endpoint_name': 'Tariff',
                        'id': '5ff4901c583745e089e55bd1',
                        'name': 'Tariff name',
                        'query': ['q1', 'q2'],
                        'response_schema': {
                            'properties': {'r1': {'type': 'string'}},
                            'type': 'object',
                        },
                        'substitutions': ['tariff', 'zone'],
                    },
                ],
            },
        ),
        (
            {'ids': ['5ff4901c583745e089e55bd1', '000000000000000000000000']},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'FAILED_TO_FIND_ALL_REQUESTS',
                'details': {
                    'found': ['5ff4901c583745e089e55bd1'],
                    'not_found': ['000000000000000000000000'],
                    'requested': [
                        '000000000000000000000000',
                        '5ff4901c583745e089e55bd1',
                    ],
                },
                'message': 'Failed to find all requests',
            },
        ),
    ],
)
@pytest.mark.config(**common.CONFIG)
async def test_post_retrieve_bulk_requests(
        api_app_client, body, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.post(
        '/v1/requests/retrieve_bulk/', json=body, headers=headers,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
