# pylint: disable=unused-variable
import datetime

import pytest

from eda_region_points.generated.cron import run_cron
from test_eda_region_points.cron import yql

EXPECTED_CARTS = [
    {'cart_id': '00000000-0000-0000-0000-000000000001', 'deleted_at': None},
    {'cart_id': '00000000-0000-0000-0000-000000000002', 'deleted_at': None},
    {'cart_id': '00000000-0000-0000-0000-000000000003', 'deleted_at': None},
    {'cart_id': '00000000-0000-0000-0000-000000000004', 'deleted_at': None},
    {
        'cart_id': '00000000-0000-0000-0000-000000000005',
        'deleted_at': datetime.datetime.strptime(
            '2021-10-10T01:00:00Z', '%Y-%m-%dT%H:%M:%S%z',
        ),
    },
]

EXPECTED_EATERS = [
    {'eater_id': '1', 'cart_id': None},
    {'eater_id': '2', 'cart_id': '00000000-0000-0000-0000-000000000001'},
    {'eater_id': '3', 'cart_id': '00000000-0000-0000-0000-000000000002'},
    {'eater_id': '4', 'cart_id': '00000000-0000-0000-0000-000000000003'},
    {'eater_id': '5', 'cart_id': '00000000-0000-0000-0000-000000000004'},
]

YQL_COLUMN_NAMES = ['place_id']
YQL_ROWS = [[1], [3], [4]]


@pytest.mark.now('2021-10-10T05:00:00Z')
@pytest.mark.config(EATS_CARTS_INTEGRATION_CARTS_BATCH_SIZE=1)
async def test_simple(patch, pgsql):
    @patch('yql.api.v1.client.YqlClient.query')
    def patch_yql_query(*args, **kwargs):
        return yql.MockYqlRequestOperation(YQL_COLUMN_NAMES, YQL_ROWS)

    await run_cron.main(
        [
            f'eda_region_points.crontasks.delete_old_integration_carts',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['eats_cart'].cursor()
    cursor.execute(
        """
        SELECT id, deleted_at
        FROM eats_cart.carts
        ORDER BY id
        """,
    )
    result = list({'cart_id': row[0], 'deleted_at': row[1]} for row in cursor)

    current_now = datetime.datetime.now(
        datetime.timezone.utc,
    ) - datetime.timedelta(minutes=1)
    for i in [0, -1, -1]:
        assert (
            result[i]['deleted_at'] and result[i]['deleted_at'] > current_now
        )
        del result[i]

    assert result == EXPECTED_CARTS

    cursor.execute(
        """
        SELECT eater_id, cart_id
        FROM eats_cart.eater_cart
        ORDER BY eater_id
        """,
    )
    result = list({'eater_id': row[0], 'cart_id': row[1]} for row in cursor)
    assert result == EXPECTED_EATERS
