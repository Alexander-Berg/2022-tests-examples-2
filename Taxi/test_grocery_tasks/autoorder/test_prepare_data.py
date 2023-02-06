# pylint: disable=protected-access
import datetime
import os

import pandas as pd
import pytest

from grocery_tasks.autoorder.data_norm import from_yt
from grocery_tasks.autoorder.data_norm import read_file
from grocery_tasks.autoorder.data_norm import to_yt
from grocery_tasks.autoorder.prepare_data import pim
from grocery_tasks.autoorder.prepare_data import prediction
from grocery_tasks.autoorder.prepare_data import seasonal
from grocery_tasks.autoorder.prepare_data.seasonal import SEASONAL_COLUMNS
from grocery_tasks.autoorder.prepare_data.weight_products import _generate
from grocery_tasks.autoorder.table import Table


def test_pim_categories():
    pim_df = pd.Series(
        [
            ('a', 'b', 'c', 'd', 'e', 'f'),
            ('a', 'b', 'c', 'd', 'e', None),
            ('a', 'b', 'c', 'd', None, None),
            ('a', 'b', 'c', None, None, None),
            ('a', 'b', None, None, None, None),
            ('a', None, None, None, None, None),
            (None, None, None, None, None, None),
            (None, 'w', None, None, None, None),
            (None, None, 'x', None, None, None),
            (None, None, None, 'y', None, None),
            (None, None, None, None, 'z', None),
            (None, None, None, None, None, 'A'),
        ],
    )
    pim_df = pim_df.apply(
        lambda x: pd.Series(pim._get_last_not_none_category(x)),
    )

    result_category = pim_df[['category_last', 'category_last_lvl']]
    expected_category = pd.DataFrame(
        [
            ('f', 7),
            ('e', 6),
            ('d', 5),
            ('c', 4),
            ('b', 3),
            ('a', 2),
            ('нет данных', 0),
            ('w', 3),
            ('x', 4),
            ('y', 5),
            ('z', 6),
            ('A', 7),
        ],
        columns=['category_last', 'category_last_lvl'],
    )

    assert result_category.to_dict() == expected_category.to_dict()


def test_pim_substitution():
    raw_substitution = pd.DataFrame(
        {'substitution': ['101', '222,111', '', '44,55,66']},
    )

    result_substitution = pd.DataFrame(
        raw_substitution.substitution.map(pim._get_first_analog),
    )

    expected_substitution = pd.DataFrame(
        {'substitution': [101, 222, pd.NaT, 44]},
    )

    pd.testing.assert_frame_equal(
        result_substitution, expected_substitution, check_dtype=False,
    )


