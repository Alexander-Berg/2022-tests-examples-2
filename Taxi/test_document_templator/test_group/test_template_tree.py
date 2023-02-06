import http

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    (
        (
            {'parent_id': '000000000000000000000001'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'description sub main',
                        'id': '000000000000000000000002',
                        'name': 'sub main',
                        'parent_id': '000000000000000000000001',
                    },
                ],
            },
        ),
        (
            None,
            http.HTTPStatus.OK,
            {'items': [{'id': '000000000000000000000001', 'name': 'main'}]},
        ),
    ),
)
@pytest.mark.parametrize(
    'url', ('/v1/dynamic_document_groups/tree/', '/v1/template_groups/tree/'),
)
async def test_group_tree(
        api_app_client, query, expected_status, expected_content, url,
):
    headers = {}
    response = await api_app_client.get(url, params=query, headers=headers)
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
