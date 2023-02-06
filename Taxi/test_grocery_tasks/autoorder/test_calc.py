# pylint: disable=invalid-name, protected-access
import pathlib
import tempfile

import pandas as pd

from grocery_tasks.autoorder import data_norm
from grocery_tasks.autoorder import run_calc
from grocery_tasks.autoorder.calc import calc
from grocery_tasks.autoorder.calc import experiments
from grocery_tasks.autoorder.calc.post_calc import add_sales
from grocery_tasks.autoorder.config import AutoorderCalcConfig
from grocery_tasks.autoorder.config import MultiprocessingConfig
from grocery_tasks.autoorder.data_norm import read_file
from grocery_tasks.autoorder.data_norm import to_yt
from grocery_tasks.autoorder.schema.yt.result_schema import RESULT_SCHEMA
from grocery_tasks.autoorder.table import get_rc_input_tables

_EXPECTED_DF_LENGTH = {
    'today_schedule': 47,
    'stock': 13,
    'stock_wms': 6,
    'stores': 7,
    'orders_on_the_way': 18,
    'pim': 22,
    'suppliers': 79,
    'warehouses': 89,
    'assortment_warehouses': 58,
    'warehouse_analog': 1,
    'seasonal': 6,
    'events': 6,
    'sales': 3,
    'prediction': 40,
    'pick_by_line': 4,
    'fixed_order': 6,
    'safety_stock': 29,
    'safety_stock_ml': 3,
    'write_offs': 15,
    'stowage_backlog': 2,
    'pbl_distribution': 2,
    'weight_products': 21,
    'min_order_sum': 3,
}

CALC_CONFIG = {'category_exception': ['Мясо, рыба, птица']}

MULTIPROCESSING_CONFIG = {'num_processes': 8}


def test_calc(
        get_file_path, get_directory_path, overwrite_options: dict = None,
):
    """
    Ввёл аргумент overwrite_options
    Зачем: позволяет переопределять test_calc, для тестирования
    различных вариаций входных данных, и не плодить при этом
    множество одинаковых тестов и входных данных
    Как пользоваться: переопределить входные данные,
    размер датафрейма, результат
    'paths': {
        'orders_on_the_way': 'empty/orders_on_the_way.csv',
        'expected_result': 'empty/expected_result.csv',
    },
    'expected_df_length': {'orders_on_the_way': 0}
    """
    if overwrite_options is None:
        overwrite_options = {}
    _EXPECTED_DF_LENGTH.update(overwrite_options.get('expected_df_length', {}))

    def test_result_schema(_result_path: str):
        _result_df = read_file(_result_path, to_yt)
        assert set(_result_df.columns.tolist()) == set(
            column['name'] for column in RESULT_SCHEMA
        ), 'Result dataframe doesn\'t match result schema'

    with tempfile.TemporaryDirectory() as temp_dir:

        order_date = pd.to_datetime('2020-02-12')
        order_date = order_date.replace(tzinfo=None)
        region_name = 'russia_center'

        yt_paths = {
            'yt_base_path': '',
            'yt_replica_path': '',
            'yt_external_path': '',
            'yt_eda_analytics_prefix': '',
        }
        input_tables = get_rc_input_tables(
            local_base_path=temp_dir,
            yt_paths=yt_paths,
            region_names=[region_name],
        )
        tmp_dir = pathlib.Path(temp_dir)

        for input_table in input_tables:
            input_table.use_common_yt_src()
            src_name = input_table.name
            file_path = get_file_path(
                overwrite_options.get('paths', {}).get(
                    src_name, f'curr_data/{src_name}.csv',
                ),
            )
            if src_name in (
                    'pim',
                    'prediction',
                    'stores',
                    'write_offs',
                    'safety_stock_ml',
                    'stowage_backlog',
                    'pbl_distribution',
                    'weight_products',
            ):
                df = pd.read_csv(file_path)
            else:
                df = data_norm.read_file(file_path, to_yt)
            assert len(df) == _EXPECTED_DF_LENGTH[src_name], src_name
            df.to_csv(str(tmp_dir.joinpath(f'{src_name}.csv')), index=False)

        result_path = run_calc.CALC_DST.format(local_base_path=tmp_dir)
        calc.calc(
            calc_paths=run_calc._get_calc_paths(input_tables, region_name),
            result_path=result_path,
            order_date=order_date,
            calc_config=AutoorderCalcConfig(CALC_CONFIG),
            mp_config=MultiprocessingConfig(MULTIPROCESSING_CONFIG),
            calc_experiments=experiments.Experiments(None),
            region_name=region_name,
        )

        test_result_schema(result_path)

        common_index = [
            'warehouse_id',
            'supplier_id',
            'lavka_id',
            'supply_date',
            'order_id',
        ]

        result_df = pd.read_csv(result_path).set_index(common_index)

        assert len(result_df) == 40, 'Correct number of rows in result'

        validated_result_df = pd.read_csv(
            get_file_path(
                overwrite_options.get('paths', {}).get(
                    'expected_result', 'curr_data/expected_result.csv',
                ),
            ),
        ).set_index(common_index)

        assert len(validated_result_df) == 40, (
            'Correct number of rows in validated result',
        )

        round_mapping = {
            'unrounded_order': 2,
            'total_prediction': 2,
            'order_price_with_VAT': 2,
            'order_sum': 2,
            'available_for_sale': 2,
            'quant': 2,
            'need': 2,
            'orders_on_the_way': 2,
            'sales_in_a_week': 2,
            'stock_prediction': 2,
        }

        result_df = result_df.round(round_mapping)
        validated_result_df = validated_result_df.round(round_mapping)

        for ind, validated_row in validated_result_df.iterrows():
            validated_row = validated_row.to_dict()
            result_row = result_df.xs(ind).to_dict()
            for k, v in validated_row.items():
                if pd.isnull(v):
                    assert pd.isnull(result_row[k]), (
                        f'Correct values for field {k} in row: {ind}',
                    )
                    continue
                assert v == result_row[k], (
                    f'Correct values for field {k} in row: {ind}',
                )


def test_add_sales(get_file_path, open_file):
    received_df = add_sales(
        sales_path=get_file_path('sales/sales.csv'),
        result_df=to_yt.result(open_file('sales/result.csv')),
    ).set_index(['lavka_id', 'warehouse_id'])
    received_df = received_df.drop(columns='order_id')  # quick fix

    expected_df = pd.read_csv(
        get_file_path('sales/final_result.csv'),
    ).set_index(['lavka_id', 'warehouse_id'])
    for ind, row in expected_df.iterrows():
        received_row = received_df.xs(ind)
        for k, v in received_row.items():
            if pd.isnull(v):
                assert pd.isnull(row[k]), (
                    f'Correct values for field {k} in row: {ind}',
                )
                continue
            assert v == row[k], (
                f'Correct values for field {k} in row: {ind}',
            )


def test_empty_orders_on_the_way(get_file_path, open_file):
    test_calc(
        get_file_path,
        open_file,
        overwrite_options={
            'paths': {
                'orders_on_the_way': 'empty/orders_on_the_way.csv',
                'stowage_backlog': 'empty/stowage_backlog.csv',
                'expected_result': 'empty/expected_result.csv',
            },
            'expected_df_length': {
                'orders_on_the_way': 0,
                'stowage_backlog': 0,
            },
        },
    )