def test_prediction_get_ingredients():
    products_columns = ['product_id', 'quants', 'external_id', 'components']
    ingredients_columns = ['product_id', 'ingredient_id', 'weight']

    products_df = pd.DataFrame(
        [
            ['1aa', 1, 10001, '[]'],
            ['1ab', 10, 10002, '[]'],
            ['1ac', 20, 10003, '[]'],
            ['1ad', 50, 10004, '[]'],
            ['1ae', 100, 10005, '[]'],
            ['1af', 500, 10006, '[]'],
            ['1ag', 1000, 10007, '[]'],
            ['1ah', 1000, 10008, '[]'],
            ['1ai', 1000, 10009, '[]'],
            ['1aj', 1000, 10010, '[]'],
            ['1ak', 1000, 10011, '[]'],
            ['1al', 1000, 10012, '[]'],
            ['1aaa', 1, 11111, '[]'],
            ['1bbb', 2, 11112, '[]'],
            [
                '1ba',
                1,
                1001,
                (
                    '[[{"count": 1, "product_id": "1ae"}],'
                    '[{"count": 14, "product_id": "1aa"}],'
                    '[{"count": 1, "product_id": "1ah"}],'
                    '[{"count": 1, "product_id": "1ab"}, '
                    '{"count": 1, "product_id": "1ai"}],'
                    '[{"count": 1, "product_id": "1al"}, '
                    '{"count": 1, "product_id": "1ak"}]]'
                ),
            ],
            [
                '1bb',
                2,
                1002,
                (
                    '[[{"count": 25, "product_id": "1ah"}, '
                    '{"count": 25, "product_id": "1ai"}, '
                    '{"count": 25, "product_id": "1aj"}],'
                    '[{"count": 1, "product_id": "1az"}],'
                    '[{"count": 35, "product_id": "1ad"}],'
                    '[{"count": 40, "product_id": "1ae"}],'
                    '[{"count": 20, "product_id": "1aa"}],'
                    '[{"count": 1, "product_id": "1ac"}],'
                    '[{"count": 1, "product_id": "1af"}],'
                    '[{"count": 33, "product_id": "1ak"}, '
                    '{"count": 33, "product_id": "1al"}]]'
                ),
            ],
            [
                '1bc',
                5,
                1003,
                (
                    '[[{"count": 1, "product_id": "1ag"}],'
                    '[{"count": 10, "product_id": "1ad"}],'
                    '[{"count": 15, "product_id": "1ab"}],'
                    '[{"count": 425, "product_id": "1ac"}],'
                    '[{"count": 5, "product_id": "1af"}],'
                    '[{"count": 50, "product_id": "1al"}]]'
                ),
            ],
            [
                '1bd',
                10,
                1004,
                (
                    '[[{"count": 1, "product_id": "1ag"}, '
                    '{"count": 1, "product_id": "1aa"}],'
                    '[{"count": 1, "product_id": "1az"}],'
                    '[{"count": 30, "product_id": "1ab"}, '
                    '{"count": 1, "product_id": "1ae"}],'
                    '[{"count": 35, "product_id": "1ai"}, '
                    '{"count": 35, "product_id": "1al"}],'
                    '[{"count": 20, "product_id": "1ah"}, '
                    '{"count": 20, "product_id": "1aj"}],'
                    '[{"count": 130, "product_id": "1ac"}, '
                    '{"count": 130, "product_id": "1ak"}],'
                    '[{"count": 12, "product_id": "1xxx"}, '
                    '{"count": 12, "product_id": "1ai"}],'
                    '[{"count": 75, "product_id": "1ad"}]]'
                ),
            ],
            [
                '1be',
                1,
                1005,
                (
                    '[[{"count": 24, "product_id": "1ad"}],'
                    '[{"count": 14, "product_id": "1ah"}],'
                    '[{"count": 300, "product_id": "1ag"}, '
                    '{"count": 300, "product_id": "1ac"}, '
                    '{"count": 300, "product_id": "1aa"}],'
                    '[{"count": 1, "product_id": "1ab"}, '
                    '{"count": 1, "product_id": "1ai"}],'
                    '[{"count": 1, "product_id": "1al"}, '
                    '{"count": 1, "product_id": "1ak"}]]'
                ),
            ],
        ],
        columns=products_columns,
    )

    result_df = prediction._get_ingredients(products_df)

    expected_df = pd.DataFrame(
        [
            [1001, 10005, 0.01],
            [1002, 10005, 0.4],
            [1001, 10001, 14],
            [1002, 10001, 20],
            [1001, 10008, 0.001],
            [1002, 10008, 0.025],
            [1004, 10008, 0.02],
            [1005, 10008, 0.014],
            [1001, 10002, 0.1],
            [1003, 10002, 1.5],
            [1004, 10002, 3],
            [1005, 10002, 0.1],
            [1001, 10012, 0.001],
            [1003, 10012, 0.05],
            [1005, 10012, 0.001],
            [1002, 10004, 0.7],
            [1003, 10004, 0.2],
            [1004, 10004, 1.5],
            [1005, 10004, 0.48],
            [1002, 10003, 0.05],
            [1003, 10003, 21.25],
            [1004, 10003, 6.5],
            [1002, 10006, 0.002],
            [1003, 10006, 0.01],
            [1002, 10011, 0.033],
            [1003, 10007, 0.001],
            [1004, 10007, 0.001],
            [1005, 10007, 0.3],
            [1004, 10009, 0.035],
        ],
        columns=ingredients_columns,
    )

    assert result_df.to_dict() == expected_df.to_dict()


