import http

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': '000000000000000000000001'},
            http.HTTPStatus.OK,
            {'id': '000000000000000000000001', 'name': 'main'},
        ),
        (
            {'id': '000000000000000000000000'},
            http.HTTPStatus.NOT_FOUND,
            {
                'code': 'GROUP_NOT_FOUND',
                'details': {},
                'message': 'Group with id=000000000000000000000000 not found',
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
@pytest.mark.parametrize(
    'url', ('/v1/dynamic_document_groups/', '/v1/template_groups/'),
)
async def test_get_group(
        api_app_client, query, expected_status, expected_content, url,
):
    headers = {}
    response = await api_app_client.get(url, params=query, headers=headers)
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
