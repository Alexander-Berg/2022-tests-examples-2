import bson

from atlas_backend.lib.tariff_zone_extractor import extractor
from atlas_backend.lib.tariff_zone_extractor import tariffs

MOSCOW_LON_LAT = (37.618, 55.751)
NONEXISTENT_LON_LAT = (90, 90)


async def test_extract_from_coordinates(cron_context, db):
    mapper = await extractor.Mapper.from_context(cron_context)

    res = mapper(MOSCOW_LON_LAT)
    assert res.home_zone == 'moscow'
    assert mapper.tz_to_city[res.home_zone] == 'Москва'

    res = mapper(NONEXISTENT_LON_LAT)
    assert res is None


async def test_extract_from_coordinates_batch(cron_context, db):
    coordinates_list = [MOSCOW_LON_LAT, NONEXISTENT_LON_LAT, (0, 0)]
    result = [
        x
        async for x in extractor.extract_tz_from_coords_batch(
            coordinates_list, cron_context,
        )
    ]

    tz_data = tariffs.TariffZoneData(
        id=bson.ObjectId('5e25852b22f2053024bff68b'),
        activation_zone='moscow_activation',
        home_zone='moscow',
        possible_tariffs={
            'comfortplus',
            'express',
            'child_tariff',
            'minivan',
            'vip',
            'econom',
        },
    )

    assert result == [tz_data, None, None]
