# pylint: disable=protected-access
import copy
import datetime as dt
import decimal

from plugins.partner_deals_cache import plugin
import pytest

from partner_offers import models

PARTNER_IDS = [1, 2, 3, 4]
LOCATION_IDS = [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 15]
DEAL_IDS = [11, 12, 21, 22, 31, 32, 13]

PARTNERS = {
    1: models.PartnerMinimal(
        partner_id=1, category='food', logo='https://example.com/image.jpg',
    ),
    2: models.PartnerMinimal(
        partner_id=2, category='service', logo='http://bronevik.com/im.png',
    ),
    3: models.PartnerMinimal(
        partner_id=3, category='help', logo='http://vodka.ru/im.png',
    ),
}

LOCATIONS = {
    11: models.Location(
        business_oid=11,
        partner_id=1,
        longitude=37.5,
        latitude=55.0,
        name='Грибница1',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
    12: models.Location(
        business_oid=12,
        partner_id=1,
        longitude=37.5,
        latitude=55.0,
        name='Грибница2',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
    13: models.Location(
        business_oid=13,
        partner_id=1,
        longitude=90.0,
        latitude=55.0,
        name='Грибница3',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
    14: models.Location(
        business_oid=14,
        partner_id=1,
        longitude=37.5,
        latitude=55.0,
        name='Грибница4',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575069000, 1575079000),),
        timezone_offset=10800,
    ),
    21: models.Location(
        business_oid=21,
        partner_id=2,
        longitude=37.5,
        latitude=55.0,
        name='Радиоволна1',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=21600,
    ),
    22: models.Location(
        business_oid=22,
        partner_id=2,
        longitude=37.5,
        latitude=55.0,
        name='Радиоволна2',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=21600,
    ),
    23: models.Location(
        business_oid=23,
        partner_id=2,
        longitude=90.0,
        latitude=55.0,
        name='Радиоволна3',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=21600,
    ),
    24: models.Location(
        business_oid=24,
        partner_id=2,
        longitude=37.5,
        latitude=55.0,
        name='Радиоволна4',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575069000, 1575080000),),
        timezone_offset=21600,
    ),
    31: models.Location(
        business_oid=31,
        partner_id=3,
        longitude=37.5,
        latitude=55.0,
        name='Водкария1',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
    32: models.Location(
        business_oid=32,
        partner_id=3,
        longitude=37.5,
        latitude=55.0,
        name='Водкария2',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
    33: models.Location(
        business_oid=33,
        partner_id=3,
        longitude=90.0,
        latitude=55.0,
        name='Водкария3',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
    34: models.Location(
        business_oid=34,
        partner_id=3,
        longitude=37.5,
        latitude=55.0,
        name='Водкария4',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    ),
}

DEALS = {
    11: models.DealMinimal(
        deal_id=11,
        partner_id=1,
        title='Some title',
        subtitle=None,
        descr_title='Some desc title',
        description=None,
        icon=None,
        kind=models.Discount(text=None, percent=decimal.Decimal(15)),
        map_pin_text=None,
        contractor_merch_offer_id=None,
    ),
    21: models.DealMinimal(
        deal_id=21,
        partner_id=2,
        title='Some title',
        subtitle=None,
        descr_title='Some desc title',
        description=None,
        icon=None,
        kind=models.Discount(text=None, percent=decimal.Decimal(20)),
        map_pin_text='MapText',
        contractor_merch_offer_id=None,
    ),
    22: models.DealMinimal(
        deal_id=22,
        partner_id=2,
        title='Some title',
        subtitle=None,
        descr_title='Some desc title',
        description=None,
        icon=None,
        kind=models.Coupon(
            text=None, price=decimal.Decimal(700), currency='RUB',
        ),
        map_pin_text=None,
        contractor_merch_offer_id=None,
    ),
    31: models.DealMinimal(
        deal_id=31,
        partner_id=3,
        title='Some title',
        subtitle=None,
        descr_title='Some desc title',
        description=None,
        icon=None,
        kind=models.Discount(text=None, percent=decimal.Decimal(20)),
        map_pin_text='MapText',
        contractor_merch_offer_id=None,
    ),
    32: models.DealMinimal(
        deal_id=32,
        partner_id=3,
        title='Some title',
        subtitle=None,
        descr_title='Some desc title',
        description=None,
        icon=None,
        kind=models.Discount(text=None, percent=decimal.Decimal(20)),
        map_pin_text=None,
        contractor_merch_offer_id=None,
    ),
}

LOC_DEALS_MAP = {
    (models.Consumer.DRIVER, 'bronze', None): {
        11: frozenset({11}),
        13: frozenset({11}),
        14: frozenset({11}),
        21: frozenset({22}),
        22: frozenset({22}),
        23: frozenset({21, 22}),
        24: frozenset({21, 22}),
    },
    (models.Consumer.DRIVER, 'platinum', None): {
        31: frozenset({31}),
        32: frozenset({31}),
        33: frozenset({31}),
        34: frozenset({31}),
    },
    (models.Consumer.COURIER, '3', None): {
        31: frozenset({32}),
        32: frozenset({32}),
        33: frozenset({32}),
        34: frozenset({32}),
    },
    (models.Consumer.DRIVER, 'bronze', 'antitag_1'): {
        23: frozenset({21}),
        24: frozenset({21}),
    },
    (models.Consumer.DRIVER, 'bronze', 'antitag_2'): {
        11: frozenset({11}),
        13: frozenset({11}),
        14: frozenset({11}),
        23: frozenset({21}),
        24: frozenset({21}),
    },
}


def _update_storage_time(
        storage: plugin._CacheStorage, time: dt.datetime,
) -> plugin._CacheStorage:
    return plugin._CacheStorage(
        partners=copy.copy(storage.partners),
        deals=copy.copy(storage.deals),
        locations=copy.copy(storage.locations),
        location_deals_mapping=copy.copy(storage.location_deals_mapping),
        partners_cursor=storage.partners_cursor,
        deals_cursor=storage.deals_cursor,
        locations_cursor=storage.locations_cursor,
        last_full_update=time,
    )


@pytest.mark.pgsql('partner_offers', files=['init_db.sql'])
async def test_incremental_caches(pgsql, web_context):
    cache = plugin.PartnerDealsCache(
        web_context,
        {'incremental_update_delay': 0.001, 'full_update_delay': 3600},
        None,
    )
    await cache.refresh_cache()

    partners = cache.get_partners(PARTNER_IDS)
    assert partners.found == PARTNERS
    assert partners.not_found == [4]

    locations = cache.get_locations(LOCATION_IDS)
    assert locations.found == LOCATIONS
    assert locations.not_found == [15]

    deals = cache.get_deals(DEAL_IDS)
    assert deals.found == DEALS
    assert deals.not_found == [12, 13]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.DRIVER, ['bronze'], frozenset(),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'bronze', None)]
    )
    assert loc_deals.not_found == [15]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.DRIVER, ['platinum'], frozenset(),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'platinum', None)]
    )
    assert loc_deals.not_found == [15]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.COURIER, ['3'], frozenset(),
    )
    assert (
        loc_deals.found == LOC_DEALS_MAP[(models.Consumer.COURIER, '3', None)]
    )
    assert loc_deals.not_found == [15]

    with pgsql['partner_offers'].cursor() as curr:
        curr.execute(
            """INSERT INTO partner
            (id, category, name, logo, created_by, updated_by, updated_at)
            VALUES (4, 'good','Грибница',
            'https://example.com/image.jpg','Ильич','Ильич',
             '2020-02-01 19:59'::timestamptz)""",
        )
        curr.execute(
            """INSERT INTO location(business_oid,partner_id,
            longitude,latitude,name,address,work_time_intervals,
            tz_offset,updated_at)
            VALUES(15, 4, 55, 37.5, 'Грибница1', 'Address',
             '[{"from": 1575039000, "to":1575069000}]', 10800,
             '2020-02-01 19:59'::timestamptz)""",
        )
        curr.execute(
            """INSERT INTO deal(id, partner_id, consumer, enabled, kind,
             kind_json, created_by, updated_by, begin_at, title,
          description_title, updated_at)
          VALUES(13, 4, 'driver', TRUE, 'discount', '{"percent":"20"}',
          'Ильич', 'Ильич', '2014-04-04 20:00:00-07'::timestamptz,
          'water', 'water', '2020-02-01 19:59'::timestamptz)
          """,
        )

    extra_partner = models.PartnerMinimal(
        partner_id=4, category='good', logo='https://example.com/image.jpg',
    )
    extra_location = models.Location(
        business_oid=15,
        partner_id=4,
        longitude=55.0,
        latitude=37.5,
        name='Грибница1',
        country=None,
        city=None,
        address='Address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    )
    extra_deal = models.DealMinimal(
        deal_id=13,
        partner_id=4,
        title='water',
        subtitle=None,
        descr_title='water',
        description=None,
        icon=None,
        kind=models.Discount(text=None, percent=decimal.Decimal(20)),
        map_pin_text=None,
        contractor_merch_offer_id=None,
    )

    await cache.refresh_cache()

    partners = cache.get_partners(PARTNER_IDS)
    assert partners.found == {
        **PARTNERS,
        extra_partner.partner_id: extra_partner,
    }
    assert partners.not_found == []

    locations = cache.get_locations(LOCATION_IDS)
    assert locations.found == {
        **LOCATIONS,
        extra_location.business_oid: extra_location,
    }
    assert locations.not_found == []

    deals = cache.get_deals(DEAL_IDS)
    assert deals.found == {**DEALS, extra_deal.deal_id: extra_deal}
    assert deals.not_found == [12]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.DRIVER, ['bronze'], frozenset(),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'bronze', None)]
    )
    assert loc_deals.not_found == []

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS,
        models.Consumer.DRIVER,
        ['bronze'],
        frozenset(['antitag_3']),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'bronze', None)]
    )
    assert loc_deals.not_found == []

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS,
        models.Consumer.DRIVER,
        ['bronze'],
        frozenset(['antitag_1']),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'bronze', 'antitag_1')]
    )
    assert loc_deals.not_found == []

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS,
        models.Consumer.DRIVER,
        ['bronze'],
        frozenset(['antitag_2']),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'bronze', 'antitag_2')]
    )
    assert loc_deals.not_found == []

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.DRIVER, ['platinum'], frozenset(),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'platinum', None)]
    )
    assert loc_deals.not_found == []

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.COURIER, ['3'], frozenset(),
    )
    assert (
        loc_deals.found == LOC_DEALS_MAP[(models.Consumer.COURIER, '3', None)]
    )
    assert loc_deals.not_found == []

    with pgsql['partner_offers'].cursor() as curr:
        curr.execute(
            """UPDATE partner SET category = 'help',
            updated_at = '2020-02-01 20:00'::timestamptz WHERE id = 1;""",
        )
        curr.execute(
            """UPDATE deal SET title = 'ЗЕМЛЯ',
            updated_at = '2020-02-01 20:00'::timestamptz WHERE id = 11;""",
        )
        curr.execute(
            """UPDATE location SET name = 'ЗЕМЛЯ', updated_at =
            '2020-02-01 20:00'::timestamptz WHERE business_oid = 11;""",
        )

    await cache.refresh_cache()

    assert cache.get_partners([1]).found[1] == models.PartnerMinimal(
        partner_id=1, category='help', logo='https://example.com/image.jpg',
    )
    assert cache.get_deals([11]).found[11] == models.DealMinimal(
        deal_id=11,
        partner_id=1,
        title='ЗЕМЛЯ',
        subtitle=None,
        descr_title='Some desc title',
        description=None,
        icon=None,
        kind=models.Discount(text=None, percent=decimal.Decimal('15')),
        map_pin_text=None,
        contractor_merch_offer_id=None,
    )
    assert cache.get_locations([11]).found[11] == models.Location(
        business_oid=11,
        partner_id=1,
        longitude=37.5,
        latitude=55.0,
        name='ЗЕМЛЯ',
        country=None,
        city=None,
        address='Simple test address',
        work_time_intervals=((1575039000, 1575069000),),
        timezone_offset=10800,
    )


