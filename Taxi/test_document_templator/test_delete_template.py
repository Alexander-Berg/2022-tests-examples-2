import http
import json

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': '000000000000000000000001'},
            http.HTTPStatus.OK,
            {'id': '000000000000000000000001'},
        ),
        (
            {'id': '1ff4901c583745e089e55be0'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'details': {},
                'code': 'FORBIDDEN_DELETING_TEMPLATE',
                'message': (
                    'You cannot delete template '
                    'with id=1ff4901c583745e089e55be0 '
                    'because it has dependent template '
                    'ids=['
                    '\'1ff4901c583745e089e55be1\', '
                    '\'1ff4901c583745e089e55be2\', '
                    '\'1ff4901c583745e089e55be3\''
                    '] '
                    'and dependent documents with ids=[]'
                ),
            },
        ),
        (
            {'id': '5ff4901c583745e089e55be1'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'details': {},
                'code': 'FORBIDDEN_DELETING_TEMPLATE',
                'message': (
                    'You cannot delete template '
                    'with id=5ff4901c583745e089e55be1 '
                    'because it has dependent template '
                    'ids=[] and dependent '
                    'documents '
                    'with ids=[\'5ff4901c583745e089e55bf1\']'
                ),
            },
        ),
        (
            {'id': '5ff4901c583745e089e55be6'},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'TEMPLATE_DELETION_IS_NOT_PERFORMED',
                'details': {},
                'message': (
                    'Deletion of template '
                    'with id="5ff4901c583745e089e55be6" is not '
                    'performed'
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
async def test_delete_template(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.delete(
        '/v1/template/', params=query, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    assert content == expected_content
