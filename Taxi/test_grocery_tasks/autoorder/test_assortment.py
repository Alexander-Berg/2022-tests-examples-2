# pylint: disable=protected-access
import pandas as pd

from grocery_tasks.autoorder.prepare_data import assortment


def test_remove_rotation_rows():
    assortment_df = pd.DataFrame(
        [
            (110, 1, 110001),
            (110, 2, 110001),
            (111, 2, 120001),
            (110, 1, 110002),
            (110, 2, 120001),
            (110, 3, 120001),
            (110, 4, 120001),
            (110, 3, 120002),
        ],
        columns=['supplier_id', 'warehouse_id', 'lavka_id'],
    )

    rotation_info_df = pd.DataFrame(
        [
            ('B', False, 120001, 2),
            ('B', False, 110001, 1),
            ('B', False, 120003, 2),
            ('B', False, 120001, 5),
            ('A', False, 120001, 3),
            ('B', True, 110001, 2),
            ('A', True, 110002, 1),
        ],
        columns=['group', 'in_rotation', 'product_id', 'store_id'],
    )

    result_df = assortment._assortment_remove_rotation_rows(
        assortment_df, rotation_info_df,
    )

    expected_df = pd.DataFrame(
        [
            (110, 2, 110001),
            (110, 1, 110002),
            (110, 3, 120001),
            (110, 4, 120001),
            (110, 3, 120002),
        ],
        columns=['supplier_id', 'warehouse_id', 'lavka_id'],
    )

    assert result_df.to_dict() == expected_df.to_dict()
