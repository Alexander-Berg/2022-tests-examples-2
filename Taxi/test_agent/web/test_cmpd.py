import pytest


@pytest.mark.parametrize(
    'url,expected_data',
    [
        ('/cmpd/callcenter_reserve', {'results': {}}),
        (
            '/cmpd/callcenter_reserve?logins=webalex',
            {
                'results': {
                    'webalex': {
                        'reserve': 1000.0,
                        'bo': 0,
                        'is_contractor': False,
                    },
                },
            },
        ),
        (
            '/cmpd/callcenter_reserve?logins=liambaev',
            {
                'results': {
                    'liambaev': {
                        'reserve': 1234.0,
                        'bo': 4321.0,
                        'is_contractor': True,
                    },
                },
            },
        ),
    ],
)
async def test_create_news(web_context, web_app_client, url, expected_data):
    response = await web_app_client.get(url)
    assert response.status == 200
    content = await response.json()
    assert content == expected_data
