import http
from unittest import mock

import pytest

from test_document_templator.test_request import common

NEW_ID = '9' * 24


@pytest.mark.parametrize(
    'body, expected_status, expected_content',
    [
        (
            {
                'name': common.NOT_IN_DB,
                'endpoint_name': common.NOT_IN_DB,
                'description': f'{common.TARIFF} description',
                'response_schema': {},
            },
            http.HTTPStatus.OK,
            {
                'description': f'{common.TARIFF} description',
                'id': NEW_ID,
                'name': common.NOT_IN_DB,
                'endpoint_name': common.NOT_IN_DB,
                'query': [],
                'response_schema': {},
                'substitutions': ['db'],
                'body_schema': {},
            },
        ),
        (
            {
                'name': f'{common.TARIFF} name',
                'endpoint_name': common.TARIFF,
                'description': f'{common.TARIFF} description',
                'response_schema': {},
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_WITH_NAME_ALREADY_EXIST',
                'details': {'name': 'Tariff name'},
                'message': 'Request with name="Tariff name" already exist.',
            },
        ),
        (
            None,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
@pytest.mark.config(**common.CONFIG)
async def test_post_request(
        api_app_client, body, expected_status, expected_content,
):
    headers = {}
    with mock.patch(
            'document_templator.models.request.generate_id',
            return_value=NEW_ID,
    ):
        response = await api_app_client.post(
            '/v1/requests/', json=body, headers=headers,
        )
    content = await response.json()
    assert response.status == expected_status, content
    assert content == expected_content
