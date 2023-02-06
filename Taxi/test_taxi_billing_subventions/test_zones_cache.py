import dataclasses
import datetime
import decimal

import pytest
import pytz

from taxi_billing_subventions import caches
from taxi_billing_subventions import config


@dataclasses.dataclass()
class TerritoriesClient:
    countries_data: list

    async def get_all_countries(self, log_extra=None) -> list:
        return self.countries_data


_COUNTRY_VAT_BY_DATE = {
    'rus': [
        {
            'end': '2019-01-01 00:00:00',
            'start': '1970-01-01 00:00:00',
            'value': 11800,
        },
        {
            'end': '2030-12-31 00:00:00',
            'start': '2019-01-01 00:00:00',
            'value': 12000,
        },
    ],
}


@pytest.mark.parametrize(
    'zone_name, conf_data, expected_vat',
    [
        pytest.param(
            'moscow',
            _COUNTRY_VAT_BY_DATE,
            '1.18',
            marks=pytest.mark.now('2018-12-31T23:59:59'),
        ),
        pytest.param(
            'moscow',
            _COUNTRY_VAT_BY_DATE,
            '1.20',
            marks=pytest.mark.now('2019-01-01T00:00:00'),
        ),
        pytest.param(
            'moscow', {}, '1.18', marks=pytest.mark.now('2019-01-02T13:30:08'),
        ),
    ],
)
async def test_zones_cache_vat(
        db, zone_name, conf_data, expected_vat, load_json,
):
    countries_data = load_json('countries_data.json')
    territories_client = TerritoriesClient(countries_data)
    conf = config.Config()
    conf.COUNTRY_VAT_BY_DATE = conf_data
    zones_cache = caches.ZonesCache(db, territories_client, conf)
    await zones_cache.refresh_cache()
    zone = zones_cache.get_zone(zone_name)
    now = datetime.datetime.now()
    now = pytz.timezone('Europe/Moscow').localize(now)
    assert zone.vat_on_date(now) == decimal.Decimal(expected_vat)


async def test_zones_cache_no_vat(db, load_json):
    countries_data = load_json('countries_data.json')
    territories_client = TerritoriesClient(countries_data)
    conf = config.Config()
    zones_cache = caches.ZonesCache(db, territories_client, conf)
    await zones_cache.refresh_cache()
    zone = zones_cache.get_zone('helsinki')
    now = datetime.datetime.now()
    with pytest.raises(ValueError):
        print(zone.vat_on_date(now))


async def test_countries_filter(db, load_json):
    countries_data = load_json('empty_countries_data.json')
    territories_client = TerritoriesClient(countries_data)
    zones_cache = caches.ZonesCache(db, territories_client, config.Config())
    await zones_cache.refresh_cache()
    assert zones_cache.zones_by_name == {}
