import pytest


@pytest.mark.config(
    OPTEUM_CARD_DRIVER_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['work_status', 'providers'],
        'enable_backend': True,
    },
    OPTEUM_CARD_DRIVER_DEFAULT_BALANCE={
        'countries': [{'code': 'rus', 'value': 3}],
        'default': 5,
    },
)
async def test_success(web_app_client, mock_parks, headers):
    response = await web_app_client.post(
        '/api/v1/cards/driver/create-settings', headers=headers,
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'required_fields': ['work_status', 'providers'],
        'default_balance_limit': 3,
    }
