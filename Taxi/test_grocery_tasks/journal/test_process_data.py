from decimal import Decimal

import pandas as pd

from grocery_tasks.journal.process_data import _make_vat_columns_names
from grocery_tasks.journal.process_data import get_result_table


def test_result_table():
    revenue_df = pd.DataFrame(
        [
            (
                'abcd-1',
                'abcd-1-grocery',
                Decimal('-1.00'),
                Decimal('-10.00'),
                Decimal('-40.80'),
                Decimal('-30.80'),
                '5.5',
                'payment',
            ),
            (
                'abcd-2',
                'abcd-2-grocery',
                Decimal('-1.00'),
                Decimal('-35.60'),
                Decimal('-118.60'),
                Decimal('-83.00'),
                '0.0',
                'payment',
            ),
            (
                'abcd-1',
                'abcd-1-grocery',
                Decimal('1.00'),
                Decimal('15.40'),
                Decimal('51.10'),
                Decimal('35.70'),
                '20.0',
                'payment',
            ),
            (
                'abcd-3',
                'abcd-3-grocery',
                Decimal('-1.00'),
                Decimal('0.00'),
                Decimal('-60.00'),
                Decimal('-60.00'),
                '10.0',
                'payment',
            ),
            (
                'abcd-3',
                'abcd-3-grocery',
                Decimal('1.00'),
                Decimal('40.00'),
                Decimal('70.00'),
                Decimal('30.00'),
                '5.5',
                'payment',
            ),
            (
                'abcd-2',
                'abcd-2-grocery',
                Decimal('1.00'),
                Decimal('10.40'),
                Decimal('40.80'),
                Decimal('30.40'),
                '0.0',
                'payment',
            ),
        ],
        columns=[
            'receipt_id',
            'order_id',
            'aggregation_sign',
            'vat_amount',
            'amount_with_vat',
            'amount_without_vat',
            'vat_rate',
            'transaction_type',
        ],
    )
    orders_df = pd.DataFrame(
        [
            ('abcd-1-grocery', 111, 'sadfa', '2021-01-01'),
            ('abcd-2-grocery', 111, 'sadfa', '2021-01-02'),
            ('abcd-3-grocery', 101, 'asfe9', '2021-01-03'),
            ('abcd-4-grocery', 110, 'ocd7', '2021-01-04'),
        ],
        columns=['order_id', 'store_id', 'user_phone_pd_id', 'created_date'],
    )
    orders_df = orders_df.merge(revenue_df, on='order_id')
    stores_df = pd.DataFrame(
        [
            (111, 'Le shoppe'),
            (101, 'Le eifel tower'),
            (110, 'Le Paris'),
            (222, 'Le Sarts'),
            (202, 'Le Zolya'),
        ],
        columns=['external_id', 'address'],
    )
    expected_df = pd.DataFrame(
        [
            (
                1,
                'payment',
                'abcd-1',
                '2021-01-01',
                111,
                'Le shoppe',
                'sadfa',
                '10.3',
                '0',
                '0',
                '35.70',
                '-30.80',
                '0',
                '0',
                '15.40',
                '-10.00',
            ),
            (
                2,
                'payment',
                'abcd-2',
                '2021-01-02',
                111,
                'Le shoppe',
                'sadfa',
                '-77.8',
                '-52.60',
                '0',
                '0',
                '0',
                '-25.20',
                '0',
                '0',
                '0',
            ),
            (
                3,
                'payment',
                'abcd-3',
                '2021-01-03',
                101,
                'Le eifel tower',
                'asfe9',
                '10.0',
                '0',
                '-60.00',
                '0',
                '30.00',
                '0',
                '0.00',
                '0',
                '40.00',
            ),
        ],
        columns=[
            'id',
            'transaction_type',
            'receipt_id',
            'created_date',
            'depot_id',
            'depot_address',
            'personal_id',
            'TTC',
            'Base_HT_0',
            'Base_HT_10',
            'Base_HT_20',
            'Base_HT_5.5',
            'VAT_0',
            'VAT_10',
            'VAT_20',
            'VAT_5.5',
        ],
    )
    result_df = get_result_table(orders_df, stores_df)
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_column_gen():
    pivot_columns = [
        ('VAT', '0.0'),
        ('VAT', '10.0'),
        ('VAT', '20.0'),
        ('VAT', '5.5'),
        ('VAT', '6.66'),
        ('VAT', '7.77'),
        ('VAT', '100'),
    ]
    expected_result = [
        'VAT_0',
        'VAT_10',
        'VAT_20',
        'VAT_5.5',
        'VAT_6.66',
        'VAT_7.77',
        'VAT_100',
    ]
    assert expected_result == _make_vat_columns_names(pivot_columns)
