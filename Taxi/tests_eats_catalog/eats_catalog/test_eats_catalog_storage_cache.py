from dateutil import parser
import pytest


from testsuite.utils import matching

from . import storage


@pytest.mark.now('2022-06-07T21:00:00+03:00')
async def test_metrics(
        taxi_eats_catalog,
        metric,
        catalog_for_layout,
        testpoint,
        eats_catalog_storage,
):
    """
    Проверяет, что в метрику отставания кеша eats-catalog-storage
    передаются правильные значения и, что метрика отдается в ожидаемом
    формате.

    NOTE(nk2ge5k): К сожалению мне не удалось добиться того чтобы метрика
    отдавала, в тесте предсказуемый результат поэтому сами значения метрики
    не проверяются.
    """
    expected_delays = set([0, 1 * 60 * 1000, 2 * 60 * 1000])

    @testpoint('CacheStatistics::AccountDelay')
    def account_delay(data):
        assert data in expected_delays

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            real_updated_at=parser.parse('2022-06-07T20:59:00+03:00'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            real_updated_at=parser.parse('2022-06-07T20:58:00+03:00'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=1,
            real_updated_at=parser.parse('2022-06-07T21:00:00+03:00'),
        ),
    )

    await catalog_for_layout(blocks=[])  # Иначе кеш очень странно наполняется

    assert account_delay.times_called == 3

    places_cache_metrics = await metric('eats-catalog-storage-places-cache')
    assert places_cache_metrics == {
        'cache_delay': {
            '1m': {
                'max': matching.non_negative_integer,
                'min': matching.non_negative_integer,
                'avg': matching.non_negative_integer,
            },
        },
        'missing_revisions': {'requested': 0, 'resolved': 0},
    }

    zones_cache_metrics = await metric('eats-catalog-storage-zones-cache')
    assert zones_cache_metrics == {
        'cache_delay': {
            '1m': {
                'max': matching.non_negative_integer,
                'min': matching.non_negative_integer,
                'avg': matching.non_negative_integer,
            },
        },
        'missing_revisions': {'requested': 0, 'resolved': 0},
    }
