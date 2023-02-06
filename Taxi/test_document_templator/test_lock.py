import asyncio
import http

import pytest


@pytest.mark.now('2019-11-20T03:00:00+03:00')
async def test_put_dynamic_document_twice(api_app_client):
    body = {
        'name': 'new name',
        'description': 'new description',
        'template_id': '000000000000000000000001',
    }
    query = {'id': '000009999988888777772222', 'version': 1}

    headers = {'X-Yandex-Login': 'robot'}
    good_expected_content = {
        'created_at': '2018-07-01T00:00:00+03:00',
        'created_by': 'venimaster',
        'description': 'new description',
        'generated_text': '---1---1.1',
        'id': '000009999988888777772222',
        'generated_at': '2019-11-20T03:00:00+03:00',
        'generated_by': 'robot',
        'is_valid': True,
        'modified_at': '2019-11-20T03:00:00+03:00',
        'modified_by': 'robot',
        'name': 'new name',
        'template_id': '000000000000000000000001',
        'version': 2,
    }
    coros = [
        api_app_client.put(
            '/v1/dynamic_documents/', params=query, json=body, headers=headers,
        )
        for _ in range(2)
    ]
    good_response, bad_response = await asyncio.gather(*coros)

    if good_response.status != http.HTTPStatus.OK:
        good_response, bad_response = bad_response, good_response

    good_content = await good_response.json()
    bad_content = await bad_response.json()

    assert good_response.status == http.HTTPStatus.OK, good_content
    assert good_content == good_expected_content
    assert bad_response.status in (
        http.HTTPStatus.INTERNAL_SERVER_ERROR,
        http.HTTPStatus.BAD_REQUEST,
    ), bad_content
