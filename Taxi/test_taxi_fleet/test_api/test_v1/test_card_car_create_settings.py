import pytest


@pytest.mark.config(
    OPTEUM_CARD_TC_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['brand', 'model'],
        'enable_backend': True,
    },
)
async def test_global_success(web_app_client, mock_parks, headers):

    response = await web_app_client.post(
        '/api/v1/cards/car/create-settings', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'required_fields': ['brand', 'model'],
        'required_categories': [],
    }


@pytest.mark.config(
    OPTEUM_CARD_TC_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['brand', 'model'],
        'enable_backend': True,
    },
)
@pytest.mark.config(
    FLEET_COUNTRY_PROPERTIES={'rus': {'required_fields': ['vin']}},
)
async def test_local_success(web_app_client, mock_parks, headers):

    response = await web_app_client.post(
        '/api/v1/cards/car/create-settings', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'required_fields': ['vin'], 'required_categories': []}
