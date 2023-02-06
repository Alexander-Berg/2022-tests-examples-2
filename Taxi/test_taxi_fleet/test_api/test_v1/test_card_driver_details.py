import aiohttp.web
import pytest


@pytest.mark.config(
    OPTEUM_CARD_DRIVER_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['work_status', 'providers'],
        'enable_backend': True,
    },
    OPTEUM_CARD_DRIVER_FIELDS_EDIT={
        'enable': True,
        'fields': ['phone'],
        'enable_backend': True,
    },
    TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'},
    FLEET_API_CAR_CATEGORIES={
        'external_categories': [],
        'internal_categories': ['econom'],
    },
)
async def test_success(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/retrieve')
    async def _driver_retrieve(request):
        assert request.json == stub['parks_driver_retrieve']['request']
        return aiohttp.web.json_response(
            stub['parks_driver_retrieve']['response'],
        )

    @mockserver.json_handler(
        '/cashbox-integration/v1/drivers/receipts/autocreation/list',
    )
    def _mock_cashbox_integration(request):
        return {
            'autocreation_list': [
                {
                    'driver_id': request.json['driver_ids'][0],
                    'is_enabled': True,
                },
            ],
        }

    response = await web_app_client.post(
        '/api/v1/cards/driver/details',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