@pytest.mark.pgsql('partner_offers', files=['init_db.sql'])
async def test_full_caches(pgsql, web_context):
    cache = plugin.PartnerDealsCache(
        web_context,
        {'incremental_update_delay': 0.001, 'full_update_delay': 3600},
        None,
    )
    await cache.refresh_cache()

    partners = cache.get_partners(PARTNER_IDS)
    assert partners.found == PARTNERS
    assert partners.not_found == [4]

    locations = cache.get_locations(LOCATION_IDS)
    assert locations.found == LOCATIONS
    assert locations.not_found == [15]

    deals = cache.get_deals(DEAL_IDS)
    assert deals.found == DEALS
    assert deals.not_found == [12, 13]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.DRIVER, ['bronze'], frozenset(),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'bronze', None)]
    )
    assert loc_deals.not_found == [15]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.DRIVER, ['platinum'], frozenset(),
    )
    assert (
        loc_deals.found
        == LOC_DEALS_MAP[(models.Consumer.DRIVER, 'platinum', None)]
    )
    assert loc_deals.not_found == [15]

    loc_deals = cache.get_location_deals_mapping(
        LOCATION_IDS, models.Consumer.COURIER, ['3'], frozenset(),
    )
    assert (
        loc_deals.found == LOC_DEALS_MAP[(models.Consumer.COURIER, '3', None)]
    )
    assert loc_deals.not_found == [15]

    # Make full update time
    cache._storage = _update_storage_time(
        cache._storage,
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=3601),
    )

    with pgsql['partner_offers'].cursor() as curr:
        curr.execute('DELETE FROM partner WHERE id = 1;')

    await cache.refresh_cache()

    def compare_not_identical(first: dict, second: dict, description: str):
        assert first == second, f'Not equal {description}'
        for key in first:
            assert first[key] is not second[key], f'Identical {description}'

    del partners.found[1]
    del deals.found[11]
    for loc in [11, 12, 13, 14]:
        del locations.found[loc]

    partners2 = cache.get_partners(PARTNER_IDS)
    compare_not_identical(partners.found, partners2.found, 'partners')
    locations2 = cache.get_locations(LOCATION_IDS)
    compare_not_identical(locations.found, locations2.found, 'locations')
    deals2 = cache.get_deals(DEAL_IDS)
    compare_not_identical(deals.found, deals2.found, 'deals')
