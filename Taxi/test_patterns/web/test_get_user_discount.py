import pytest


@pytest.mark.parametrize(
    'query, body_file',
    [
        ({'pattern_id': '5d0d164f21893e00011b4bcf'}, 'request_body_0.json'),
        ({'pattern_id': '5d0d164f21893e00011b4bcf'}, 'request_body_1.json'),
    ],
)
async def test_handler(query, body_file, web_app_client, load_json):
    body = load_json(body_file)
    response = await web_app_client.request(
        'GET', '/v1/get/user_discounts/', params=query, json=body,
    )
    assert response.status == 200
