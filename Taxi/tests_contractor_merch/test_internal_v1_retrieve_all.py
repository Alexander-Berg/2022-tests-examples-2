import pytest

from tests_contractor_merch import util

TRANSLATIONS = util.STQ_TRANSLATIONS
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS


@pytest.fixture(name='mock_tags')
def _mock_tags(mockserver, load_json):
    @mockserver.json_handler('driver-tags/v1/drivers/match/profile')
    async def _match_profile(request):
        assert request.json == {
            'dbid': 'park_id',
            'uuid': 'driver_profile_id',
            'topics': ['marketplace'],
        }

        return {'tags': ['Silver', 'Bronze']}

    return _match_profile


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_ok(
        taxi_contractor_merch,
        mock_billing_replication,
        mock_feeds,
        mock_fleet_parks,
        mock_parks_replica,
        mock_tags,
):
    response = await taxi_contractor_merch.post(
        '/internal/contractor-merch/v1/offers/retrieve-all',
        json={
            'driver': {
                'park_id': 'park_id',
                'driver_profile_id': 'driver_profile_id',
            },
        },
    )

    assert response.status == 200
    assert response.json() == {
        'categories': [
            {
                'icon_url': '<url_to_pins_icon>',
                'icon_url_night': '<url_to_pins_night_icon>',
                'id': 'tire',
                'name': 'Категория шины',
                'priority': 1,
            },
            {
                'icon_url': '<url_to_pins_icon>',
                'icon_url_night': '<url_to_pins_night_icon>',
                'id': 'washing',
                'name': 'Категория мойка',
                'priority': 2,
            },
            {
                'id': 'keking',
                'name': 'Категория мойка',
                'icon_url': '<url_to_pins_icon>',
                'icon_url_night': '<url_to_pins_night_icon>',
                'priority': 0,
            },
        ],
        'feeds': [
            {
                'category_ids': ['tire'],
                'feed_id': 'feed-id-1',
                'feeds_admin_id': 'feeds-admin-id-1',
                'price': '200.0000',
                'title': 'Title',
            },
            {
                'category_ids': ['tire', 'food'],
                'feed_id': 'feed-id-2',
                'feeds_admin_id': 'feeds-admin-id-x',
                'title': 'Title',
                'subtitle': '<subtitle>',
                'description': '<description>',
                'image_url': 'yandex.ru',
            },
        ],
    }

    assert mock_tags.times_called == 1
    assert mock_feeds.fetch.times_called == 1
    assert mock_feeds.fetch.next_call()['request'].json == {
        'service': 'contractor-marketplace',
        'channels': [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_profile_id',
            'tag:Silver',
            'tag:Bronze',
        ],
        'locale': 'ru',
    }