def test_prediction_join_ingredients():
    dp_columns = ['store_id', 'product_id', '1970-01-01', '1970-01-02']

    dp_df = pd.DataFrame(
        [
            [100, 1000, 1, 1],
            [100, 1001, 1, 1],
            [200, 1000, 1, 1],
            [200, 1001, 1, 1],
            [300, 1000, 1, 1],
            [300, 1001, 1, 1],
        ],
        columns=dp_columns,
    )

    ingredients_df = pd.DataFrame(
        [
            [1000, 10005, 0.2],
            [1001, 10005, 0.5],
            [1001, 10001, 14],
            [1001, 10008, 0.001],
            [1002, 10008, 0.025],
            [1000, 10008, 0.02],
            [1001, 10002, 0.1],
        ],
        columns=['product_id', 'ingredient_id', 'weight'],
    )

    purchasing_assortment_df = pd.DataFrame()
    purchasing_assortment_df['lavka_id'] = dp_df.product_id
    purchasing_assortment_df['warehouse_id'] = dp_df.store_id

    result_df = prediction._prediction_join_ingredients(
        dp_df, ingredients_df, purchasing_assortment_df,
    )
    result_df = result_df.set_index(['store_id', 'product_id'])
    result_df.columns = pd.to_datetime(result_df.columns)

    expected_df = pd.DataFrame(
        [
            [100, 10001, 14, 14],
            [200, 10001, 14, 14],
            [300, 10001, 14, 14],
            [100, 10002, 0.1, 0.1],
            [200, 10002, 0.1, 0.1],
            [300, 10002, 0.1, 0.1],
            [100, 10005, 0.7, 0.7],
            [200, 10005, 0.7, 0.7],
            [300, 10005, 0.7, 0.7],
            [100, 10008, 0.021, 0.021],
            [200, 10008, 0.021, 0.021],
            [300, 10008, 0.021, 0.021],
        ],
        columns=dp_columns,
    )
    expected_df = expected_df.set_index(['store_id', 'product_id'])
    expected_df.columns = pd.to_datetime(expected_df.columns)

    assert result_df.to_dict() == expected_df.to_dict()


def test_weight_products_generate():
    products_columns = [
        'product_id',
        'parent_id',
        'external_id',
        'lower_weight_limit',
        'upper_weight_limit',
        'vars',
    ]
    products_df = pd.DataFrame(
        [
            [100, 200, 1, pd.NA, pd.NA, '{"virtual_product": false}'],
            [200, 300, 2, 1000, pd.NA, '{"virtual_product": false}'],
            [
                500,
                600,
                3,
                pd.NA,
                2000,
                '{"imported": {"virtual_product": true}}',
            ],
            [
                600,
                700,
                4,
                3000,
                4000,
                '{"imported": {"virtual_product": true}}',
            ],
            [200, 500, 8, 5000, 6000, pd.NA],
        ],
        columns=products_columns,
    )
    result_df = _generate(products_df)
    expected_columns = [
        'parent_id',
        'product_id',
        'lowerWeightLimit',
        'upperWeightLimit',
    ]
    expected_df = pd.DataFrame([[2, 1, 1000, 1000]], columns=expected_columns)
    assert expected_df.to_dict() == result_df.to_dict()


def test_prediction_apply_rotation():
    prediction_df = pd.DataFrame(
        [
            (1, 111, 1.0, 0.0),
            (1, 113, 0.0, 1.0),
            (1, 211, 2.0, 2.0),
            (1, 213, 2.0, 2.0),
            (1, 413, 0.0, 0.0),
            (1, 511, 3.0, 3.0),
            (1, 611, 3.0, 3.0),
        ],
        columns=['store_id', 'product_id', '2020-02-12', '2020-02-13'],
    )
    rotation_results_df = pd.DataFrame(
        [
            (111, 'СЭНДВИЧИ И БУРГЕРЫ', 'МСК', True),
            (112, 'СЭНДВИЧИ И БУРГЕРЫ', 'МСК', True),
            (113, 'СЭНДВИЧИ И БУРГЕРЫ', 'МСК', False),
            (211, 'СУПЫ', 'МСК', True),
            (212, 'СУПЫ', 'МСК', True),
            (213, 'СУПЫ', 'МСК', False),
            (311, 'МОРОЖЕНОЕ', 'МСК', False),
            (312, 'МОРОЖЕНОЕ', 'МСК', False),
            (411, 'БЛИНЧИКИ', 'МСК', True),
            (412, 'БЛИНЧИКИ', 'МСК', True),
            (413, 'БЛИНЧИКИ', 'МСК', False),
            (511, 'ОВОЩИ', 'МСК', True),
            (512, 'ОВОЩИ', 'МСК', True),
            (611, 'ФРУКТЫ', 'МСК', True),
            (612, 'ФРУКТЫ', 'МСК', False),
        ],
        columns=['product_id', 'category_name', 'cluster', 'is_selected'],
    )
    stores_clusters_df = pd.DataFrame(
        [(1, 'МСК'), (2, 'МСК'), (3, 'МСК'), (4, 'МСК')],
        columns=['store_id', 'cluster'],
    )

    rotation_prediction = prediction._get_rotated_prediction(
        prediction_df, rotation_results_df, stores_clusters_df,
    )
    rotation_prediction_grouped = (
        rotation_prediction.merge(rotation_results_df, on='product_id')
        .groupby('category_name')
        .sum()
        .drop(columns=['store_id', 'product_id', 'is_selected'])
    )
    prediction_grouped_old = (
        prediction_df.merge(rotation_results_df, on='product_id')
        .groupby('category_name')
        .sum()
        .drop(columns=['store_id', 'product_id', 'is_selected'])
    )

    assert (
        rotation_prediction_grouped.to_dict()
        == prediction_grouped_old.to_dict()
    )


