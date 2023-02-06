import http

import pytest


@pytest.mark.now('2020-03-05T10:00:00')
async def test_generate_preview_with_iterable(api_app_client):
    body = {
        'template': {
            'name': 'test',
            'description': 'test',
            'items': [{'template_id': '000000000000000000000001'}],
        },
    }
    headers = {'X-Yandex-Login': 'robot'}
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.json()
    assert response.status == http.HTTPStatus.OK
    assert content['generated_text'] == 'Date: 2020-03-05T07:00:00+00:00'
