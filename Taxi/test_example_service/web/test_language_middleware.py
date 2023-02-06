import pytest


@pytest.mark.config(LOCALES_SUPPORTED=['ru', 'en', 'fr'])
@pytest.mark.parametrize(
    'accept_language, expected_language',
    [
        ('', 'ru'),
        ('en-US', 'en'),
        ('de-CH, en;q=0.9, fr;q=0.8, *;q=0.5', 'en'),
    ],
    ids=('missing header', 'single_locale', 'quality_locales'),
)
async def test_language(web_app_client, accept_language, expected_language):
    headers = {'Accept-Language': accept_language}

    response = await web_app_client.get('/language/echo', headers=headers)
    assert response.status == 200
    response_json = await response.json()
    assert response_json['language'] == expected_language
