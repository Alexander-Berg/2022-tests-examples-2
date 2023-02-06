import http
import json

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    (
        (
            {'template_id': '5ff4901c583745e089e55be1'},
            http.HTTPStatus.OK,
            {
                'dependencies': [
                    {
                        'id': '5ff4901c583745e089e55be2',
                        'name': 'text',
                        'dependencies': [],
                    },
                    {
                        'id': '5ff4901c583745e089e55ba4',
                        'name': 'empty template',
                        'dependencies': [],
                    },
                ],
                'id': '5ff4901c583745e089e55be1',
                'name': 'test',
            },
        ),
        (
            {'template_id': '5ff4901c583745e089e55bb4'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'TEMPLATE_NOT_FOUND_ERROR',
                'message': (
                    'template with id=5ff4901c583745e089e55bb4 not found'
                ),
                'details': {},
            },
        ),
        (
            None,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'template_id is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
    ),
)
async def test_get_template_dependencies(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/template/dependencies/', params=query, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    assert content == expected_content
