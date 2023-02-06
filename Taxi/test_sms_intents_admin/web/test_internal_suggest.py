import pytest


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': ['example_service'],
        'cost_center': ['one', 'two'],
        'random_name': ['foo', 'bar'],
        'provider_settings': {'yasms': {'route': ['taxi']}},
    },
)
async def test_suggest(web_app_client):
    response = await web_app_client.get('/v1/internal/suggest')
    assert response.status == 200

    content = await response.json()
    assert content == {
        'business_group': ['example_service'],
        'cost_center': ['one', 'two'],
        'meta_type': [],
        'provider_settings': {
            'yasms': {'route': ['taxi'], 'sender': []},
            'infobip': {'account': []},
        },
    }
