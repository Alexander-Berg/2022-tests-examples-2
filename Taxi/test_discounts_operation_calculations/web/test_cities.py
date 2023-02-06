import pytest


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_CITY_TZ_MAPPING={
        'Москва': ['moscow', 'lobnja', 'krasnogorsk'],
    },
)
async def test_get_cities(web_app_client):
    response = await web_app_client.get('/v1/cities')
    assert response.status == 200
    content = await response.json()
    assert content == [
        {
            'name': 'Москва',
            'tariff_zones': ['moscow', 'lobnja', 'krasnogorsk'],
        },
    ]
