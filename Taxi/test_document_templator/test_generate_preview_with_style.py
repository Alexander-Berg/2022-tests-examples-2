import http
from unittest import mock

import pytest


@pytest.mark.parametrize(
    'item, generated_text',
    (
        pytest.param(
            {'content': 'content'},
            '<span class=111111111111111111111111>\n'
            '<style>\n'
            '[class="111111111111111111111111"] p {\n'
            'color: red;'
            '\n}'
            '\n'
            '[class="111111111111111111111111"] table {\n'
            'width: 100%;'
            '\n'
            '}\n'
            '</style>\n'
            'content\n'
            '</span>\n',
            id='ok',
        ),
    ),
)
async def test_generate_preview_with_style(
        api_app_client, item, generated_text,
):
    body = {
        'template': {
            'name': 'test',
            'params': [{'name': 'custom_param', 'type': 'string'}],
            'description': 'test',
            'css_style': (
                """
p {
color: red;
}

table {
width: 100%;
}
""".strip()
            ),
            'items': [item],
        },
        'requests_params': [],
        'params': [{'name': 'custom_param', 'value': '1'}],
    }
    expected_data = {'generated_text': generated_text}
    headers = {'X-Yandex-Login': 'test_name'}
    with mock.patch(
            'document_templator.models.template.generate_template_id',
            return_value='1' * 24,
    ):

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
