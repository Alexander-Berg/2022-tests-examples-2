# pylint: disable=W0212
import datetime

import pytest

from taxi.util import dates

from taxi_tariffs.modules.tariff_settings import main
from taxi_tariffs.modules.tariff_settings import models


def dttm_from_str(date_str: str) -> datetime.datetime:
    return dates.parse_timestring(date_str, 'UTC')


METADATA = [
    main._MetaTariffSettings(
        home_zone='zone_1', updated=dttm_from_str('2020-04-01T11:00:00+03:00'),
    ),
    main._MetaTariffSettings(
        home_zone='zone_2', updated=dttm_from_str('2020-04-02T11:00:00+03:00'),
    ),
    main._MetaTariffSettings(
        home_zone='zone_3', updated=dttm_from_str('2020-04-03T11:00:00+03:00'),
    ),
    main._MetaTariffSettings(
        home_zone='zone_4', updated=dttm_from_str('2020-04-04T11:00:00+03:00'),
    ),
    main._MetaTariffSettings(
        home_zone='zone_5', updated=dttm_from_str('2020-04-04T11:00:00+03:00'),
    ),
    main._MetaTariffSettings(
        home_zone='zone_6', updated=dttm_from_str('2020-04-06T11:00:00+03:00'),
    ),
]


@pytest.mark.parametrize(
    'last_update,last_zone,expected',
    [
        (
            '2020-04-01T11:00:00+03:00',
            'moscow',
            'MjAyMC0wNC0wMVQxMTowMDowMCswMzowMCYmbW9zY293',
        ),
    ],
)
async def test_encode_cursor(last_update, last_zone, expected):
    dttm = dates.parse_timestring(last_update, timezone='UTC')
    cursor = models.Cursor(last_update=dttm, last_zone=last_zone)
    result = models.encode_cursor(cursor)
    assert result == expected


@pytest.mark.parametrize(
    'last_update,last_zone,cursor',
    [
        (
            '2020-04-01T11:00:00+03:00',
            'moscow',
            'MjAyMC0wNC0wMVQxMTowMDowMCswMzowMCYmbW9zY293',
        ),
    ],
)
async def test_decode_cursor_ok(last_update, last_zone, cursor):
    dttm = dates.parse_timestring(last_update, 'UTC')
    result = models.decode_cursor(cursor)
    assert result.last_zone == last_zone
    assert result.last_update == dttm


@pytest.mark.parametrize(
    'cursor', [('',), ('xxx',), ('bad_cursor',), ('23,',)],
)
async def test_decode_cursor_fail(cursor):
    with pytest.raises(models.BadCursor):
        result = models.decode_cursor(cursor)
        assert result.last_update


@pytest.mark.parametrize(
    'last_update,last_zone,expected',
    [
        ('2019-04-01T11:00:00+03:00', None, 0),
        ('2019-04-01T11:00:00+03:00', 'zone_1', 0),
        ('2020-04-01T11:00:00+03:00', 'zone_1', 1),
        ('2020-04-01T11:00:00+03:00', None, 0),
        ('2020-04-04T11:00:00+03:00', 'zone_4', 4),
        ('2020-04-04T11:00:00+03:00', None, 3),
        ('2021-04-04T11:00:00+03:00', None, 6),
        ('2021-04-04T11:00:00+03:00', 'zone_6', 6),
    ],
)
async def test_calc_offset(last_update, last_zone, expected):
    head = await main._calc_next_bulk_head(
        METADATA, dttm_from_str(last_update), last_zone=last_zone,
    )
    assert head == expected


@pytest.mark.parametrize(
    'last_update,last_zone', [('2020-04-04T11:00:00+03:00', 'azone_5')],
)
async def test_calc_offset_fail(last_update, last_zone):
    with pytest.raises(main.BaseError):
        assert await main._calc_next_bulk_head(
            METADATA, dttm_from_str(last_update), last_zone=last_zone,
        )


@pytest.mark.parametrize(
    'meta_bulk,expected_date,expected_zone',
    [
        ([], '2020-04-06T11:00:00+03:00', 'zone_6'),
        ([METADATA[0]], '2020-04-01T11:00:00+03:00', 'zone_1'),
        ([METADATA[2]], '2020-04-03T11:00:00+03:00', 'zone_3'),
    ],
)
async def test_build_cursor(meta_bulk, expected_date, expected_zone):
    cursor = main._build_cursor(meta_bulk, METADATA)
    assert cursor.last_zone == expected_zone
    assert cursor.last_update == dttm_from_str(expected_date)


