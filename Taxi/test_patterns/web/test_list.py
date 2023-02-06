import pytest


@pytest.mark.parametrize(
    'query, body_file',
    [
        ({}, 'request_body_0.json'),
        (
            {
                'pattern_type': 'str_value',
                'limit': '1',
                'newer_than': '5d1092fbde8d2800015f25c9',
                'older_than': '5d1092fbde8d2800015f25ca',
            },
            'request_body_1.json',
        ),
    ],
)
async def test_handler(query, body_file, web_app_client, load_json):
    body = load_json(body_file)
    response = await web_app_client.request(
        'GET', '/v1/list/', params=query, json=body,
    )
    assert response.status == 200
