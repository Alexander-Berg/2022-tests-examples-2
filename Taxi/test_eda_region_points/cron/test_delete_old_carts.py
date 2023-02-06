# pylint: disable=unused-variable
import datetime

import pytest

from eda_region_points.generated.cron import run_cron

EXPECTED_CARTS = [
    {'cart_id': '00000000-0000-0000-0000-000000000000', 'deleted_at': None},
    {
        'cart_id': '00000000-0000-0000-0000-000000000001',
        'deleted_at': datetime.datetime.strptime(
            '2021-12-10T01:00:00Z', '%Y-%m-%dT%H:%M:%S%z',
        ),
    },
]

EXPECTED_EATERS = [
    {'eater_id': '1', 'cart_id': '00000000-0000-0000-0000-000000000000'},
    {'eater_id': '2', 'cart_id': None},
    {'eater_id': '3', 'cart_id': None},
    {'eater_id': '4', 'cart_id': None},
]

EXPECTED_ITEMS = [{'id': 2}]

EXPECTED_DISCOUNTS = [{'id': 2}]


@pytest.mark.now('2022-01-01T05:00:00Z')
@pytest.mark.config(EATS_DELETE_OLD_CARTS_BATCH_SIZE=1)
async def test_delete_old_carts(patch, pgsql):
    await run_cron.main(
        [f'eda_region_points.crontasks.delete_old_carts', '-t', '0'],
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

    cursor.execute(
        """
        SELECT id
        FROM eats_cart.cart_items
        """,
    )
    result = list({'id': row[0]} for row in cursor)
    assert result == EXPECTED_ITEMS

    cursor.execute(
        """
        SELECT id
        FROM eats_cart.cart_item_discounts
        """,
    )
    result = list({'id': row[0]} for row in cursor)
    assert result == EXPECTED_DISCOUNTS
