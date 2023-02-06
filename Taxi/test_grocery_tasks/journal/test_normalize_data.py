from decimal import Decimal
from decimal import getcontext

import pandas as pd

from grocery_tasks.journal.normalize_data import _calculate_vat
from grocery_tasks.journal.normalize_data import _round
from grocery_tasks.journal.normalize_data import calculate_order_revenue_vat
from grocery_tasks.journal.normalize_data import norm_stores


def test_norm_stores():
    stores_df = pd.DataFrame(['1102', '1103', '1104'], columns=['external_id'])
    result_df = pd.DataFrame([1102, 1103, 1104], columns=['external_id'])
    pd.testing.assert_frame_equal(norm_stores(stores_df), result_df)


def test_vat_estimation():
    source_df = pd.DataFrame(
        [
            (Decimal(10), 5.5),
            (Decimal(15), 5.5),
            (Decimal(-10), 5.5),
            (Decimal(10), 20),
            (Decimal(-10), 20),
        ],
        columns=['amount_with_vat', 'vat_rate'],
    )
    result_series = source_df.apply(_calculate_vat, axis=1).apply(_round)
    expected_series = (
        pd.Series([0.52, 0.78, -0.52, 1.67, -1.67])
        .apply(Decimal)
        .apply(_round)
    )
    pd.testing.assert_series_equal(result_series, expected_series)


def test_norm_revenue():
    getcontext().prec = 51
    revenue_df = pd.DataFrame(
        [
            (
                '7',
                -1,
                10.0,
                40.8,
                30.8,
                '5.5',
                'abcd-1',
                'abcd-1-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '6',
                -1,
                35.6,
                118.6,
                83,
                '5.5',
                'abcd-2',
                'abcd-2-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '7',
                1,
                15.4,
                50.1,
                35.7,
                '5.5',
                'abcd-1',
                'abcd-1-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '5',
                -1,
                0,
                60.0,
                60.0,
                '5.5',
                'abcd-3',
                'abcd-3-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '5',
                1,
                40,
                70,
                30,
                '5.5',
                'abcd-3',
                'abcd-3-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '6',
                1,
                10.4,
                40.4,
                30.4,
                '5.5',
                'abcd-2',
                'abcd-2-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '7',
                1,
                8,
                21.0,
                13,
                '5.5',
                'abcd-1',
                'abcd-1-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '7',
                1,
                1.5,
                31.8,
                30.3,
                '5.5',
                'abcd-1',
                'abcd-1-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
            (
                '7',
                1,
                6,
                40,
                34,
                '5.5',
                'abcd-1',
                'abcd-1-grocery',
                1,
                '2021',
                'abcd',
                'payment',
            ),
        ],
        columns=[
            'store_id',
            'aggregation_sign',
            'vat_amount',
            'amount_with_vat',
            'amount_without_vat',
            'vat_rate',
            'receipt_id',
            'order_id',
            'item_id',
            'created_date',
            'user_phone_pd_id',
            'transaction_type',
        ],
    )
    result_columns = [
        'receipt_id',
        'order_id',
        'vat_amount',
        'amount_with_vat',
        'amount_without_vat',
    ]
    result_df = pd.DataFrame(
        [
            (
                'abcd-1',
                'abcd-1-grocery',
                round(Decimal(5.32), 2),
                round(Decimal(102.1), 2),
                round(Decimal(96.78), 2),
            ),
            (
                'abcd-2',
                'abcd-2-grocery',
                round(Decimal(-4.08), 2),
                round(Decimal(-78.1999), 2),
                round(Decimal(-74.12), 2),
            ),
            (
                'abcd-3',
                'abcd-3-grocery',
                round(Decimal(0.52), 2),
                round(Decimal(10.0), 2),
                round(Decimal(9.48), 2),
            ),
        ],
        columns=result_columns,
    )
    expected_df = calculate_order_revenue_vat(revenue_df)[result_columns]
    expected_df['amount_with_vat'] = expected_df['amount_with_vat'].apply(
        lambda x: round(x, 2),
    )
    pd.testing.assert_frame_equal(expected_df, result_df)