def test_prediction_add_analogs():
    prediction_columns = ['store_id', 'product_id', '1970-01-01', '1970-01-02']

    prediction_df = pd.DataFrame(
        [
            [100, 1000, 1, 1],
            [100, 1001, 1, 1],
            [100, 2201, 1, 1],
            [200, 1001, 1, 1],
            [200, 1002, 1, 1],
            [300, 1003, 1, 1],
            [300, 1004, 1, 1],
            [400, 4000, 2, 2],
            [400, 4001, 1, 1],
            [500, 5001, 1, 1],
            [500, 5002, 1, 1],
            [600, 6002, 1, 1],
            [700, 7002, 1, 1],
            [700, 7003, 1, 1],
        ],
        columns=prediction_columns,
    )

    pim_df = pd.DataFrame(
        [
            [2001, 1001],
            [2201, 2001],
            [2003, 1003],
            [1002, 2222],
            [1005, 2222],
            [4000, 4001],
            [5001, 5002],
            [6001, 6002],
            [7000, 7002],
            [7001, 7002],
            [7003, 7002],
        ],
        columns=['product_id', 'substitution'],
    )

    assortment_warehouses_df = pd.DataFrame(
        [
            [2001, 100],
            [2201, 100],
            [1001, 100],
            [2001, 200],
            [1003, 300],
            [4000, 400],
            [4001, 400],
            [5002, 500],
            [6001, 600],
            [7000, 700],
            [7002, 700],
            [7003, 700],
        ],
        columns=['lavka_id', 'warehouse_id'],
    )

    result_df = prediction._prediction_add_analogs(
        prediction_df, pim_df, assortment_warehouses_df, 0.5,
    )
    result_df = result_df.set_index(['store_id', 'product_id'])
    result_df.columns = pd.to_datetime(result_df.columns)
    expected_df = pd.DataFrame(
        [
            [100, 1000, 1, 1],
            [100, 1001, 0.5, 0.5],
            [200, 1001, 1, 1],
            [100, 2001, 0.5, 0.5],
            [100, 2201, 1, 1],
            [200, 2001, 1, 1],
            [200, 1002, 1, 1],
            [300, 1003, 1, 1],
            [300, 1004, 1, 1],
            [400, 4000, 2, 2],
            [400, 4001, 1, 1],
            [500, 5001, 1, 1],
            [500, 5002, 1, 1],
            [600, 6001, 1, 1],
            [600, 6002, 1, 1],
            [700, 7000, 0.5, 0.5],
            [700, 7002, 0.5, 0.5],
            [700, 7003, 1, 1],
        ],
        columns=prediction_columns,
    )

    expected_df = expected_df.set_index(['store_id', 'product_id'])
    expected_df.columns = pd.to_datetime(expected_df.columns)
    assert result_df.to_dict() == expected_df.to_dict()


