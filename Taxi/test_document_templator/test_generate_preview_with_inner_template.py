import json

import pytest


@pytest.mark.parametrize(
    'item, expected_content, expected_status',
    (
        pytest.param(
            {
                'template': {
                    'name': 'String Provider',
                    'description': 'String Provider',
                    'requests': [],
                    'params': [
                        {
                            'name': 'param',
                            'type': 'string',
                            'inherited': False,
                            'enabled': True,
                        },
                    ],
                    'items': [
                        {
                            'id': '5e73d2599519e9df383de392',
                            'content': '<a data-variable="param"/>',
                            'inherited': False,
                            'enabled': True,
                        },
                    ],
                },
                'params': [
                    {
                        'name': 'param',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'param_value',
                    },
                ],
                'custom_item_id': 'INNER_TEMPLATE',
            },
            {'generated_text': 'param_value'},
            200,
            id='ok',
        ),
        pytest.param(
            {
                'template': {
                    'name': 'String Provider',
                    'description': 'String Provider',
                    'requests': [],
                    'params': [
                        {
                            'name': 'param',
                            'type': 'string',
                            'inherited': False,
                            'enabled': True,
                        },
                    ],
                    'items': [
                        {
                            'id': '5e73d2599519e9df383de392',
                            'content': '<a data-variable="param"/>',
                            'inherited': False,
                            'enabled': True,
                        },
                    ],
                },
                'params': [
                    {
                        'name': 'param',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'param_value',
                    },
                ],
            },
            {
                'code': 'INVALID_TEMPLATE_ITEM',
                'message': (
                    'Only in \'INNER_TEMPLATE\' custom_item '
                    'template allowed and required'
                ),
                'details': {},
            },
            400,
            id='template_without_INNER_TEMPLATE',
        ),
        pytest.param(
            {
                'content': 'test',
                'params': [
                    {
                        'name': 'param',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'param_value',
                    },
                ],
                'custom_item_id': 'INNER_TEMPLATE',
            },
            {
                'code': 'INVALID_TEMPLATE_ITEM',
                'message': (
                    'Only in \'INNER_TEMPLATE\' custom_item '
                    'template allowed and required'
                ),
                'details': {},
            },
            400,
            id='INNER_TEMPLATE_without_template',
        ),
    ),
)
async def test_generate_with_inner_template(
        api_app_client, item, expected_content, expected_status,
):
    headers = {'X-Yandex-Login': 'test_name'}

    body = {
        'template': {'name': 'name', 'description': 'test', 'items': [item]},
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content
