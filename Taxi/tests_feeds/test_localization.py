import pytest


async def _fetch(taxi_feeds, locale=None, locales=None):
    response = await taxi_feeds.post(
        '/v1/fetch',
        json={
            'service': 'service',
            'channels': ['channel'],
            'locale': locale,
            'locales': locales,
        },
    )

    assert response.status_code == 200
    return [feed['payload']['text'] for feed in response.json()['feed']]


TRANSLATIONS = {
    'key1': {'ru': 'ru1', 'en': 'en1'},
    'key2': {'en': 'en2', 'az': 'az2'},
    'key3': {'az': 'az3'},
}


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': '-',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
        },
    },
)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.pgsql('feeds-pg', files=['test_localize.sql'])
async def test_skip_failed_localizations(taxi_feeds):
    # key3 don't have 'en' and no default_locale in service - skip it
    assert await _fetch(taxi_feeds, locale='en') == ['en1', 'en2', 'ok']


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': '-',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'default_locale': 'ru',
        },
    },
)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.pgsql('feeds-pg', files=['test_localize.sql'])
async def test_default_locale(taxi_feeds):
    assert await _fetch(taxi_feeds) == await _fetch(taxi_feeds, 'ru')


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': '-',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'fallback_locales': ['en', 'az'],
        },
    },
)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.pgsql('feeds-pg', files=['test_localize.sql'])
async def test_fallback_locales(taxi_feeds):
    # key1 don't have 'az' - fallback to 'en'
    assert await _fetch(taxi_feeds, locale='az') == ['en1', 'az2', 'az3', 'ok']

    # key2, key3 don't have 'ru' - fallback to 'en'
    assert await _fetch(taxi_feeds, locale='ru') == ['ru1', 'en2', 'az3', 'ok']

    # key1, key2, key3 don't have 'fr' - fallback to 'en', then 'az'
    assert await _fetch(taxi_feeds, locale='fr') == ['en1', 'en2', 'az3', 'ok']


@pytest.mark.config(
    FEEDS_SERVICES={
        'service': {
            'description': '-',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
            'fallback_locales': ['az'],
        },
    },
)
@pytest.mark.now('2018-12-10T00:00:00Z')
@pytest.mark.translations(client_messages=TRANSLATIONS)
@pytest.mark.pgsql('feeds-pg', files=['test_localize.sql'])
async def test_multiple_locales(taxi_feeds):
    assert await _fetch(taxi_feeds, locales=['ru', 'en']) == [
        'ru1',
        'en2',
        'az3',
        'ok',
    ]
