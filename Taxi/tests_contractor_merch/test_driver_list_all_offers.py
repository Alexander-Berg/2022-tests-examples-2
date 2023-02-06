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
        mock_umlaas_contractors,
):
    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/list-all',
        headers=HEADERS,
        json={'pagination': {'limit': 100}},
    )

    assert response.status == 200
    content = response.json()
    assert content == load_json('rus_offers.json')

    assert mock_feeds.fetch.times_called == 1
    assert mock_feeds.fetch.next_call()['request'].json['channels'] == [
        'country:rus',
        'city:city1',
        'contractor:park_id_driver_id',
        'experiment:contractor_merch_offer_matched',
        'tag:bronze',
        'tag:silver',
        'tag:gold',
    ]


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
async def test_cursor(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        mock_umlaas_contractors,
        load_json,
):
    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/list-all',
        headers=HEADERS,
        json={'pagination': {'limit': 1}},
    )

    assert response.status == 200
    content = response.json()
    expected_json = load_json('rus_offers.json')
    expected_json['offers'] = expected_json['offers'][:1]
    expected_json['next_cursor'] = '{\"offset\":1}'
    assert content == expected_json


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
async def test_next_cursor(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        mock_umlaas_contractors,
        load_json,
):
    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/list-all',
        headers=HEADERS,
        json={'pagination': {'cursor': '{\"offset\":1}', 'limit': 1}},
    )

    assert response.status == 200
    content = response.json()
    expected_json = load_json('rus_offers.json')
    expected_json['offers'] = expected_json['offers'][1:2]
    expected_json['next_cursor'] = '{\"offset\":2}'
    assert content == expected_json


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
async def test_category_id_filter(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        mock_umlaas_contractors,
        load_json,
):
    mock_feeds.tags_param_for_fetch = ['washing']
    mock_umlaas_contractors.custom_pinned_with_ranked_offers_json = load_json(
        'umlaas/pinned_with_ranked_offers.json',
    )[1:2]
    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/list-filter',
        headers=HEADERS,
        json={'category_id': 'washing', 'pagination': {'limit': 1}},
    )

    assert response.status == 200
    content = response.json()
    expected_json = load_json('rus_offers.json')
    expected_json['next_cursor'] = '{\"offset\":1}'
    expected_json['offers'] = expected_json['offers'][1:2]
    assert content == expected_json


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
async def test_invalid_cursor(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        mock_umlaas_contractors,
        load_json,
):
    response = await taxi_contractor_merch.post(
        '/driver/v1/contractor-merch/v1/list-all',
        headers=HEADERS,
        json={'pagination': {'cursor': 'keking_online'}},
    )

    assert response.status == 400
    content = response.json()
    expected_json = {'code': '400', 'message': 'Invalid cursor'}
    assert content == expected_json
