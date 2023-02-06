import http
import json

import pytest


@pytest.mark.parametrize(
    'item, expected_status, expected_content',
    (
        (
            {
                'custom_item_id': 'ITERABLE',
                'properties': {'item_param_name': 'test'},
                'params': [
                    {
                        'name': '#items',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'items': ['first', 'second', 'last']},
                            {'items': [11, 12, 13]},
                        ],
                    },
                ],
                'items': [
                    {
                        'custom_item_id': 'ITERABLE',
                        'properties': {
                            'item_param_name': 'other',
                            'item_index_param_name': 'index',
                        },
                        'params': [
                            {
                                'name': '#items',
                                'type': 'array',
                                'data_usage': 'PARENT_TEMPLATE_DATA',
                                'value': 'test.items',
                            },
                        ],
                        'items': [
                            {
                                'content': (
                                    '<span data-variable="index"/>)'
                                    '<span data-variable="test"/>-'
                                    '<span data-variable="other"/>\n'
                                ),
                            },
                        ],
                    },
                ],
            },
            http.HTTPStatus.OK,
            (
                '1){\'items\': [\'first\', \'second\', \'last\']}-first\n'
                '2){\'items\': [\'first\', \'second\', \'last\']}-second\n'
                '3){\'items\': [\'first\', \'second\', \'last\']}-last\n'
                '1){\'items\': [11, 12, 13]}-11\n'
                '2){\'items\': [11, 12, 13]}-12\n'
                '3){\'items\': [11, 12, 13]}-13\n'
            ),
        ),
        (
            {
                'custom_item_id': 'ITERABLE',
                'params': [
                    {
                        'name': '#items',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'items': ['first', 'second', 'last']},
                            {'items': [11, 12, 13]},
                        ],
                    },
                ],
                'items': [
                    {
                        'custom_item_id': 'ITERABLE',
                        'properties': {'item_index_param_name': 'index'},
                        'params': [
                            {
                                'name': '#items',
                                'type': 'array',
                                'data_usage': 'PARENT_TEMPLATE_DATA',
                                'value': '#item.items',
                            },
                        ],
                        'items': [
                            {
                                'content': (
                                    '<span data-variable="index"/>)'
                                    '<span data-variable="#item"/>\n'
                                ),
                            },
                        ],
                    },
                ],
            },
            http.HTTPStatus.OK,
            '1)first\n2)second\n3)last\n1)11\n2)12\n3)13\n',
        ),
        (
            {
                'custom_item_id': 'ITERABLE',
                'properties': {'item_param_name': 'test'},
                'params': [
                    {
                        'name': '#items',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'items': ['first', 'second', 'last']},
                            {'items': [11, 12, 13]},
                        ],
                    },
                ],
                'items': [
                    {
                        'custom_item_id': 'ITERABLE',
                        'properties': {
                            'item_param_name': 'other',
                            'item_index_param_name': 'index',
                        },
                        'params': [
                            {
                                'name': '#items',
                                'type': 'array',
                                'data_usage': 'PARENT_TEMPLATE_DATA',
                                'value': 'test.items',
                            },
                        ],
                        'items': [
                            {
                                'content': (
                                    '<span data-variable="index"/>)'
                                    '<span data-variable="test"/>-'
                                    '<span data-variable="other"/>\n'
                                ),
                            },
                        ],
                    },
                ],
                'else_items': [
                    {
                        'custom_item_id': 'ITERABLE',
                        'properties': {
                            'item_param_name': 'other',
                            'item_index_param_name': 'index',
                        },
                        'params': [
                            {
                                'name': '#items',
                                'type': 'array',
                                'data_usage': 'PARENT_TEMPLATE_DATA',
                                'value': 'test.items',
                            },
                        ],
                        'items': [
                            {
                                'content': (
                                    '<span data-variable="index"/>)'
                                    '<span data-variable="test"/>-'
                                    '<span data-variable="other"/>\n'
                                ),
                            },
                        ],
                    },
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            (
                {
                    'code': 'INVALID_TEMPLATE_ITEM',
                    'details': {},
                    'message': (
                        'Only in \'CONDITIONAL\' custom_item '
                        'else_items allowed'
                    ),
                }
            ),
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
