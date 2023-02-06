import copy

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
        '/driver/v1/contractor-merch/v1/list', headers=HEADERS,
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


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
async def test_feeds_count_metrics(
        taxi_contractor_merch,
        taxi_contractor_merch_monitor,
        mockserver,
        mocked_time,
        mock_billing_replication,
        mock_driver_tags,
        mock_fleet_parks,
        mock_parks_replica,
):
    @mockserver.json_handler('/feeds/v1/fetch')
    async def _feeds(request):
        return {
            'polling_delay': 100,
            'etag': '100',
            'feed': [
                {
                    'feed_id': 'feed-id-1',
                    'request_id': 'request_id',
                    'package_id': 'feeds-admin-id-1',
                    'created': '2021-06-11T03:00:15.890537+0000',
                    'expire': '2021-07-09T03:00:15.890537+0000',
                    'last_status': {
                        'status': 'published',
                        'created': '2021-06-11T03:00:15.896104+0000',
                    },
                    'payload': {
                        'feeds_admin_id': 'feeds-admin-id-1',
                        'price': '200.0000',
                        'categories': ['tire'],
                        'name': 'RRRR',
                        'partner': {'name': 'Apple'},
                        'balance_payment': True,
                        'meta_info': {},
                        'title': 'Title',
                        'actions': [
                            {
                                'data': 'https://media.5ka.ru/',
                                'text': 'Медиа',
                                'type': 'link',
                            },
                        ],
                        'place_id': 1,
                        'offer_id': 'metric',
                    },
                },
            ] * 100,
            'has_more': False,
        }

    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/list', headers=HEADERS,
    )

    assert response.status == 200
    assert len(response.json()['offers']) == 100

    metrics = await taxi_contractor_merch_monitor.get_metrics('feeds-count')

    assert metrics['feeds-count']['1min']['max'] == 100


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
async def test_personalizing_offers(
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
        '/driver/v1/contractor-merch/v1/list', headers=HEADERS,
    )
    assert response.headers['X-Selection-Provider'] == selection_id
    assert response.headers['X-Driver-Profile-Id'] == DRIVER_ID
    content = response.json()
    expected_response = load_json('rus_offers.json')
    if not match_enabled:
        expected_ml_times_called = 0
    else:
        expected_ml_times_called = 1
        for i in range(len(expected_response['offers'])):
            offer = expected_response['offers'][i]
            offer['offer_data']['place_id'] = i
    assert (
        mock_umlaas_contractors.umlaas_contractors_offers_list.times_called
        == expected_ml_times_called
    )
    assert content == expected_response


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['crawler_data.sql'])
async def test_crawler_data_removal(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_feeds,
        mock_driver_tags,
        mock_fleet_parks,
        mock_parks_replica,
        mock_umlaas_contractors,
        load_json,
):
    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/list', headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    expected_response = load_json('rus_offers.json')
    del expected_response['offers'][1]
    assert content == expected_response


TRANSLATIONS_WITHOUT_SOME_TRANSLATIONS = copy.deepcopy(TRANSLATIONS)
TRANSLATIONS_WITHOUT_SOME_TRANSLATIONS.pop('category.tire')
TRANSLATIONS_WITHOUT_SOME_TRANSLATIONS.pop('category.shawerma.slider')


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS_WITHOUT_SOME_TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3(
    filename='experiments3_for_testing_translations.json',
)
async def test_category_has_no_translation(
        taxi_contractor_merch,
        taxi_contractor_merch_monitor,
        mock_billing_replication,
        mock_feeds,
        mock_driver_tags,
        mock_fleet_parks,
        mock_parks_replica,
        load_json,
        mockserver,
):
    @mockserver.json_handler('feeds/v1/fetch')
    async def _fetch(request):
        return load_json('feeds_response_for_testing_translations.json')

    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/list', headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    expected_response = load_json('rus_offers_for_testing_translations.json')
    assert content == expected_response

    metrics = await taxi_contractor_merch_monitor.get_metrics(
        'categories-without-translation',
    )

    assert metrics['categories-without-translation'] == 2


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
async def test_offers_place_id_sort(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        load_json,
):
    mock_feeds.response = load_json(
        'responses/feeds_response_place_id_test.json',
    )

    response = await taxi_contractor_merch.get(
        '/driver/v1/contractor-merch/v1/list', headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    assert content == load_json('rus_offers_place_id_test.json')

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