def test_prediction_demand_new_cities():
    dp_columns = ['store_id', 'product_id', '1970-01-01', '1970-01-02']

    dp_df = pd.DataFrame(
        [
            [100, 1000, 1, 1],
            [100, 1001, 2, 4],
            [200, 1001, 2, 1],
            [200, 1002, 1, 1],
            [300, 1003, 1, 1],
            [300, 1004, 1, 1],
        ],
        columns=dp_columns,
    )

    forecast_new_city_df = pd.DataFrame(
        [
            [1001, 111024, 3],
            [1000, 222222, 1],  # does not affect result
            [1002, 111024, 0.5],
            [1111, 111024, 3],
        ],
        columns=['product_id', 'region_id', 'forecast'],
    )

    stores_df = pd.DataFrame(
        [[111024, 100], [111024, 200], [333333, 1000]],
        columns=['region_id', 'store_id'],
    )

    result_df = prediction._set_default_demand_prediction(
        dp_df, forecast_new_city_df, stores_df,
    )
    result_df = result_df.set_index(['store_id', 'product_id'])
    result_df.columns = pd.to_datetime(result_df.columns)

    expected_df = pd.DataFrame(
        [
            [100, 1000, 1.0, 1.0],
            [100, 1001, 3.0, 4.0],  # changed
            [200, 1001, 3.0, 3.0],  # changed
            [100, 1002, 0.5, 0.5],  # added
            [200, 1002, 1.0, 1.0],
            [300, 1003, 1.0, 1.0],
            [300, 1004, 1.0, 1.0],
            [100, 1111, 3, 3],  # added
            [200, 1111, 3, 3],  # added
        ],
        columns=dp_columns,
    )
    expected_df = expected_df.set_index(['store_id', 'product_id'])
    expected_df.columns = pd.to_datetime(expected_df.columns)
    assert result_df.to_dict() == expected_df.to_dict()


def test_seasonal(get_file_path):
    raw_seasonal_df = read_file(
        get_file_path('seasonal/raw_seasonal.csv'), from_yt,
    )
    seasonal_table = Table(name='seasonal', dataframe=raw_seasonal_df)
    pim_df = read_file(get_file_path('seasonal/pim.csv'), from_yt)
    stores_df = read_file(get_file_path('seasonal/stores.csv'), from_yt)
    assortment_warehouses_df = read_file(
        get_file_path('seasonal/assortment_warehouses.csv'), to_yt,
    )

    result_table = seasonal.join(
        seasonal_table=seasonal_table,
        pim_df=pim_df,
        stores_df=stores_df,
        assortment_warehouses_df=assortment_warehouses_df,
        calc_date=datetime.date(2021, 5, 1),
    )
    result_df = result_table.dataframe[SEASONAL_COLUMNS]

    # TODO: add test cases when only product_id or store_id are set
    #  in raw_seasonal
    expected_df = pd.DataFrame(
        [
            # Following store_id/product_id pairs are skipped because they
            # are not in assortment_warehouses.csv:
            # 116365, 13906
            # 103811, 10379
            [391727, 13906, '2021-05-01', '2021-05-05', 0.99, 1],
            [106375, 13906, '2021-05-01', '2021-05-05', 0.99, 1],
            [112330, 13906, '2021-05-03', '2021-05-03', 0.95, 1],
            [103811, 13906, '2021-05-03', '2021-05-03', 0.95, 1],
            [116365, 10379, '2021-05-03', '2021-05-03', 1.70, 1],
            [391727, 10379, '2021-05-03', '2021-05-03', 1.70, 1],
            [106375, 10379, '2021-05-03', '2021-05-03', 1.70, 1],
            [116365, 10379, '2021-05-10', '2021-05-10', 1.30, 1],
            [391727, 10379, '2021-05-10', '2021-05-10', 1.30, 1],
            [106375, 10379, '2021-05-10', '2021-05-10', 1.30, 1],
            [112330, 10379, '2021-05-03', '2021-05-03', 1.60, 1],
            [112330, 10379, '2021-05-10', '2021-05-10', 1.20, 1],
            [19, 19, '2021-05-01', '2021-05-05', 0.019, 1],
            [19, 18, '2021-05-01', '2021-05-05', 0.019, 1],
            [18, 19, '2021-05-01', '2021-05-05', 0.019, 1],
            [18, 18, '2021-05-01', '2021-05-05', 0.019, 1],
            [2222, 200, '2021-05-01', '2021-05-05', 1.70, 1],
            [19, 19, '2021-05-01', '2021-05-05', 0.19, 3],
            [19, 18, '2021-05-01', '2021-05-05', 0.19, 3],
            [1111, 100, '2021-05-03', '2021-05-07', 1.13, 1],
            [19, 19, '2021-05-01', '2021-05-05', 1.9, 2],
            [18, 19, '2021-05-01', '2021-05-05', 1.9, 2],
        ],
        columns=SEASONAL_COLUMNS,
    )
    expected_df['start_date'] = pd.to_datetime(
        expected_df['start_date'], errors='coerce', format='%Y-%m-%d',
    )
    expected_df['ending_date'] = pd.to_datetime(
        expected_df['ending_date'], errors='coerce', format='%Y-%m-%d',
    )

    assert result_df.to_dict() == expected_df.to_dict()


