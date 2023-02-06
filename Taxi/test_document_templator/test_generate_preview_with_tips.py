import http

import pytest


@pytest.mark.parametrize(
    'item, generated_text',
    (
        (
            {'content': '<span data-variable="custom_param"></span>'},
            '<span style="position:relative;color:#4296ea;">1<span '
            'style="position: absolute; top: -4px; right: -10px; '
            'font-size: 8px; color: Coral">custom_param</span></span>',
        ),
        (
            {
                'content': (
                    '<span data-template-item-id='
                    '"000000000000000000000003"/>'
                ),
                'items': [
                    {
                        'id': '000000000000000000000003',
                        'template_id': '000000000000000000000001',
                        'enumerators': [
                            {
                                'name': 'base',
                                'template_enumerator_name': 'main',
                            },
                            {
                                'name': 'sub_base',
                                'template_enumerator_name': 'sub_main',
                            },
                        ],
                    },
                ],
            },
            '<span style="position: relative;box-shadow: 0 1px '
            '#CA6F1E; line-height: 24px">'
            '<span style="position: absolute;left: 0;top: '
            '-13px;font-size: 8px;color: #CA6F1E;white-space: '
            'nowrap">has no dependency</span>---2---2.2</span>',
        ),
        (
            {'content': '<span data-enumerator="main"></span>'},
            '<span style="position:relative;color:#6fc016;">2<span '
            'style="position: absolute; top: -4px; right: -10px; '
            'font-size: 8px; color: Coral">main</span></span>',
        ),
        (
            {'template_id': '000000000000000000000001'},
            '<span style="position: relative;box-shadow: 0 1px '
            '#CA6F1E; line-height: 24px">'
            '<span style="position: absolute;left: 0;top: '
            '-13px;font-size: 8px;color: #CA6F1E;white-space: '
            'nowrap">has no dependency</span>---1---1.1</span>',
        ),
    ),
)
async def test_generate_preview_with_tips(
        api_app_client, item, generated_text,
):
    body = {
        'template': {
            'name': 'test',
            'params': [{'name': 'custom_param', 'type': 'string'}],
            'description': 'test',
            'enumerators': [
                {
                    'name': 'main',
                    'formatter': {
                        'code': 'ARABIC_NUMBER',
                        'start_symbol': '2',
                    },
                },
                {
                    'name': 'sub_main',
                    'formatter': {
                        'code': 'ARABIC_NUMBER',
                        'start_symbol': '2',
                    },
                    'parent_name': 'main',
                },
            ],
            'items': [item],
        },
        'requests_params': [],
        'params': [{'name': 'custom_param', 'value': '1'}],
    }
    expected_data = {'generated_text': generated_text}
    headers = {'X-Yandex-Login': 'test_name'}
    response = await api_app_client.post(
        '/v1/templates/preview/generate/',
        json=body,
        headers=headers,
        params={'show_tips': 'true'},
    )
    assert response.status == http.HTTPStatus.OK, await response.json()
    content = await response.json()
    content.pop('id')
    content.pop('status')
    assert content == expected_data
