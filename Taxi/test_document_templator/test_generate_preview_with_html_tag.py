import http
import json

import pytest


@pytest.mark.parametrize(
    'item, expected_status, expected_content',
    (
        (
            {
                'id': '5ea2da0eff4168fb0b369208',
                'custom_item_id': 'HTML_TAG',
                'params': [
                    {
                        'name': '#html-tag-name',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'a',
                    },
                    {
                        'name': '#html-tag-text',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'Yandex',
                    },
                    {
                        'name': 'href',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'https://www.yandex.ru',
                    },
                ],
            },
            http.HTTPStatus.OK,
            '<a href="https://www.yandex.ru">Yandex</a>',
        ),
        (
            {
                'id': '5ea2da0eff4168fb0b369208',
                'custom_item_id': 'HTML_TAG',
                'params': [
                    {
                        'name': '#html-tag-text',
                        'type': 'string',
                        'data_usage': 'OWN_DATA',
                        'value': 'Yandex',
                    },
                ],
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'NOT_ALL_PARAMETERS_SET',
                'details': {},
                'message': (
                    'Not all parameters set. Got: "#html-tag-text". '
                    'Need: "#html-tag-name".'
                ),
            },
        ),
    ),
)
async def test_generate_preview_with_html_tag(
        api_app_client, item, expected_status, expected_content,
):
    body = {
        'template': {
            'name': 'test',
            'description': 'test',
            'items': [
                {
                    'id': '5ea2c190eb5846af1fae1a59',
                    'content': (
                        '<a title="Dynamic Link" '
                        'data-template-item-id="5ea2da0eff4168fb0b369208">'
                        'Dynamic Link</a>'
                    ),
                    'items': [item],
                    'inherited': False,
                    'enabled': True,
                },
            ],
        },
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
