import pytest

TRANSLATIONS = {'Food': {'ru': 'Еда', 'en': 'Food'}}


@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=[
        {
            'category': 'food',
            'name': 'Food',
            'icon_url': 'https://example.com/im.png',
            'icon_url_night': 'https://example.com/im.png',
        },
        {
            'category': 'service',
            'name': 'invalid_key',
            'icon_url': 'https://example.com/im.png',
            'icon_url_night': 'https://example.com/im.png',
        },
        {
            'category': 'zip',
            'name': 'other_key',
            'icon_url': 'https://example.com/im.png',
            'icon_url_night': 'https://example.com/im.png',
            'priority': 1,
        },
    ],
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_partner_categories(web_app_client):
    response = await web_app_client.post(
        '/internal/v1/partners/categories/list',
        headers={'Accept-Language': 'en-US,en'},
    )
    assert response.status == 200, await response.text()
    expected = {
        'categories': [
            {'code': 'zip', 'label': 'zip'},
            {'code': 'food', 'label': 'Food'},
            {'code': 'service', 'label': 'service'},
        ],
    }
    resp_json = await response.json()
    assert resp_json == expected
