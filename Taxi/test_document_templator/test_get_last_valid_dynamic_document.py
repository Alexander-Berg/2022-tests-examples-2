import http
import json

import pytest


@pytest.mark.parametrize(
    'query, headers, expected_status, expected_content',
    (
        (
            {'id': '5ff4901c583745e089e55bf1'},
            {},
            http.HTTPStatus.OK,
            {
                'id': '5ff4901c583745e089e55bf1',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'text': 'some generated text',
                'description': 'some text',
                'name': 'test',
                'version': 1,
            },
        ),
        (
            {'id': '000009999988888777771111'},
            {},
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
            # last valid modified at in 2018
            {'id': '5ff4901c583745e089e55bf1'},
            {'If-Modified-Since': '2019-07-01T01:00:00+03:00'},
            http.HTTPStatus.OK,
            {
                'id': '5ff4901c583745e089e55bf1',
                'modified_at': '2018-07-01T01:00:00+03:00',
                'name': 'test',
                'description': 'some text',
                'text': 'some generated text',
                'version': 1,
            },
        ),
        (
            # last valid modified at in 2018
            {'id': '5ff4901c583745e089e55bf1'},
            {'If-Modified-Since': '2017-07-01T01:00:00+03:00'},
            http.HTTPStatus.NOT_MODIFIED,
            '',
        ),
        (
            # last version is not valid, but previous valid
            {'id': '1ff4901c583745e089e55bf0'},
            {'If-Modified-Since': '2019-07-01T01:00:00+03:00'},
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
            {'id': '000009999988888777776666'},
            {},
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
            # invalid header
            {'id': '000009999988888777776666'},
            {'If-Modified-Since': 'invalid'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for If-Modified-Since: failed to parse '
                        'datetime from \'invalid\''
                    ),
                },
                'message': 'Some parameters are invalid',
            },
        ),
        (
            # id is not exist
            {'id': '111119999988888777776666'},
            {},
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
        query, headers, expected_status, expected_content, api_app_client,
):
    response = await api_app_client.get(
        '/v1/dynamic_documents/last_valid/', params=query, headers=headers,
    )
    assert response.status == expected_status, await response.text()
    content = await response.text()
    if isinstance(expected_content, dict):
        content = json.loads(content)
    assert content == expected_content
