import pytest


@pytest.mark.parametrize(
    'query, body_file',
    [({}, 'request_body_0.json'), ({}, 'request_body_1.json')],
)
async def test_handler(query, body_file, web_app_client, load_json):
    body = load_json(body_file)
    response = await web_app_client.request(
        'POST',
        '/v1/validate/subvention_daily_rules/',
        params=query,
        json=body,
    )
    assert response.status == 200
