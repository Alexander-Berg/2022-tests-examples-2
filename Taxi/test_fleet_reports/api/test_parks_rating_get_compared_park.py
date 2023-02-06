import datetime

import pytest

from fleet_reports.api.parks_rating_metrics_chart_data import (  # noqa pylint: disable = C5521
    _get_compared_park,
)


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29d',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 10,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29e',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 15,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29f',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 20,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29g',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 50,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29f',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29h',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 55,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29f',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29i',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 60,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29f',
            'last',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_default.sql',))
async def test_compared_parks_default(
        web_context, db_park, compared_park_priority, compared_park_id,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29d',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 10,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29e',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 15,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29f',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 20,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_without_gold.sql',))
async def test_compared_park_without_gold(
        web_context, db_park, compared_park_id, compared_park_priority,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29d',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 10,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29e',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 15,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29f',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 20,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_without_silver.sql',))
async def test_compared_park_without_silver(
        web_context, db_park, compared_park_id, compared_park_priority,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29d',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 10,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29e',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 15,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29f',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 20,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29c',
            'last',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_without_bronze.sql',))
async def test_compared_park_without_bronze(
        web_context, db_park, compared_park_id, compared_park_priority,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'gold',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_only_gold.sql',))
async def test_compared_park_only_gold(
        web_context, db_park, compared_park_id, compared_park_priority,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'silver',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_only_silver.sql',))
async def test_compared_park_only_silver(
        web_context, db_park, compared_park_id, compared_park_priority,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority


@pytest.mark.parametrize(
    'db_park,compared_park_id,compared_park_priority',
    [
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29a',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 2,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29b',
            'second',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29b',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 5,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
        (
            {
                'park_id': '7ad36bc7560449998acbe2c57a75c29c',
                'city_id': 'bd3776545b1a30036c37934cad88e70e',
                'rank': 7,
                'tier': 'bronze',
            },
            '7ad36bc7560449998acbe2c57a75c29a',
            'first',
        ),
    ],
)
@pytest.mark.pgsql('fleet_reports', files=('dump_parks_only_bronze.sql',))
async def test_compared_park_only_bronze(
        web_context, db_park, compared_park_id, compared_park_priority,
):
    result, priority = await _get_compared_park(
        context=web_context,
        db_park=db_park,
        date_from=datetime.datetime.fromisoformat('2021-04-01 00:00:00'),
        date_to=datetime.datetime.fromisoformat('2021-04-30 23:59:59'),
    )
    assert result['park_id'] == compared_park_id
    assert priority == compared_park_priority
