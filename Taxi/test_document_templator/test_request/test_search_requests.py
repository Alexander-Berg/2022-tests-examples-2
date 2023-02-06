import http

import pytest

from test_document_templator.test_request import common


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'search_string': 'Tar', 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': f'{common.TARIFF} description',
                        'id': common.REQUEST_ID_BY_NAME[common.TARIFF],
                        'name': f'{common.TARIFF} name',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 1,
            },
        ),
        (
            {'search_string': 'description', 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': f'{common.SURGE} description',
                        'id': common.REQUEST_ID_BY_NAME[common.SURGE],
                        'name': common.SURGE,
                    },
                    {
                        'description': f'{common.TARIFF} description',
                        'id': common.REQUEST_ID_BY_NAME[common.TARIFF],
                        'name': f'{common.TARIFF} name',
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 2,
            },
        ),
        (
            {'offset': 1, 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': f'{common.TARIFF} description',
                        'id': common.REQUEST_ID_BY_NAME[common.TARIFF],
                        'name': f'{common.TARIFF} name',
                    },
                ],
                'limit': 10,
                'offset': 1,
                'total': 2,
            },
        ),
        (
            {'search_string': common.SURGE[1:4], 'offset': 0, 'limit': 10},
            http.HTTPStatus.OK,
            {
                'items': [
                    {
                        'description': f'{common.SURGE} description',
                        'id': common.REQUEST_ID_BY_NAME[common.SURGE],
                        'name': common.SURGE,
                    },
                ],
                'limit': 10,
                'offset': 0,
                'total': 1,
            },
        ),
    ],
)
async def test_search_requests(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.get(
        '/v1/requests/search/', params=query, headers=headers,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
