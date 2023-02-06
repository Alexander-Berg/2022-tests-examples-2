import http
import json

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    (
        (
            {'id': '5ff4901c583745e089e55bf1', 'version': 1},
            http.HTTPStatus.OK,
            {
                'id': '5ff4901c583745e089e55bf1',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'text': 'some generated text',
                'name': 'test',
                'description': 'some text',
                'version': 1,
            },
        ),
        (
            {'id': '000009999988888777771111', 'version': 2},
            http.HTTPStatus.OK,
            {
                'id': '000009999988888777771111',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'name': 'two last version is not valid',
                'description': 'generated based on child11 template',
                'text': 'generated text',
                'version': 2,
            },
        ),
        (
            # last version is not valid, but previous valid
            {'id': '1ff4901c583745e089e55bf0', 'version': 0},
            http.HTTPStatus.OK,
            {
                'id': '1ff4901c583745e089e55bf0',
                'text': 'some text',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'name': 'n11',
                'description': 'generated based on child11 template',
                'version': 0,
            },
        ),
        (
            # last version is removed
            {'id': '000009999988888777776666', 'version': 0},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document with '
                    'id=000009999988888777776666 not found'
                ),
            },
        ),
        (
            # id is not exist
            {'id': '111119999988888777776666', 'version': 0},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'DYNAMIC_DOCUMENT_NOT_FOUND',
                'details': {},
                'message': (
                    'dynamic document '
                    'with id=111119999988888777776666 not found'
                ),
            },
        ),
    ),
)
async def test_get_last_valid_dynamic_document(
        query, expected_status, expected_content, api_app_client,
):
    response = await api_app_client.get(
        '/v1/dynamic_documents/valid/', params=query,
    )
    assert response.status == expected_status, await response.text()
    content = await response.text()
    if isinstance(expected_content, dict):
        content = json.loads(content)
    assert content == expected_content
