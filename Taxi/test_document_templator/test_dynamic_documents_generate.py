import datetime
import http

import pytest
import pytz

from document_templator.generated.api import web_context
from test_document_templator import common


@pytest.mark.parametrize(
    'body, expected_status, expected_content, headers',
    [
        (
            {
                'ids': [
                    '5ff4901c583745e089e55bf1',
                    '5ff4901c583745e089e55bf2',
                    '5ff4901c583745e089e55bf4',
                    '5ff4901c583745e089e55bf5',
                    '5ff4901c583745e089e55bf8',
                    '1ff4901c583745e089e55bf0',
                ],
            },
            http.HTTPStatus.OK,
            {},
            {'X-Yandex-Login': 'venimaster'},
        ),
        # repeated ids
        (
            {'ids': ['5ff4901c583745e089e55bf1', '5ff4901c583745e089e55bf1']},
            http.HTTPStatus.OK,
            {},
            {'X-Yandex-Login': 'venimaster'},
        ),
        (
            None,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {'reason': 'body is required'},
                'message': 'Some parameters are invalid',
            },
            {'X-Yandex-Login': 'venimaster'},
        ),
    ],
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_dynamic_documents_generate(
        api_app_client, body, expected_status, expected_content, headers,
):
    context = web_context.Context()
    await context.on_startup()

    response = await api_app_client.post(
        '/v1/dynamic_documents/generate/', json=body, headers=headers,
    )
    assert response.status == expected_status, await response.text()
    content = await response.json()
    assert content == expected_content, content
    body = body or {}
    query = """
        SELECT count(*)
        FROM document_templator.dynamic_documents
        WHERE
            persistent_id = $1
            AND NOT removed
            AND outdated_at = $2;
    """
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    for document_id in body.get('ids', []):
        count = await context.pg.master.fetchval(query, document_id, now)
        assert count == 1
