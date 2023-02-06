# pylint: disable=no-member

import pytest
import test_utils


@pytest.mark.parametrize(
    'order_by', ['1', '1, 2', '1, a.assortment_id', ' 1, a.assortment_id'],
)
def test_ok(order_by):
    remarks = test_utils.check_string(
        """
    SELECT a.assortment_id,
       f.product_id,
FROM filtered_items f
JOIN active_items a ON (a.assortment_id = f.assortment_id)"""
        + f' ORDER BY {order_by}',
    )
    assert len(remarks) == 1
    assert remarks[0].message == (
        'Do not use ORDER BY with integer arguments (output column '
        'number), it is error-prone.'
    )


def test_no_number():
    remarks = test_utils.check_string(
        """
    SELECT f.assortment_id,
       f.product_id,
       a.updated,
       a.hide_timeout
FROM filtered_items f
JOIN active_items a ON (a.assortment_id = f.assortment_id
                    AND a.product_id = f.product_id)
ORDER BY f.assortment_id, a.updated

    """,
    )
    assert not remarks
