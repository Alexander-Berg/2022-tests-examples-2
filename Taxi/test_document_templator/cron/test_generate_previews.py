import http

import pytest

from document_templator.generated.cron import run_cron


@pytest.mark.parametrize(
    'item, expected_status, expected_content',
    (
        pytest.param(
            {
                'custom_item_id': 'CONDITIONAL',
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'equal',
                                'lhs_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': 2,
                                },
                                'rhs_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': 2,
                                },
                            },
                        },
                    ],
                },
                'items': [{'content': 'valid data'}],
            },
            http.HTTPStatus.OK,
            {'generated_text': 'valid data', 'status': 'FINISHED'},
            id='ok',
        ),
        pytest.param(
            {
                'custom_item_id': 'CONDITIONAL',
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'equal',
                                'lhs_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': '#item.param',
                                },
                                'rhs_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                },
                            },
                        },
                    ],
                },
                'items': [{'content': 'valid data'}],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_TEMPLATE_ITEM_PROPERTY',
                'details': {
                    'detail': 'value is required property',
                    'property': {
                        'filter_groups': [
                            {
                                'filter': {
                                    'condition': 'equal',
                                    'lhs_instruction': {
                                        'data_usage': 'OWN_DATA',
                                        'type': 'string',
                                        'value': '#item.param',
                                    },
                                    'rhs_instruction': {
                                        'data_usage': 'OWN_DATA',
                                        'type': 'string',
                                    },
                                },
                            },
                        ],
                    },
                },
                'message': 'Invalid template item property.',
            },
            id='generating_failed',
        ),
    ),
)
async def test_generate_previews(
        api_app_client, item, expected_status, expected_content,
):
    body = {
        'template': {'name': 'test', 'description': 'test', 'items': [item]},
    }
    headers = {'X-Yandex-Login': 'robot'}
    response = await api_app_client.post(
        '/v1/templates/preview/generate/?is_async=true',
        json=body,
        headers=headers,
    )
    assert response.status == 200, await response.json()
    preview_id = (await response.json())['id']

    response = await api_app_client.get(
        '/v1/templates/preview/', params={'id': preview_id}, headers=headers,
    )
    assert await response.json() == {'status': 'CREATED', 'id': preview_id}

    await run_cron.main(
        ['document_templator.crontasks.generate_previews', '-t', '0'],
    )

    response = await api_app_client.get(
        '/v1/templates/preview/', params={'id': preview_id}, headers=headers,
    )
    content = await response.json()
    content.pop('id', None)
    assert content == expected_content


@pytest.mark.parametrize(
    'preview_id',
    ['80ed41cf-6416-4994-8118-f835f8f6c809', '111111111111111111111111'],
)
async def test_get_generated_preview(api_app_client, preview_id):
    response = await api_app_client.get(
        '/v1/templates/preview/', params={'id': preview_id},
    )
    assert response.status == 404
    assert await response.json() == {
        'code': 'PREVIEW_NOT_FOUND',
        'details': {},
        'message': f'preview with id={preview_id} not found',
    }
