import http

import pytest


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'search_string': 'sub sub', 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'description sub sub main',
                        'id': '000000000000000000000003',
                        'name': 'sub sub main',
                        'parent_id': '000000000000000000000002',
                    },
                    {
                        'description': (
                            'description sub sub main with document'
                        ),
                        'id': '000000000000000000000004',
                        'name': 'sub sub main with document',
                        'parent_id': '000000000000000000000002',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {'limit': '2'},
            http.HTTPStatus.OK,
            {
                'items': [
                    {'id': '000000000000000000000001', 'name': 'main'},
                    {
                        'description': 'description sub main',
                        'id': '000000000000000000000002',
                        'name': 'sub main',
                        'parent_id': '000000000000000000000001',
                    },
                ],
                'limit': 2,
                'offset': 0,
                'total': 4,
            },
        ),
        (
            {'offset': '1', 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': 'description sub main',
                        'id': '000000000000000000000002',
                        'name': 'sub main',
                        'parent_id': '000000000000000000000001',
                    },
                    {
                        'description': 'description sub sub main',
                        'id': '000000000000000000000003',
                        'name': 'sub sub main',
                        'parent_id': '000000000000000000000002',
                    },
                    {
                        'description': (
                            'description sub sub main with document'
                        ),
                        'id': '000000000000000000000004',
                        'name': 'sub sub main with document',
                        'parent_id': '000000000000000000000002',
                    },
                ],
                'limit': 10,
                'offset': 1,
                'total': 4,
            },
        ),
        (
            {'offset': 'invalid', 'limit': 2},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for offset: '
                        '\'invalid\' is not instance of int'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'url',
    ('/v1/dynamic_document_groups/search/', '/v1/template_groups/search/'),
)
async def test_get_groups(
        api_app_client, query, expected_status, expected_content, url,
):
    headers = {}
    response = await api_app_client.get(url, params=query, headers=headers)
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
