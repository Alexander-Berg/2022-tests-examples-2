import http
import json

import pytest


@pytest.mark.parametrize(
    'item, expected_status, expected_content',
    (
        pytest.param(
            {
                'custom_item_id': 'TABLE',
                'properties': {
                    'item_param_name': 'test',
                    'table_data': {
                        'columns': [
                            {
                                'head': 'Head a',
                                'content': (
                                    '<a data-template-item-id='
                                    '"5ff4901c583745e089e55ba6"/>'
                                ),
                                'items': [
                                    {
                                        'id': '5ff4901c583745e089e55ba6',
                                        'template_id': (
                                            '5d27219b73f3b64036c0a03a'
                                        ),
                                        'params': [
                                            {
                                                'name': 'str',
                                                'value': 'test.a',
                                                'data_usage': (
                                                    'PARENT_TEMPLATE_DATA'
                                                ),
                                                'type': 'string',
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                'head': 'Head b',
                                'content': '<span data-variable="test.b"/>',
                            },
                        ],
                    },
                },
                'params': [
                    {
                        'name': '#rows',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 'first', 'b': 2},
                            {'a': 'second', 'b': 5},
                        ],
                    },
                ],
            },
            http.HTTPStatus.OK,
            (
                '<table>'
                '<tr>'
                '<td style="border: 1px solid;">Head a</td>'
                '<td style="border: 1px solid;">Head b</td>'
                '</tr>'
                '<tr>'
                '<td style="border: 1px solid;">'
                'Simple text and resolved parent template '
                'parameter&nbsp;first</td>'
                '<td style="border: 1px solid;">2</td>'
                '</tr>'
                '<tr>'
                '<td style="border: 1px solid;">'
                'Simple text and resolved parent '
                'template parameter&nbsp;second</td>'
                '<td style="border: 1px solid;">5</td>'
                '</tr>'
                '</table>'
            ),
            id='ok',
        ),
        pytest.param(
            {
                'custom_item_id': 'TABLE',
                'properties': {
                    'item_param_name': 'test',
                    'table_data': {
                        'columns': [
                            {
                                'head': 'Head a',
                                'content': (
                                    '<a data-template-item-id='
                                    '"5ff4901c583745e089e55ba6"/>'
                                ),
                                'items': [
                                    {
                                        'id': '5ff4901c583745e089e55ba6',
                                        'template_id': (
                                            '5d27219b73f3b64036c0a03a'
                                        ),
                                        'params': [
                                            {
                                                'name': 'str',
                                                'value': 'test.a',
                                                'data_usage': (
                                                    'PARENT_TEMPLATE_DATA'
                                                ),
                                                'type': 'string',
                                            },
                                        ],
                                    },
                                ],
                            },
                            {
                                'head': 'Head b',
                                'content': '<span data-variable="test.b"/>',
                            },
                        ],
                    },
                },
                'params': [
                    {
                        'name': '#rows',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 'first', 'b': 2},
                            {'a': 'second', 'b': 5},
                        ],
                    },
                    {
                        'name': '#table-attrs',
                        'type': 'object',
                        'data_usage': 'OWN_DATA',
                        'value': {'border': '1'},
                    },
                ],
            },
            http.HTTPStatus.OK,
            (
                '<table border="1">'
                '<tr>'
                '<td style="border: 1px solid;">Head a</td>'
                '<td style="border: 1px solid;">Head b</td>'
                '</tr>'
                '<tr>'
                '<td style="border: 1px solid;">'
                'Simple text and resolved parent template '
                'parameter&nbsp;first</td>'
                '<td style="border: 1px solid;">2</td>'
                '</tr>'
                '<tr>'
                '<td style="border: 1px solid;">'
                'Simple text and resolved parent '
                'template parameter&nbsp;second</td>'
                '<td style="border: 1px solid;">5</td>'
                '</tr>'
                '</table>'
            ),
            id='ok-with-attrs',
        ),
        pytest.param(
            {
                'custom_item_id': 'TABLE',
                'properties': {
                    'table_data': {
                        'columns': [
                            {
                                'head': 'with invalid items(param not valid)',
                                'items': [
                                    {
                                        'id': '5ff4901c583745e089e55ba6',
                                        'template_id': (
                                            '5d27219b73f3b64036c0a03a'
                                        ),
                                        'params': [{'name': 'str'}],
                                    },
                                ],
                            },
                        ],
                    },
                },
                'params': [
                    {
                        'name': '#rows',
                        'type': 'array',
                        'data_usage': 'OWN_DATA',
                        'value': [{'b': 2}],
                    },
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_TEMPLATE_ITEM_PROPERTY',
                'message': 'Invalid template item property.',
                'details': {
                    'detail': (
                        'Invalid value for params_item: discriminator '
                        'property `data_usage` is missing'
                    ),
                    'property': {
                        'table_data': {
                            'columns': [
                                {
                                    'head': (
                                        'with invalid items(param '
                                        'not valid)'
                                    ),
                                    'items': [
                                        {
                                            'id': '5ff4901c583745e089e55ba6',
                                            'params': [{'name': 'str'}],
                                            'template_id': (
                                                '5d27219b73f3b64036c0a03a'
                                            ),
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                },
            },
            id='invalid-property',
        ),
    ),
)
async def test_generate_preview_with_table(
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
    if expected_status == http.HTTPStatus.OK:
        assert content['generated_text'] == expected_content
    else:
        assert content == expected_content
