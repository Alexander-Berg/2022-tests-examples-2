# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import datetime

import pytest


SETTINGS = {'delay': 5, 'memoize_time': 300}


@pytest.fixture
def cache_handler(db):
    from taxi_tariffs.caches import tariff_settings
    return tariff_settings.TariffSettingsHandler(db, SETTINGS)


async def test_base(db, cache_handler):
    now = datetime.datetime.utcnow()

    # empty
    await cache_handler.refresh_cache()
    assert not cache_handler._cache.zones

    # insert zone
    await db.tariff_settings.insert_one(
        {'hz': 'moscow', 'driver_change_cost': True, 'updated': now},
    )

    await cache_handler.refresh_cache()
    tariff_settings_zones = set(cache_handler._cache.zones.keys())
    assert tariff_settings_zones == {'moscow'}

    # insert one, modify other
    await db.tariff_settings.insert_one(
        {'hz': 'balaha', 'driver_change_cost': False, 'updated': now},
    )
    await db.tariff_settings.update_one(
        {'hz': 'moscow'}, {'$set': {'driver_change_cost': False}},
    )

    await cache_handler.refresh_cache()
    tariff_settings_zones = set(cache_handler._cache.zones.keys())
    assert tariff_settings_zones == {'moscow', 'balaha'}