@pytest.mark.parametrize(
    'local_file_path',
    ['empty/raw_seasonal.csv', 'does_not_exist/raw_seasonal.csv'],
)
def test_seasonal_empty_or_not_exist_table(
        local_file_path, get_file_path, get_directory_path,
):
    """Script should work correctly if table is empty"""
    raw_seasonal_df = read_file(
        os.path.join(get_directory_path('seasonal'), local_file_path), from_yt,
    )
    seasonal_table = Table(name='seasonal', dataframe=raw_seasonal_df)
    pim_df = read_file(get_file_path('seasonal/pim.csv'), from_yt)
    stores_df = read_file(get_file_path('seasonal/stores.csv'), from_yt)
    assortment_warehouses_df = read_file(
        get_file_path('seasonal/assortment_warehouses.csv'), to_yt,
    )

    result_table = seasonal.join(
        seasonal_table=seasonal_table,
        pim_df=pim_df,
        stores_df=stores_df,
        assortment_warehouses_df=assortment_warehouses_df,
    )
    result_df = result_table.dataframe[SEASONAL_COLUMNS]

    expected_df = pd.DataFrame([], columns=SEASONAL_COLUMNS)

    assert result_df.to_dict() == expected_df.to_dict()


def test_filter_rows_by_dates():
    now = datetime.date(1970, 3, 1)
    raw_df = pd.DataFrame(
        [
            # min=1970-03-01, max=1970-03-31
            [100, 1, '1970-03-05', '1970-03-10', 1.0, 1],  # min, d1, d2, max
            [200, 2, '1970-01-01', '1970-01-05', 1.0, 1],  # d1, d2, min, max
            [300, 3, '1970-02-01', '1970-03-05', 1.0, 1],  # d1, min, d2, max
            [400, 4, '1970-03-07', '1970-04-05', 1.0, 1],  # min, d1, max, d2
            [500, 5, '1970-05-07', '1970-05-10', 1.0, 1],  # min, max, d1, d2
            [600, 6, '1970-01-01', '1970-05-01', 1.0, 1],  # d1, min, max, d2
            [700, 7, '1970-03-01', '1970-05-01', 1.0, 1],  # min==d1, max, d2
            [800, 8, '1970-01-01', '1970-03-31', 1.0, 1],  # d1, min, max==d2
            [900, 9, '1970-01-01', '1970-03-01', 1.0, 1],  # d1, d2==min, max
            [1000, 10, '1970-03-31', '1970-05-01', 1.0, 1],  # min, max==d1, d2
        ],
        columns=SEASONAL_COLUMNS,
    )
    raw_df['start_date'] = pd.to_datetime(
        raw_df['start_date'], errors='coerce', format='%Y-%m-%d',
    )
    raw_df['ending_date'] = pd.to_datetime(
        raw_df['ending_date'], errors='coerce', format='%Y-%m-%d',
    )
    result_df = seasonal._filter_rows_by_dates(raw_df, now)

    expected_df = pd.DataFrame(
        [
            [100, 1, '1970-03-05', '1970-03-10', 1.0, 1],
            [300, 3, '1970-02-01', '1970-03-05', 1.0, 1],
            [400, 4, '1970-03-07', '1970-04-05', 1.0, 1],
            [600, 6, '1970-01-01', '1970-05-01', 1.0, 1],
            [700, 7, '1970-03-01', '1970-05-01', 1.0, 1],
            [800, 8, '1970-01-01', '1970-03-31', 1.0, 1],
            [900, 9, '1970-01-01', '1970-03-01', 1.0, 1],
            [1000, 10, '1970-03-31', '1970-05-01', 1.0, 1],
        ],
        columns=SEASONAL_COLUMNS,
    )
    expected_df['start_date'] = pd.to_datetime(
        expected_df['start_date'], errors='coerce', format='%Y-%m-%d',
    )
    expected_df['ending_date'] = pd.to_datetime(
        expected_df['ending_date'], errors='coerce', format='%Y-%m-%d',
    )
    assert result_df.to_dict() == expected_df.to_dict()
