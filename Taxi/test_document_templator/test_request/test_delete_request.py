import http

import pytest

from test_document_templator.test_request import common


@pytest.mark.parametrize(
    'query, expected_status, expected_content',
    [
        (
            {'id': common.REQUEST_ID_BY_NAME[common.TARIFF]},
            http.HTTPStatus.OK,
            {'id': '5ff4901c583745e089e55bd1'},
        ),
        (
            {'id': '1' * 24},
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_DELETION_IS_NOT_PERFORMED',
                'details': {},
                'message': (
                    'Deletion of request with id='
                    '"111111111111111111111111" is not performed'
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
async def test_delete_request(
        api_app_client, query, expected_status, expected_content,
):
    headers = {}
    response = await api_app_client.delete(
        '/v1/requests/', params=query, headers=headers,
    )

    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
