# pylint: disable=unused-variable
import datetime

import pytest

from eda_region_points.generated.cron import run_cron
from test_eda_region_points.cron import yql

PG_DATA = [
    {'place_id': 1, 'place_menu_item_id': 1, 'quantity': 10},
    {'place_id': 2, 'place_menu_item_id': 2, 'quantity': 11},
    {'place_id': 2, 'place_menu_item_id': 3, 'quantity': 12},
    {'place_id': 3, 'place_menu_item_id': 8, 'quantity': 7},
]

YQL_COLUMN_NAMES = ['place_id', 'place_menu_item_id', 'quantity']
YQL_ROWS = [(1, 1, 10), (2, 2, 11), (2, 3, 12)]


SYNC_START_TIME = datetime.datetime.now() + datetime.timedelta(days=8)


@pytest.mark.now(SYNC_START_TIME.isoformat())
@pytest.mark.parametrize(
    'empty_db',
    [
        pytest.param(True, id='empty_db'),
        pytest.param(
            False,
            marks=pytest.mark.pgsql('eats_misc', files=['fill_db.sql']),
            id='filled_db',
        ),
    ],
)
async def test_simple(patch, pgsql, empty_db):
    @patch('yql.api.v1.client.YqlClient.query')
    def patch_yql_query(*args, **kwargs):
        return yql.MockYqlRequestOperation(YQL_COLUMN_NAMES, YQL_ROWS)

    await run_cron.main(
        [f'eda_region_points.crontasks.popular_menu_items', '-t', '0'],
    )

    cursor = pgsql['eats_misc'].cursor()
    cursor.execute(
        """
        SELECT place_id, place_menu_item_id, ordered_count
        FROM eats_misc.items_popularity
        ORDER BY place_id, place_menu_item_id
        """,
    )
    result = list(
        {'place_id': row[0], 'place_menu_item_id': row[1], 'quantity': row[2]}
        for row in cursor
    )

    result_data = PG_DATA.copy()
    if empty_db:
        result_data.pop()

    assert result == result_data
