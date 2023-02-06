import datetime

import pytest

from taxi.util import dates

from eats_courier_scoring.common import db

NOW = dates.utc_with_tz()


@pytest.mark.parametrize(
    ('days', 'expected_result'),
    (
        (1, {}),
        (2, {'long_block': {'region': 1}}),
        (3, {'long_block': {'region': 2}, 'temp_block': {'region': 1}}),
        (
            4,
            {
                'long_block': {'region': 2, 'region_2': 1},
                'temp_block': {'region': 1, 'region_2': 1},
            },
        ),
        (
            5,
            {
                'long_block': {'region': 2, 'region_2': 1},
                'temp_block': {'region': 1, 'region_2': 1, 'region_3': 1},
            },
        ),
    ),
)
@pytest.mark.pgsql('eats_courier_scoring', files=['init_punishments_db.sql'])
async def test_get_regions_stats(cron_context, days, expected_result):
    result = await db.get_regions_stats(
        context=cron_context,
        punishments_start_date=NOW - datetime.timedelta(days=days),
    )
    assert result == expected_result
