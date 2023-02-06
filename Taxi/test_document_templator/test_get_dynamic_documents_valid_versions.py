import http

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': '5ff4901c583745e089e55bf1'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'some text',
                        'id': '5ff4901c583745e089e55bf1',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'version': 1,
                    },
                    {
                        'description': 'some text',
                        'id': '5ff4901c583745e089e55bf1',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'test',
                        'version': 0,
                    },
                ],
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bf2'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'id': '5ff4901c583745e089e55bf2',
                        'modified_at': '2018-07-01T01:00:00+03:00',
                        'name': 'text',
                        'description': 'some',
                        'version': 1,
                    },
                ],
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bf6'},  # removed dynamic document
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf6 not found'
                ),
            },
        ),
        (
            {'id': '5ff4901c583745e089e55bf7'},  # missing dynamic document
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=5ff4901c583745e089e55bf7 not found'
                ),
            },
        ),
    ],
)
async def test_get_dynamic_documents_valid_versions(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/dynamic_documents/valid_versions/', params=query, headers=headers,
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()

    if expected_status == http.HTTPStatus.OK:
        items = content['items']
        expected_items = expected_content['items']
        assert items == expected_items
    else:
        assert content == expected_content
