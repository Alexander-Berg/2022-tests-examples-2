# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import datetime

import pytest


NOW = datetime.datetime.utcnow().replace(microsecond=0)
SETTINGS = {'get_by_name_memoize_time': 0}


@pytest.fixture
def cache_handler(web_context):
    from corp_tariffs.caches import tariff_zones
    return tariff_zones.TariffZonesHandler(web_context, SETTINGS)


async def test_empty(db, cache_handler, mock_tariff_zones):
    mock_tariff_zones.data.zones = []

    await cache_handler.refresh_cache()
    assert not cache_handler._cache.tariff_zones


@pytest.mark.parametrize('refresh_disabled', [False, True])
async def test_refresh_disabled(
        web_context, cache_handler, refresh_disabled, mock_tariff_zones,
):

    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'tariff_zones': {'refresh_disabled': refresh_disabled},
    }

    mock_tariff_zones.data.zones = {
        'zones': [
            {
                'name': 'spb',
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': 'Санкт-Петербург',
                'currency': 'RUB',
            },
        ],
    }

    await cache_handler.refresh_cache()
    assert bool(cache_handler._cache.tariff_zones) != refresh_disabled


@pytest.mark.parametrize(
    'disabled',
    [
        pytest.param(False, id='cache_enabled'),
        pytest.param(True, id='cache_disabled'),
    ],
)
@pytest.mark.parametrize(
    'refresh_disabled',
    [
        pytest.param(False, id='refresh_enabled'),
        pytest.param(True, id='refresh_disabled'),
    ],
)
async def test_get_by_name(
        web_context,
        cache_handler,
        disabled,
        refresh_disabled,
        mock_tariff_zones,
):

    web_context.config.CORP_TARIFFS_CACHE_SETTINGS = {
        'tariff_zones': {
            'disabled': disabled,
            'refresh_disabled': refresh_disabled,
        },
    }

    mock_tariff_zones.data.zones = {
        'zones': [
            {
                'name': 'spb',
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': 'Санкт-Петербург',
                'currency': 'RUB',
            },
        ],
    }

    await cache_handler.refresh_cache()
    zone = await cache_handler.get_by_name('spb')
    assert zone == {
        'name': 'spb',
        'time_zone': 'Europe/Moscow',
        'country': 'rus',
        'translation': 'Санкт-Петербург',
        'currency': 'RUB',
    }


@pytest.mark.now(NOW.isoformat())
async def test_base(cache_handler, mock_tariff_zones):
    mock_tariff_zones.data.zones = {
        'zones': [
            {
                'name': 'moscow',
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': 'Москва',
                'currency': 'RUB',
            },
            {
                'name': 'spb',
                'time_zone': 'Europe/Moscow',
                'country': 'rus',
                'translation': 'Санкт-Петербург',
                'currency': 'RUB',
            },
        ],
    }

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_zones.keys() == {'moscow', 'spb'}


@pytest.mark.now(NOW.isoformat())
async def test_modified(cache_handler, mock_tariff_zones):
    zones = [
        {
            'country': 'ct1',
            'name': 'zone1',
            'time_zone': 'Europe/Moscow',
            'translation': 'zone1',
            'currency': 'RUB',
        },
        {
            'country': 'ct1',
            'name': 'to_delete',
            'time_zone': 'Europe/Moscow',
            'translation': 'to_delete',
            'currency': 'RUB',
        },
    ]

    mock_tariff_zones.data.zones = {'zones': zones}

    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_zones.keys() == {'zone1', 'to_delete'}

    zones = [
        {
            'country': 'ct1',
            'name': 'zone1',
            'time_zone': 'Europe/Moscow',
            'translation': 'zone1',
            'currency': 'RUB',
        },
        {
            'country': 'ct2',
            'name': 'zone2',
            'time_zone': 'Europe/Moscow',
            'translation': 'zone2',
            'currency': 'RUB',
        },
    ]

    mock_tariff_zones.data.zones = {'zones': zones}
    await cache_handler.refresh_cache()
    assert cache_handler._cache.tariff_zones.keys() == {'zone1', 'zone2'}
