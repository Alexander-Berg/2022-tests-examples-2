import pytest

from tests_contractor_merch import util

PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.50',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Selection-Id': 'selection_id_1',
    'Accept-Language': 'en_GB',
}

TRANSLATIONS = {
    'list_v1.title': {'en': 'Title'},
    'list_v1.subtitle': {'en': 'Subtitle'},
    'category.tire': {'en': 'Tires and so'},
    'category.washing': {'en': 'Washing and so'},
    'category.washing.slider': {'en': 'WASH-WASH-WASH'},
    'category.shawerma': {'en': 'Best Shawerma'},
    'category.shawerma.slider': {'en': 'EAT-EAT-EAT'},
}
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
async def test_ok(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        load_json,
):
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/categories', headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    assert content == load_json('ok_response.json')
