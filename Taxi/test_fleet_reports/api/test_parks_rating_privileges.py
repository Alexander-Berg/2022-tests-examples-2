import pytest

ENDPOINT = '/reports-api/v1/parks-rating/privileges'


@pytest.mark.config(
    FLEET_REPORTS_PARKS_RATING_PRIVILEGES={
        'bronze': {},
        'gold': {
            'back_call': True,
            'driver_priority': 12,
            'faster_support_response': True,
            'service_discount': 100,
        },
        'silver': {'service_discount': 40},
    },
)
async def test_success(web_app_client, headers):
    response = await web_app_client.get(ENDPOINT, headers=headers)

    assert response.status == 200

    data = await response.json()
    assert data == {
        'bronze': {},
        'gold': {
            'back_call': True,
            'driver_priority': 12,
            'faster_support_response': True,
            'service_discount': 100,
        },
        'silver': {'service_discount': 40},
    }