async def test_get_metadata(cache_shield, web_context):
    metadata = await main._get_meta_tariff_settings(web_context)
    expected = ['zone_1', 'zone_2', 'zone_3', 'zone_4', 'zone_5', 'zone_6']
    assert [x.home_zone for x in metadata] == expected


@pytest.mark.config(TARIFF_SETTINGS_BULK_SIZE=3)
async def test_get_bulk(cache_shield, web_context):
    # bulk 1
    bulk_1 = await main.get_tariff_settings_bulk(web_context)
    assert [x['home_zone'] for x in bulk_1.zones] == [
        'zone_1',
        'zone_2',
        'zone_3',
    ]
    assert bulk_1.next_cursor.last_update == dttm_from_str(
        '2020-04-03T12:00:00+03:00',
    )
    assert bulk_1.next_cursor.last_zone == 'zone_3'

    # bulk 2
    bulk_2 = await main.get_tariff_settings_bulk(
        web_context, cursor=bulk_1.next_cursor,
    )
    assert [x['home_zone'] for x in bulk_2.zones] == [
        'zone_4',
        'zone_5',
        'zone_6',
    ]
    assert bulk_2.next_cursor.last_update == dttm_from_str(
        '2020-04-06T12:00:00+03:00',
    )
    assert bulk_2.next_cursor.last_zone == 'zone_6'

    # final
    bulk_3 = await main.get_tariff_settings_bulk(
        web_context, cursor=bulk_2.next_cursor,
    )
    assert not bulk_3.zones
    assert bulk_3.next_cursor.last_update == dttm_from_str(
        '2020-04-06T12:00:00+03:00',
    )
    assert bulk_3.next_cursor.last_zone == 'zone_6'


@pytest.mark.parametrize(
    'cursor,expected,iterations',
    [
        (
            None,
            [
                'zone_1',
                'zone_2',
                'zone_3',
                'zone_7',
                'zone_6',
                'zone_5',
                'zone_4',
                'zone_8',
            ],
            5,
        ),
        (
            'MjAyMC0wNC0wMVQxMjowMDowMCswMzowMCYmem9uZV83',
            ['zone_6', 'zone_5', 'zone_4', 'zone_8'],
            3,
        ),
    ],
)
@pytest.mark.filldb(tariff_settings='many_updated')
@pytest.mark.config(TARIFF_SETTINGS_BULK_SIZE=2)
async def test_get_bulk_finite_algo(
        web_context, cache_shield, cursor, expected, iterations,
):
    steps = 1
    cursor = models.decode_cursor(cursor) if cursor else None
    bulk = await main.get_tariff_settings_bulk(web_context, cursor=cursor)
    zones = bulk.zones
    while bulk.zones:
        steps += 1
        bulk = await main.get_tariff_settings_bulk(
            web_context, cursor=bulk.next_cursor,
        )
        zones.extend(bulk.zones)

    assert steps == iterations
    assert [z['home_zone'] for z in zones] == expected


@pytest.mark.config(TARIFF_SETTINGS_BULK_SIZE=3)
async def test_get_list_ok(web_app_client, cache_shield):
    response = await web_app_client.get('/v1/tariff_settings/list')

    data = await response.json()
    assert response.status == 200
    assert 'next_cursor' in data
    assert len(data['zones']) == 3


@pytest.mark.config(TARIFF_SETTINGS_LIST_ENABLED=False)
async def test_get_list_disabled(web_app_client, cache_shield):
    response = await web_app_client.get('/v1/tariff_settings/list')
    assert response.status == 409


@pytest.mark.config(TARIFF_SETTINGS_BULK_SIZE=2)
@pytest.mark.filldb(tariff_settings='many_updated')
@pytest.mark.parametrize(
    'cursor,iterations',
    [
        ('MjAyMC0wNC0wMVQxMjowMDowMCswMzowMCYmem9uZV83', 3),
        (None, 5),
        ('MjAyMC0wNC0wMVQxMjowMDowMCswMzowMCYmem9uZV84MA==', 5),
    ],
)
async def test_get_list_finite_algo(
        web_app_client, cache_shield, cursor, iterations,
):
    steps = 0
    while steps < 100:  # endless pagination
        params = {'cursor': cursor} if cursor else {}
        response = await web_app_client.get(
            '/v1/tariff_settings/list', params=params,
        )

        data = await response.json()
        cursor = data['next_cursor']
        steps += 1

        if not data['zones']:
            break

    assert steps == iterations
