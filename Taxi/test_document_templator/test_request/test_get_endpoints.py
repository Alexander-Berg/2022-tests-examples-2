import http

import pytest

from test_document_templator.test_request import common


@pytest.mark.config(**common.CONFIG)
async def test_getting_endpoints(api_app_client):
    headers = {}
    expected_status = http.HTTPStatus.OK
    expected_content = {
        'items': [
            {
                'name': common.TARIFF,
                'substitutions': ['tariff', 'zone'],
                'method': 'POST',
            },
            {'name': common.SURGE, 'substitutions': [], 'method': 'GET'},
            {
                'name': common.NOT_IN_DB,
                'substitutions': ['db'],
                'method': 'GET',
            },
        ],
    }
    response = await api_app_client.get(
        '/v1/requests/endpoints/', headers=headers,
    )
    content = await response.json()
    assert response.status == expected_status, content
    content['items'] = [
        item
        for item in content['items']
        if not item['name'].startswith('configs/')
    ]
    assert content == expected_content
