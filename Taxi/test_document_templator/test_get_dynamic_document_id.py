import http

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    (
        (
            {'name': 'test'},
            http.HTTPStatus.OK,
            {'id': '5ff4901c583745e089e55bf1'},
        ),
        (
            {'name': 'not exist name'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND_BY_NAME',
                'details': {},
                'message': (
                    'dynamic document with name=not exist name not found'
                ),
            },
        ),
        (
            {},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'name is required parameter'},
                'message': 'Some parameters are invalid',
            },
        ),
    ),
)
async def test_get_dynamic_document_id(
        query, expected_status, expected_content, api_app_client,
):
    response = await api_app_client.get(
        '/v1/dynamic_documents/document_id/', params=query, headers={},
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_content
