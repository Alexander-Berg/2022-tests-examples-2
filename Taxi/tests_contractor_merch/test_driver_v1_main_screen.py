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
    'category.shopping': {'en': 'Best shopping'},
    'category.shopping.slider': {'en': 'shopping'},
    'category.groceries': {'en': 'Best groceries'},
    'category.groceries.slider': {'en': 'groceries'},
    'category.tech': {'en': 'Best tech'},
    'category.tech.slider': {'en': 'tech'},
}
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.parametrize(
    'long_categories',
    [
        pytest.param(
            False, marks=(pytest.mark.experiments3()), id='two categories',
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_many_categories.json',
                )
            ),
            id='many categories',
        ),
    ],
)
@pytest.mark.config(CONTRACTOR_MERCH_MAIN_CATEGORIES_NUMBER=3)
async def test_ok(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_feeds,
        mock_driver_tags,
        mock_parks_replica,
        mock_fleet_parks,
        mock_umlaas_contractors,
        load_json,
        long_categories,
):
    if long_categories:
        mock_feeds.set_response(load_json('responses/big_feeds_response.json'))

    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/main-screen', headers=HEADERS,
    )
    assert response.status == 200
    content = response.json()
    expected_response = load_json('response.json')
    if not long_categories:
        assert content == expected_response
    else:
        expected_response['categories'].append(
            {
                'background_color': 'blue',
                'category_id': 'shopping',
                'category_image': '<url>',
                'name': 'Best shopping',
                'text_color': 'white',
            },
        )
        assert content == expected_response

    assert (
        mock_umlaas_contractors.umlaas_contractors_offers_list_flutter.times_called  # noqa: E501
        == 1
    )

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
async def test_not_found(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_feeds,
        mock_driver_tags,
        mock_parks_replica,
        mock_fleet_parks,
        mock_umlaas_contractors,
        load_json,
):
    mock_umlaas_contractors.make_flutter_list_failure()
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/main-screen', headers=HEADERS,
    )
    assert response.status == 500
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
