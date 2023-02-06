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
        mock_feeds,
        mock_driver_tags,
        mock_parks_replica,
        mock_fleet_parks,
        load_json,
):
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/slider', headers=HEADERS,
    )
    assert response.status == 200
    assert response.headers['X-Polling-Delay-Sec'] == '300'
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
@pytest.mark.parametrize(
    ['match_enabled', 'selection_id'],
    [
        pytest.param(
            True,
            'ml',
            marks=(
                pytest.mark.experiments3(
                    filename='personalize_offers_experiment_match.json',
                )
            ),
            id='experiment match',
        ),
        pytest.param(
            False,
            'handcrafted',
            marks=(
                pytest.mark.experiments3(
                    filename='personalize_offers_experiment_no_match.json',
                )
            ),
            id='experiment not match',
        ),
    ],
)
async def test_personalization(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_feeds,
        mock_driver_tags,
        mock_fleet_parks,
        mock_parks_replica,
        mock_umlaas_contractors,
        load_json,
        match_enabled,
        selection_id,
):
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/slider', headers=HEADERS,
    )
    assert response.headers['X-Selection-Provider'] == selection_id
    content = response.json()
    expected_response = load_json('rus_offers.json')
    if match_enabled:
        expected_response['offers'][0], expected_response['offers'][1] = (
            expected_response['offers'][1],
            expected_response['offers'][0],
        )
    if not match_enabled:
        expected_ml_times_called = 0
    else:
        expected_ml_times_called = 1
    assert (
        mock_umlaas_contractors.umlaas_contractors_offers_list.times_called
        == expected_ml_times_called
    )
    assert content == expected_response
