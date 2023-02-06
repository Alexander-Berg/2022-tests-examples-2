# pylint: disable=protected-access
import datetime

import pandas as pd
import pytest

from grocery_tasks.autoorder.prepare_data import write_off_date


@pytest.mark.now('2020-02-12 06:20:00')
def test_otw_write_off_date():
    orders_on_the_way_df = pd.DataFrame(
        [
            (60287, 100004, 1049, datetime.date(2020, 2, 12), 12),
            (100, 100003, 1757, datetime.date(2020, 2, 12), 8),
            (60287, 100010, 2137, datetime.date(2020, 2, 12), 7),
            (60287, 100, 2137, datetime.date(2020, 2, 13), 8),
            (71249, 100012, 2332, datetime.date(2020, 2, 12), 2),
            (60287, 100006, 2547, datetime.date(2020, 2, 12), 8),
            (60287, 100006, 2547, datetime.date(2020, 2, 13), 8),
            (100, 100006, 2547, datetime.date(2020, 2, 13), 7),
        ],
        columns=['warehouse_id', 'supplier_id', 'lavka_id', 'date', 'qty'],
    )

    pim_df = pd.DataFrame(
        [
            (1049, 365, 14),
            (1757, 999, 10),
            (2137, 14, 0),
            (2332, 10, 5),
            (2547, pd.NA, pd.NA),
        ],
        columns=['product_id', 'shelf_life', 'expired_count'],
    )

    warehouses_df = pd.DataFrame(
        [
            (
                60287,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                71249,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Франчайзинг',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                72413,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                72554,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                100,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Распределительный центр',
                5,
                datetime.date(2020, 2, 12),
                0,
                1,
                1,
            ),
            (
                91452,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
        ],
        columns=[
            'store_id',
            'name',
            'address',
            'group',
            'purchase_date',
            'open_date',
            'active',
            'store_type',
            'days_before_filling',
            'employee_start_date',
            'delivery_period',
            'prepare_period',
            'unpacking_period',
        ],
    )
    pick_by_line_df = pd.DataFrame(
        [
            (100006, 60287, 777, 1),
            (100010, 60287, 100, 2),
            (100012, 71249, 100, 1),
            (100012, 0, 100, 1),
            (100010, 32, 100, 2),
            (100010, 60287, 777, 5),
        ],
        columns=[
            'supplier_id',
            'warehouse_id',
            'distribution_center_id',
            'lag',
        ],
    )

    assortment_warehouses_df = pd.DataFrame(
        [
            (100004, 60287, 1049, 'PBL'),
            (100003, 100, 1757, 'Хранение'),
            (100010, 60287, 2137, 'PBL'),
            (100, 60287, 2137, 'PBL'),
            (100012, 71249, 2332, 'PBL'),
            (100006, 60287, 2547, 'PBL'),
            (100006, 60287, 2547, 'Хранение'),
            (100006, 100, 2547, 'Хранение'),
        ],
        columns=['supplier_id', 'warehouse_id', 'lavka_id', 'delivery_type'],
    )

    expected_otw_df = orders_on_the_way_df.copy()

    result_df = write_off_date._otw_or_stowage_add_periods(
        src_df=orders_on_the_way_df,
        pim_df=pim_df,
        warehouses_df=warehouses_df,
        pick_by_line_df=pick_by_line_df,
        assortment_warehouses_df=assortment_warehouses_df,
        rsl_coeff=1.0,
        default_shelf_life=9999,
        default_expired_count=0,
    )
    result_df['date'] = pd.to_datetime(result_df['date'])
    result_df['write_off_date'] = pd.to_datetime(result_df['write_off_date'])

    expected_otw_df['write_off_date'] = pd.Series(
        [
            datetime.date(2021, 1, 27),
            datetime.date(2022, 10, 27),
            datetime.date(2020, 2, 23),
            datetime.date(2020, 2, 24),
            datetime.date(2020, 2, 15),
            datetime.date(2047, 6, 27),
            datetime.date(2047, 6, 28),
            datetime.date(2047, 6, 29),
        ],
    )
    expected_otw_df['date'] = pd.to_datetime(expected_otw_df['date'])
    expected_otw_df['write_off_date'] = pd.to_datetime(
        expected_otw_df['write_off_date'],
    )
    diff = pd.concat([result_df, expected_otw_df]).drop_duplicates(keep=False)
    assert diff.empty, diff


@pytest.mark.now('2020-02-12 06:20:00')
def test_stowage_write_off_date():
    pim_df = pd.DataFrame(
        [
            (1049, 365, 14),
            (1757, 999, 10),
            (2137, 14, 0),
            (2332, 10, 5),
            (2547, pd.NA, pd.NA),
        ],
        columns=['product_id', 'shelf_life', 'expired_count'],
    )

    stowage_df = pd.DataFrame(
        [
            (60287, 1049, 1, datetime.date(2020, 2, 12)),
            (100, 1757, 1, datetime.date(2020, 2, 12)),
            (60287, 2137, 1, datetime.date(2020, 2, 12)),
        ],
        columns=['warehouse_id', 'lavka_id', 'qty', 'date'],
    )

    warehouses_df = pd.DataFrame(
        [
            (
                60287,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                71249,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Франчайзинг',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                72413,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                72554,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
            (
                100,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Распределительный центр',
                5,
                datetime.date(2020, 2, 12),
                0,
                1,
                1,
            ),
            (
                91452,
                '',
                '',
                'Москва',
                datetime.date(2020, 2, 12),
                datetime.date(2020, 2, 12),
                1,
                'Лавка',
                5,
                datetime.date(2020, 2, 12),
                0,
                0,
                0,
            ),
        ],
        columns=[
            'store_id',
            'name',
            'address',
            'group',
            'purchase_date',
            'open_date',
            'active',
            'store_type',
            'days_before_filling',
            'employee_start_date',
            'delivery_period',
            'prepare_period',
            'unpacking_period',
        ],
    )
    pick_by_line_df = pd.DataFrame(
        [
            (100006, 60287, 777, 1),
            (100010, 60287, 100, 2),
            (100012, 71249, 100, 0),
            (100012, 71249, 100, 1),
            (100012, 0, 100, 1),
            (100012, 71249, 100, 1),
            (100012, 71249, 100, 1),
            (100010, 32, 100, 2),
            (100010, 60287, 777, 5),
        ],
        columns=[
            'supplier_id',
            'warehouse_id',
            'distribution_center_id',
            'lag',
        ],
    )

    assortment_warehouses_df = pd.DataFrame(
        [
            (110, 1, 110001, 'PBL'),
            (110, 2, 110001, 'Хранение'),
            (111, 2, 120001, 'PBL'),
            (110, 1, 110002, 'PBL'),
            (110, 2, 120001, 'PBL'),
            (110, 3, 120001, 'PBL'),
            (110, 4, 120001, 'Хранение'),
            (110, 3, 120002, 'Хранение'),
        ],
        columns=['supplier_id', 'warehouse_id', 'lavka_id', 'delivery_type'],
    )

    expected_otw_df = stowage_df.copy()

    result_df = write_off_date._otw_or_stowage_add_periods(
        src_df=stowage_df,
        pim_df=pim_df,
        warehouses_df=warehouses_df,
        pick_by_line_df=pick_by_line_df,
        assortment_warehouses_df=assortment_warehouses_df,
        rsl_coeff=1.0,
        default_shelf_life=9999,
        default_expired_count=0,
    )
    result_df['write_off_date'] = pd.to_datetime(result_df['write_off_date'])

    expected_otw_df['write_off_date'] = pd.Series(
        [
            datetime.date(2021, 1, 27),
            datetime.date(2022, 10, 27),
            datetime.date(2020, 2, 25),
        ],
    )
    expected_otw_df['write_off_date'] = pd.to_datetime(
        expected_otw_df['write_off_date'],
    )
    expected_otw_df['date'] = pd.to_datetime(expected_otw_df['date'])

    diff = pd.concat([result_df, expected_otw_df]).drop_duplicates(keep=False)
    assert diff.empty, diff
