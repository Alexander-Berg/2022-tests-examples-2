import http
import json

import pytest


@pytest.mark.parametrize(
    'item, expected_status, expected_content',
    (
        (
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
            'valid data',
        ),
        (
            {
                'custom_item_id': 'CONDITIONAL',
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'empty',
                                'that_instruction': {
                                    'data_usage': 'PARENT_TEMPLATE_DATA',
                                    'type': 'string',
                                    'value': '#item.param.invalid',
                                },
                            },
                        },
                    ],
                },
                'items': [{'content': 'valid data'}],
            },
            http.HTTPStatus.OK,
            'valid data',
        ),
        (
            {
                'custom_item_id': 'CONDITIONAL',
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'empty',
                                'that_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': 'not_empty_string',
                                },
                            },
                        },
                    ],
                },
                'items': [{'content': 'valid data'}],
            },
            http.HTTPStatus.OK,
            '',
        ),
        (
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
        ),
        (
            {
                'custom_item_id': 'CONDITIONAL',
                'params': [
                    {
                        'name': '#item',
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                        'value': {'param': 1},
                    },
                ],
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'equal',
                                'lhs_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                },
                                'rhs_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': '#item.param',
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
                                    },
                                    'rhs_instruction': {
                                        'data_usage': 'OWN_DATA',
                                        'type': 'string',
                                        'value': '#item.param',
                                    },
                                },
                            },
                        ],
                    },
                },
                'message': 'Invalid template item property.',
            },
        ),
        (
            {
                'custom_item_id': 'CONDITIONAL',
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'empty',
                                'that_instruction': {
                                    'data_usage': 'OWN_DATA',
                                    'type': 'string',
                                    'value': 'not_empty_string',
                                },
                            },
                        },
                    ],
                },
                'items': [{'content': 'valid data'}],
                'else_items': [{'content': 'else valid data'}],
            },
            http.HTTPStatus.OK,
            'else valid data',
        ),
        (
            {
                'custom_item_id': 'CONDITIONAL',
                'properties': {
                    'filter_groups': [
                        {
                            'filter': {
                                'condition': 'not_empty',
                                'that_instruction': {
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
                                    'condition': 'not_empty',
                                    'that_instruction': {
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
        ),
    ),
)
async def test_generate_preview_with_iterable(
        api_app_client, item, expected_status, expected_content,
):
    body = {
        'template': {'name': 'test', 'description': 'test', 'items': [item]},
    }
    headers = {'X-Yandex-Login': 'robot'}
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    if response.status == http.HTTPStatus.OK:
        assert content['generated_text'] == expected_content
    else:
        assert content == expected_content
